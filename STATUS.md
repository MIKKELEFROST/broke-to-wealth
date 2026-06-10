# STATUS — produktion pr. video

## ⚠️ Redningsstatus (10. juni 2026)
Pipeline-koden (`~/.claude/skills/finance-yt-video/`), `.env` og `.venv` blev fundet SLETTET.
- ✅ Backup af `output/` (420M): `~/Desktop/broke-to-wealth-output-backup-20260610.tar.gz` — **flyt den til ekstern disk/sky!**
- ✅ Pipeline genopbygget i `pipeline/` (inde i repoet, så den ikke kan forsvinde igen).
  Verificeret mod de gamle artefakter: scenes/timeline byte-identiske, mp4-render
  frame-identisk (6141 frames, samme x264-profil). Brug: `pipeline/README.md`.
- ✅ `.env` genskabt med alle 4 nøgler inkl. `ELEVENLABS_VOICE_ID` (10/6 kl. 9:35).
  **Husk:** gem nøgler + voice_id i password manager — .env er uden for git og backup.
- ✅ `.venv` genskabt (`pipeline/requirements.txt`).
- ❌ **DIG:** Kør `gh auth login`, derefter kan repoet pushes til privat GitHub-remote.

Manuelt vedligeholdt overblik. Opdatér når en video skrider videre.
"Uploadet" udledes af `video_id` i `website/build.py` (tom = ikke uploadet).

| slug | titel | script | .mp4 | thumbnail | website-post | uploadet (video_id) | noter |
|---|---|:--:|:--:|:--:|:--:|---|---|
| zero-to-10k | How I'd Go From $0 to $10,000 | ✅ | ✅ | ✅ | ✅ | ✅ `VP9t9DnjXoo` | — |
| broke-vs-rich | How Broke People Think vs. Rich People | ✅ | ✅ | ✅ | ✅ | ✅ `71SS_NJ-wLI` | — |
| made-by-ai | I Make Faceless YouTube Videos With AI | ✅ | ✅ | ✅ | ✅ | ✅ `NiL0IPPHN2U` | YouTube-titel: "...With Claude AI" |
| debt-one-number | 6 Ways Rich People Use Debt | ✅ | ✅ | ⚠️ | ✅ | ✅ `l7dCY18IomU` | thumbnail kun 93K (vs ~750-950K) — bør regenereres |
| ai-money-99 | 99% Don't Know How to Use AI to Make Money | ✅ | ✅ | ✅ | ✅ | ✅ (ID mangler i build.py) | live på YouTube — indsæt `video_id` i `website/build.py` + kør `build.py` |
| compound-interest | How Compound Interest Makes the Rich Richer While You Sleep | ✅ | ✅ | ✅ | ❌ | ❌ | produceret 10/6 — KLAR til upload (planlagt søn 14/6) |
| broke-psychology | The Psychology of Being Broke | ✅ | ❌ | ❌ | ❌ | ❌ | planlagt: ons 17/6 |
| middle-class-trap | Why the Middle Class Will Never Be Rich | ✅ | ❌ | ❌ | ❌ | ❌ | planlagt: søn 21/6 |
| saving-wont-work | Why Saving Money Will Never Make You Rich | ✅ | ❌ | ❌ | ❌ | ❌ | planlagt: ons 24/6 |
| lifestyle-creep | How Lifestyle Creep Quietly Bankrupts People | ✅ | ❌ | ❌ | ❌ | ❌ | planlagt: søn 28/6 |

**Forklaring:** ✅ = klar · ❌ = mangler · ⚠️ = problem, se noter.

## Udgivelsesplan juni 2026

**Kadence: 2 videoer/uge — onsdag + søndag.** Alle 5 hidtidige videoer er live.
Manuskripterne nedenfor er skrevet og klar i `scripts/` — de teaser hinanden i
rækkefølgen herunder (binge-loop), så behold rækkefølgen.

| Dato | Slug | Idé (BRAND.md) | YouTube-titel (forslag) |
|---|---|---|---|
| Søn 14/6 | compound-interest | #14 | How Compound Interest Makes the Rich Richer While You Sleep |
| Ons 17/6 | broke-psychology | #8 | The Psychology of Being Broke |
| Søn 21/6 | middle-class-trap | #1 | Why the Middle Class Will Never Be Rich |
| Ons 24/6 | saving-wont-work | #7 | Why Saving Money Will Never Make You Rich |
| Søn 28/6 | lifestyle-creep | #18 | How Lifestyle Creep Quietly Bankrupts People |

**Produktionskommandoer** (kør 2-3 dage før hver udgivelsesdato, fra projektroden):

```
.venv/bin/python pipeline/run.py compound-interest --title "How Compound Interest Makes the Rich Richer While You Sleep" --hook "Richer while you sleep"
.venv/bin/python pipeline/run.py broke-psychology  --title "The Psychology of Being Broke" --hook "Your brain keeps you broke"
.venv/bin/python pipeline/run.py middle-class-trap --title "Why the Middle Class Will Never Be Rich" --hook "Comfort is the trap"
.venv/bin/python pipeline/run.py saving-wont-work  --title "Why Saving Money Will Never Make You Rich" --hook "Saving keeps you poor"
.venv/bin/python pipeline/run.py lifestyle-creep   --title "How Lifestyle Creep Quietly Bankrupts People" --hook "The silent killer of every raise"
```

**Udestående manuelle opgaver:**
- `video_id` for ai-money-99 mangler i `website/build.py` (posten `how-to-actually-use-ai-to-make-money`) — indsæt + kør `build.py`.
- Thumbnail til debt-one-number er kun 93K — regenerér når pipelinen kører igen.

**Workflow pr. video:** idé → `scripts/<slug>.txt` → kør pipeline (`run.py`) →
`output/<slug>/<slug>.mp4` + thumbnail → skriv `output/<slug>/upload.txt` (TITEL +
BESKRIVELSE + TAGS, jf. `docs/STRUKTUR.md`) → upload til YouTube → indsæt `video_id` i
`website/build.py` → kør `build.py`.
