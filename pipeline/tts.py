"""Trin 1: Voiceover — ElevenLabs TTS med ord-timestamps.

scripts/<slug>.txt  ->  output/<slug>/voiceover.mp3 + words.json

words.json (datakontrakt §2): JSON-array af {"word", "start", "end"} hvor
"word" er manuskriptets egne tokens (inkl. klistret tegnsætning) og tiderne
er rå TTS-tider afrundet til 3 decimaler. Manuskriptet whitespace-splittet
skal give PRÆCIS samme ordliste som words.json.
"""

import argparse
import base64
import re
import time
from pathlib import Path

import common

MODEL_ID = "eleven_multilingual_v2"   # dokumenteret default ("bedst");
                                      # skift til "eleven_flash_v2_5" for halv pris
OUTPUT_FORMAT = "mp3_44100_128"       # 44.1 kHz mono 128 kbps CBR — matcher kontrakt §7
MAX_TTS_CHARS = 9000                  # multilingual_v2-grænsen er 10.000 tegn; lidt margen.
                                      # (Den gamle pipeline delte ved ~2.500 tegn — den nye
                                      # grænse giver færre kald og en renere single-stream-mp3
                                      # for korte manuskripter; bevidst afvigelse.)
TTS_RETRIES = 3                       # forsøg pr. chunk ved transiente API-fejl (429/5xx/netværk)


def split_script(text: str) -> list[str]:
    """Deler manuskriptet i bidder <= MAX_TTS_CHARS på sætningsgrænser.
    Lange manuskripter (fx debt-one-number, ~2.500 ord) overskrider
    modellens tegngrænse og kræver flere TTS-kald.
    """
    if len(text) <= MAX_TTS_CHARS:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        # Nødfald: en enkelt sætning over grænsen hårddeles på ord —
        # og uden mellemrum (fx ét gigantisk token) klippes der hårdt på
        # tegngrænsen, så løkken ALTID forkorter og aldrig hænger.
        while len(sentence) > MAX_TTS_CHARS:
            cut = sentence.rfind(" ", 0, MAX_TTS_CHARS)
            if cut <= 0:
                head, sentence = sentence[:MAX_TTS_CHARS], sentence[MAX_TTS_CHARS:]
            else:
                head, sentence = sentence[:cut], sentence[cut + 1:]
            if current:
                chunks.append(current)
                current = ""
            chunks.append(head)
        if current and len(current) + 1 + len(sentence) > MAX_TTS_CHARS:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence
    if current:
        chunks.append(current)
    return chunks


def words_from_alignment(alignment, offset: float) -> list[dict]:
    """Grupperer ElevenLabs' karakter-niveau-timing til ord på whitespace.
    API'et leverer kun tider pr. tegn; et ords start = første tegns start,
    et ords end = sidste tegns end. `offset` forskyder tiderne ved flere chunks.
    """
    words: list[dict] = []
    current = None
    for ch, start, end in zip(alignment.characters,
                              alignment.character_start_times_seconds,
                              alignment.character_end_times_seconds):
        if ch.isspace():
            if current is not None:
                words.append(current)
                current = None
        elif current is None:
            current = {"word": ch, "start": offset + start, "end": offset + end}
        else:
            current["word"] += ch
            current["end"] = offset + end
    if current is not None:
        words.append(current)
    return words


def _audio_duration(audio: bytes, out_dir: Path) -> float:
    """Måler mp3-bytes' reelle varighed via ffprobe. Kaldes på den AKKUMULEREDE
    lyd efter hver chunk (ikke pr. enkelt-chunk), så ord-offsets ikke driver
    pga. frame-afrunding/encoder-padding hen over chunk-grænser."""
    import os
    tmp = out_dir / f".tts_chunk.{os.getpid()}.tmp.mp3"
    tmp.write_bytes(audio)
    try:
        return common.ffprobe_duration(tmp)
    finally:
        tmp.unlink(missing_ok=True)


def _tts_call(client, voice_id: str, chunks: list[str], i: int):
    """Ét convert_with_timestamps-kald med retry på transiente fejl (429/5xx/netværk).
    previous_text/next_text giver ElevenLabs prosodi-kontekst hen over chunk-grænser."""
    kwargs = dict(voice_id=voice_id, text=chunks[i], model_id=MODEL_ID,
                  output_format=OUTPUT_FORMAT)
    if i > 0:
        kwargs["previous_text"] = chunks[i - 1]
    if i < len(chunks) - 1:
        kwargs["next_text"] = chunks[i + 1]

    last_error = None
    for attempt in range(1, TTS_RETRIES + 1):
        try:
            return client.text_to_speech.convert_with_timestamps(**kwargs)
        except Exception as e:
            status = getattr(e, "status_code", None)
            transient = (status in (429,) or (isinstance(status, int) and status >= 500)
                         or isinstance(e, (ConnectionError, TimeoutError)))
            if not transient:
                common.die(f"ElevenLabs afviste TTS-kaldet (status {status}): {e}\n"
                           "  -> Tjek ELEVENLABS_API_KEY/ELEVENLABS_VOICE_ID i .env "
                           "og dit abonnements kvote på elevenlabs.io.")
            last_error = e
            common.log(f"    TTS-forsøg {attempt}/{TTS_RETRIES} fejlede (status {status}) "
                       f"— prøver igen om {10 * attempt} s ...")
            if attempt < TTS_RETRIES:
                time.sleep(10 * attempt)
    common.die(f"ElevenLabs fejlede {TTS_RETRIES} gange i træk. Sidste fejl: {last_error}")


