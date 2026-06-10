"""Trin 3: Scenebilleder — scenes.json -> images/scene_NNNN_tSS.SSs.png.

Ét billede pr. scene via Gemini ("nano-banana") med kanalens master-prompt
(ordret fra docs/BRAND.md). Output normaliseres til kontraktens 1344x768
PNG RGB (kontrakt §5), så renderen altid får samme input.

Idempotent/resume-bar: billeder der allerede findes springes over — slet
dårlige billeder i images/ og kør scriptet igen for kun at regenerere dem.
"""

import argparse
import json
import time
from pathlib import Path

import common

# Den faste figur — kanalens "ansigt" (krav for YouTubes faceless-politik).
# Defineret KUN her; skift figuren ét sted og alle prompts følger med.
DEFAULT_CHARACTER = "a simple bald round-headed stick man wearing a small black necktie"

# Master-prompten — ordret fra docs/BRAND.md. {SCENE} = scenens narration
# (eller et manuelt udfyldt 'visual'-felt); {CHARACTER} = DEFAULT_CHARACTER.
MASTER_PROMPT = (
    "A crude, childlike drawing made in MS Paint illustrating this idea: {SCENE}. "
    "STYLE RULES (must follow exactly): extremely simple beginner doodle drawn quickly "
    "by hand with a computer mouse; thick wobbly uneven black outlines; flat solid fill "
    "colors; plain pure-white background; NO shading, NO gradients, NO 3D, NO photorealism, "
    "NO cinematic lighting, NO fine detail. It should look like someone who is bad at "
    "drawing made it in 30 seconds. Clear and readable, single simple scene, lots of empty "
    "white space. Finance and money theme. Whenever a person appears, draw the SAME "
    "recurring character: {CHARACTER}. Keep him identical every time. "
    "16:9 horizontal composition."
)

# Negativ prompt — ordret fra docs/BRAND.md. Gemini har ingen dedikeret
# negativ-prompt-parameter, så den sendes som en eksplicit forbudsliste
# i slutningen af selve prompten.
NEGATIVE_PROMPT = ("photorealistic, realistic, 3d render, detailed, shaded, gradient, "
                   "cinematic, professional illustration, beautiful, polished")

IMG_WIDTH, IMG_HEIGHT = 1344, 768  # kontrakt §5 — renderen opskalerer til 1920x1080
RETRIES = 3                        # alm. transiente fejl pr. billede før vi giver op
RETRIES_RATE = 6                   # rate limits (429) — lange videoer (185 scener) RAMMER
                                   # kvote-lofter; kræver tålmodighed, ikke hurtig opgivelse


def build_prompt(scene: dict) -> str:
    """Master-prompt for én scene. Tomt 'visual' -> narrationen bruges direkte."""
    motif = (scene.get("visual") or "").strip() or scene["text"]
    prompt = MASTER_PROMPT.format(SCENE=motif, CHARACTER=DEFAULT_CHARACTER)
    return f"{prompt}\n\nNEGATIVE PROMPT — the image must contain NONE of this: {NEGATIVE_PROMPT}"


def _is_rate_limit(e: Exception) -> bool:
    """429/RESOURCE_EXHAUSTED skal behandles som 'vent længe', ikke 'giv op'."""
    try:
        from google.genai import errors
        if isinstance(e, errors.APIError) and getattr(e, "code", None) == 429:
            return True
    except ImportError:
        pass
    text = str(e)
    return "429" in text or "RESOURCE_EXHAUSTED" in text


def _generate_with_retry(prompt: str, label: str):
    """Kalder Gemini med retry. Rate limits (429) får flere forsøg og
    eksponentiel ventetid op til 2 min — alm. fejl giver hurtigere op."""
    last_error = None
    attempt = 0
    while True:
        attempt += 1
        try:
            return common.gemini_generate_image(prompt)
        except SystemExit:
            raise
        except Exception as e:
            last_error = e
            if _is_rate_limit(e):
                limit, delay = RETRIES_RATE, min(120, 15 * 2 ** (attempt - 1))
                kind = "rate limit"
            else:
                limit, delay = RETRIES, 5 * attempt
                kind = "API-fejl"
            common.log(f"    forsøg {attempt}/{limit} ({kind}): {e}")
            if attempt >= limit:
                break
            common.log(f"    venter {delay} s ...")
            time.sleep(delay)
    common.die(f"Kunne ikke generere {label} efter {attempt} forsøg. Sidste fejl: {last_error}")


def run(out_dir: Path, force: bool = False) -> tuple[int, int]:
    """Genererer manglende scenebilleder. Returnerer (genereret, sprunget over)."""
    scenes_path = out_dir / "scenes.json"
    if not scenes_path.exists():
        common.die(f"{scenes_path} findes ikke — kør build_scenes.py først.")
    scenes = json.loads(scenes_path.read_text(encoding="utf-8"))

    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0
    for scene in scenes:
        path = images_dir / common.scene_filename(scene["index"], scene["start"])
        if path.exists() and not force:
            skipped += 1
            continue  # idempotent: regenererer kun det der mangler
        common.log(f"  [{scene['index']}/{len(scenes)}] {path.name} ...")
        image = _generate_with_retry(build_prompt(scene), path.name)
        image = common.fit_image(image, IMG_WIDTH, IMG_HEIGHT)  # garanterer 1344x768 RGB
        common.save_png_atomic(image, path)
        generated += 1

    common.log(f"  Billeder: {generated} genereret, {skipped} fandtes allerede "
               f"({len(scenes)} scener i alt).")
    return generated, skipped


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trin 3: scenes.json -> images/ (ét doodle-billede pr. scene)")
    parser.add_argument("slug", help="videonavn — arbejder i output/<slug>/")
    parser.add_argument("--force", action="store_true",
                        help="regenerér ALLE billeder (default: kun manglende)")
    args = parser.parse_args()
    common.validate_slug(args.slug)
    run(common.OUTPUT_DIR / args.slug, force=args.force)


if __name__ == "__main__":
    main()
