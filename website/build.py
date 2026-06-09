#!/usr/bin/env python3
"""Bygger Broke to Wealth-bloggen (statisk HTML) fra POSTS-listen.
Kør: python3 build.py  →  genererer index.html, about.html, posts/*.html
Tilføj nye indlæg ved at tilføje en dict i POSTS og køre igen.
"""
from pathlib import Path

CHANNEL = "https://www.youtube.com/@broke-to-wealth"
SITE = Path(__file__).resolve().parent

# ── Indlæg ─────────────────────────────────────────────────────────────
# video_id: YouTube-id (fra youtu.be/XXXX). Tom string -> viser thumbnail
#           som "Watch on YouTube"-poster indtil du har id'et.
POSTS = [
 {
  "slug":"how-id-go-from-0-to-10000",
  "title":"How I'd Go From $0 to $10,000 Starting Over",
  "video_id":"VP9t9DnjXoo",
  "img":"zero-to-10k.png",
  "date":"Episode 1",
  "excerpt":"If I lost everything tomorrow, here's the exact path I'd use to rebuild my first $10,000 — and it has nothing to do with luck.",
  "body":"""
<p>Imagine you woke up tomorrow with nothing. No savings, no job, no safety net. Most people would panic. But if you understand a few simple money moves, starting from zero isn't a death sentence — it's a starting line.</p>
<h2>The plan, step by step</h2>
<ul>
<li><b>Hunt for problems, not jobs.</b> Every problem is something someone will pay to solve. On day one you look for work nobody wants to do — cash in hand, today.</li>
<li><b>Chase your first $100, not $10,000.</b> Once you prove you can make $100 from nothing, something in your brain changes forever.</li>
<li><b>Split every dollar: half to live, half to grow.</b> Broke people spend what they earn. Wealthy people plant it.</li>
<li><b>Buy leverage, not stuff.</b> A cheap tool that lets you charge more for the same hour beats anything that just looks nice.</li>
<li><b>Ask every customer for a referral.</b> One happy customer becomes three. That's not luck — that's asking.</li>
<li><b>Raise your prices, build a system, and keep going when it gets boring.</b> Boredom isn't a stop sign. It's proof the system works.</li>
</ul>
<p>The $10,000 was never really the point. The point is who you become while earning it. You don't need money to start — you need a different way of seeing.</p>
"""
 },
 {
  "slug":"how-broke-people-think-vs-rich-people",
  "title":"How Broke People Think vs. How Rich People Think",
  "video_id":"71SS_NJ-wLI",
  "img":"broke-vs-rich.png",
  "date":"Episode 2",
  "excerpt":"Two people can earn the exact same paycheck. One stays broke forever. The other quietly gets rich. The difference is six ways they think.",
  "body":"""
<p>The gap between broke and rich was never about the size of the paycheck. It's about the thinking behind it. Here are the mindset shifts that quietly separate the two.</p>
<h2>The six shifts</h2>
<ul>
<li><b>Price vs. value.</b> Broke people see the price tag. Rich people see the whole cost over time.</li>
<li><b>Earning vs. owning.</b> A paycheck stops when you stop. Owned assets keep paying while you sleep.</li>
<li><b>Looking rich vs. being rich.</b> One chases the feeling of wealth. The other builds the real thing.</li>
<li><b>Blame vs. ownership.</b> Blame feels good for a second. Ownership is the only thing that gives you power to change.</li>
<li><b>Stuck vs. curious.</b> Where broke eyes see a wall, rich eyes see a door nobody opened yet.</li>
<li><b>Time vs. systems.</b> One trades hours for money. The other builds things that earn without them.</li>
</ul>
<p>Notice that none of these are about how much money you already have. Money doesn't make you rich — the way you think does. The money just follows.</p>
"""
 },
 {
  "slug":"how-to-actually-use-ai-to-make-money",
  "title":"99% of People Don't Know How to Actually Use AI to Make Money",
  "video_id":"",
  "img":"ai-money-99.png",
  "date":"Episode 3",
  "excerpt":"Most people use AI like a toy. A tiny group uses the exact same tool to make money. Here's the one shift between them.",
  "body":"""
<p>99% of people treat AI like a toy — a search engine, a homework machine — then wonder why it never makes them a dollar. The 1% understand one thing almost nobody else does.</p>
<h2>The shift</h2>
<p>Most people ask AI to <i>give</i> them something: an answer, a joke, a summary. The few ask AI to <i>build</i> them something another person will pay for. One group consumes. The other produces. Only one of those ever leads to money.</p>
<ul>
<li><b>There is no magic tool.</b> AI doesn't pay you — people pay you. AI is leverage, not a lottery ticket.</li>
<li><b>Point it at what people already pay for.</b> Writing, design, editing, marketing, admin — then deliver it faster and cheaper using AI.</li>
<li><b>Start ugly.</b> The 1% offer a rough service today and learn by doing. The 99% are still "getting ready".</li>
</ul>
<p>Stop asking AI "what can you do for me?" and start asking "who would pay for what we just made?" Answer that, and you've crossed the line most people never will.</p>
"""
 },
 {
  "slug":"i-make-faceless-youtube-videos-with-ai",
  "title":"I Make Faceless YouTube Videos With AI (Here's How)",
  "video_id":"NiL0IPPHN2U",
  "img":"made-by-ai.png",
  "date":"Episode 4",
  "excerpt":"The voice isn't human. The drawings were made by AI. The script was written by AI. And it cost about the price of a sandwich.",
  "body":"""
<p>No camera. No microphone. No face. I type a single sentence, and AI does the rest — it writes the script, creates the voice, draws every image, and edits the whole video automatically. Fifteen minutes later I have a finished video, for a couple of dollars.</p>
<h2>Why this quietly builds wealth</h2>
<ul>
<li><b>It removes every wall.</b> No equipment, no editing skills, no need to show your face.</li>
<li><b>It scales.</b> One video, a hundred videos, even multiple channels — each one a tiny asset that can earn for years.</li>
<li><b>High-value topics pay more.</b> In money and finance, the ad share is among the highest there is.</li>
</ul>
<p>But it's not a magic button. The tools do the heavy lifting — you still have to pick good topics, hit publish, and keep going. The tools are available to everyone. The only difference is who actually opens the laptop and begins.</p>
"""
 },
 {
  "slug":"6-ways-rich-people-use-debt",
  "title":"6 Ways Rich People Use Debt to Get Richer",
  "video_id":"l7dCY18IomU",
  "img":"debt-one-number.png",
  "date":"Episode 5",
  "excerpt":"There's one number that decides whether debt destroys you or makes you rich — and it isn't the interest rate.",
  "body":"""
<p>Two people can take the exact same loan, at the exact same rate, on the exact same day. One ends up buried, the other ends up richer. The difference is one number.</p>
<h2>Debt is just rented money</h2>
<p>A loan is renting money. Interest is the rent. The only question that matters: does what you do with that money earn more than the rent costs? That gap is called <b>the spread</b> — and your return on your own cash is the spread multiplied by how many dollars you control for every dollar of your own.</p>
<h2>The six ways</h2>
<ul>
<li><b>Trade credit.</b> Control inventory with none of your own money using supplier terms.</li>
<li><b>Real estate.</b> Buy below value, force it up, refinance, and recycle your entire down payment.</li>
<li><b>Buy &amp; borrow.</b> Borrow against assets instead of selling them.</li>
<li><b>The dark side.</b> Margin calls and short selling — leverage multiplies in <i>both</i> directions.</li>
<li><b>0% arbitrage.</b> Move high-interest debt onto 0% — a guaranteed return almost no investment matches.</li>
<li><b>Your cost of money.</b> A better borrowing reputation lowers the rent on every loan for life.</li>
</ul>
<p>The poor pay debt off as fast as they can. The rich ask what the spread is and how many dollars they can control. Same loans, same rates, one number.</p>
"""
 },
]

