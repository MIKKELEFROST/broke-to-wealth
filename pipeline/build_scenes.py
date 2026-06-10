"""Trin 2: Sceneopdeling — words.json -> scenes.json + timeline.json.

Deterministisk segmentering (ingen LLM): ordene grupperes til scener ud fra
ord-timingen alene, efter den rekonstruerede algoritme i datakontrakten §6.
Tempo-mål fra BRAND.md: target 2,8 s / max 4,5 s pr. scene (~50 billeder/video).

scenes.json   (kontrakt §3): {"index", "start", "end", "text", "visual"}
timeline.json (kontrakt §4): {"file", "start", "text"} — 1:1 med scenes.json.
"visual" er altid tom som udgangspunkt ("rå v1"-stilen); den kan udfyldes
manuelt før generate_images.py for mere styrede billedprompts.
"""

import argparse
import json
from pathlib import Path

import common

MAX_SCENE_DUR = 4.5     # sekunder — hårdt loft; klip EFTER ordet der krydser loftet
MIN_SENTENCE_DUR = 2.8  # sekunder — min-varighed før et sætningsslut må klippe
SENTENCE_END = ".?!"    # komma klipper IKKE (kontrakt §6)


def segment(words: list[dict]) -> list[list[dict]]:
    """Grupperer ordlisten i scener.

    For hvert ord: scenens varighed = ordets end minus første ords start
    (RÅ 3-decimals tider — afrunding til 2 decimaler sker først ved skrivning).
    Klip når varigheden når 4,5 s (forced cut), eller når ordet slutter en
    sætning og varigheden er mindst 2,8 s. Resterende ord bliver sidste scene
    (må gerne være vilkårligt kort).
    """
    scenes: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        current.append(word)
        duration = word["end"] - current[0]["start"]
        ends_sentence = word["word"][-1] in SENTENCE_END
        if duration >= MAX_SCENE_DUR or (ends_sentence and duration >= MIN_SENTENCE_DUR):
            scenes.append(current)
            current = []
    if current:
        scenes.append(current)
    return scenes


def run(out_dir: Path) -> None:
    """Læser words.json og skriver scenes.json + timeline.json."""
    words_path = out_dir / "words.json"
    if not words_path.exists():
        common.die(f"{words_path} findes ikke — kør tts.py først.")
    words = json.loads(words_path.read_text(encoding="utf-8"))
    if not words:
        common.die(f"{words_path} er tom.")

    groups = segment(words)

    scenes = []
    timeline = []
    for i, group in enumerate(groups, start=1):
        start = round(group[0]["start"], 2)   # 2 decimaler ved skrivning (kontrakt §3)
        scene = {
            "index": i,
            "start": start,
            "end": round(group[-1]["end"], 2),
            "text": " ".join(w["word"] for w in group),
            "visual": "",  # reserveret felt til manuel billedprompt (default tom = "rå v1")
        }
        scenes.append(scene)
        # timeline har bevidst ingen end/duration: renderen holder billede i
        # fra start[i] til start[i+1]; sidste billede holdes til lydens slutning.
        timeline.append({
            "file": common.scene_filename(i, start),
            "start": start,
            "text": scene["text"],
        })

    common.dump_json(scenes, out_dir / "scenes.json")
    common.dump_json(timeline, out_dir / "timeline.json")

    total = scenes[-1]["end"] - scenes[0]["start"]
    common.log(f"  Skrev scenes.json + timeline.json: {len(scenes)} scener, "
               f"~{total / len(scenes):.1f} s/scene i gennemsnit.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trin 2: words.json -> scenes.json + timeline.json")
    parser.add_argument("slug", help="videonavn — arbejder i output/<slug>/")
    args = parser.parse_args()
    common.validate_slug(args.slug)
    run(common.OUTPUT_DIR / args.slug)


if __name__ == "__main__":
    main()
