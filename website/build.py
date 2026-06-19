#!/usr/bin/env python3
"""Bygger Broke to Wealth-bloggen (statisk HTML) fra POSTS-listen.
Kør: python3 build.py  →  genererer index.html, about.html, posts/*.html
Tilføj nye indlæg ved at tilføje en dict i POSTS og køre igen.
"""
import html, json
from pathlib import Path

CHANNEL = "https://www.youtube.com/@broke-to-wealth"
FACEBOOK = "https://www.facebook.com/broke.to.wealth"
SITE_URL = "https://broke-to-wealth.onlinemarketing.nu"
SUB = CHANNEL + "?sub_confirmation=1"   # åbner abonner-dialogen direkte
SITE = Path(__file__).resolve().parent

def esc(s):
    """HTML-escape til attributter (title/description/Open Graph)."""
    return html.escape(str(s), quote=True)

# Organisation-skema (JSON-LD) genbruges på alle sider og knytter brandet til YouTube + Facebook
ORG = {
    "@type": "Organization",
    "@id": SITE_URL + "/#org",
    "name": "Broke to Wealth",
    "url": SITE_URL + "/",
    "logo": {"@type": "ImageObject", "url": SITE_URL + "/img/logo.png"},
    "sameAs": [CHANNEL, FACEBOOK],
}

