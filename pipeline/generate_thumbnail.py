"""Trin 5: Thumbnails — Gemini -> output/<slug>/thumbnail-1..3.png (1280x720).

Genererer 3 VIDT FORSKELLIGE koncepter pr. video (alle relevante for emnet, alle med
hook-teksten), så den bedste kan vælges manuelt ved upload:
  1. REACTION       — nærbillede af den faste figur med en stærk følelse
  2. CONTRAST/VS    — venstre-mod-højre modsætning fra emnet
  3. MONEY BREAKDOWN — pengebunke brudt ned i pile/søjler/% (figuren peger)
Samme doodle-stil som videoen + den faste figur; STOR hook-tekst (2-4 ord), høj kontrast.

VIGTIGT — validering: en tidligere kørsel producerede en defekt 93 KB-thumbnail
(typisk størrelse er ~750-950 KB). Derfor valideres hver variant (korrekte
dimensioner + filstørrelse > 200 KB) og der retries én gang ved fejl.
"""

import argparse
import json
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
ATTEMPTS = 2                # 1 forsøg + 1 retry pr. variant
THUMB_COUNT = 3             # antal thumbnail-varianter pr. video (vælg den bedste ved upload)


def thumbnail_is_healthy(path: Path) -> bool:
    """Samme tjek som genererings-valideringen — bruges også af run.py's
    skip-logik, så 'ser sund ud' betyder det samme begge steder."""
    if not path.exists() or path.stat().st_size < MIN_BYTES:
        return False
    from PIL import Image
    with Image.open(path) as img:
        return img.size == (WIDTH, HEIGHT)


def thumbnail_paths(out_dir: Path, count: int = THUMB_COUNT) -> list[Path]:
    """Variant-stierne: thumbnail-1.png ... thumbnail-N.png."""
    return [out_dir / f"thumbnail-{i}.png" for i in range(1, count + 1)]


def all_thumbnails_healthy(out_dir: Path, count: int = THUMB_COUNT) -> bool:
    """True kun hvis ALLE N varianter findes og er sunde — bruges af run.py's skip-logik."""
    return all(thumbnail_is_healthy(p) for p in thumbnail_paths(out_dir, count))


# FALLBACK-kompositioner — bruges KUN hvis de dynamiske, video-specifikke vinkler
# (dynamic_ideas) ikke kan hentes. Primært udledes hver videos 3 vinkler dynamisk (A/B-test).
FALLBACK_CONCEPTS = [
    "Composition A — REACTION: a large close-up of the recurring character reacting with one "
    "strong, exaggerated emotion about the topic (shock, worry, or a lightbulb 'aha' moment). "
    "The character dominates one side of the frame.",
    "Composition B — CONTRAST: a clear left-versus-right split showing two opposite situations "
    "from the topic (for example broke vs rich, before vs after, or feeling vs reality), with a "
    "bold dividing line or a hand-drawn 'VS', and the recurring character on at least one side.",
    "Composition C — MONEY BREAKDOWN: a crude hand-drawn money breakdown — a pile or stack of "
    "cash or coins broken apart by big arrows into a simple bar chart, a pie, or a few labeled "
    "chunks, with one or two short number or percent labels, and the recurring character "
    "pointing at it.",
]

THUMB_BASE = (
    "A crude, childlike YouTube thumbnail drawn in MS Paint for a video about: {TITLE}. "
    "{CONCEPT} "
    'The thumbnail MUST also contain the text "{HOOK}" written in HUGE, bold, slightly wobbly '
    "hand-drawn capital letters that fill a large part of the image, in very high contrast "
    "(thick black or red letters on the plain white background). "
    "STYLE RULES (must follow exactly): extremely simple beginner doodle drawn quickly by hand "
    "with a computer mouse; thick wobbly uneven black outlines; FLAT SOLID FILL COLORS (fully "
    "colored, not just black-and-white line art); plain pure-white background; NO shading, "
    "NO gradients, NO 3D, NO photorealism, NO cinematic lighting, NO fine detail. "
    "Finance and money theme. The recurring character is: {CHARACTER}. Keep him identical "
    "every time. 16:9 horizontal composition."
)


def guess_title(slug: str) -> str:
    """Fallback når --title udelades: slug -> læsbar titel ('zero-to-10k' -> 'Zero To 10K')."""
    return slug.replace("-", " ").strip().title()


def guess_hook(slug: str) -> str:
    """Fallback når --hook udelades: max 4 ord fra slug'en i versaler (BRAND: 2-4 ord)."""
    words = slug.replace("-", " ").upper().split()
    return " ".join(words[:4])


def build_prompt(title: str, hook: str, concept: str) -> str:
    prompt = THUMB_BASE.format(TITLE=title, HOOK=hook, CONCEPT=concept, CHARACTER=DEFAULT_CHARACTER)
    return f"{prompt}\n\nNEGATIVE PROMPT — the image must contain NONE of this: {NEGATIVE_PROMPT}"


