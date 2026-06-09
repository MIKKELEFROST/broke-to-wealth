# STATUS — produktion pr. video

Manuelt vedligeholdt overblik. Opdatér når en video skrider videre.
"Uploadet" udledes af `video_id` i `website/build.py` (tom = ikke uploadet).

| slug | titel | script | .mp4 | thumbnail | website-post | uploadet (video_id) | noter |
|---|---|:--:|:--:|:--:|:--:|---|---|
| zero-to-10k | How I'd Go From $0 to $10,000 | ✅ | ✅ | ✅ | ✅ | ✅ `VP9t9DnjXoo` | — |
| broke-vs-rich | How Broke People Think vs. Rich People | ✅ | ✅ | ✅ | ✅ | ✅ `71SS_NJ-wLI` | — |
| made-by-ai | I Make Faceless YouTube Videos With AI | ✅ | ✅ | ✅ | ✅ | ✅ `NiL0IPPHN2U` | YouTube-titel: "...With Claude AI" |
| debt-one-number | 6 Ways Rich People Use Debt | ✅ | ✅ | ⚠️ | ✅ | ✅ `l7dCY18IomU` | thumbnail kun 93K (vs ~750-950K) — bør regenereres |
| ai-money-99 | 99% Don't Know How to Use AI to Make Money | ✅ | ✅ | ✅ | ✅ | ❌ ikke uploadet | produceret men ikke uploadet til YouTube endnu |

**Forklaring:** ✅ = klar · ❌ = mangler · ⚠️ = problem, se noter.

**Workflow pr. video:** idé → `scripts/<slug>.txt` → kør pipeline (`run.py`) →
`output/<slug>/<slug>.mp4` + thumbnail → upload til YouTube → indsæt `video_id` i
`website/build.py` → kør `build.py`.
