#!/usr/bin/env python3
"""
make_fb_clip.py — byg et lodret (9:16) Facebook-teaser-klip ud fra en eksisterende
"Broke to Wealth"-video.

Tager den færdige 16:9-video + words.json (ord-tidsstempler) og samler en NY
lodret video til Facebook/Reels:
  - hvid baggrund (brand-look), 16:9-panel i midten med sort doodle-ramme
  - brand-mærke øverst
  - indbrændte undertekster (vigtigt for lydløst autoplay)
  - rød "WATCH THE FULL VIDEO"-CTA nederst
  - kort end-card der peger på YouTube

Denne ffmpeg-build mangler drawtext/subtitles, så al tekst genereres som
PNG-overlays med PIL og lægges på med ffmpeg `overlay`.

Brug:  python3 pipeline/make_fb_clip.py <video-navn> [cut_end_sekunder]
Eks:   python3 pipeline/make_fb_clip.py zero-to-10k 56.2
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------- parametre ----------
NAME = sys.argv[1] if len(sys.argv) > 1 else "zero-to-10k"
CUT_END = float(sys.argv[2]) if len(sys.argv) > 2 else 56.2
PLATFORM = sys.argv[3].lower() if len(sys.argv) > 3 else "facebook"
FADE = 0.6           # audio-fade-out i slutningen
ENDCARD_SEC = 3.0
FPS = 30
W, H = 1080, 1920

# platform-specifik tekst/CTA + output-placering.
# Shorts: seeren er ALLEREDE på YouTube → peg på fuld video i beskrivelsen, ikke "søg".
CFG = {
    "facebook": dict(dir="facebook", prefix="fb_",
                     cta1="WATCH THE FULL VIDEO", cta2="on YouTube",
                     ec_btn="WATCH ON YOUTUBE", ec_sub="Search:  Broke to Wealth"),
    "shorts": dict(dir="shorts", prefix="short_",
                   cta1="WATCH THE FULL VIDEO", cta2="link in description",
                   ec_btn="WATCH THE FULL VIDEO", ec_sub="Link in the description"),
}[PLATFORM]

ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIR = ROOT / "output" / NAME
SRC = VIDEO_DIR / f"{NAME}.mp4"
WORDS = VIDEO_DIR / "words.json"
OUT = VIDEO_DIR / CFG["dir"]
ASSET = OUT / "_assets"
OUT.mkdir(parents=True, exist_ok=True)
ASSET.mkdir(parents=True, exist_ok=True)

# ---------- fonte ----------
FB = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FBOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start, max_w):
    """Vælg største skriftstørrelse (≤ start) der holder teksten under max_w."""
    size = start
    while size > 22:
        fnt = ImageFont.truetype(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return ImageFont.truetype(path, size)


# ---------- panel-geometri ----------
PANEL_W, PANEL_H = 1000, 562
PANEL_X, PANEL_Y = 40, 380

RED = (225, 20, 20, 255)
BLACK = (15, 15, 15, 255)
GRAY = (95, 95, 95, 255)
WHITE = (255, 255, 255, 255)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_centered_block(draw, lines, font, cy, fill, line_gap=14):
    # mål total højde
    heights = []
    for ln in lines:
        b = draw.textbbox((0, 0), ln, font=font)
        heights.append(b[3] - b[1])
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = cy - total / 2
    for ln, h in zip(lines, heights):
        b = draw.textbbox((0, 0), ln, font=font)
        draw.text((W / 2, y - b[1]), ln, font=font, fill=fill, anchor="la"
                  ) if False else None
        # centreret horisontalt via anchor mm pr. linje
        draw.text((W / 2, y + h / 2), ln, font=font, fill=fill, anchor="mm")
        y += h + line_gap


# ---------- base.png (statisk lag: brand + ramme + CTA) ----------
def build_base():
    img = Image.new("RGBA", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    # brand top
    d.text((W / 2, 96), "BROKE TO WEALTH", font=f(FB, 60), fill=BLACK, anchor="mm")
    d.text((W / 2, 170), "THE MONEY MOVES THEY NEVER TAUGHT YOU",
           font=f(FBOLD, 26), fill=GRAY, anchor="mm")
    # panel-ramme (doodle-look)
    d.rectangle([PANEL_X - 6, PANEL_Y - 6, PANEL_X + PANEL_W + 6, PANEL_Y + PANEL_H + 6],
                outline=BLACK, width=7)
    # CTA-knap
    d.rounded_rectangle([90, 1600, 990, 1792], radius=30, fill=RED)
    d.text((W / 2, 1662), CFG["cta1"], font=f(FB, 54), fill=WHITE, anchor="mm")
    d.text((W / 2, 1730), CFG["cta2"], font=f(FBOLD, 40), fill=WHITE, anchor="mm")
    d.text((W / 2, 1858), "@broke-to-wealth", font=f(FBOLD, 34), fill=GRAY, anchor="mm")
    p = ASSET / "base.png"
    img.save(p)
    return p


# ---------- caption-png pr. chunk ----------
def build_caption_png(idx, text):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = f(FB, 82)
    lines = wrap(d, text.upper(), font, 940)
    if len(lines) > 2:  # hold det kort
        lines = [lines[0], " ".join(lines[1:])]
    draw_centered_block(d, lines, font, 1270, BLACK, line_gap=12)
    p = ASSET / f"cap_{idx:03d}.png"
    img.save(p)
    return p


# ---------- end-card ----------
def build_endcard():
    img = Image.new("RGBA", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 560), "WANT THE FULL PLAN?", font=f(FB, 78), fill=BLACK, anchor="mm")
    d.text((W / 2, 660), "The full $0 → $10,000 system", font=f(FBOLD, 42),
           fill=(60, 60, 60, 255), anchor="mm")
    d.rounded_rectangle([150, 820, 930, 1012], radius=32, fill=RED)
    d.text((W / 2, 916), CFG["ec_btn"], font=fit_font(d, CFG["ec_btn"], FB, 58, 700),
           fill=WHITE, anchor="mm")
    d.text((W / 2, 1140), CFG["ec_sub"], font=f(FB, 46), fill=BLACK, anchor="mm")
    d.text((W / 2, 1500), "BROKE TO WEALTH", font=f(FB, 50), fill=BLACK, anchor="mm")
    d.text((W / 2, 1566), "@broke-to-wealth", font=f(FBOLD, 34), fill=GRAY, anchor="mm")
    p = ASSET / "endcard.png"
    img.save(p)
    return p


# ---------- captions ud af words.json ----------
def build_chunks():
    words = json.load(open(WORDS))
    words = [w for w in words if w["start"] < CUT_END]
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        last = w["word"].strip()
        ends_sentence = last.endswith((".", "?", "!", ":"))
        if len(cur) >= 3 or ends_sentence:
            text = " ".join(x["word"].strip() for x in cur)
            chunks.append({"text": text, "start": cur[0]["start"], "end": cur[-1]["end"]})
            cur = []
    if cur:
        text = " ".join(x["word"].strip() for x in cur)
        chunks.append({"text": text, "start": cur[0]["start"], "end": cur[-1]["end"]})
    # hold hver caption indtil den næste starter (ingen flimmer/huller)
    for i in range(len(chunks) - 1):
        chunks[i]["end"] = chunks[i + 1]["start"]
    chunks[-1]["end"] = min(chunks[-1]["end"] + 0.4, CUT_END)
    return chunks


def run(cmd):
    print("›", " ".join(str(c) for c in cmd[:8]), "…")
    subprocess.run(cmd, check=True)


def main():
    print(f"== {PLATFORM}-klip: {NAME}  (0 → {CUT_END}s) ==")
    base = build_base()
    endcard_png = build_endcard()
    chunks = build_chunks()
    cap_pngs = [build_caption_png(i, c["text"]) for i, c in enumerate(chunks)]
    print(f"  {len(chunks)} undertekst-chunks")

    # ---- main.mp4 : komposit + captions + lyd ----
    inputs = ["-loop", "1", "-t", str(CUT_END), "-i", str(base),
              "-ss", "0", "-t", str(CUT_END), "-i", str(SRC)]
    for p in cap_pngs:
        inputs += ["-loop", "1", "-t", str(CUT_END), "-i", str(p)]

    fc = []
    fc.append(f"[1:v]scale={PANEL_W}:{PANEL_H},setsar=1[panel]")
    fc.append(f"[0:v][panel]overlay={PANEL_X}:{PANEL_Y}[v0]")
    prev = "v0"
    for i, c in enumerate(chunks):
        inp = i + 2  # input-index for caption-png
        nxt = f"v{i+1}"
        fc.append(f"[{prev}][{inp}:v]overlay=0:0:enable='between(t,{c['start']:.3f},{c['end']:.3f})'[{nxt}]")
        prev = nxt
    fc.append(f"[{prev}]format=yuv420p[vout]")
    fc.append(f"[1:a]afade=t=out:st={CUT_END - FADE:.3f}:d={FADE}[aout]")

    main_mp4 = OUT / "_main.mp4"
    run(["ffmpeg", "-y", *inputs,
         "-filter_complex", ";".join(fc),
         "-map", "[vout]", "-map", "[aout]",
         "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         str(main_mp4)])

    # ---- endcard.mp4 ----
    endcard_mp4 = OUT / "_endcard.mp4"
    run(["ffmpeg", "-y",
         "-loop", "1", "-t", str(ENDCARD_SEC), "-i", str(endcard_png),
         "-f", "lavfi", "-t", str(ENDCARD_SEC), "-i", "anullsrc=r=44100:cl=stereo",
         "-vf", f"scale={W}:{H},format=yuv420p", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(endcard_mp4)])

    # ---- concat ----
    final = OUT / f"{CFG['prefix']}{NAME}.mp4"
    run(["ffmpeg", "-y", "-i", str(main_mp4), "-i", str(endcard_mp4),
         "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(final)])

    print(f"\n✅ FÆRDIG: {final}")


if __name__ == "__main__":
    main()
