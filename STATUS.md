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
| money-dysmorphia | Money Dysmorphia: Why You Feel Broke (Even When You're Not) | ✅ | ✅ | ✅ | ❌ | ❌ | TREND (21/6); **RENDERET 18/6** (89 scener, 8:11, ~29 kr via batch); `upload.txt` m. kapitel-tider klar. ADSKILT fra broke-psychology: forvrænget *opfattelse*, ikke de mentale fælder |
| loud-budgeting | Loud Budgeting: The Money Trend Quietly Making People Rich | ✅ | ❌ | ❌ | ❌ | ❌ | TREND (24/6); script + `upload.txt` klar — **endnu IKKE forlænget til 8-9 min** (1103 ord ≈ 6 min) |
| invest-300-a-month | How $300 a Month in the NASDAQ 100 Quietly Makes You a Millionaire | ✅ | ✅ | ✅ | ❌ | ❌ | MONEY BREAKDOWN (5/7); **RENDERET 18/6** (108 scener, 10:21, ~35 kr via batch); script ~10,3 min (1797 ord) + `upload.txt` m. kapitel-tider klar. NASDAQ 100 hele vejen; forklarer hvad indekset indeholder (Apple/MSFT/NVIDIA…) + udsigter næste 10 år (AI). **Hero: sidste 10 år ved ~20% → $36k bliver ~$113k i dag.** 30 år bevidst nedjusteret til konservative 13% → ~$1,3 mio (millionær); overlevede dot-com + 2008; 1 ærlig "ikke garanteret"-linje |
| investing-vs-saving | Saving vs. Investing: Why One Makes You Rich and One Keeps You Safe | ✅ | ✅ | ✅ | ❌ | ✅ (ID mangler i build.py) | SEEDANCE-ANIMERET (engangs-eksperiment) — uploadet 10/6; indsæt `video_id` i `website/build.py` |
| investing-vs-saving-stills | Should You Save or Invest First? The Right Order to Build Wealth | (deler script) | ✅ | ✅ | — | ❌ | samme lyd/billeder som investing-vs-saving men EGEN titel/thumbnail/beskrivelse ("rækkefølge"-vinkel) — klassisk still-render |

> **Politik (10/6-2026):** Seedance/Higgsfield-animation bruges IKKE igen, medmindre det
> eksplicit efterspørges — stillbilleder foretrækkes. `pipeline/assemble_clips.py` beholdes
> som mulighed.

**Forklaring:** ✅ = klar · ❌ = mangler · ⚠️ = problem, se noter.

## Udgivelsesplan (fra 17/6 2026)

**Kadence: 2 videoer/uge — onsdag + søndag.** Rækkefølgen er en binge-loop: videoerne
teaser hinanden i denne rækkefølge, så behold den. 🔥 = trend-drevet (2026-analyse:
penge-psykologi/adfærd, højt CPM, annoncørvenligt).

| Dato | Slug | YouTube-titel | Render-status |
|---|---|---|---|
| **Ons 17/6** (i dag) | broke-psychology | The Psychology of Being Broke | ❌ script klar — render i dag |
| Søn 21/6 🔥 | money-dysmorphia | Money Dysmorphia: Why You Feel Broke (Even When You're Not) | ✅ **RENDERET 18/6** (89 scener, 8:11, ~29 kr via batch) — klar til upload |
| Ons 24/6 🔥 | loud-budgeting | Loud Budgeting: The Money Trend Quietly Making People Rich | ❌ klar A-Z — **render senest ~22/6** |
| Søn 28/6 | middle-class-trap | Why the Middle Class Will Never Be Rich | ❌ script klar |
| Ons 1/7 | saving-wont-work | Why Saving Money Will Never Make You Rich | ❌ script klar |
| Søn 5/7 🆕 | invest-300-a-month | How $300 a Month in the NASDAQ 100 Quietly Makes You a Millionaire | ✅ **RENDERET 18/6** (108 scener, 10:21, ~35 kr) — klar til upload |
| Ons 8/7 | lifestyle-creep | How Lifestyle Creep Quietly Bankrupts People | ❌ script klar |

> compound-interest (planlagt 14/6) er **renderet** og klar til upload — ligger uden for
> denne fremad-plan. Husk upload + `video_id` i `website/build.py`.

**Binge-loop:** Trend-parret er rykket FORREST (17/6-2026) fordi trends er ferskvare; evergreen
skubbet bagud. Intakt: money-dysmorphia → loud-budgeting, og evergreen-kæden middle-class-trap →
saving-wont-work → lifestyle-creep (lifestyle-creeps referencer til "the saving video" + "the
compound video" holder stadig). **Ét brud:** broke-psychology slutter med at tease *middle-class-trap*,
som nu først kommer 28/6 — sæt evt. end-screen/kort på broke-psychology manuelt til money-dysmorphia.

**Produktionskommandoer** (kør 2-3 dage før hver dato, fra projektroden, i denne rækkefølge):

```
.venv/bin/python pipeline/run.py broke-psychology --title "The Psychology of Being Broke" --hook "Your brain keeps you broke"
.venv/bin/python pipeline/run.py money-dysmorphia --title "Money Dysmorphia: Why You Feel Broke (Even When You're Not)" --hook "Richer than you feel"
.venv/bin/python pipeline/run.py loud-budgeting --title "Loud Budgeting: The Money Trend Quietly Making People Rich" --hook "Broke on purpose"
.venv/bin/python pipeline/run.py middle-class-trap --title "Why the Middle Class Will Never Be Rich" --hook "Comfort is the trap"
.venv/bin/python pipeline/run.py saving-wont-work --title "Why Saving Money Will Never Make You Rich" --hook "Saving keeps you poor"
.venv/bin/python pipeline/run.py invest-300-a-month --title "How \$300 a Month in the NASDAQ 100 Quietly Makes You a Millionaire" --hook "\$300 a month"
.venv/bin/python pipeline/run.py lifestyle-creep --title "How Lifestyle Creep Quietly Bankrupts People" --hook "The silent killer of every raise"
```

money-dysmorphia + loud-budgeting har **`output/<slug>/upload.txt` pre-staget** (titel +
beskrivelse + tags + kapitel-titler). Efter render: slå starttider op i `words.json` og udfyld
de `0:00`-placeholdere (run.py rører ikke upload.txt).

**Beslutninger 18/6-2026:**
- **Billed-tempo ændret:** `build_scenes.py` → min **3,5 s** / max **6,0 s** (roligere look). Gælder ALLE fremtidige renders. Effekt: ~0,2 billeder/sek (fx money-dysmorphia 96 billeder mod 116 med gammelt tempo).
- **Videolængde:** mål nu **8-9 min** (låser mid-roll op). money-dysmorphia forlænget til 1450 ord (~8,25 min). **Mangler stadig forlængelse:** loud-budgeting + de 4 evergreen-scripts.
- **Affiliate-blok:** udskudt (ikke nu).
- **3 thumbnails pr. video — DYNAMISKE A/B-vinkler:** `thumbnail-1/2/3.png` genereres nu med 3 video-specifikke vinkler udledt af titel + manuskript via LLM (`dynamic_ideas`, INTET preset — generiske `FALLBACK_CONCEPTS` kun hvis LLM fejler). Til A/B-test. Verificeret live på money-dysmorphia.
- **Tekst i billeder:** scene-prompten forbyder nu fulde sætninger/undertekster — kun korte labels (1-3 ord). Verificeret på testscener (`output/_test/text-rule/`). Gælder loud-budgeting + alle fremtidige renders. money-dysmorphia **re-renderet 18/6 med den rene prompt** ✅ (kun billeder regenereret, ~20 kr; TTS/scener/thumbnails genbrugt).
- **Billed-API → Batch (50% rabat):** alle scenebilleder + thumbnails sendes nu i ét asynkront Gemini Batch-job (`common.gemini_generate_images_batch`), SAMME model `gemini-3.1-flash-image` (nul kvalitetsændring). Synkron fallback pr. billede hvis batch fejler. Slå fra ved hastværk med `BTW_BATCH=0`. **Effekt: ~52 → ~29 kr/video** (~190 kr/md sparet). **Verificeret live 18/6:** 89-billed-batch SUCCEEDED på ~1 min; hele renderen 4,1 min. Pris: async (op til 24t turnaround, men var minutter i praksis).

**Udestående manuelle opgaver:**
- money-dysmorphia: kapitel-tider udfyldt ✅ — klar til upload (sæt "altered/synthetic content"-flag + indsæt `video_id` i `website/build.py` efter upload). loud-budgeting: udfyld kapitel-tider efter render.
- `video_id` for ai-money-99 mangler i `website/build.py` (posten `how-to-actually-use-ai-to-make-money`) — indsæt + kør `build.py`.
- Thumbnail til debt-one-number er kun 93K — regenerér når pipelinen kører igen.

**Workflow pr. video:** idé → `scripts/<slug>.txt` → kør pipeline (`run.py`) →
`output/<slug>/<slug>.mp4` + thumbnail → skriv `output/<slug>/upload.txt` (TITEL +
BESKRIVELSE + TAGS, jf. `docs/STRUKTUR.md`) → upload til YouTube → indsæt `video_id` i
`website/build.py` → kør `build.py`.
