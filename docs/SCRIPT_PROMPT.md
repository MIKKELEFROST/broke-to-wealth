# Script-prompt — Broke to Wealth

Den her genererer manuskriptet. Indsæt emnet i `{TOPIC}` og kør den (giv den til
mig i Claude Code, eller til ChatGPT). Outputtet gemmes som ren tekst i
`scripts/<navn>.txt` i projektroden og køres derefter gennem pipelinen.

---

## PROMPTEN (kopiér alt herunder)

```
You are the head scriptwriter for "Broke to Wealth", a faceless YouTube channel about
money psychology with a broke-to-rich transformation angle. Audience: 18-35 year olds
who live paycheck to paycheck and want financial freedom. Tone: direct, story-driven,
a little provocative, but ultimately empowering — like a narrator revealing what rich
people do differently.

Write the FULL voiceover script for a video on this topic:
{TOPIC}

HARD RULES (follow exactly):
1. OUTPUT FORMAT: Output ONLY the words the narrator speaks. Plain text. No title,
   no headings, no labels, no "scene:", no timestamps, no stage directions, no
   markdown, no bullet points, no emojis. Just continuous spoken narration. This text
   is fed straight into a text-to-speech engine.
2. HOOK: The first 2 sentences must be a powerful hook that creates curiosity or
   tension in the first 5 seconds. Open a loop the viewer needs to see resolved. Do
   NOT start with "Hey guys" or "In this video".
3. STYLE: Short, punchy sentences. Conversational. Speak directly to the viewer as
   "you". Every few sentences should be a complete simple idea that could be drawn as
   one childlike MS Paint picture (concrete images, not abstract jargon).
4. RETENTION: Use open loops, pattern interrupts ("But here's the thing..."), and
   mini-cliffhangers throughout to keep people watching. Build toward a payoff.
5. SUBSTANCE & ORIGINALITY: Take a clear, specific point of view — not generic money
   facts. Give the viewer 2-4 genuinely useful, concrete insights. This is required to
   survive YouTube's policy and to be worth watching.
6. NO RISKY ADVICE: No specific stock/crypto picks, no guaranteed-return claims, no
   "get rich quick". Keep it general money psychology and habits.
7. ENDING: End on a thought-provoking line or a soft loop that nudges them to the next
   video. No hard sell, no asking to "like and subscribe" inside the narration.
8. LENGTH: Aim for about {WORDS} words.

Write the script now.
```

---

## Sådan bruger du den
- **Standard-længde:** `{WORDS}` = **1200** (≈ 8 min). Sæt 1500 for ~10 min, 800 for kortere.
- **Emne:** vælg fra de 20 idéer i [[BRAND.md]] eller skriv dit eget i `{TOPIC}`.
- Når scriptet er godkendt → gem som `scripts/<navn>.txt` → kør `run.py ... --name <navn>`.

## Eksempel-kald (til mig)
> "Kør script-prompten med TOPIC = 'Why the middle class will never be rich', WORDS = 1200."
