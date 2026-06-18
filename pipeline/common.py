"""Fælles hjælpefunktioner for "Broke to Wealth"-pipelinen.

Holder stier, .env-indlæsning, atomiske filskrivninger, JSON-serialisering
(som SKAL matche den gamle pipelines format 1:1) og Gemini-billedkald
samlet ét sted, så de fem trin-scripts kan forblive små og læsbare.
"""

import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Stier — alt er relativt til denne fil, ingen hardcodede absolutte stier.
# pipeline/ ligger i projektroden, så roden er én mappe op.
# ---------------------------------------------------------------------------
PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PIPELINE_DIR.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"   # manuskripter: scripts/<slug>.txt
OUTPUT_DIR = PROJECT_ROOT / "output"     # resultater:   output/<slug>/
ENV_FILE = PROJECT_ROOT / ".env"         # API-nøgler (holdes ude af git)


def log(msg: str) -> None:
    """Ensartet logging til stdout (flush så fremdrift ses live)."""
    print(msg, flush=True)


def die(msg: str) -> None:
    """Fejl højt og tydeligt, og stop med exit-kode 1."""
    print(f"\nFEJL: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def validate_slug(slug: str) -> str:
    """Afviser slugs der ville give path-traversal ('../x', 'a/b') eller
    ødelagte filnavne. Kaldes af run.py og alle trin-scripts før OUTPUT_DIR / slug."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,80}", slug):
        die(f"Ugyldig slug '{slug}' — brug kun små bogstaver a-z, 0-9 og bindestreg/underscore "
            "(fx 'zero-to-10k').")
    return slug


# ---------------------------------------------------------------------------
# .env / API-nøgler
# ---------------------------------------------------------------------------
_env_loaded = False


def load_env() -> None:
    """Indlæser .env fra projektroden (kun én gang pr. kørsel)."""
    global _env_loaded
    if _env_loaded:
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        die("Pakken 'python-dotenv' mangler — kør:\n"
            f"  pip install -r {PIPELINE_DIR / 'requirements.txt'}")
    load_dotenv(ENV_FILE)
    _env_loaded = True


def require_env(name: str, hint: str) -> str:
    """Henter en påkrævet miljøvariabel — fejler højt med vejledning hvis den mangler."""
    load_env()
    value = os.environ.get(name, "").strip()
    if not value:
        die(f"Miljøvariablen {name} mangler eller er tom.\n"
            f"  -> Tilføj linjen '{name}=...' i {ENV_FILE}\n"
            f"  -> {hint}")
    return value


# ---------------------------------------------------------------------------
# Atomiske filskrivninger — temp-fil + os.replace, så en afbrudt kørsel
# aldrig efterlader halvskrevne/korrupte filer. Temp-navnet indeholder pid,
# så to samtidige kørsler på samme slug ikke kan promovere hinandens halve filer.
# ---------------------------------------------------------------------------
def _tmp_name(path: Path) -> Path:
    return path.with_name(f"{path.name}.{os.getpid()}.tmp")


def dump_json(data, path: Path) -> None:
    """Skriver JSON PRÆCIS som den gamle pipeline gjorde (datakontrakt §2-4):
    indent=1 (ét mellemrums indrykning), ASCII, INGEN afsluttende newline.
    """
    tmp = _tmp_name(path)
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def write_bytes_atomic(path: Path, data: bytes) -> None:
    """Skriver rå bytes (fx mp3) atomisk."""
    tmp = _tmp_name(path)
    tmp.write_bytes(data)
    os.replace(tmp, path)


def save_png_atomic(img, path: Path) -> None:
    """Gemmer et PIL-billede som PNG atomisk."""
    tmp = _tmp_name(path)
    img.save(tmp, format="PNG")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Navngivning (datakontrakt §4): scene_NNNN_tSS.SSs.png
# Bruges af både build_scenes.py (timeline.json) og generate_images.py,
# så formlen kun findes ét sted.
# ---------------------------------------------------------------------------
def scene_filename(index: int, start: float) -> str:
    """4-cifret nulpaddet 1-baseret sceneindeks + starttid med 2 decimaler."""
    return f"scene_{index:04d}_t{start:.2f}s.png"


# ---------------------------------------------------------------------------
# ffmpeg/ffprobe (systemafhængighed: brew install ffmpeg)
# ---------------------------------------------------------------------------
def ffprobe_duration(path: Path) -> float:
    """Returnerer varigheden af en medie-fil i sekunder via ffprobe."""
    cmd = ["ffprobe", "-v", "error",
           "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        die("ffprobe/ffmpeg er ikke installeret — kør: brew install ffmpeg")
    except subprocess.CalledProcessError as e:
        die(f"ffprobe fejlede på {path}:\n{e.stderr}")
    out = result.stdout.strip()
    try:
        return float(out)
    except ValueError:  # ffprobe printer 'N/A'/tom streng på korrupte filer
        die(f"ffprobe kunne ikke bestemme varigheden af {path} (output: {out!r}) "
            "— filen er muligvis korrupt; slet den og kør trinnet igen.")


# ---------------------------------------------------------------------------
# Billedhjælpere (PIL)
# ---------------------------------------------------------------------------
def fit_image(img, width: int, height: int):
    """Konverterer til RGB og skalerer + center-beskærer ("cover") til præcis
    width x height. Bruges til at garantere kontrakt-dimensionerne uanset
    hvad Gemini-modellen leverer (1344x768 scenebilleder, 1280x720 thumbnail).
    """
    from PIL import Image  # lazy import — kun nødvendig i billed-trinnene

    img = img.convert("RGB")  # kontrakten kræver RGB uden alpha (colortype 2)
    scale = max(width / img.width, height / img.height)
    new_w = max(width, math.ceil(img.width * scale))
    new_h = max(height, math.ceil(img.height * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - width) // 2
    top = (new_h - height) // 2
    return img.crop((left, top, left + width, top + height))


# ---------------------------------------------------------------------------
# Gemini ("nano-banana") billedgenerering — delt af scenebilleder + thumbnail.
# Prøver nyeste model først og falder tilbage hvis et model-id ikke findes
# (id'erne har historisk skiftet mellem preview/stabile navne).
# ---------------------------------------------------------------------------
GEMINI_IMAGE_MODELS = [
    "gemini-3.1-flash-image",          # "Nano Banana 2" — anbefalet (juni 2026)
    "gemini-3.1-flash-image-preview",  # ældre preview-id for samme model
    "gemini-2.5-flash-image",          # stabil legacy-fallback
]

_genai_client = None
_working_model = None  # husker hvilken model der virkede, så vi ikke prøver forfra
_working_text_model = None  # samme idé for tekst-modellen (dynamiske thumbnail-idéer)
GEMINI_TEXT_MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

# Batch-tilstand: ÉT asynkront job for alle billeder = 50% rabat (op til 24t turnaround).
# Slå fra med BTW_BATCH=0 (synkron, fuld pris, hurtigere ved hastværk).
BATCH_IMAGES = os.environ.get("BTW_BATCH", "1") != "0"


def _pil_from_response(response):
    """Find første IMAGE-part i en GenerateContentResponse -> PIL-billede (ellers None).
    Bygger selv PIL fra rå bytes (part.as_image() giver google-genai's egen type)."""
    for part in (getattr(response, "parts", None) or []):
        if part.inline_data is not None and part.inline_data.data:
            from io import BytesIO
            from PIL import Image as PILImage
            return PILImage.open(BytesIO(part.inline_data.data))
    return None


def gemini_generate_image(prompt: str):
    """Genererer ét 16:9-billede fra en tekstprompt og returnerer et PIL-billede."""
    global _genai_client, _working_model

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        die("Pakken 'google-genai' mangler — kør:\n"
            f"  pip install -r {PIPELINE_DIR / 'requirements.txt'}")

    if _genai_client is None:
        require_env("GEMINI_API_KEY", "Opret en nøgle på https://aistudio.google.com/apikey")
        _genai_client = genai.Client()  # læser GEMINI_API_KEY fra miljøet

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
    )

    def _is_not_found(e: Exception) -> bool:
        try:
            from google.genai import errors
            if isinstance(e, errors.APIError) and getattr(e, "code", None) == 404:
                return True
        except ImportError:
            pass
        text = str(e).lower()
        return "not_found" in text or "not found" in text or "404" in text

    models = [_working_model] if _working_model else GEMINI_IMAGE_MODELS
    last_error = None
    for model in models:
        try:
            response = _genai_client.models.generate_content(
                model=model, contents=[prompt], config=config)
        except Exception as e:  # model-id findes ikke -> prøv næste i listen
            if _is_not_found(e):
                last_error = e
                continue
            raise
        # Responsen kan indeholde både TEXT- og IMAGE-parts — find billedet.
        img = _pil_from_response(response)
        if img is not None:
            _working_model = model
            return img
        raise RuntimeError(f"Gemini-modellen {model} returnerede intet billede "
                           "(muligvis blokeret af sikkerhedsfilter) — prøv igen.")
    # En cached model kan trækkes tilbage midt i en kørsel — nulstil cachen og
    # prøv hele fallback-listen forfra, før vi giver op.
    if _working_model is not None:
        _working_model = None
        return gemini_generate_image(prompt)
    raise RuntimeError(f"Ingen af Gemini-billedmodellerne {GEMINI_IMAGE_MODELS} "
                       f"kunne kaldes. Sidste fejl: {last_error}")


def gemini_generate_images_batch(prompts, *, poll_interval=20, max_wait=3600, label="billeder"):
    """Genererer mange 16:9-billeder i ÉT asynkront Batch-job (50% rabat vs. realtid).

    Returnerer en liste af PIL-billeder i SAMME rækkefølge som prompts (None for
    de billeder der fejlede — kalderen falder tilbage til synkron generering for dem).
    Rejser ved totalt jobsvigt, så kalderen kan falde helt tilbage til synkron mode.
    """
    global _genai_client, _working_model
    if not prompts:
        return []
    import time
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        die("Pakken 'google-genai' mangler — kør:\n"
            f"  pip install -r {PIPELINE_DIR / 'requirements.txt'}")

    if _genai_client is None:
        require_env("GEMINI_API_KEY", "Opret en nøgle på https://aistudio.google.com/apikey")
        _genai_client = genai.Client()

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9"),
    )
    src = [types.InlinedRequest(contents=[p], config=config) for p in prompts]

    def _is_not_found(e):
        try:
            from google.genai import errors
            if isinstance(e, errors.APIError) and getattr(e, "code", None) == 404:
                return True
        except ImportError:
            pass
        t = str(e).lower()
        return "not_found" in t or "not found" in t or "404" in t

    # Samme model-fallback som synkron: prøv cached/nyeste først, fald tilbage ved 404.
    models = [_working_model] if _working_model else list(GEMINI_IMAGE_MODELS)
    job = last_error = None
    for model in models:
        try:
            job = _genai_client.batches.create(model=model, src=src)
            _working_model = model
            break
        except Exception as e:
            if _is_not_found(e):
                last_error = e
                continue
            raise
    if job is None:
        raise RuntimeError(f"Kunne ikke oprette batch-job (model ikke fundet). Sidste fejl: {last_error}")

    log(f"  Batch-job oprettet ({len(prompts)} {label}): {job.name}")
    TERMINAL = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED",
                "JOB_STATE_EXPIRED", "JOB_STATE_PARTIALLY_SUCCEEDED"}
    waited = 0
    while True:
        state = getattr(job.state, "name", None) or str(job.state)
        if state in TERMINAL:
            break
        if waited >= max_wait:
            raise RuntimeError(f"Batch-job {job.name} blev ikke færdigt inden for {max_wait}s "
                               f"(status: {state}). Jobbet kører videre hos Google.")
        log(f"  Batch {label}: {state} ... ({waited}s)")
        time.sleep(poll_interval)
        waited += poll_interval
        job = _genai_client.batches.get(name=job.name)

    state = getattr(job.state, "name", None) or str(job.state)
    if state in ("JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"):
        raise RuntimeError(f"Batch-job {job.name} sluttede som {state}: {getattr(job, 'error', None)}")

    dest = getattr(job, "dest", None)
    responses = (getattr(dest, "inlined_responses", None) or []) if dest else []
    images = []
    for r in responses:
        if getattr(r, "error", None) or getattr(r, "response", None) is None:
            images.append(None)
        else:
            images.append(_pil_from_response(r.response))
    if len(images) < len(prompts):          # manglende svar -> synkron fallback hos kalderen
        images += [None] * (len(prompts) - len(images))
    ok = sum(1 for i in images if i is not None)
    log(f"  Batch {label} færdig ({state}): {ok}/{len(prompts)} billeder modtaget.")
    return images[:len(prompts)]


