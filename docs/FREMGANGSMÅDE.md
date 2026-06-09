# Fremgangsmåde — lav én finans-video

Faceless engelsk finans-kanal. ~10-15 min aktivt arbejde pr. video (mest script-
godkendelse + manuel upload); selve genereringen kører selv. "Du" = dig.
"Claude" = mig (her i Claude Code).

---

## ENGANGS — før første video
- [ ] Køb **ElevenLabs Starter** ($5/md) → kopiér API-nøgle (Settings → API Keys)
- [ ] Indsæt nøglen i `~/broke-to-wealth/.env` på `ELEVENLABS_API_KEY=`
      (filen har også `GEMINI_API_KEY` + `ELEVENLABS_VOICE_ID`)
- [ ] Opret projektets venv:
      `python3 -m venv ~/broke-to-wealth/.venv` →
      `~/broke-to-wealth/.venv/bin/pip install -r ~/.claude/skills/finance-yt-video/scripts/requirements.txt`
- [ ] Installér **ffmpeg** (`brew install ffmpeg`) — bruges til at samle videoen
- [ ] Opret **YouTube-kanal** (eget Google-login, intet link til dig/piece.dk),
      kanalnavn + logo (kan laves med nano-banana)
- [ ] (Valgfrit) En video-editor — kun hvis du vil finjustere. Ikke nødvendig;
      `run.py` samler selv den færdige video.

---

## PR. VIDEO — 5 trin

### 1. Vælg emne + vinkel  *(du + Claude, ~2 min)*
Vælg en underniche-vinkel (penge-psykologi, FIRE, spare-/gældshistorie, rich vs. poor).
**Vigtigst:** én klar, lidt provokerende vinkel/holdning — ikke generiske fakta.
Sig fx til Claude: *"Lav video om hvorfor middelklassen aldrig bliver rig."*

### 2. Script  *(Claude skriver, du godkender, ~5 min)*
Claude skriver et engelsk script med:
- **Hook i de første 5 sek.** (det afgør alt på engelsk YouTube)
- Fortællende, voiceover-tungt (tale > 30% af tiden), original holdning
- Længde efter mål (8-12 min ≈ 1.200-1.800 ord)
Gemmes som `~/broke-to-wealth/scripts/<navn>.txt`. Du læser igennem og retter.

### 3. Kør hele flowet  *(én kommando, kører ~10-15 min selv)*
```
~/broke-to-wealth/.venv/bin/python \
  ~/.claude/skills/finance-yt-video/scripts/run.py \
  ~/broke-to-wealth/scripts/<navn>.txt --name <navn> \
  --title "How I'd go from $0 to $10k" --hook "$0 TO $10K"
```
Kører alle 5 trin automatisk: voiceover → scener → billeder → **samlet .mp4** → **thumbnail**.
Resultat i `~/broke-to-wealth/output/<navn>/`:
- `<navn>.mp4` — færdig video (1080p), klar til upload
- `thumbnail.png` — YouTube-thumbnail (1280×720)
- + `voiceover.mp3`, `scenes.json`, `images/`, `timeline.json`

Dette er **brand-defaulten: rå v1** (ingen manuel billedredigering — hurtig, energisk).
`--title`/`--hook` styrer thumbnailen (udelades de, gættes de ud fra `--name`).

### 4. Tjek videoen  *(du, ~3 min)*
→ **Se `<navn>.mp4` igennem.** Lyder stemmen naturlig? Passer billederne nogenlunde?
- Dårlig stemme: skift `ELEVENLABS_VOICE_ID` i `.env` og kør igen.
- Enkelte dårlige billeder: slet dem i `images/` og kør `generate_images.py` +
  `assemble_video.py` igen (regenererer kun de manglende).

### 5. Upload manuelt  *(du, ~5 min)*
- Upload `<navn>.mp4` til YouTube (YouTube API-upload er bevidst ikke automatiseret — du gør det selv).
- Sæt `thumbnail.png` som thumbnail.
- **Titel:** kort, nysgerrigheds-drevet, engelsk.
- **Beskrivelse:** brug skabelonen i BRAND.md (husk AI-disclosure-linjen + sæt
  "altered/synthetic content"-flaget ved upload — YouTube-krav).
- Sæt fast udgivelses-rytme (fx 3-4/uge).

---

## Valgfrit: bedre billeder (fravalgt som default)
Brand-defaulten er rå v1. Vil du alligevel løfte billedkvaliteten på en enkelt video:
1. Kør trin 3 med `--skip-images` (stopper efter `scenes.json`).
2. Claude udfylder `visual`-feltet pr. scene med en KONKRET tegnebeskrivelse
   (fx "a stick man looking sadly at an empty wallet"). Tom `visual` → narrationen bruges direkte.
3. Kør de resterende enkelt-trin: `generate_images.py → assemble_video.py → generate_thumbnail.py`
   (se Enkelt-trin i SKILL.md).

---

## TJEKLISTE: undgå demonetisering (jan-2026-reglerne)
- [ ] Original vinkel/holdning i scriptet — ikke gen-genererede fakta
- [ ] Samme tilbagevendende figur i billederne (kanalens "ansigt")
- [ ] Voiceover-tungt (tale > 30% af runtime)
- [ ] Naturlig stemme (lyt efter robot-klang)
- [ ] Ikke ren copy-paste-volumen — hver video skal have substans

---

## Tal pr. video
- Tid: ~10-15 min aktivt (script-godkendelse + upload); genereringen kører selv
- Stemme: ~$0,45 (flash) – $0,90 (multilingual)
- Billeder: nano-banana (Gemini)
→ Trivielt mod finans-CPM.
