# Pipeline — "Broke to Wealth"

Laver én færdig YouTube-video ud fra et manuskript:
`scripts/<slug>.txt` → `output/<slug>/` med `<slug>.mp4` + `thumbnail.png`
(+ `voiceover.mp3`, `words.json`, `scenes.json`, `timeline.json`, `images/`).
Sidste trin er ALTID manuel upload til YouTube.

## Opsætning (engangs)

```bash
cd "/Users/onlinemarketingnu/Claude code/Youtube Kanal"
python3 -m venv .venv
.venv/bin/pip install -r pipeline/requirements.txt
brew install ffmpeg            # render-trinnet bruger ffmpeg/ffprobe
```

`.env` i projektroden (holdes ude af git) skal indeholde:

```
ELEVENLABS_API_KEY=...    # elevenlabs.io -> Settings -> API Keys
ELEVENLABS_VOICE_ID=...   # den faste dybe mandlige fortæller — SAMME hver gang
GEMINI_API_KEY=...        # aistudio.google.com/apikey (billeder + thumbnail)
OPENROUTER_API_KEY=...    # KUN til Seedance-eksperimenter — bruges ikke af pipelinen
```

Mangler en nøgle, stopper pipelinen med en tydelig fejl og vejledning.

## Brug

```bash
# Hele kæden (voiceover -> scener -> billeder -> .mp4 -> thumbnail), ~10-15 min:
.venv/bin/python pipeline/run.py zero-to-10k --title "How I'd go from \$0 to \$10k" --hook "\$0 TO \$10K"

# --title/--hook kan udelades — så gættes de ud fra slug'en.
# Genoptageligt: et trin springes over hvis dets output er FRISKT (findes og er
# nyere end trinnets inputs — et ændret manuskript genkører altså nedstrøms trin);
# --force gentager alt. Nøgler valideres FØR der bruges tid/penge (fail-fast).

# Kvalitets-workflow: stop efter scenes.json, udfyld 'visual'-felter manuelt, kør resten enkeltvis:
.venv/bin/python pipeline/run.py zero-to-10k --skip-images
.venv/bin/python pipeline/generate_images.py zero-to-10k
.venv/bin/python pipeline/assemble_video.py zero-to-10k
.venv/bin/python pipeline/generate_thumbnail.py zero-to-10k --title ... --hook ...

# Dårlige billeder: slet dem i output/<slug>/images/ og kør generate_images +
# assemble_video igen — kun de manglende billeder regenereres.
```

## Komponenter

- **`run.py`** — orkestrator. Kører de 5 trin med pr.-trin-logging og
  spring-over-logik (resume). `--skip-images` stopper efter `scenes.json`,
  `--force` gentager alt, `--name` overstyrer slug'en.
- **`tts.py`** — ElevenLabs (`eleven_multilingual_v2`, `mp3_44100_128`) →
  `voiceover.mp3` + `words.json`. Bruger `convert_with_timestamps` og grupperer
  karakter-timing til ord; lange manuskripter chunkes automatisk på
  sætningsgrænser (modelgrænse ~10.000 tegn).
- **`build_scenes.py`** — deterministisk segmentering af `words.json` til
  scener: klip ved sætningsslut efter ≥ 2,8 s, hårdt loft ved 4,5 s (≈ ét
  billede hvert ~4. sekund, ~50 pr. video). Skriver `scenes.json` (med tomt
  `visual`-felt) + `timeline.json` (filnavn `scene_NNNN_tSS.SSs.png` + start).
- **`generate_images.py`** — ét doodle-billede pr. scene via Gemini
  ("nano-banana") med master-prompten fra `docs/BRAND.md`; den faste figur er
  konstanten `DEFAULT_CHARACTER` (skift kun dér). Normaliserer output til
  1344×768 PNG RGB. Idempotent: genererer kun manglende filer.
- **`assemble_video.py`** — ffmpeg-render: stillbilleder efter `timeline.json`
  + `voiceover.mp3` → `<slug>.mp4` (1920×1080, H.264 High@4.0, yuv420p,
  24 fps, AAC mono 160 kbps, `-shortest`). Manglende billeder = højlydt fejl;
  `--reuse-previous` genbruger forrige billede eksplicit i stedet.
- **`generate_thumbnail.py`** — `thumbnail.png` (1280×720) i samme stil med
  STOR hook-tekst. Validerer resultatet (1280×720 og > 200 KB — en tidligere
  kørsel gav en defekt 93 KB-fil) og prøver én gang til ved fejl.
- **`common.py`** — fælles hjælpere: stier (alt findes relativt til denne
  mappe), `.env`-indlæsning, atomiske skrivninger (temp-fil + rename),
  JSON-format (`indent=1`, ASCII, ingen slut-newline — matcher de gamle
  output-filer 1:1), scene-filnavnsformlen og Gemini-billedkaldet med
  model-fallback.

## Noter

- JSON-formater, billeddimensioner og mp4/mp3-profil matcher de eksisterende
  mapper under `output/` 1:1 — de kan bruges som facit ved regressionstjek.
- YouTube-upload er bevidst IKKE automatiseret. Husk ved upload:
  "altered/synthetic content"-flaget + disclosure-linjen
  "⚠️ This video contains AI-assisted narration and illustrations."
- Efter upload: opdatér `STATUS.md` og indsæt `video_id` i `website/build.py`.
