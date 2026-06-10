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
        # NB: part.as_image() returnerer google-genai's egen Image-type (uden
        # .convert/.resize), så vi bygger selv et PIL-billede fra de rå bytes.
        for part in (response.parts or []):
            if part.inline_data is not None and part.inline_data.data:
                _working_model = model
                from io import BytesIO
                from PIL import Image as PILImage
                return PILImage.open(BytesIO(part.inline_data.data))
        raise RuntimeError(f"Gemini-modellen {model} returnerede intet billede "
                           "(muligvis blokeret af sikkerhedsfilter) — prøv igen.")
    # En cached model kan trækkes tilbage midt i en kørsel — nulstil cachen og
    # prøv hele fallback-listen forfra, før vi giver op.
    if _working_model is not None:
        _working_model = None
        return gemini_generate_image(prompt)
    raise RuntimeError(f"Ingen af Gemini-billedmodellerne {GEMINI_IMAGE_MODELS} "
                       f"kunne kaldes. Sidste fejl: {last_error}")
