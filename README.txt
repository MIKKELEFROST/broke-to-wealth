BROKE TO WEALTH — faceless finans-YouTube
=========================================
docs/BRAND.md           → kanal-identitet, fast figur, master-prompt, video-idéer
docs/FREMGANGSMÅDE.md   → trin-for-trin opskrift til at lave én video
docs/SCRIPT_PROMPT.md   → prompten der skriver manuskripterne
.env                    → API-nøgler (ElevenLabs + Gemini; OpenRouter til Seedance)
.venv/                  → projektets Python-miljø (requirements i pipeline/requirements.txt)
branding/               → banner, profil, watermark, kanalbeskrivelse
scripts/                → dine manuskripter (.txt)
output/                 → færdige videoer pr. mappe: <navn>.mp4 + thumbnail-1..3.png
                          + voiceover.mp3 + images/ (valgfrit facebook/ + shorts/ 9:16-teasere;
                          _test = testkørsel, seedance-tests = eksperimenter)
website/                → statisk blog (build.py genererer index/about/posts)
docs/STRUKTUR.md        → fuld struktur + konventioner
STATUS.md               → produktions-status pr. video

run.py samler selv den færdige .mp4 + thumbnail. Sidste trin = MANUEL upload til YouTube.
Selve programmet ligger i: pipeline/ (i dette repo).
make_fb_clip.py laver lodrette 9:16-teasere til Facebook/Shorts.
(Dette er et kort overblik; CLAUDE.md + docs/STRUKTUR.md er de autoritative.)
