"""Trin 5: Thumbnail — Gemini -> output/<slug>/thumbnail.png (1280x720).

Samme doodle-stil som videoen + den faste figur (BRAND.md-konventioner):
STOR tekst (2-4 ord), høj kontrast, ét tydeligt motiv.

VIGTIGT — validering: en tidligere kørsel producerede en defekt 93 KB-thumbnail
(typisk størrelse er ~750-950 KB). Derfor valideres resultatet (korrekte
dimensioner + filstørrelse > 200 KB) og der retries én gang ved fejl.
"""

import argparse
from pathlib import Path

import common
from generate_images import (DEFAULT_CHARACTER, NEGATIVE_PROMPT,  # figur defineres KUN ét sted
                             _generate_with_retry)

WIDTH, HEIGHT = 1280, 720   # YouTube-standard (kontrakt §9)
# Defekt-detektor: ren filstørrelse. Empirisk kalibreret mod de 5 eksisterende
# thumbnails: de 4 sunde er 750-944 KB, den kendte defekte er 92 KB — og
# indholds-statistik (gråtone-stddev, farveantal) kan IKKE skelne dem (målt:
# den defekte har stddev 87,9 / 64 farver, helt på niveau med de sunde).
# 200 KB ligger midt i 8x-gabet.
MIN_BYTES = 200_000
ATTEMPTS = 2                # 1 forsøg + 1 retry


def thumbnail_is_healthy(path: Path) -> bool:
    """Samme tjek som genererings-valideringen — bruges også af run.py's
    skip-logik, så 'ser sund ud' betyder det samme begge steder."""
    if not path.exists() or path.stat().st_size < MIN_BYTES:
        return False
    from PIL import Image
    with Image.open(path) as img:
        return img.size == (WIDTH, HEIGHT)

THUMB_PROMPT = (
    "A crude, childlike YouTube thumbnail drawn in MS Paint for a video about: {TITLE}. "
    'The thumbnail MUST contain the text "{HOOK}" written in HUGE, bold, slightly wobbly '
    "hand-drawn capital letters that fill a large part of the image, in very high contrast "
    "colors (thick black or red letters on the plain white background). "
    "Besides the text, exactly ONE clear simple motif featuring the recurring character: "
    "{CHARACTER}. "
    "STYLE RULES (must follow exactly): extremely simple beginner doodle drawn quickly "
    "by hand with a computer mouse; thick wobbly uneven black outlines; flat solid fill "
    "colors; plain pure-white background; NO shading, NO gradients, NO 3D, NO photorealism, "
    "NO cinematic lighting, NO fine detail. Finance and money theme. "
    "16:9 horizontal composition."
)


def guess_title(slug: str) -> str:
    """Fallback når --title udelades: slug -> læsbar titel ('zero-to-10k' -> 'Zero To 10K')."""
    return slug.replace("-", " ").strip().title()


def guess_hook(slug: str) -> str:
    """Fallback når --hook udelades: max 4 ord fra slug'en i versaler (BRAND: 2-4 ord)."""
    words = slug.replace("-", " ").upper().split()
    return " ".join(words[:4])


def build_prompt(title: str, hook: str) -> str:
    prompt = THUMB_PROMPT.format(TITLE=title, HOOK=hook, CHARACTER=DEFAULT_CHARACTER)
    return f"{prompt}\n\nNEGATIVE PROMPT — the image must contain NONE of this: {NEGATIVE_PROMPT}"


def run(out_dir: Path, title: str, hook: str) -> None:
    """Genererer og validerer thumbnail.png; retry én gang ved defekt resultat."""
    prompt = build_prompt(title, hook)
    out_path = out_dir / "thumbnail.png"

    for attempt in range(1, ATTEMPTS + 1):
        common.log(f'  Genererer thumbnail (forsøg {attempt}/{ATTEMPTS}): '
                   f'titel="{title}", hook="{hook}" ...')
        image = _generate_with_retry(prompt, "thumbnail.png")  # retry på transiente API-fejl
        image = common.fit_image(image, WIDTH, HEIGHT)  # garanterer 1280x720 RGB
        common.save_png_atomic(image, out_path)

        if thumbnail_is_healthy(out_path):
            common.log(f"  Skrev thumbnail.png ({out_path.stat().st_size // 1024} KB, "
                       f"{WIDTH}x{HEIGHT}).")
            return
        common.log(f"  ADVARSEL: thumbnail er kun {out_path.stat().st_size // 1024} KB "
                   f"(minimum {MIN_BYTES // 1024} KB) — ligner en defekt generering.")

    common.die(f"thumbnail.png er stadig under {MIN_BYTES // 1024} KB efter {ATTEMPTS} forsøg.\n"
               f"  -> Prøv igen med en mere konkret --title/--hook, eller generér manuelt.\n"
               f"  -> Den defekte fil ligger i {out_path} (upload den IKKE).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trin 5: genererer + validerer output/<slug>/thumbnail.png (1280x720)")
    parser.add_argument("slug", help="videonavn — arbejder i output/<slug>/")
    parser.add_argument("--title", help="videotitel til motivet (default: gættes ud fra slug)")
    parser.add_argument("--hook", help="kort tekst PÅ thumbnailen, 2-4 ord (default: gættes ud fra slug)")
    args = parser.parse_args()

    common.validate_slug(args.slug)
    out_dir = common.OUTPUT_DIR / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    run(out_dir,
        title=args.title or guess_title(args.slug),
        hook=args.hook or guess_hook(args.slug))


if __name__ == "__main__":
    main()