def jsonld(*objs):
    data = {"@context": "https://schema.org", "@graph": list(objs)}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

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
  "video_id":"tTbZeiEH0mw",
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
 {
  "slug":"saving-vs-investing",
  "title":"Saving vs. Investing: Why One Makes You Rich and One Keeps You Safe",
  "video_id":"nlJqjvWWzJA",
  "img":"saving-vs-investing.png",
  "date":"Episode 6",
  "excerpt":"Two people save the exact same $100 a month for 20 years. One walks away with double the other — not from working harder, but from where the money lived.",
  "body":"""
<p>You and a friend each put away $100 a month. Same income, same discipline, same twenty years. At the end, your friend walks away with more than double your money — not because they worked harder, but because their money lived in a different place.</p>
<h2>Your money lives in a vault or a field</h2>
<p>A <b>vault</b> is your savings account: money goes in, sits still, stays safe. A <b>field</b> is investing: money goes in, gets planted, and grows into something bigger. Both feel responsible. Only one keeps up with the world.</p>
<ul>
<li><b>The vault leaks.</b> It pays 1–2% interest while inflation raises the price of everything by 2–3%+ a year. The number on screen never drops, but what it can buy shrinks every year.</li>
<li><b>The field grows — bumpily.</b> Investing means owning things that grow: pieces of businesses, assets that produce value while you sleep. Historically ~7–10% a year on average, but never in a straight line. The bumpiness is the price of admission.</li>
</ul>
<h2>Same sacrifice, very different result</h2>
<p>$100 a month for twenty years lands around <b>$26,000</b> in the vault versus roughly <b>$59,000</b> in the field. Stretch it to thirty years and the gap becomes a canyon: about <b>$45,000</b> versus <b>$150,000</b>. That isn't a detail — it's a different life.</p>
<h2>Vault, then field — in that order</h2>
<ul>
<li><b>Fill the vault first.</b> Three to six months of expenses. This is your oxygen — it's allowed to leak, because its job is to keep you from selling investments in a storm.</li>
<li><b>Short-term money stays in the vault.</b> Anything you'll need within five years — a deposit, a car, a wedding — is too soon for the field's bumps.</li>
<li><b>Long-term money goes in the field.</b> Every dollar you won't need for five, ten, twenty years is where time smooths the bumps and compounding does the heavy lifting.</li>
</ul>
<p>So look at each dollar and ask one question: when will I need you? Soon means vault. Not for years means field. Savers protect money and investors grow money — wealthy people do both, in exactly that order.</p>
"""
 },
 {
  "slug":"how-compound-interest-makes-you-rich",
  "title":"How Compound Interest Makes the Rich Richer While You Sleep",
  "video_id":"7yFX_k3jpYk",
  "img":"compound-interest.png",
  "date":"Episode 7",
  "excerpt":"The same force that quietly builds wealthy fortunes is working on you right now — except for most people, it's running in reverse.",
  "body":"""
<p>Last night, while you slept, the richest families on earth got a little richer — no meetings, no work. Their money grew in the dark by itself. The uncomfortable part: the exact same force is working on you right now. For most people, it's just running in reverse.</p>
<h2>Money that earns money</h2>
<p>Compound interest is a snowball at the top of a hill. One small push and it's pathetic — but every layer of snow helps it grab even more. The bigger it gets, the faster it grows. Money earns money, and then that new money earns money too.</p>
<h2>The penny that doubles</h2>
<p>Would you rather have $1,000,000 today, or a penny that doubles every day for thirty days? The penny wins — barely $5 after ten days, around $5,000 after twenty, then it goes vertical to <b>over $5 million</b> by day thirty. The growth is back-loaded: the beginning feels like nothing, the end feels like magic, and the only thing between them is time.</p>
<h2>The boring middle</h2>
<p>Most people never feel the magic — not because the math stops, but because the early years are dull. The line barely moves, friends are buying new cars, and people quit in the flat part of the curve that exists purely to test them. The wealthy don't quit there, because they've seen the steep end of the hill.</p>
<h2>The rule of 72</h2>
<p>Divide 72 by a yearly growth rate to see how long it takes to double. At 7% a year, money doubles roughly every decade. But flip it over: a credit card at 24% doubles the <i>debt</i> in about three years. Same force, opposite direction — carry expensive debt and you're the snowball, rolling downhill for someone else.</p>
<h2>The playbook</h2>
<ul>
<li><b>Get off the paying side first.</b> Killing 20%-a-year debt is like earning 20% guaranteed, tax-free.</li>
<li><b>Start now, even if it's tiny.</b> Time is the magic ingredient, and it's the one thing you can't buy later.</li>
<li><b>Automate it, then leave it alone.</b> Every dollar you pull out also takes every future double that dollar would have made.</li>
<li><b>Make peace with the boring middle.</b> Flat, flat, flat, then vertical. The dull years are the price of admission everyone pays.</li>
</ul>
<p>The rich aren't richer just because they work harder — their money works the night shift. Yours could too. The best day to push the snowball was years ago; the second best is the next time you get paid.</p>
"""
 },
 {
  "slug":"money-dysmorphia-why-you-feel-broke",
  "title":"Money Dysmorphia: Why You Feel Broke (Even When You're Not)",
  "video_id":"sAitAAVrpys",
  "img":"money-dysmorphia.png",
  "date":"Episode 8",
  "excerpt":"You can have money in the bank and still feel broke. There's a name for that broken feeling now — and it's quietly costing you.",
  "body":"""
<p>You can have money in the bank and still feel broke — actually anxious, actually convinced everyone your age is sprinting ahead. You check the account, the number is fine, and the panic doesn't go away. Study after study finds the same thing: most people who feel like they're drowning aren't. Their numbers are fine. Their feeling is broken.</p>
<h2>A broken lens, not a broken account</h2>
<p>You've heard of body dysmorphia — someone sees a body in the mirror that isn't really there, because the problem is the lens, not the body. <b>Money dysmorphia</b> is the same trick aimed at your bank account. You don't see the real number; you see a feeling. More than eight in ten people who have it say they feel behind everyone around them — even when those people are just as scared, faking it just as hard.</p>
<h2>The comparison machine</h2>
<p>Every day you scroll past a highlight reel: the beach, the new car, the first home. Your brain takes someone's best day and compares it to your average Tuesday. Nobody posts the loan bolted to the car or the statement under the vacation photo. You're measuring your full, messy reality against everyone else's best three seconds — the game is rigged before you open your eyes.</p>
<h2>It cuts both ways</h2>
<ul>
<li><b>Gauge stuck on empty.</b> People with real savings still feel one bad week from disaster, so they never invest, flinch at every purchase, and hoard out of fear — anxiety wearing the costume of discipline.</li>
<li><b>Gauge stuck on full.</b> Others feel rich while the card balance climbs and the future empties behind them. They feel wealthy precisely because they're spending like it.</li>
</ul>
<h2>Three moves to read the real dial</h2>
<ul>
<li><b>Turn the feeling into a number.</b> Write down what you have, what you owe, what comes in and goes out. Fog is terrifying because it has no edges — give it edges. Nine times out of ten the real number is less scary than the feeling.</li>
<li><b>Cut the comparison feed.</b> Your social feed is a broken scale you step on fifty times a day. Each time you feel the stab of being behind, name it: that's a trailer, not the movie.</li>
<li><b>Pick a scoreboard you can win.</b> There will always be someone richer. Stop racing strangers and race past-you: are you saving a little more, owing a little less, panicking a little slower than a year ago?</li>
</ul>
<p>The feeling of being behind is a symptom, not evidence. Your account has a real number and your anxiety has a different one — and most people spend years trusting the wrong one. You might be doing far better than you feel.</p>
"""
 },
]