def run(script_path: Path, out_dir: Path) -> None:
    """Genererer voiceover.mp3 + words.json fra manuskriptet."""
    api_key = common.require_env(
        "ELEVENLABS_API_KEY",
        "Hentes på elevenlabs.io -> Settings -> API Keys (Starter-abonnement, $5/md).")
    voice_id = common.require_env(
        "ELEVENLABS_VOICE_ID",
        "Voice-id for den faste dybe mandlige fortæller (fx Adam: pNInz6obpgDQGcFmaJgB). "
        "Brug SAMME stemme hver gang.")
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        common.die("Pakken 'elevenlabs' mangler — kør:\n"
                   f"  pip install -r {common.PIPELINE_DIR / 'requirements.txt'}")

    text = script_path.read_text(encoding="utf-8").strip()
    if not text:
        common.die(f"Manuskriptet er tomt: {script_path}")

    chunks = split_script(text)
    if len(chunks) > 1:
        common.log(f"  Manuskript på {len(text)} tegn deles i {len(chunks)} TTS-kald "
                   f"(modelgrænse ~{MAX_TTS_CHARS} tegn).")

    client = ElevenLabs(api_key=api_key)
    audio = b""
    words: list[dict] = []
    offset = 0.0
    for i, chunk in enumerate(chunks):
        common.log(f"  TTS-kald {i + 1}/{len(chunks)} ({len(chunk)} tegn, {MODEL_ID}) ...")
        response = _tts_call(client, voice_id, chunks, i)
        # NB: SDK'ets attribut hedder audio_base_64 (JSON-aliaset er 'audio_base64')
        part = base64.b64decode(response.audio_base_64)
        # VIGTIGT: brug 'alignment' (rå), IKKE 'normalized_alignment' — words.json
        # skal matche manuskriptets egne tokens 1:1 (kontrakt §2); normalized
        # omskriver tal/forkortelser ("$10k" -> "ten thousand dollars").
        alignment = response.alignment or response.normalized_alignment
        if alignment is None:
            common.die("ElevenLabs returnerede ingen alignment-data — kan ikke lave words.json.")
        words += words_from_alignment(alignment, offset)
        audio += part  # 128 kbps CBR-mp3'er kan kædes direkte sammen
        if i < len(chunks) - 1:
            # Offset = den AKKUMULEREDE lyds varighed (ikke summen af chunk-
            # estimater), så ord-tider ikke driver hen over chunk-grænser.
            offset = _audio_duration(audio, out_dir)

    # Rå TTS-præcision = 3 decimaler (kontrakt §2). Afrundes først her, ved skrivning.
    for w in words:
        w["start"] = round(w["start"], 3)
        w["end"] = round(w["end"], 3)

    # Sanity-tjek mod kontraktens invariant: manuskript-tokens == words.json-tokens.
    if [w["word"] for w in words] != text.split():
        common.log("  ADVARSEL: ordene fra TTS-alignment matcher ikke manuskriptet 1:1 "
                   "— efterse words.json før du fortsætter.")

    common.write_bytes_atomic(out_dir / "voiceover.mp3", audio)
    common.dump_json(words, out_dir / "words.json")

    # Sanity: sidste ords sluttid må ikke overskride lydens reelle varighed.
    total = common.ffprobe_duration(out_dir / "voiceover.mp3")
    if words and words[-1]["end"] > total + 0.5:
        common.log(f"  ADVARSEL: sidste ord slutter ved {words[-1]['end']:.2f} s, men lyden "
                   f"er kun {total:.2f} s — ord-timingen er muligvis drevet. Efterse words.json.")
    common.log(f"  Skrev voiceover.mp3 ({len(audio) // 1024} KB, {total:.1f} s) "
               f"og words.json ({len(words)} ord).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trin 1: ElevenLabs-voiceover + ord-timing (voiceover.mp3 + words.json)")
    parser.add_argument("slug", help="videonavn — læser scripts/<slug>.txt, skriver output/<slug>/")
    args = parser.parse_args()

    common.validate_slug(args.slug)
    script_path = common.SCRIPTS_DIR / f"{args.slug}.txt"
    if not script_path.exists():
        common.die(f"Manuskriptet findes ikke: {script_path}")
    out_dir = common.OUTPUT_DIR / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    run(script_path, out_dir)


if __name__ == "__main__":
    main()
