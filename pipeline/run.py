#!/usr/bin/env python3
"""Orkestrator for "Broke to Wealth"-pipelinen — kører alle 5 trin:

  voiceover -> scener -> billeder -> samlet .mp4 -> thumbnail

Brug:
  python pipeline/run.py <slug>                          # læser scripts/<slug>.txt
  python pipeline/run.py scripts/<navn>.txt --name <slug>
  ... --title "How I'd go from $0 to $10k" --hook "$0 TO $10K"
  ... --skip-images     # stop efter scenes.json (udfyld 'visual'-felter manuelt,
                        #  kør derefter generate_images/assemble_video/generate_thumbnail enkeltvis)
  ... --force           # gentag trin selvom output-filerne allerede findes

Alle trin er genoptagelige: findes et trins output allerede, springes det
over (medmindre --force). Sidste trin er ALTID manuel upload til YouTube
(husk "altered/synthetic content"-flaget + AI-disclosure i beskrivelsen).
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Gør sibling-modulerne importérbare uanset hvor scriptet kaldes fra.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import common
import tts
import build_scenes
import generate_images
import assemble_video
import generate_thumbnail


def resolve_script_and_slug(arg: str, name: str | None) -> tuple[Path, str]:
    """Accepterer både en slug ('zero-to-10k') og en sti ('scripts/zero-to-10k.txt').
    --name overstyrer altid slug'en (og dermed output-mappen)."""
    path = Path(arg)
    if arg.endswith(".txt") or path.is_file():
        script_path = path.resolve()
        slug = name or script_path.stem
    else:
        slug = name or arg
        script_path = common.SCRIPTS_DIR / f"{slug}.txt"
    if not script_path.is_file():
        common.die(f"Manuskriptet findes ikke: {script_path}\n"
                   f"  -> Læg det som {common.SCRIPTS_DIR / (slug + '.txt')} (ren tekst, kun narration).")
    return script_path, slug


def step(n: int, total: int, title: str) -> None:
    common.log(f"\n[{n}/{total}] {title}")


def fresh(out: Path, *inputs: Path) -> bool:
    """Findes output OG er det nyere end alle sine inputs? Ren eksistens er ikke
    nok som resume-tjek: et ændret manuskript eller en regenereret mellemfil
    ville ellers give tavs A/V-desync, fordi nedstrøms trin springes over."""
    if not out.exists():
        return False
    mtime = out.stat().st_mtime
    return all(mtime >= p.stat().st_mtime for p in inputs if p.exists())


