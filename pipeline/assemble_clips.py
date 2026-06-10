"""Render-variant (eksperiment): ANIMEREDE klip i stedet for stillbilleder.

clips/ + images/ + timeline.json + voiceover.mp3 -> <slug>.mp4

Mixed-mode pr. scene: findes `clips/scene_NNNN.mp4` (NNNN = sceneindeks)
bruges klippet; ellers falder scenen tilbage til stillbilledet i images/.
Det gør renderen robust over for budgetlofter og fejlede klip-genereringer
— delvis animation er et gyldigt resultat.

To-trins render:
  1) Pr. scene normaliseres kilden til et segment med scenens EKSAKTE
     varighed: 1920x1080, yuv420p, 24 fps, uden lyd (Seedance-klip har eget
     lydspor som IKKE må med). Klip kortere end scenen forlænges ved at
     holde sidste frame (tpad stop_mode=clone); længere klip trimmes (-t).
  2) Segmenterne sammensættes med concat-demuxeren + voiceover.mp3 til
     kontraktens mp4-profil (samme som assemble_video.py: H.264 High@4.0,
     CRF 23, AAC mono 160k, -shortest, +faststart).

Scenetider følger assemble_video.py 1:1 (1/25-grid-kvantisering, første
scene = 0.0, sidste scene holdes til lydens slutning).
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
AUDIO_BITRATE = "160k"
CRF = "23"            # slutrender — som assemble_video.py
SEGMENT_CRF = "18"    # mellemformat: næsten tabsfrit, så dobbelt-encoding ikke ses

SCALE_VF = (f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p,fps={FPS}")


def clip_filename(index: int) -> str:
    """Klip-navnekonvention: scene_NNNN.mp4 (4-cifret 1-baseret sceneindeks)."""
    return f"scene_{index:04d}.mp4"


def _ffmpeg(args: list[str], context: str) -> None:
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                       check=True)
    except FileNotFoundError:
        common.die("ffmpeg er ikke installeret — kør: brew install ffmpeg")
    except subprocess.CalledProcessError as e:
        common.die(f"ffmpeg fejlede (exit {e.returncode}) under {context} — se output ovenfor.")


def _concat_line(path: Path) -> str:
    escaped = str(path).replace("'", "'\\''")
    return f"file '{escaped}'"


def run(out_dir: Path, slug: str) -> None:
    """Renderer den færdige mp4 fra klip (med stillbillede-fallback)."""
    timeline_path = out_dir / "timeline.json"
    audio_path = out_dir / "voiceover.mp3"
    images_dir = out_dir / "images"
    clips_dir = out_dir / "clips"
    for p in (timeline_path, audio_path):
        if not p.exists():
            common.die(f"{p} findes ikke — kør de foregående trin først.")

    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    if not timeline:
        common.die(f"{timeline_path} er tom.")
    audio_duration = common.ffprobe_duration(audio_path)

    # Scenetider — samme kvantisering og semantik som assemble_video.py.
    qstarts = [math.floor(item["start"] * 25 + 0.5) / 25 for item in timeline]
    qstarts[0] = 0.0

    # Trin 1: ét normaliseret segment pr. scene (klip hvis det findes, ellers still).
    seg_dir = out_dir / ".segments.tmp"
    seg_dir.mkdir(exist_ok=True)
    segments: list[Path] = []
    n_clips = 0
    n_stills = 0
    missing: list[str] = []
    for i, item in enumerate(timeline):
        index = i + 1
        end = qstarts[i + 1] if i + 1 < len(timeline) else audio_duration
        duration = max(1.0 / FPS, end - qstarts[i])
        seg_path = seg_dir / f"seg_{index:04d}.mp4"
        clip_path = clips_dir / clip_filename(index)
        still_path = images_dir / item["file"]

        if clip_path.exists():
            n_clips += 1
            # tpad holder sidste frame hvis klippet er kortere end scenen;
            # -t trimmer til scenens eksakte varighed. -an dropper klip-lyden.
            _ffmpeg(["-i", str(clip_path),
                     "-vf", f"{SCALE_VF},tpad=stop_mode=clone:stop_duration={duration:.3f}",
                     "-t", f"{duration:.3f}", "-an",
                     "-c:v", "libx264", "-preset", "fast", "-crf", SEGMENT_CRF,
                     str(seg_path)],
                    f"segment {index} (klip)")
        elif still_path.exists():
            n_stills += 1
            _ffmpeg(["-loop", "1", "-t", f"{duration:.3f}", "-i", str(still_path),
                     "-vf", SCALE_VF, "-an",
                     "-c:v", "libx264", "-preset", "fast", "-crf", SEGMENT_CRF,
                     str(seg_path)],
                    f"segment {index} (stillbillede)")
        else:
            missing.append(f"scene {index}: hverken {clip_path.name} eller {item['file']}")
            continue
        segments.append(seg_path)

    if missing:
        common.die(f"{len(missing)} scene(r) mangler både klip og stillbillede:\n  "
                   + "\n  ".join(missing))

    common.log(f"  Segmenter: {n_clips} animerede klip, {n_stills} stillbilleder "
               f"({len(timeline)} scener i alt).")

    # Trin 2: concat + voiceover -> kontraktens mp4-profil.
    concat_path = out_dir / f".concat_clips.{os.getpid()}.tmp.txt"
    concat_path.write_text("\n".join(_concat_line(s) for s in segments) + "\n",
                           encoding="utf-8")
    out_path = out_dir / f"{slug}.mp4"
    tmp_path = out_dir / f"{slug}.tmp.mp4"
    common.log(f"  Renderer {out_path.name} ({len(segments)} scener, "
               f"{audio_duration:.1f} s lyd, {WIDTH}x{HEIGHT}@{FPS}fps) ...")
    try:
        _ffmpeg(["-f", "concat", "-safe", "0", "-i", str(concat_path),
                 "-i", str(audio_path),
                 "-c:v", "libx264", "-preset", "fast", "-crf", CRF,
                 "-profile:v", "high", "-level:v", "4.0",
                 "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ac", "1", "-ar", "44100",
                 "-shortest", "-movflags", "+faststart",
                 str(tmp_path)],
                "slutrender")
    finally:
        concat_path.unlink(missing_ok=True)
        for s in segments:
            s.unlink(missing_ok=True)
        seg_dir.rmdir()

    os.replace(tmp_path, out_path)
    common.log(f"  Skrev {out_path.name} ({out_path.stat().st_size // (1024 * 1024)} MB).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render-variant: clips/ (+ images/-fallback) + voiceover -> <slug>.mp4")
    parser.add_argument("slug", help="videonavn — arbejder i output/<slug>/")
    args = parser.parse_args()
    common.validate_slug(args.slug)
    run(common.OUTPUT_DIR / args.slug, args.slug)


if __name__ == "__main__":
    main()