# ── Skabeloner ─────────────────────────────────────────────────────────
def head(title, desc, rel="", path="", image="img/logo.png", og_type="website", ld=""):
    canonical = SITE_URL + "/" + path
    img_url = SITE_URL + "/" + image
    t = esc(title); d = esc(desc)
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#1faa3f">
<link rel="icon" type="image/png" href="{rel}img/logo.png">
<link rel="apple-touch-icon" href="{rel}img/logo.png">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Broke to Wealth">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{img_url}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img_url}">
<link rel="preconnect" href="https://www.youtube.com">
<link rel="stylesheet" href="{rel}style.css">
{ld}
</head><body>
<header class="site"><div class="nav">
<a class="brand" href="{rel}index.html"><img src="{rel}img/logo.png" alt="Broke to Wealth"><span><span class="b">Broke to</span> <span class="k">Wealth</span></span></a>
<nav><a class="navlink" href="{rel}index.html">Blog</a><a class="navlink" href="{rel}about.html">About</a>
<a class="yt" href="{CHANNEL}" target="_blank" rel="noopener">▶ YouTube</a><a class="fb" href="{FACEBOOK}" target="_blank" rel="noopener">f Facebook</a></nav>
</div></header>"""

def footer(rel=""):
    return f"""<footer class="site"><div class="wrap">
<p><b>Broke to Wealth</b> · <a href="{CHANNEL}" target="_blank" rel="noopener">YouTube</a> · <a href="{FACEBOOK}" target="_blank" rel="noopener">Facebook</a> · <a href="{rel}about.html">About</a></p>
<p class="disc">Broke to Wealth is educational content, not financial advice. Videos contain AI-assisted narration and illustrations. Do your own research before making money decisions.</p>
</div></footer></body></html>"""

def subscribe():
    return f"""<div class="sub">
<h3>Subscribe to Broke to Wealth on YouTube</h3>
<p>New no-fluff breakdowns of money psychology, investing, and how the wealthy actually think — every week. Hit subscribe so the next one finds you.</p>
<a class="btn-yt" href="{SUB}" target="_blank" rel="noopener">▶ Subscribe on YouTube</a>
<small>Free · new video every week.</small></div>"""

def video_block(p, rel=""):
    if p["video_id"]:
        return f'<div class="embed"><iframe src="https://www.youtube.com/embed/{p["video_id"]}" title="{p["title"]}" allowfullscreen loading="lazy"></iframe></div>'
    return f'<a class="poster embed" href="{CHANNEL}" target="_blank" rel="noopener" style="padding-bottom:0;height:auto"><img src="{rel}img/{p["img"]}" alt="{p["title"]}"><span class="play"><span>▶ Watch on YouTube</span></span></a>'

def cta():
    return f"""<div class="cta"><h3>Watch the full breakdown on YouTube</h3>
<p>New videos every week. Subscribe so the algorithm stops hiding us.</p>
<a class="btn" href="{SUB}" target="_blank" rel="noopener">▶ Subscribe on YouTube</a></div>"""

# ── Byg ────────────────────────────────────────────────────────────────
def build_index():
    cards = ""
    for p in POSTS:
        cards += f"""<a class="card" href="posts/{p['slug']}.html">
<img src="img/{p['img']}" alt="{p['title']}">
<div class="body"><h3>{p['title']}</h3><p>{p['excerpt']}</p>
<span class="more">Read more →</span></div></a>\n"""
    desc = ("No-fluff breakdowns of money psychology, personal finance, and how the rich "
            "think, earn, and keep their money. New videos every week on YouTube.")
    ld = jsonld(ORG, {
        "@type": "WebSite", "@id": SITE_URL + "/#website", "name": "Broke to Wealth",
        "url": SITE_URL + "/", "publisher": {"@id": SITE_URL + "/#org"},
        "inLanguage": "en", "description": desc,
    })
    html = head("Broke to Wealth — Money Psychology & Wealth-Building Habits", desc,
                path="", image="img/logo.png", og_type="website", ld=ld)
    html += f"""<div class="hero"><img src="img/logo.png" alt="Broke to Wealth logo">