def gemini_generate_text(prompt: str, *, as_json: bool = False) -> str:
    """Et tekst-kald til Gemini (bruges fx til dynamiske thumbnail-idéer).
    as_json=True beder modellen om ren JSON. Falder tilbage gennem GEMINI_TEXT_MODELS
    hvis et model-id ikke findes."""
    global _genai_client, _working_text_model
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        die("Pakken 'google-genai' mangler — kør:\n"
            f"  pip install -r {PIPELINE_DIR / 'requirements.txt'}")
    if _genai_client is None:
        require_env("GEMINI_API_KEY", "Opret en nøgle på https://aistudio.google.com/apikey")
        _genai_client = genai.Client()
    config = types.GenerateContentConfig(response_mime_type="application/json") if as_json else None

    def _is_not_found(e):
        t = str(e).lower()
        return "not_found" in t or "not found" in t or "404" in t

    models = [_working_text_model] if _working_text_model else list(GEMINI_TEXT_MODELS)
    last_error = None
    for model in models:
        try:
            response = _genai_client.models.generate_content(
                model=model, contents=[prompt], config=config)
        except Exception as e:
            if _is_not_found(e):
                last_error = e
                continue
            raise
        _working_text_model = model
        return response.text or ""
    if _working_text_model is not None:   # cached model trukket tilbage -> prøv listen forfra
        _working_text_model = None
        return gemini_generate_text(prompt, as_json=as_json)
    raise RuntimeError(f"Ingen af Gemini-tekstmodellerne {GEMINI_TEXT_MODELS} kunne kaldes. "
                       f"Sidste fejl: {last_error}")
