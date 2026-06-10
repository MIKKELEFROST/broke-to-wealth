BROKE TO WEALTH — faceless finans-YouTube
=========================================
docs/BRAND.md           → kanal-identitet, fast figur, master-prompt, video-idéer
docs/FREMGANGSMÅDE.md   → trin-for-trin opskrift til at lave én video
docs/SCRIPT_PROMPT.md   → prompten der skriver manuskripterne
.env                    → API-nøgler (ElevenLabs + Gemini; OpenRouter til Seedance)
.venv/                  → projektets Python-miljø (requirements i skill'ens scripts/)
branding/               → banner, profil, watermark, kanalbeskrivelse
scripts/                → dine manuskripter (.txt)
output/                 → færdige videoer pr. mappe: <navn>.mp4 + thumbnail.png
                          + voiceover.mp3 + images/ (_test = testkørsel)
website/                → statisk blog (build.py genererer index/about/posts)
docs/STRUKTUR.md        → fuld struktur + konventioner
STATUS.md               → produktions-status pr. video

run.py samler selv den færdige .mp4 + thumbnail. Sidste trin = MANUEL upload til YouTube.
Selve programmet ligger i: pipeline/ (i dette repo)