<h1>Broke to <span class="k">Wealth</span></h1>
<p class="tag">The money moves they never taught you.</p>
<p class="intro">No-fluff breakdowns of money psychology, personal finance, and how the wealthy actually think, earn, and keep their money. Watch the videos, read the recaps, and subscribe on YouTube.</p></div>
<div class="wrap">{subscribe()}
<div class="section-title">Latest episodes</div>
<div class="grid">{cards}</div></div>{footer()}"""
    (SITE/"index.html").write_text(html, encoding="utf-8")

def build_about():
    desc = ("Broke to Wealth breaks down money psychology, personal finance, and the habits "
            "that separate the broke from the wealthy. New videos every week on YouTube.")
    ld = jsonld(ORG, {
        "@type": "AboutPage", "url": SITE_URL + "/about.html",
        "name": "About — Broke to Wealth", "isPartOf": {"@id": SITE_URL + "/#website"},
        "about": {"@id": SITE_URL + "/#org"},
    })
    html = head("About — Broke to Wealth", desc, path="about.html", og_type="website", ld=ld)
    html += f"""<div class="wrap"><article>
<h1>About Broke to Wealth</h1>
<p>Most people spend their whole lives broke — not because they don't work hard, but because nobody taught them how money actually works.</p>
<p><b>Broke to Wealth</b> breaks down the money moves, mindset shifts, and habits that separate the broke from the wealthy. No hype. No get-rich-quick schemes. Just the stuff they never taught you in school — explained simply, in a few minutes.</p>
<p>New videos every week on <a href="{CHANNEL}" target="_blank" rel="noopener">YouTube</a>. Each post here is the written companion to a video.</p>
{subscribe()}
<div class="disclaimer">⚠️ Broke to Wealth is for education and entertainment only — it is not financial advice. Content includes AI-assisted narration and illustrations.</div>
</article></div>{footer()}"""
    (SITE/"about.html").write_text(html, encoding="utf-8")

def build_posts():
    for i,p in enumerate(POSTS):
        prev_l = f'<a href="{POSTS[i-1]["slug"]}.html">← {POSTS[i-1]["title"][:28]}…</a>' if i>0 else '<a href="../index.html">← All posts</a>'
        next_l = f'<a href="{POSTS[i+1]["slug"]}.html">{POSTS[i+1]["title"][:28]}… →</a>' if i<len(POSTS)-1 else '<a href="../index.html">All posts →</a>'
        canonical = SITE_URL + f"/posts/{p['slug']}.html"
        ld = jsonld(ORG, {
            "@type": "BlogPosting",
            "headline": p["title"],
            "description": p["excerpt"],
            "image": SITE_URL + "/img/" + p["img"],
            "url": canonical,
            "mainEntityOfPage": canonical,
            "inLanguage": "en",
            "author": {"@id": SITE_URL + "/#org"},
            "publisher": {"@id": SITE_URL + "/#org"},
        })
        html = head(p["title"]+" — Broke to Wealth", p["excerpt"], rel="../",
                    path=f"posts/{p['slug']}.html", image="img/"+p["img"], og_type="article", ld=ld)
        html += f"""<div class="wrap"><article>
<h1>{p['title']}</h1>
<div class="meta">{p['date']} · Broke to Wealth</div>
{video_block(p, rel="../")}
{p['body']}
{cta()}
<div class="disclaimer">⚠️ Educational only, not financial advice.</div>
<div class="backlinks">{prev_l}{next_l}</div>
</article>
{subscribe()}
</div>{footer(rel="../")}"""
        (SITE/"posts"/f"{p['slug']}.html").write_text(html, encoding="utf-8")

def build_sitemap():
    urls = [SITE_URL + "/", SITE_URL + "/about.html"] + [SITE_URL + f"/posts/{p['slug']}.html" for p in POSTS]
    body = "".join(f"\n  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>" for u in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + body + "\n</urlset>\n")
    (SITE/"sitemap.xml").write_text(xml, encoding="utf-8")

def build_robots():
    txt = "User-agent: *\nAllow: /\n\nSitemap: " + SITE_URL + "/sitemap.xml\n"
    (SITE/"robots.txt").write_text(txt, encoding="utf-8")

build_index(); build_about(); build_posts(); build_sitemap(); build_robots()
print(f"✅ Bygget: index.html, about.html + {len(POSTS)} indlæg + sitemap.xml + robots.txt")
