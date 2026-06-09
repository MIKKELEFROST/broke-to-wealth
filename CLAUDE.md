# Youtube Kanal — "Broke to Wealth"

## Formål
Faceless finans-YouTube-kanal. Projektet er en pipeline der laver én færdig video
(manuskript → voiceover → billeder → samlet .mp4 + thumbnail) til manuel upload på YouTube.
Engelsksproget indhold om penge, mindset og vaner. Ny video hver uge.

## Struktur
- `docs/BRAND.md` — kanal-identitet, fast figur, master-prompt, video-idéer
- `docs/FREMGANGSMÅDE.md` — trin-for-trin opskrift til at lave én video
- `docs/SCRIPT_PROMPT.md` — prompten der skriver manuskripterne
- `docs/STRUKTUR.md` — autoritativ beskrivelse af mappestruktur + konventioner
- `branding/` — banner, profil, watermark, kanalbeskrivelse
- `scripts/` — manuskripter (.txt), ét pr. video
- `output/<navn>/` — færdig video: `<navn>.mp4` + `thumbnail.png` + `voiceover.mp3` + `images/`
  (`_test` = testkørsel, `seedance-tests` = video-eksperimenter)
- `website/` — statisk blog; `build.py` genererer index/about/posts
- `.env` — API-nøgler (ElevenLabs + Gemini; OpenRouter til Seedance) — IKKE i git
- `.venv/` — Python-miljø — IKKE i git

## Noter
- Selve programmet/skill'en ligger i `~/.claude/skills/finance-yt-video/` (uden for denne mappe).
- `run.py` samler den færdige .mp4 + thumbnail. Sidste trin = MANUEL upload til YouTube.

## Konventioner
- Et manuskript i `scripts/<navn>.txt` → output havner i `output/<navn>/`.
- Hold `.env` ude af git (API-nøgler).
- Produktions-status pr. video: se `STATUS.md` i roden.
- Detaljer om struktur/navngivning: se `docs/STRUKTUR.md`.
