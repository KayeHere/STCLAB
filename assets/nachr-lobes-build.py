#!/usr/bin/env python3
"""nAChR distribution on a lobed lateral brain.

The cerebrum is built as four filled lobes rather than one outline: the margin
is densified so named landmarks keep exact indices, then the central sulcus,
lateral (Sylvian) fissure and parieto-occipital boundary cut it into frontal,
parietal, temporal and occipital regions that share exact edges.

Anterior faces left. Deep structures are projected onto the lateral view.
"""
import os, math

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 640, 400
PS = 8                     # samples per landmark segment


def P(*v):
    return " ".join(f"{x:.1f}" for x in v)


def _cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2
                        + (-a + 3 * b - 3 * c + d) * t3)
                 for a, b, c, d in zip(p0, p1, p2, p3))


def densify(pts, per_seg=PS, closed=True):
    """dense[i*per_seg] == pts[i], which is what keeps the junctions exact."""
    n, out = len(pts), []
    for i in range(n if closed else n - 1):
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1, p2 = pts[i % n], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        for k in range(per_seg):
            out.append(_cr(p0, p1, p2, p3, k / per_seg))
    if not closed:
        out.append(pts[-1])
    return out


def normals(pts, closed=True):
    n = len(pts)
    cx = sum(q[0] for q in pts) / n
    cy = sum(q[1] for q in pts) / n
    out = []
    for i, (x, y) in enumerate(pts):
        a = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        b = pts[(i + 1) % n] if closed else pts[min(i + 1, n - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = ty / L, -tx / L
        if closed and (nx * (x - cx) + ny * (y - cy)) < 0:
            nx, ny = -nx, -ny
        out.append((nx, ny))
    return out


TERMS = [(12, 1.0, .6), (25, .34, 2.2), (39, .16, 4.1)]


def wave(i, n, terms=TERMS):
    return sum(w * math.sin(2 * math.pi * f * (i / n) + ph) for f, w, ph in terms)


def roughen(pts, amp, terms=TERMS, closed=True):
    nrm = normals(pts, closed)
    n = len(pts)
    return [(x + nx * amp * wave(i, n, terms), y + ny * amp * wave(i, n, terms))
            for i, ((x, y), (nx, ny)) in enumerate(zip(pts, nrm))]


def poly(pts, closed=True):
    return "M " + " L ".join(P(*q) for q in pts) + (" Z" if closed else "")


def arc_slice(dense, i0, i1):
    """Margin points from i0 forward to i1, wrapping."""
    n = len(dense)
    out, i = [], i0
    while True:
        out.append(dense[i % n])
        if i % n == i1 % n:
            break
        i += 1
    return out


# ------------------------------------------------------------- the cerebrum
LM = [(150, 150), (154, 118), (168, 92), (196, 70), (228, 56),
      (264, 48),                                   # 5  A  central sulcus top
      (298, 48),
      (338, 58),                                   # 7  C  parieto-occipital top
      (378, 74), (410, 98), (434, 130), (444, 162), (438, 192),
      (420, 214),                                  # 13 D  preoccipital notch
      (392, 232), (358, 244), (322, 252), (284, 254), (246, 248), (210, 234),
      (188, 214),
      (170, 186),                                  # 21 B  Sylvian, anterior end
      (160, 166)]
A_i, C_i, D_i, B_i = 5 * PS, 8 * PS, 13 * PS, 21 * PS

MARGIN = roughen(densify(LM), 3.8)
NM = len(MARGIN)
A_pt, C_pt, D_pt, B_pt = MARGIN[A_i], MARGIN[C_i], MARGIN[D_i], MARGIN[B_i]

# lateral fissure, anterior margin -> junction J with the parieto-occipital line
SYL = densify([B_pt, (208, 202), (252, 210), (298, 210), (348, 198), (400, 180)],
              closed=False)
S_i = 12                       # where the central sulcus meets it
J_syl = len(SYL) - 1

# parieto-occipital boundary, superior margin -> preoccipital notch, through J
PO = densify([C_pt, (392, 112), (398, 152), (400, 180), (410, 198), D_pt],
             closed=False)
J_po = 3 * PS

CENTRAL = densify([A_pt, (250, 96), (238, 148), SYL[S_i]], closed=False)

FRONTAL = poly(arc_slice(MARGIN, B_i, A_i) + CENTRAL + SYL[:S_i + 1][::-1])
PARIETAL = poly(arc_slice(MARGIN, A_i, C_i) + PO[:J_po + 1]
                + SYL[S_i:J_syl + 1][::-1] + CENTRAL[::-1])
OCCIPITAL = poly(arc_slice(MARGIN, C_i, D_i) + PO[::-1])
TEMPORAL = poly(arc_slice(MARGIN, D_i, B_i) + SYL + PO[J_po:][::-1])

# gyri: clefts at the troughs of the margin wave, plus a shorter inner rank
GYRI = []
_nm = normals(MARGIN)
for i in range(NM):
    if wave(i, NM) < wave(i - 1, NM) and wave(i, NM) <= wave((i + 1) % NM, NM):
        (x, y), (nx, ny) = MARGIN[i], _nm[i]
        dx, dy = -nx, -ny
        px, py = -dy, dx
        d = 24 + 6 * math.sin(i * 1.3)
        lean = 9 * math.sin(i * .7)
        GYRI.append(poly([(x, y), (x + dx * d * .5 + px * lean, y + dy * d * .5 + py * lean),
                          (x + dx * d, y + dy * d)], closed=False))
        j = (i + NM // 24) % NM
        (x2, y2), (nx2, ny2) = MARGIN[j], _nm[j]
        dx2, dy2 = -nx2, -ny2
        GYRI.append(poly([(x2 + dx2 * 30, y2 + dy2 * 30),
                          (x2 + dx2 * 44 - ny2 * 5, y2 + dy2 * 44 + nx2 * 5),
                          (x2 + dx2 * 52, y2 + dy2 * 52)], closed=False))

THALAMUS = poly(densify([(300, 148), (322, 140), (344, 148), (350, 162),
                         (342, 176), (320, 180), (302, 172), (296, 160)]))

# ------------------------------------------------- brainstem and cerebellum
BRAINSTEM = poly(densify([(338, 226), (332, 252), (328, 276), (334, 300),
                          (340, 324), (344, 350), (372, 350), (370, 324),
                          (368, 300), (370, 276), (374, 252), (374, 226)],
                         closed=True))
CEREBELLUM = poly(roughen(densify([(374, 258), (396, 246), (424, 250), (444, 268),
                                   (448, 294), (434, 316), (408, 326), (384, 318),
                                   (372, 298), (368, 276)]),
                          1.1, [(17, 1.0, 1.2), (31, .35, 3.1)]))
FOLIA = ["M 380 268 C 396 258 420 259 438 270",
         "M 378 284 C 394 276 420 277 444 286",
         "M 382 300 C 396 294 416 294 434 302",
         "M 388 314 C 400 309 414 309 426 315"]

# ------------------------------------------------------------- receptor map
SITES = {                                   # (x, y), rx, ry, density
    "MGB": ((322, 158), 10.5, 8.0, 0.95),
    "IC":  ((370, 248), 9.0, 7.0, 0.72),
    "SOC": ((342, 294), 8.0, 6.0, 0.55),
    "CN":  ((368, 318), 7.5, 5.5, 0.50),
}
AC_ARC = "M 240 220 C 260 230 284 232 304 222"
AC_MID = (272, 227)
COCHLEA_C = (284, 298)
BF = (224, 172)
PPT = (370, 276)


def cochlea(cx, cy, turns=2.3, r0=1.5, r1=10.5, n=90):
    out = []
    for i in range(n + 1):
        t = i / n
        th = t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * (1 - t)
        out.append(("M" if i == 0 else "L") + f" {P(cx + r*math.cos(th), cy + r*math.sin(th))}")
    return " ".join(out)


def lead(x0, y0, x1, y1):
    return f'<path class="fx-lead" d="M {P(x0, y0)} L {P(x1, y1)}"/>'


def arrowhead(x, y, ang, size=6):
    a = math.radians(ang)
    p1 = (x - size * math.cos(a) + size * .5 * math.sin(a),
          y - size * math.sin(a) - size * .5 * math.cos(a))
    p2 = (x - size * math.cos(a) - size * .5 * math.sin(a),
          y - size * math.sin(a) + size * .5 * math.cos(a))
    return f'<path class="fx-arrowhead" d="M {P(x, y)} L {P(*p1)} L {P(*p2)} Z"/>'


def between(a, b, ta, tb):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    return (a[0] + ux * ta, a[1] + uy * ta, b[0] - ux * tb, b[1] - uy * tb,
            math.degrees(math.atan2(uy, ux)))


def connector(a, b):
    x0, y0, x1, y1, ang = between(a, b, 13, 13)
    return f'<path class="fx-arrow" d="M {P(x0, y0)} L {P(x1, y1)}"/>' + arrowhead(x1, y1, ang)


def text(x, y, s, cls="fx-t", anchor="start"):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>'


# -------------------------------------------------------------------- build
p = []
p.append(f'<path class="fx-lobe fx-pale" d="{CEREBELLUM}"/>')
for f in FOLIA:
    p.append(f'<path class="fx-gyrus" d="{f}"/>')
p.append(f'<path class="fx-lobe fx-pale" d="{BRAINSTEM}"/>')
p.append(f'<path class="fx-lobe fx-lobe-t" d="{TEMPORAL}"/>')
p.append(f'<path class="fx-lobe fx-lobe-o" d="{OCCIPITAL}"/>')
p.append(f'<path class="fx-lobe fx-lobe-p" d="{PARIETAL}"/>')
p.append(f'<path class="fx-lobe fx-lobe-f" d="{FRONTAL}"/>')
for g in GYRI:
    p.append(f'<path class="fx-gyrus" d="{g}"/>')
p.append(f'<path class="fx-lobe fx-pale" d="{THALAMUS}"/>')

CHAIN = [COCHLEA_C, SITES["CN"][0], SITES["SOC"][0], SITES["IC"][0],
         SITES["MGB"][0], AC_MID]
for a, b in zip(CHAIN, CHAIN[1:]):
    p.append(connector(a, b))
for a, b in ((BF, AC_MID), (PPT, SITES["MGB"][0]), (PPT, SITES["IC"][0])):
    x0, y0, x1, y1, ang = between(a, b, 11, 15)
    p.append(f'<path class="fx-dash" d="M {P(x0, y0)} L {P(x1, y1)}"/>')
    p.append(arrowhead(x1, y1, ang))

for (x, y), rx, ry, dens in SITES.values():
    p.append(f'<ellipse class="fx-dot-red fx-site" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" '
             f'fill-opacity="{dens:.2f}"/>')
p.append(f'<path class="fx-ac" d="{AC_ARC}" stroke-opacity="0.55"/>')
p.append(f'<path class="fx-cochlea" d="{cochlea(*COCHLEA_C)}"/>')
for (x, y) in (BF, PPT):
    p.append(f'<circle class="fx-dot-blue fx-site" cx="{x}" cy="{y}" r="5.5"/>')

# ---- labels: left column ends x=140, right starts x=460
p.append(lead(144, 148, 218, 168))
p.append(text(140, 142, "BASAL FOREBRAIN", anchor="end"))
p.append(text(140, 157, "CHOLINERGIC SOURCE", anchor="end"))

p.append(lead(144, 226, 236, 224))
p.append(text(140, 214, "AUDITORY CORTEX", anchor="end"))
p.append(text(140, 229, "nicotinic +", cls="fx-sub", anchor="end"))
p.append(text(140, 243, "muscarinic", cls="fx-sub", anchor="end"))

p.append(lead(144, 302, 272, 300))
p.append(text(140, 292, "COCHLEA", anchor="end"))
p.append(text(140, 307, "(HAIR CELLS)", anchor="end"))
p.append(text(140, 322, "&#945;9&#945;10", cls="fx-sub", anchor="end"))

p.append(lead(456, 96, 332, 152))
p.append(text(460, 82, "MEDIAL GENICULATE"))
p.append(text(460, 97, "(AUDITORY THALAMUS)"))
p.append(text(460, 112, "dense &#945;4&#946;2", cls="fx-sub"))

p.append(lead(456, 232, 380, 246))
p.append(text(460, 226, "INFERIOR COLLICULUS"))
p.append(text(460, 241, "&#945;7 &#183; &#945;4&#946;2 &#183; &#945;3&#946;4", cls="fx-sub"))

p.append(lead(456, 288, 379, 278))
p.append(text(460, 282, "PONTOMESENCEPHALIC"))
p.append(text(460, 297, "CHOLINERGIC SOURCE"))

p.append(lead(456, 344, 351, 298))
p.append(text(460, 338, "SUPERIOR OLIVARY"))
p.append(text(460, 353, "COMPLEX &#183; &#945;7 &#183; &#945;4&#946;2", cls="fx-sub"))

p.append(lead(456, 386, 376, 324))
p.append(text(460, 380, "COCHLEAR NUCLEUS"))
p.append(text(460, 395, "&#945;7", cls="fx-sub"))

p.append(text(14, 62, "nAChR DENSITY"))
for i, dens in enumerate((0.30, 0.60, 0.95)):
    p.append(f'<circle class="fx-dot-red fx-site" cx="{24 + i*26}" cy="82" r="6.5" '
             f'fill-opacity="{dens:.2f}"/>')
p.append(text(24, 104, "LOW", anchor="middle"))
p.append(text(76, 104, "HIGH", anchor="middle"))

svg = (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
       'aria-label="A lateral view of the brain with the frontal, parietal, temporal and '
       'occipital lobes shaded separately and gyri drawn, showing the ascending auditory '
       'pathway from cochlea to auditory cortex with each stage shaded by nicotinic '
       'acetylcholine receptor density, and the basal forebrain and pontomesencephalic '
       'cholinergic nuclei projecting to cortex and thalamus.">' + "".join(p) + '</svg>')

open(os.path.join(OUT, "fig-nachr-lobes.svg"), "w").write(svg)
print(f"wrote fig-nachr-lobes.svg  {len(svg)} bytes, {len(GYRI)} gyral strokes")
