import math, os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb, io

FD = "/tmp/claude-0/-home-claude/1b563b14-189b-51c1-918b-189c6a661041/scratchpad/fonts/node_modules/@fontsource"
OUT = "/home/claude/taru-category-launch/brand/logo"
C = dict(heartwood="#1F3A2F", kora="#F3EEE4", ink="#2B2926", indigo="#26324D", madder="#84302A", haldi="#C8912F", khadi="#D9C9A8", lichen="#9DA283")

def static_font(path, loc=None):
    f = TTFont(path)
    if loc: f = instantiateVariableFont(f, loc)
    f.flavor = None
    b = io.BytesIO(); f.save(b); data = b.getvalue()
    return TTFont(io.BytesIO(data)), data

fr, fr_bytes = static_font(FD + "-variable/fraunces/files/fraunces-latin-full-normal.woff2", {"opsz":144,"wght":500,"SOFT":30,"WONK":0})
tiro, tiro_bytes = static_font(FD + "/tiro-devanagari-hindi/files/tiro-devanagari-hindi-devanagari-400-normal.woff2")
plex, plex_bytes = static_font(FD + "/ibm-plex-sans/files/ibm-plex-sans-latin-500-normal.woff2")

def shape(font, data, text, size, tracking_em=0.0, features=None):
    """Return (svg path d, width, cap/ascent info) with baseline at y=0, text scaled to `size` units per em."""
    face = hb.Face(data); hbf = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, features or {"kern": True, "liga": True})
    upm = font["head"].unitsPerEm; s = size / upm
    gs = font.getGlyphSet(); order = font.getGlyphOrder()
    x = 0; parts = []
    n = len(buf.glyph_infos)
    for i,(info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        g = order[info.codepoint]
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (s, 0, 0, -s, (x + pos.x_offset) * s, -pos.y_offset * s))
        gs[g].draw(tp)
        parts.append(pen.getCommands())
        x += pos.x_advance + (tracking_em * upm if i < n - 1 else 0)
    return " ".join(parts), x * s

def bounds(font, data, text, size, tracking_em=0.0):
    d, w = shape(font, data, text, size, tracking_em)
    return d, w

# ---------- Ring Seal ----------
KERF = 13.0  # width of the straight cut at twelve o'clock, in seal units (outer radius = 100)
def ring_path(cx, cy, r0, amp, k, ph, steps=240, kerf=None):
    # a parallel-sided cut: each ring's gap angle is set so the gap has the same width on every ring
    kerf = KERF * (r0 / 100 if False else 1) if kerf is None else kerf
    half = math.degrees(math.asin(min(0.95, (kerf / 2) / r0)))
    a0 = math.radians(-90 + half); a1 = math.radians(270 - half)
    pts = []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        r = r0 * (1 + amp * math.sin(k * a + ph))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)

RINGS = [  # radius, stroke, wobble amp, k, phase, centre offset
    (100, 8.0, 0.008, 3, 0.4, (0.0, 0.0)),
    (79,  6.8, 0.010, 4, 1.9, (0.6, -0.4)),
    (60,  5.6, 0.011, 3, 3.1, (-0.5, 0.5)),
    (43,  4.4, 0.012, 5, 0.9, (0.3, 0.6)),
]
def seal(cx, cy, scale, color, qr=False):
    out = []
    for r, w, amp, k, ph, (ox, oy) in RINGS:
        out.append(f'<path d="{ring_path(cx + ox*scale, cy + oy*scale, r*scale, amp, k, ph, kerf=KERF*scale)}" fill="none" stroke="{color}" stroke-width="{w*scale:.2f}" stroke-linecap="butt"/>')
    if qr:
        s = 52 * scale
        out.append(f'<rect x="{cx - s/2:.1f}" y="{cy - s/2:.1f}" width="{s:.1f}" height="{s:.1f}" fill="none" stroke="{color}" stroke-width="{1.2*scale:.2f}" stroke-dasharray="{3*scale:.1f} {3*scale:.1f}"/>')
    return "\n".join(out)
SEAL_R = 100 + 4.0  # outer extent incl. half stroke

# ---------- Wordmark ----------
CAP = fr["OS/2"].sCapHeight / fr["head"].unitsPerEm   # cap height as fraction of em
TRACK = 0.04
def wordmark(x, y_base, cap_px, color):
    size = cap_px / CAP
    d, w = shape(fr, fr_bytes, "TARU", size, TRACK)
    return f'<path transform="translate({x:.2f} {y_base:.2f})" d="{d}" fill="{color}"/>', w

