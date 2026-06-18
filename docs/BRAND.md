# BROKE TO WEALTH — brand & statisk opsætning

Det faste fundament for kanalen. Alt her ændres sjældent — det er det der gør
videoerne genkendelige og holder kanalen konsistent (og på rette side af YouTubes
2026-politik).

---

## Kanal-identitet
- **Navn:** Broke to Wealth
- **Handle:** @broke-to-wealth  *(det faktiske handle på den oprettede kanal)*
- **Tagline:** "From broke to wealth — the money moves they never taught you."
- **Sprog:** Engelsk
- **Niche:** Finans / økonomi, AI, automation, penge-psykologi, "how to get rich" — alt samlet under penge-paraplyen (fattig → rig)
- **Målgruppe:** 18-35, vil ud af at leve fra løn til løn, drømmer om økonomisk frihed
- **Tone:** Direkte, fortællende, motiverende/håbefuld OG **handlingsorienteret/rådgivende** — giv konkrete trin og "gør-dette"-råd.
  GUARDRAIL (opdateret 18/6-2026): INGEN individuelle aktie/krypto-tips og INGEN garantier (beskytter monetisering). Brede, populære indeks (S&P 500, NASDAQ 100) er OK som generel uddannelse. Tonen må gerne være stærkt optimistisk, men behold ALTID mindst én kort ærlig linje ("ikke garanteret / markedet kan falde / ikke finansiel rådgivning").

## Den faste figur (kanalens "ansigt")
Samme tilbagevendende karakter i HVER video — krav for at overleve YouTubes
faceless-politik og det der gør kanalen genkendelig:
> En simpel skaldet stick-mand med rundt hoved og et lille sort slips.
> Tegnet identisk hver gang. Han er "helten" der går fra broke til wealth.

(Defineret i `generate_images.py` → `DEFAULT_CHARACTER`. Skift kun ét sted.)

## Visuel stil (fast)
- Ekstremt simpel MS Paint / barnlig doodle, tykke skæve sorte streger
- Flade farver, ren hvid baggrund, ingen skygger/3D/cinematic
- 16:9, masser af tom plads, ét tydeligt motiv pr. billede
- **Tekst-regel:** korte labels/overskrifter OK (1-3 ord), men INGEN fulde sætninger/undertekster i billedet — voiceoveren bærer teksten (juni 2026)
- **Roligt tempo: skift hvert ~3,5-6 sek.** (min 3.5/max 6.0 — valgt juni 2026 for et roligere essay-look). Billedantal skalerer med længden: ~0,2 billeder/sek, ~14-16 ord/billede.
- Kør den RÅ v1: `visual`-felter udfyldes IKKE (hurtig produktion, energisk look)

## Stemme (fast)
- ElevenLabs, voice_id i `.env` (`ELEVENLABS_VOICE_ID`) — dyb mandlig fortæller
- Model: `eleven_multilingual_v2` (bedst) — skift til `eleven_flash_v2_5` for halv pris
- Brug SAMME stemme hver gang (genkendelighed)

---

## 🎯 MASTER-PROMPTEN (fra videoen WODnqHPLR38)

### Original-prompten han bruger i videoen (reference):
> You are going to generate images for a YouTube script. **One image for every
> timestamp in the script.** Your job is to read the script carefully and create a
> separate image for each timestamp. If the script has timestamps like 0 seconds,
> 3 seconds, 7 seconds, 10 seconds, 12 seconds, 20 seconds, then you must generate
> one image for each of those timestamps.
>
> **Style requirements:** The image must look like it's an extremely simple beginner
> drawing made in MS Paint. It should look like someone who is not good at drawing
> created it quickly by hand. White background, no 3D, no cinematic lighting.

### Vores version (Broke to Wealth — bygget ind i pipelinen):
I vores flow leverer `tts.py` + `build_scenes.py` automatisk "ét billede pr.
timestamp"-delen, så master-prompten er reduceret til ren STIL og kører pr. scene
i `generate_images.py`. Det er denne prompt der faktisk sendes til nano-banana:

