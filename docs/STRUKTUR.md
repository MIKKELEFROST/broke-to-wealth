# STRUKTUR — "Broke to Wealth"

Autoritativ beskrivelse af mappestruktur og konventioner. Ved tvivl: denne fil gælder.
`CLAUDE.md` giver overblikket; her er detaljerne.

## Mappe-for-mappe

| Mappe / fil | Formål | Hvad må ligge der |
|---|---|---|
| `docs/` | Projekt-dokumentation | BRAND.md, FREMGANGSMÅDE.md, SCRIPT_PROMPT.md, STRUKTUR.md (denne) |
| `branding/` | Visuelle YouTube-assets | banner, profil, watermark (+ `_thumb` versioner), `channel-description.txt` |
| `scripts/` | Rå manuskripter, ét pr. video | `<slug>.txt` — kun rigtige scripts, ingen placeholders |
| `pipeline/` | Selve programmet (genopbygget juni 2026) | `run.py` + trin-moduler + `requirements.txt` + `README.md` |
| `output/<slug>/` | Genereret video + mellemfiler | se "Output-mappe" nedenfor |
| `website/` | Statisk blog | `build.py`, `*.html`, `style.css`, `img/`, `posts/` |
| `STATUS.md` (rod) | Produktions-status pr. video | se `STATUS.md` |
| `README.txt` (rod) | Kort tekst-overblik (dublerer `CLAUDE.md` — hold dem i sync, eller fjern README.txt) | — |
| `.env` (rod) | API-nøgler — **IKKE i git** | ElevenLabs + Gemini + OpenRouter (Seedance) |
| `.env.example` (rod) | Skabelon for `.env` (committes) | nøgle-navne uden værdier + instruktioner |
| `.venv/` (rod) | Python-miljø — **IKKE i git** | — |

## Konventionen: ét script → én output-mappe

Et manuskript i `scripts/<slug>.txt` producerer mappen `output/<slug>/`:

```
output/<slug>/
├── <slug>.mp4        ← færdig video (manuel upload til YouTube)
├── thumbnail-1.png  ← 3 thumbnail-varianter (~750-950K typisk); vælg den bedste ved upload
├── thumbnail-2.png
├── thumbnail-3.png
├── upload.txt        ← upload-metadata: TITEL + BESKRIVELSE + TAGS (se nedenfor)
├── voiceover.mp3     ← stemme-track (ElevenLabs)
├── images/           ← scene-billeder (~50 stk pr. video)
├── scenes.json       ← scene-metadata
├── timeline.json     ← timing-data
├── words.json        ← ord/timing-log
├── facebook/         ← (valgfrit) lodret 9:16 FB-teaser fra make_fb_clip.py → fb_<slug>.mp4
├── shorts/           ← (valgfrit) lodret 9:16 Shorts-teaser fra make_fb_clip.py → short_<slug>.mp4
└── clips/            ← (valgfrit) animerede scene-klip (Seedance) til assemble_clips.py → scene_NNNN.mp4
```

Thumbnail: nye videoer har `thumbnail-1/2/3.png` (3 varianter); ældre videoer kan
have en enkelt `thumbnail.png`. `facebook/` og `shorts/` indeholder desuden et
`_assets/`-arbejdsbibliotek (PNG-overlays) som make_fb_clip.py genererer undervejs.

`upload.txt` skrives sammen med videoen (copy-paste til YouTube ved upload) og har tre
sektioner med overskrifterne `TITEL`, `BESKRIVELSE` og `TAGS`. Beskrivelsen følger
skabelonen i `docs/BRAND.md` (hook, "In this video:"-punkter, AI-disclosure-linjen,
hashtags); TAGS er én kommasepareret linje (~10-15 tags).

Reserverede output-mapper (ikke videoer):
- `output/_test/` — testkørsel / udvikling
- `output/seedance-tests/` — video-eksperimenter (Seedance)

Varianter af samme video:
- `output/<slug>-stills/` — stillbillede-versionen når der også findes en animeret
  (Seedance) version i `output/<slug>/` (fx `investing-vs-saving` + `investing-vs-saving-stills`).
  Stillbilleder er kanalens foretrukne format; den animerede er undtagelsen.

Ad-hoc analyse (ikke en del af pipelinen): mapper som `Analyze video/` i roden
(downloadede undertekster/`*.info.json` til research) er midlertidige — hører ikke
til output-konventionen og kan ryddes væk når analysen er færdig.

## Navngivning

- **slug** = kebab-case, fx `zero-to-10k`, `debt-one-number`.
- **Samme slug** bruges i `scripts/<slug>.txt` og `output/<slug>/`.
- Website bruger sine **egne** slugs (læsbare titler), defineret i `website/build.py` `POSTS`.
  Mapping mellem video-slug og website-slug holdes i `STATUS.md`.

## Git

Ignoreret (se `.gitignore`): `.env`, `.env.*`, `.venv/`, `__pycache__/`, `*.pyc`,
`output/`, `*.mp4`, `*.mp3`, `.DS_Store`. Dvs. tunge medier og hemmeligheder commit'es ikke —
kun scripts, docs, branding og website.

## Programmet

Selve pipelinen ligger i `pipeline/` **i dette repo** (flyttet ind juni 2026, efter at den
gamle placering `~/.claude/skills/finance-yt-video/` blev slettet — koden er genopbygget
fra output-artefakterne). `pipeline/run.py` orkestrerer alle trin og samler den færdige
`.mp4` + thumbnail. Se `pipeline/README.md` for brug. Sidste trin er altid MANUEL upload
til YouTube.

## Cross-posting / teasers

- `pipeline/make_fb_clip.py` — bygger et lodret **9:16-teaser-klip** ud fra en færdig
  16:9-video (+ `words.json`): brand-baggrund, indbrændte undertekster, CTA + end-card.
  Standalone (ffmpeg + PIL), uafhængigt af hovedpipelinen. To platform-varianter:
  `facebook` → `output/<slug>/facebook/fb_<slug>.mp4` og `shorts` →
  `output/<slug>/shorts/short_<slug>.mp4`. Brug: `python3 pipeline/make_fb_clip.py <slug> [cut_end_sek] [facebook|shorts]`.
- `pipeline/assemble_clips.py` — render-variant med animerede klip (Seedance) i stedet
  for stillbilleder; bruges KUN på eksplicit ønske (jf. `pipeline/README.md`).