# ── Skabeloner ─────────────────────────────────────────────────────────
def head(title, desc, rel=""):
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{rel}style.css">
</head><body>
<header class="site"><div class="nav">
<a class="brand" href="{rel}index.html"><img src="{rel}img/logo.png" alt="Broke to Wealth"><span><span class="b">Broke to</span> <span class="k">Wealth</span></span></a>
<nav><a class="navlink" href="{rel}index.html">Blog</a><a class="navlink" href="{rel}about.html">About</a>
<a class="yt" href="{CHANNEL}" target="_blank" rel="noopener">▶ YouTube</a></nav>
</div></header>"""

def footer(rel=""):
    return f"""<footer class="site"><div class="wrap">
<p><b>Broke to Wealth</b> · <a href="{CHANNEL}" target="_blank" rel="noopener">YouTube</a> · <a href="{rel}about.html">About</a></p>
<p class="disc">Broke to Wealth is educational content, not financial advice. Videos contain AI-assisted narration and illustrations. Do your own research before making money decisions.</p>
</div></footer></body></html>"""

def newsletter():
    return """<div class="news">
<h3>Get the money moves in your inbox</h3>
<p>One short email a week. No spam, no fluff — just how the rich actually think, earn, and keep their money.</p>
<form action="#" method="post" onsubmit="alert('Connect this form to your newsletter tool (Beehiiv / Mailchimp).');return false;">
<input type="email" placeholder="you@email.com" required>
<button type="submit">Join free</button>
</form>
<small>Unsubscribe anytime.</small></div>"""

def video_block(p, rel=""):
    if p["video_id"]:
        return f'<div class="embed"><iframe src="https://www.youtube.com/embed/{p["video_id"]}" title="{p["title"]}" allowfullscreen loading="lazy"></iframe></div>'
    return f'<a class="poster embed" href="{CHANNEL}" target="_blank" rel="noopener" style="padding-bottom:0;height:auto"><img src="{rel}img/{p["img"]}" alt="{p["title"]}"><span class="play"><span>▶ Watch on YouTube</span></span></a>'

def cta():
    return f"""<div class="cta"><h3>Watch the full breakdown on YouTube</h3>