def _missing_images(out_dir: Path) -> bool:
    """True hvis scenes.json mangler, eller hvis et af dens billeder mangler —
    bruges til fail-fast-tjek af GEMINI_API_KEY, før der bruges tid og penge."""
    scenes_path = out_dir / "scenes.json"
    if not scenes_path.exists():
        return True
    scenes = json.loads(scenes_path.read_text(encoding="utf-8"))
    images_dir = out_dir / "images"
    return any(not (images_dir / common.scene_filename(s["index"], s["start"])).exists()
               for s in scenes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Laver én færdig video: manuskript -> voiceover -> billeder -> .mp4 + thumbnail")
    parser.add_argument("script", help="slug ELLER sti til scripts/<slug>.txt")
    parser.add_argument("--name", help="slug/output-mappe (default: afledt af script-filnavnet)")
    parser.add_argument("--title", help="videotitel til thumbnailen (default: gættes ud fra slug)")
    parser.add_argument("--hook", help="kort thumbnail-tekst, 2-4 ord (default: gættes ud fra slug)")
    parser.add_argument("--skip-images", action="store_true",
                        help="stop efter scenes.json (til manuel udfyldning af 'visual'-felter)")
    parser.add_argument("--force", action="store_true",
                        help="gentag alle trin selvom output allerede findes")
    args = parser.parse_args()

    script_path, slug = resolve_script_and_slug(args.script, args.name)
    common.validate_slug(slug)
    out_dir = common.OUTPUT_DIR / slug

    voiceover = out_dir / "voiceover.mp3"
    words = out_dir / "words.json"
    scenes = out_dir / "scenes.json"
    timeline = out_dir / "timeline.json"
    images_dir = out_dir / "images"
    mp4_path = out_dir / f"{slug}.mp4"
    thumb_path = out_dir / "thumbnail.png"

    # Fail-fast: valider nøglerne for de trin der reelt skal køre, FØR vi
    # bruger tid/penge — i stedet for at opdage en manglende nøgle midt i kørslen.
    tts_needed = args.force or not (fresh(voiceover, script_path) and fresh(words, script_path))
    if tts_needed:
        common.require_env("ELEVENLABS_API_KEY",
                           "Hentes på elevenlabs.io -> Settings -> API Keys.")
        common.require_env("ELEVENLABS_VOICE_ID",
                           "Den faste dybe mandlige fortæller — SAMME stemme hver gang.")
    if not args.skip_images and (args.force or tts_needed or _missing_images(out_dir)
                                 or not generate_thumbnail.thumbnail_is_healthy(thumb_path)):
        common.require_env("GEMINI_API_KEY",
                           "Opret en nøgle på https://aistudio.google.com/apikey")

    out_dir.mkdir(parents=True, exist_ok=True)  # først EFTER nøgletjek (ingen tomme mapper)
    t0 = time.time()
    total = 2 if args.skip_images else 5

    common.log(f"== Broke to Wealth: '{slug}' ==")
    common.log(f"   manuskript: {script_path}")
    common.log(f"   output:     {out_dir}")

    # ----- Trin 1: voiceover + ord-timing (ElevenLabs) -----
    step(1, total, "Voiceover (ElevenLabs)")
    if not tts_needed:
        common.log("  springes over — voiceover.mp3 + words.json er friske (brug --force for at gentage).")
    else:
        tts.run(script_path, out_dir)

    # ----- Trin 2: sceneopdeling (deterministisk, ud fra ord-timing) -----
    step(2, total, "Scener (segmentering 2,8 s / 4,5 s)")
    if not args.force and fresh(scenes, words) and fresh(timeline, words):
        common.log("  springes over — scenes.json + timeline.json er friske (brug --force for at gentage).")
    else:
        build_scenes.run(out_dir)

    if args.skip_images:
        common.log(f"\n--skip-images: stopper efter scenes.json.\n"
                   f"Udfyld evt. 'visual'-felter i {out_dir / 'scenes.json'} og kør derefter:\n"
                   f"  python pipeline/generate_images.py {slug}\n"
                   f"  python pipeline/assemble_video.py {slug}\n"
                   f"  python pipeline/generate_thumbnail.py {slug} --title ... --hook ...")
        return

    # ----- Trin 3: scenebilleder (Gemini/nano-banana) -----
    # Altid kaldt: trinnet er selv idempotent og genererer kun manglende billeder.
    step(3, total, "Billeder (Gemini, ét doodle pr. scene)")
    generate_images.run(out_dir, force=args.force)

    # ----- Trin 4: render (ffmpeg) -----
    step(4, total, "Video (ffmpeg-render, 1920x1080 @ 24 fps)")
    if not args.force and fresh(mp4_path, timeline, voiceover, *images_dir.glob("*.png")):
        common.log(f"  springes over — {mp4_path.name} er frisk (brug --force for at gentage).")
    else:
        assemble_video.run(out_dir, slug)

    # ----- Trin 5: thumbnail (Gemini + validering) -----
    step(5, total, "Thumbnail (1280x720)")
    if not args.force and generate_thumbnail.thumbnail_is_healthy(thumb_path):
        common.log(f"  springes over — {thumb_path.name} findes og ser sund ud "
                   "(brug --force for at gentage).")
    else:
        generate_thumbnail.run(
            out_dir,
            title=args.title or generate_thumbnail.guess_title(slug),
            hook=args.hook or generate_thumbnail.guess_hook(slug))

    minutes = (time.time() - t0) / 60
    common.log(f"\nFÆRDIG på {minutes:.1f} min. Klar til MANUEL upload:")
    common.log(f"  video:     {mp4_path}")
    common.log(f"  thumbnail: {thumb_path}")
    common.log('  Husk: "altered/synthetic content"-flag + AI-disclosure-linjen i beskrivelsen,')
    common.log("  og opdatér STATUS.md + website/build.py (video_id) efter upload.")


if __name__ == "__main__":
    main()