def dynamic_ideas(title: str, script_text: str, n: int = THUMB_COUNT) -> list[tuple[str, str]]:
    """Beder en LLM om N VIDEO-SPECIFIKKE thumbnail-vinkler (til A/B-test) ud fra titel +
    manuskript. Returnerer [(hook, concept), ...]. Rejser ved fejl, så run() kan falde tilbage."""
    script = " ".join((script_text or "").split())[:3500]
    prompt = (
        "You design YouTube thumbnails for a faceless finance channel called 'Broke to Wealth' "
        "(extremely simple MS-Paint doodle style; a recurring bald round-headed stick man with a "
        "small black necktie; audience 18-35; money psychology; broke-to-rich angle). "
        f"VIDEO TITLE: {title}\n"
        f"SCRIPT EXCERPT: {script}\n\n"
        f"Design {n} thumbnails for A/B TESTING — each MUST be a different angle to test against "
        "the others: a different emotion, a different visual idea, AND different hook wording. "
        "Base them on THIS specific video, not a generic template. "
        "Return ONLY a JSON array of " + str(n) + " objects, each with: "
        '"hook" = 2-4 word ALL-CAPS punchy text to put on the thumbnail (curiosity or tension), '
        '"concept" = one sentence describing the simple doodle composition for this video, '
        "including the recurring stick man, flat solid colors and a plain white background. "
        "Make the three genuinely different from one another."
    )
    raw = common.gemini_generate_text(prompt, as_json=True)
    data = json.loads(raw)
    if isinstance(data, dict):  # nogle svar pakker listen i en nøgle
        data = next((v for v in data.values() if isinstance(v, list)), [])
    ideas = [(str(d["hook"]).strip(), str(d["concept"]).strip())
             for d in data if isinstance(d, dict) and d.get("hook") and d.get("concept")]
    if len(ideas) < n:
        raise ValueError(f"LLM gav kun {len(ideas)} brugbare idéer (ville have {n})")
    return ideas[:n]


def _generate_one(out_path: Path, prompt: str, title: str, hook: str) -> None:
    """Genererer + validerer ÉN thumbnail-fil; retry ATTEMPTS gange ved defekt resultat."""
    for attempt in range(1, ATTEMPTS + 1):
        common.log(f'  {out_path.name} (forsøg {attempt}/{ATTEMPTS}): '
                   f'titel="{title}", hook="{hook}" ...')
        image = _generate_with_retry(prompt, out_path.name)   # retry på transiente API-fejl
        image = common.fit_image(image, WIDTH, HEIGHT)         # garanterer 1280x720 RGB
        common.save_png_atomic(image, out_path)
        if thumbnail_is_healthy(out_path):
            common.log(f"  Skrev {out_path.name} ({out_path.stat().st_size // 1024} KB, "
                       f"{WIDTH}x{HEIGHT}).")
            return
        common.log(f"  ADVARSEL: {out_path.name} er kun {out_path.stat().st_size // 1024} KB "
                   f"(minimum {MIN_BYTES // 1024} KB) — ligner en defekt generering.")
    common.die(f"{out_path.name} er stadig under {MIN_BYTES // 1024} KB efter {ATTEMPTS} forsøg.\n"
               f"  -> Prøv igen med en mere konkret --title/--hook, eller generér manuelt.\n"
               f"  -> Den defekte fil ligger i {out_path} (upload den IKKE).")


def run(out_dir: Path, title: str, hook: str, count: int = THUMB_COUNT) -> None:
    """Genererer COUNT thumbnail-varianter til A/B-test. Vinklerne udledes DYNAMISK pr. video
    (forskellige hooks/greb, baseret på titel + manuskript) via dynamic_ideas; falder tilbage
    til hook + generiske FALLBACK_CONCEPTS hvis LLM'en fejler. Batch + synkron fallback pr. billede."""
    paths = thumbnail_paths(out_dir, count)

    try:
        script_path = common.SCRIPTS_DIR / f"{out_dir.name}.txt"
        script_text = script_path.read_text(encoding="utf-8") if script_path.exists() else ""
        ideas = dynamic_ideas(title, script_text, count)
        common.log(f"  Dynamiske A/B-vinkler ({len(ideas)}):")
        for i, (h, c) in enumerate(ideas, 1):
            common.log(f'    {i}. "{h}" — {c[:75]}')
    except Exception as e:
        common.log(f"  Dynamiske vinkler utilgængelige ({e}) — bruger hook + generiske greb.")
        ideas = [(hook, FALLBACK_CONCEPTS[i % len(FALLBACK_CONCEPTS)]) for i in range(count)]

    prompts = [build_prompt(title, h, c) for (h, c) in ideas]

    batch_images = [None] * count
    if common.BATCH_IMAGES:
        try:
            batch_images = common.gemini_generate_images_batch(prompts, label="thumbnails")
        except SystemExit:
            raise
        except Exception as e:
            common.log(f"  Batch fejlede ({e}) — falder tilbage til synkron generering.")
            batch_images = [None] * count

    for path, prompt, image in zip(paths, prompts, batch_images):
        if image is not None:
            common.save_png_atomic(common.fit_image(image, WIDTH, HEIGHT), path)
            if thumbnail_is_healthy(path):
                common.log(f"  Skrev {path.name} (batch, {path.stat().st_size // 1024} KB).")
                continue
            common.log(f"  {path.name} fra batch ser defekt ud — regenererer synkront.")
        _generate_one(path, prompt, title, hook)  # synkron fallback (egen retry + validering)
    common.log(f"  {count} thumbnail-varianter (dynamiske A/B-vinkler) klar — vælg den bedste.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trin 5: genererer + validerer output/<slug>/thumbnail-1..3.png (1280x720)")
    parser.add_argument("slug", help="videonavn — arbejder i output/<slug>/")
    parser.add_argument("--title", help="videotitel til motivet (default: gættes ud fra slug)")
    parser.add_argument("--hook", help="kort tekst PÅ thumbnailen, 2-4 ord (default: gættes ud fra slug)")
    parser.add_argument("--count", type=int, default=THUMB_COUNT, help=f"antal varianter (default {THUMB_COUNT})")
    args = parser.parse_args()

    common.validate_slug(args.slug)
    out_dir = common.OUTPUT_DIR / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    run(out_dir,
        title=args.title or guess_title(args.slug),
        hook=args.hook or guess_hook(args.slug),
        count=args.count)


if __name__ == "__main__":
    main()
