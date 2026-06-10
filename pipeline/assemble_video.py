"""Trin 4: Render — images/ + timeline.json + voiceover.mp3 -> <slug>.mp4.

ffmpeg-baseret (systemafhængighed: brew install ffmpeg). Output matcher
kontrakten §8: 1920x1080, H.264 High@4.0, yuv420p, 24 fps konstant,
AAC mono 44,1 kHz ~160 kbps, video klippes til lyden (-shortest).

Render-semantik (kontrakt §4/§8): billede i vises fra timeline[i].start til
timeline[i+1].start; sidste billede holdes til lydens slutning. Derfor har
timeline.json bevidst ingen end/duration-felter.

Manglende billeder: fejler højt som default (læren fra debt-one-number,
kontrakt §12.1, hvor et manglende billede blev ignoreret stille). Med
--reuse-previous genbruges forrige scenes billede EKSPLICIT med en advarsel.
"""

import argparse
import json
import math
import os
import subprocess
from pathlib import Path

import common

FPS = 24
WIDTH, HEIGHT = 1920, 1080
AUDIO_BITRATE = "160k"  # AAC mono ~160 kbps (kontrakt §8)
CRF = "23"              # kvalitetsstyret encoding — statiske doodles giver lav bitrate


def _concat_line(path: Path) -> str:
    """Én 'file'-linje til ffmpeg's concat-demuxer, med korrekt quoting
    (projektstien indeholder mellemrum)."""
    escaped = str(path).replace("'", "'\\''")
    return f"file '{escaped}'"


def run(out_dir: Path, slug: str, reuse_previous: bool = False) -> None:
    """Renderer den færdige mp4 ud fra timeline + billeder + voiceover."""
    timeline_path = out_dir / "timeline.json"
    audio_path = out_dir / "voiceover.mp3"
    images_dir = out_dir / "images"
    for p in (timeline_path, audio_path):
        if not p.exists():
            common.die(f"{p} findes ikke — kør de foregående trin først.")

    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    if not timeline:
        common.die(f"{timeline_path} er tom.")
    audio_duration = common.ffprobe_duration(audio_path)

    # Saml (billedsti, starttid) — og håndtér manglende billeder eksplicit.
    entries: list[tuple[Path, float]] = []
    previous: Path | None = None
    missing: list[str] = []
    for item in timeline:
        path = images_dir / item["file"]
        if not path.exists():
            if reuse_previous and previous is not None:
                common.log(f"  ADVARSEL: {item['file']} mangler — genbruger {previous.name}.")
                path = previous
            else:
                missing.append(item["file"])
                continue
        else:
            previous = path
        entries.append((path, item["start"]))
    if missing:
        common.die(f"{len(missing)} billede(r) mangler i {images_dir}:\n  "
                   + "\n  ".join(missing)
                   + "\nKør generate_images.py igen (regenererer kun manglende), "
                     "eller brug --reuse-previous for bevidst at genbruge forrige billede.")

    # Byg concat-listen: billede i holdes fra start[i] til start[i+1];
    # sidste billede holdes til lydens slutning.
    #
    # Timing-paritet med de gamle videoer (verificeret frame-for-frame mod
    # zero-to-10k, 58/58 skift): den oprindelige render kvantiserede starttider
    # til et 1/25-sekunders grid FØR CFR-afrunding til 24 fps — formlen
    # frame = round(round(start*25)/25 * 24). Derfor kvantiserer vi her, og
    # 24 fps håndhæves med fps-filteret (round=near) i stedet for '-r' (se -vf).
    qstarts = [math.floor(start * 25 + 0.5) / 25 for _, start in entries]
    # Første billede starter ved t=0 — ellers forskyder TTS'ens indledende
    # stilhed ALLE billeder for tidligt, og -shortest klipper lydens slutning.
    qstarts[0] = 0.0
    lines: list[str] = []
    for i, (path, _start) in enumerate(entries):
        end = qstarts[i + 1] if i + 1 < len(entries) else audio_duration
        duration = max(1.0 / FPS, end - qstarts[i])  # aldrig under én frame
        lines.append(_concat_line(path))
        lines.append(f"duration {duration:.3f}")
    # ffmpeg-quirk (dokumenteret): sidste fil SKAL gentages uden duration,
    # ellers ignoreres den sidste duration og totalvarigheden bliver forkert.
    lines.append(_concat_line(entries[-1][0]))

    concat_path = out_dir / f".concat_list.{os.getpid()}.tmp.txt"
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out_path = out_dir / f"{slug}.mp4"
    tmp_path = out_dir / f"{slug}.tmp.mp4"  # atomisk: render til temp, rename til sidst
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_path),
        "-i", str(audio_path),
        # Billederne er 1344x768 (7:4) — skalér til at dække 1920x1080 og
        # center-beskær (1920x1097 -> crop 1080). format=yuv420p er påkrævet
        # for at QuickTime/YouTube kan afspille H.264 fra PNG-kilder.
        "-vf", (f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p,fps={FPS}"),
        # '-preset fast' uden -tune: matcher x264-parametrene indlejret i de
        # gamle artefakter (medium/stillimage gav +44 % filstørrelse).
        "-c:v", "libx264", "-preset", "fast", "-crf", CRF,
        "-profile:v", "high", "-level:v", "4.0",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ac", "1", "-ar", "44100",
        "-shortest",              # klip video til lyden (kontrakt §8: 1-2 frames kortere er ok)
        "-movflags", "+faststart",
        str(tmp_path),
    ]
    common.log(f"  Renderer {out_path.name} ({len(entries)} scener, "
               f"{audio_duration:.1f} s lyd, {WIDTH}x{HEIGHT}@{FPS}fps) ...")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        common.die("ffmpeg er ikke installeret — kør: brew install ffmpeg")
    except subprocess.CalledProcessError as e:
        tmp_path.unlink(missing_ok=True)
        common.die(f"ffmpeg fejlede (exit {e.returncode}) — se output ovenfor.")
    finally:
        concat_path.unlink(missing_ok=True)

    os.replace(tmp_path, out_path)
    common.log(f"  Skrev {out_path.name} ({out_path.stat().st_size // (1024 * 1024)} MB).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trin 4: images/ + timeline.json + voiceover.mp3 -> <slug>.mp4")
    parser.add_argument("slug", help="videonavn — arbejder i output/<slug>/")
    parser.add_argument("--reuse-previous", action="store_true",
                        help="genbrug forrige billede hvis et billede mangler (default: fejl højt)")
    args = parser.parse_args()
    common.validate_slug(args.slug)
    run(common.OUTPUT_DIR / args.slug, args.slug, reuse_previous=args.reuse_previous)


if __name__ == "__main__":
    main()