def deva(x, y_base, size, color):
    d, w = shape(tiro, tiro_bytes, "तरु", size)
    return f'<path transform="translate({x:.2f} {y_base:.2f})" d="{d}" fill="{color}"/>', w

def label(x, y_base, text, size, color, track=0.12, anchor="start"):
    d, w = shape(plex, plex_bytes, text, size, track)
    if anchor == "middle": x = x - w/2
    return f'<path transform="translate({x:.2f} {y_base:.2f})" d="{d}" fill="{color}"/>', w

def svg(w, h, body, bg=None):
    rect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}">{rect}{body}</svg>'

# ---------- Lockups (built at cap height 100) ----------
CAPPX = 100
def primary(fg):
    seal_h = CAPPX * 1.6; sc = seal_h / (2 * SEAL_R); pad = CAPPX  # clear space = 1 cap height
    gap = CAPPX * 0.6
    cy = pad + seal_h/2; cx = pad + seal_h/2
    base = cy + CAPPX/2
    wm, ww = wordmark(pad + seal_h + gap, base, CAPPX, fg)
    W = pad + seal_h + gap + ww + pad; H = pad*2 + seal_h
    return seal(cx, cy, sc, fg) + wm, W, H

def stacked(fg, with_deva=False):
    seal_h = CAPPX * 2.2; sc = seal_h / (2 * SEAL_R); pad = CAPPX
    _, ww = shape(fr, fr_bytes, "TARU", CAPPX / CAP, TRACK)
    W = pad*2 + max(ww, seal_h)
    cy = pad + seal_h/2
    body = seal(W/2, cy, sc, fg)
    base = pad + seal_h + CAPPX*0.55 + CAPPX
    wm, _ = wordmark(W/2 - ww/2, base, CAPPX, fg); body += wm
    H = base + pad
    if with_deva:
        dsize = CAPPX * 0.9
        _, dw = shape(tiro, tiro_bytes, "तरु", dsize)
        dm, _ = deva(W/2 - dw/2, base + CAPPX*1.05, dsize, fg); body += dm
        H = base + CAPPX*1.05 + pad*0.8
    return body, W, H

def wordmark_only(fg):
    pad = CAPPX; wm, ww = wordmark(pad, pad + CAPPX, CAPPX, fg)
    return wm, pad*2 + ww, pad*2 + CAPPX

def seal_only(fg, qr=False):
    pad = 40; sc = 1.0; W = H = 2*SEAL_R + 2*pad
    return seal(W/2, H/2, sc, fg, qr), W, H

def descriptor(fg, line):
    pad = CAPPX; wm, ww = wordmark(pad, pad + CAPPX, CAPPX, fg)
    lb, lw = label(pad + ww/2, pad + CAPPX + CAPPX*0.75, line.upper(), CAPPX*0.34/0.698, fg, 0.12, "middle")  # Plex cap ~0.698 em
    return wm + lb, pad*2 + ww, pad*2 + CAPPX*1.75

variants = {"heartwood": (C["heartwood"], None), "reversed": (C["kora"], C["heartwood"]), "ink": (C["ink"], None)}
made = {}
for name, fn in [("primary", primary), ("stacked", stacked), ("wordmark", wordmark_only), ("seal", seal_only)]:
    for v, (fg, bg) in variants.items():
        body, W, H = fn(fg)
        p = f"{OUT}/taru_{name}_{v}.svg"; open(p, "w").write(svg(W, H, body, bg)); made[(name, v)] = p
body, W, H = stacked(C["heartwood"], True); open(f"{OUT}/taru_stacked_bilingual_heartwood.svg","w").write(svg(W,H,body))
body, W, H = seal_only(C["heartwood"], True); open(f"{OUT}/taru_seal_qr_heartwood.svg","w").write(svg(W,H,body))
for line, col, bg in [("Everyday", C["heartwood"], None), ("Festive", C["kora"], C["indigo"]), ("Ceremonial", C["kora"], C["madder"])]:
    body, W, H = descriptor(col, line); open(f"{OUT}/taru_descriptor_{line.lower()}.svg","w").write(svg(W,H,body,bg))
d, w = shape(tiro, tiro_bytes, "तरु", 200)
open(f"{OUT}/taru_devanagari_heartwood.svg","w").write(svg(w+80, 260, f'<path transform="translate(40 190)" d="{d}" fill="{C["heartwood"]}"/>'))
print(sorted(os.listdir(OUT)))
print("cap frac", CAP)