```
A crude, childlike drawing made in MS Paint illustrating this idea: {SCENE}.
Convey the idea through the DRAWING itself, not through writing.
STYLE RULES (must follow exactly): extremely simple beginner doodle drawn quickly
by hand with a computer mouse; thick wobbly uneven black outlines; flat solid fill
colors; plain pure-white background; NO shading, NO gradients, NO 3D, NO photorealism,
NO cinematic lighting, NO fine detail. It should look like someone who is bad at
drawing made it in 30 seconds. Clear and readable, single simple scene, lots of empty
white space.
TEXT RULE (critical): do NOT write the sentence, a caption or a subtitle, and do NOT
paraphrase the narration as text. At most a FEW very short label words are allowed
(1-3 words, e.g. one word on an object or a short contrast label) — NEVER a full sentence.
Finance and money theme. Whenever a person appears, draw the SAME
recurring character: a simple bald round-headed stick man wearing a small black
necktie. Keep him identical every time. 16:9 horizontal composition.
```
- `{SCENE}` = scenens narration (eller det konkrete `visual`-felt vi udfylder)
- Negative prompt: `photorealistic, realistic, 3d render, detailed, shaded, gradient, cinematic, professional illustration, beautiful, polished`

---

## Titel-konventioner (pr. video)
- Kort, nysgerrigheds-drevet, engelsk. Tal/kontrast virker.
- Mønstre: "Why the middle class will never be rich", "The $5 habit that keeps you broke",
  "How broke people think (vs. rich people)"

## Thumbnail-konventioner
- Samme doodle-stil som videoen + den faste figur
- STOR tekst (2-4 ord), høj kontrast, ét tydeligt motiv
- Genereres med nano-banana i 16:9
- **3 dynamiske A/B-thumbnails pr. video** (`thumbnail-1/2/3.png`): vinklerne udledes pr. video fra titel + manuskript (forskellige hooks/greb, INTET preset) til A/B-test; vælg den bedste ved upload

## Beskrivelse-skabelon (pr. video)
Rigtig YouTube-beskrivelse med SEO for øje: de første ~150 tegn vises i
søgeresultaterne, så videoens vigtigste SØGEORD skal stå FORREST, vævet
naturligt ind (ingen keyword-stuffing).
```
<2-3 linjer der åbner med videoens vigtigste søgeord og gentager løftet>

<kort afsnit: overblik over hvad videoen gennemgår — flere søgeord naturligt indarbejdet>

Chapters:
0:00 <hook>
M:SS <sektion>
... (tiderne slås op i output/<slug>/words.json — find starttiden på hver sektions første ord)

⚠️ This video contains AI-assisted narration and illustrations.

#money #personalfinance #wealth #financialfreedom #brokeToWealth <+ 1-2 video-specifikke>
```
**AI-disclosure:** sæt "altered/synthetic content"-flaget ved upload (YouTube-krav).
Færdig beskrivelse + titel + tags gemmes i `output/<slug>/upload.txt` (jf. `docs/STRUKTUR.md`).

---

## 20 video-idéer (Broke to Wealth — content-pipeline)
1. Why the middle class will never be rich
2. How broke people think vs. how rich people think
3. The $5 coffee habit that's costing you $1,000,000
4. Why your salary is keeping you poor
5. The money trap nobody warns you about in your 20s
6. How the rich use debt (and you use it wrong)
7. Why saving money will never make you rich
8. The psychology of being broke
9. What banks don't want you to know about your money
10. How I'd go from $0 to $10k if I had to start over
11. The real reason you're always out of money
12. Why budgeting doesn't work for most people
13. The invisible spending that's draining you
14. How compound interest makes the rich richer while you sleep
15. The lie about "good debt" vs "bad debt"
16. Why being busy keeps you broke
17. The 1 money skill schools never teach
18. How lifestyle creep quietly bankrupts people
19. Poor habits that feel responsible (but aren't)
20. The mindset shift that turns broke into wealth
21. Loud budgeting: the money trend quietly making people rich  *(2026-trend; klar A-Z, planlagt 24/6)*
22. Money dysmorphia: why you feel broke (even when you're not)  *(2026-trend; klar A-Z, planlagt 21/6)*
23. How $300 a month in the NASDAQ 100 quietly makes you a millionaire  *(money breakdown; klar A-Z, planlagt 5/7)*

Relateret: [[faceless-youtube-finans-flow]]