<p>New videos every week. Subscribe so the algorithm stops hiding us.</p>
<a class="btn" href="{CHANNEL}" target="_blank" rel="noopener">▶ Subscribe on YouTube</a></div>"""

# ── Byg ────────────────────────────────────────────────────────────────
def build_index():
    cards = ""
    for p in POSTS:
        cards += f"""<a class="card" href="posts/{p['slug']}.html">
<img src="img/{p['img']}" alt="{p['title']}">
<div class="body"><h3>{p['title']}</h3><p>{p['excerpt']}</p>
<span class="more">Read more →</span></div></a>\n"""
    html = head("Broke to Wealth — How the rich actually think, earn & keep money",
                "Short, no-fluff breakdowns of money psychology, AI, and wealth. New videos every week.")
    html += f"""<div class="hero"><img src="img/logo.png" alt="Broke to Wealth">
<h1>Broke to <span class="k">Wealth</span></h1>
<p class="tag">The money moves they never taught you.</p>
<p class="intro">No-fluff breakdowns of money psychology, AI, and how the wealthy actually think, earn, and keep their money. Watch the videos, read the recaps.</p></div>
<div class="wrap">{newsletter()}
<div class="section-title">Latest episodes</div>
<div class="grid">{cards}</div></div>{footer()}"""
    (SITE/"index.html").write_text(html, encoding="utf-8")

def build_about():
    html = head("About — Broke to Wealth", "What Broke to Wealth is about.", )
    html += f"""<div class="wrap"><article>
<h1>About Broke to Wealth</h1>
<p>Most people spend their whole lives broke — not because they don't work hard, but because nobody taught them how money actually works.</p>
<p><b>Broke to Wealth</b> breaks down the money moves, mindset shifts, and habits that separate the broke from the wealthy. No hype. No get-rich-quick schemes. Just the stuff they never taught you in school — explained simply, in a few minutes.</p>
<p>New videos every week on <a href="{CHANNEL}" target="_blank" rel="noopener">YouTube</a>. Each post here is the written companion to a video.</p>
{newsletter()}
<div class="disclaimer">⚠️ Broke to Wealth is for education and entertainment only — it is not financial advice. Content includes AI-assisted narration and illustrations.</div>
</article></div>{footer()}"""
    (SITE/"about.html").write_text(html, encoding="utf-8")

def build_posts():
    for i,p in enumerate(POSTS):
        prev_l = f'<a href="{POSTS[i-1]["slug"]}.html">← {POSTS[i-1]["title"][:28]}…</a>' if i>0 else '<a href="../index.html">← All posts</a>'
        next_l = f'<a href="{POSTS[i+1]["slug"]}.html">{POSTS[i+1]["title"][:28]}… →</a>' if i<len(POSTS)-1 else '<a href="../index.html">All posts →</a>'
        html = head(p["title"]+" — Broke to Wealth", p["excerpt"], rel="../")
        html += f"""<div class="wrap"><article>
<h1>{p['title']}</h1>
<div class="meta">{p['date']} · Broke to Wealth</div>
{video_block(p, rel="../")}
{p['body']}
{cta()}
<div class="disclaimer">⚠️ Educational only, not financial advice.</div>
<div class="backlinks">{prev_l}{next_l}</div>
</article>
{newsletter()}
</div>{footer(rel="../")}"""
        (SITE/"posts"/f"{p['slug']}.html").write_text(html, encoding="utf-8")

build_index(); build_about(); build_posts()
print(f"✅ Bygget: index.html, about.html + {len(POSTS)} indlæg")
