#!/usr/bin/env python3
"""Regenerate the STC Lab logo assets.

Run:  python3 logo-build.py
Needs: pip install --user fonttools brotli uharfbuzz
Draws the mark from the AMPS envelope below and outlines the wordmark from
the .woff2 files in fonts/, so the lockup carries no font dependency.
"""
import os, tempfile
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
import uharfbuzz as hb

# lives in stc-lab/assets/ ; regenerates every logo-*.svg beside it
OUT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(OUT, "fonts")
SCRATCH = tempfile.mkdtemp(prefix="stc-logo-")

# Plain hex throughout: CSS var() silently fails in PowerPoint, Word and
# Illustrator, so the distributed files must not depend on it. Dark-mode
# variants ship as separate files instead.
LIGHT = dict(red="#a6192e", slate="#98a0ae", ink="#1a1a1a", muted="#5c5f66")
DARK = dict(red="#ef6076", slate="#6d7686", ink="#e9eaee", muted="#a3a8b2")

# ---------------------------------------------------------------- the mark
# A speech envelope: six syllable-like arches of unequal height. The third
# is excised from the red signal and redrawn in slate — the part the
# listener supplies rather than receives.
AMPS = [0.60, 0.94, 0.78, 0.52, 1.00, 0.66]
X0, X1, Y, BASE = 12, 108, 60, 27
N = len(AMPS)
L = (X1 - X0) / N
GAP_I = 2
SW = 10

def arc(i):
    x0 = X0 + i * L
    amp = BASE * AMPS[i]
    peak = Y - 1.33 * amp if i % 2 == 0 else Y + 1.33 * amp
    return f"C {x0+0.36*L:.2f} {peak:.2f} {x0+0.64*L:.2f} {peak:.2f} {x0+L:.2f} {Y:.2f}"

def span(a, b):
    return f"M {X0 + a*L:.2f} {Y:.2f} " + " ".join(arc(i) for i in range(a, b))

LEFT, MID, RIGHT = span(0, GAP_I), span(GAP_I, GAP_I + 1), span(GAP_I + 1, N)

# tight bounding box of the stroked wave
up_max = BASE * max(AMPS[i] for i in range(0, N, 2))
dn_max = BASE * max(AMPS[i] for i in range(1, N, 2))
BX, BY = X0 - SW / 2, Y - up_max - SW / 2
BW, BH = (X1 - X0) + SW, up_max + dn_max + SW
VB = f"{BX:.2f} {BY:.2f} {BW:.2f} {BH:.2f}"

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
        'role="img" aria-labelledby="t">{title}')
TITLE = ('<title id="t">Speech, Tinnitus, and Cognition Lab</title>')

def wave_group(red, slate, sw=SW, ghost=True):
    g = [f'<g fill="none" stroke-linecap="round" stroke-width="{sw}">']
    g.append(f'<path d="{LEFT}" stroke="{red}"/>')
    g.append(f'<path d="{RIGHT}" stroke="{red}"/>')
    if ghost:
        g.append(f'<path d="{MID}" stroke="{slate}"/>')
    g.append('</g>')
    return "".join(g)

# 1. two-colour mark, light and dark
for suffix, C in (("", LIGHT), ("-dark", DARK)):
    m = HEAD.format(vb=VB, title=TITLE) + wave_group(C["red"], C["slate"]) + '</svg>'
    open(os.path.join(OUT, f"logo-mark{suffix}.svg"), "w").write(m)

# 2. one-colour reduction: the excised arch is simply absent
mark_mono = (HEAD.format(vb=VB, title=TITLE)
             + wave_group("currentColor", None, ghost=False) + '</svg>')
open(os.path.join(OUT, "logo-mark-mono.svg"), "w").write(mark_mono)

# 3. tile — favicon / avatar. rx matches the existing favicon's 20% radius.
tile_inner = wave_group("#ffffff", "#ffffff", sw=9)
tile_inner = tile_inner.replace('stroke="#ffffff"/></g>', 'stroke="#ffffff" opacity="0.42"/></g>')
tile = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" '
        f'role="img" aria-labelledby="t">{TITLE}'
        f'<rect width="120" height="120" rx="25" fill="{LIGHT["red"]}"/>'
        '<g transform="translate(60 60) scale(0.74) translate(-60 -60)">'
        f'{tile_inner}</g></svg>')
open(os.path.join(OUT, "logo-tile.svg"), "w").write(tile)

# ------------------------------------------------------------- the lockup
def ttf(path):
    """woff2 -> temp ttf so harfbuzz can shape it."""
    f = TTFont(path)
    f.flavor = None
    tmp = os.path.join(SCRATCH, os.path.basename(path).replace(".woff2", ".ttf"))
    f.save(tmp)
    return tmp

def text_path(ttf_path, text, size, tracking=0.0, origin=(0, 0)):
    """Shape with harfbuzz, outline with fontTools. Returns (path_d, width)."""
    blob = hb.Blob.from_file_path(ttf_path)
    face = hb.Face(blob)
    font = hb.Font(face)
    upem = face.upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)

    tt = TTFont(ttf_path)
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    scale = size / upem
    ox, oy = origin
    cursor = 0.0
    d = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = order[info.codepoint]
        t = (Transform()
             .translate(ox + (cursor + pos.x_offset) * scale, oy - pos.y_offset * scale)
             .scale(scale, -scale))
        pen = SVGPathPen(gs)
        gs[gname].draw(TransformPen(pen, t))
        cmds = pen.getCommands()
        if cmds:
            d.append(cmds)
        cursor += pos.x_advance + tracking * upem
    return " ".join(d), cursor * scale

serif = ttf(os.path.join(FONTS, "ibm-plex-serif-600.woff2"))
mono = ttf(os.path.join(FONTS, "ibm-plex-mono-500.woff2"))

L1_SIZE, L2_SIZE, TRACK = 31, 11.5, 0.10
L1_BASE, L2_BASE = 50, 74

MARK_H = 54
mscale = MARK_H / BH
MARK_W = BW * mscale
GAP = 30
TEXT_X = MARK_W + GAP

l1, w1 = text_path(serif, "Speech, Tinnitus, and Cognition Lab", L1_SIZE, 0, (TEXT_X, L1_BASE))
l2, w2 = text_path(mono, "SAN DIEGO STATE UNIVERSITY", L2_SIZE, TRACK, (TEXT_X, L2_BASE))

TOTAL_W = TEXT_X + max(w1, w2)
TOTAL_H = 92
mark_y = (TOTAL_H - MARK_H) / 2

for suffix, C in (("", LIGHT), ("-dark", DARK)):
    lockup = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTAL_W:.1f} {TOTAL_H}" '
              f'role="img" aria-labelledby="t">{TITLE}'
              f'<g transform="translate(0 {mark_y:.2f}) scale({mscale:.5f}) '
              f'translate({-BX:.2f} {-BY:.2f})">{wave_group(C["red"], C["slate"])}</g>'
              f'<path d="{l1}" fill="{C["ink"]}"/>'
              f'<path d="{l2}" fill="{C["muted"]}"/>'
              '</svg>')
    open(os.path.join(OUT, f"logo-lockup{suffix}.svg"), "w").write(lockup)

print(f"mark viewBox: {VB}")
print(f"lockup: {TOTAL_W:.1f} x {TOTAL_H}  (line1 {w1:.1f}, line2 {w2:.1f})")
print("wrote:", [f for f in sorted(os.listdir(OUT)) if f.startswith("logo")])
