#!/usr/bin/env python3
"""The three Methods diagrams the home page mentions but does not yet show.

Same idiom as fig-behaviour / fig-eeg: 360x220, --fig-line for apparatus,
--fig-sig for the signal or the finding, --fig-soft for fills, no text inside
the SVG (the caption carries the words).
"""
import os, math, random

OUT = os.path.dirname(os.path.abspath(__file__))
LINE = "var(--fig-line, #98a0ae)"
SIG = "var(--fig-sig, #a6192e)"
SOFT = "var(--fig-soft, #f7f7f8)"

# the shared listener, lifted verbatim from the two existing figures
HEAD = ("M 88.00 50.00 C 107.00 49.62 120.68 58.36 121.82 73.56 C 122.20 78.12 "
        "121.44 81.54 123.34 84.58 C 127.14 89.14 130.56 91.04 129.80 94.84 C "
        "129.04 97.50 125.24 96.74 122.20 98.26 C 124.48 101.30 123.72 103.96 "
        "120.68 105.86 C 119.54 110.80 115.36 114.60 107.76 116.88 C 98.64 119.54 "
        "75.08 118.40 61.40 107.00 C 51.52 97.88 50.00 71.28 65.20 58.36 C 72.80 "
        "51.90 80.02 50.00 88.00 50.00 Z")
SHOULDERS = ("M 76.60 116.12 C 75.08 126.76 72.04 132.84 65.20 138.92 C 44.30 "
             "150.32 29.10 198.00 26.44 220.00 M 103.20 116.12 C 104.72 127.52 "
             "107.00 133.60 113.08 138.92 C 129.80 148.80 135.88 194.00 136.64 220.00")


def P(*v):
    return " ".join(f"{x:.2f}" for x in v)


def wiggle(x0, x1, y, amp, seed, pts=70, gaps=()):
    """Speech-like trace; gaps are (t0, t1) fractions left silent."""
    rng = random.Random(seed)
    c = [rng.uniform(-1, 1) for _ in range(6)]
    segs, cur = [], []
    for i in range(pts + 1):
        t = i / pts
        if any(a <= t <= b for a, b in gaps):
            if cur:
                segs.append(cur)
                cur = []
            continue
        v = sum(ci * math.sin((k + 1) * math.pi * t * 3.2 + ci * 4) / (k * .7 + 1.5)
                for k, ci in enumerate(c))
        cur.append(("M" if not cur else "L") + f" {P(x0 + (x1 - x0) * t, y + v * amp)}")
    if cur:
        segs.append(cur)
    return " ".join(" ".join(s) for s in segs)


def svg(label, body):
    return (f'<svg viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg" role="img"\n'
            f'        aria-label="{label}">\n{body}\n        </svg>')


def g(stroke, w, body, cap="round", join="round", fill="none"):
    return (f'        <g fill="{fill}" stroke="{stroke}" stroke-width="{w}" '
            f'stroke-linecap="{cap}" stroke-linejoin="{join}">\n{body}\n        </g>')


# ============================================ 1. standardized cognitive assessment
def fig_cognitive():
    chips = "".join(
        f'<rect x="{184 + i*32}" y="60" width="24" height="22" rx="4"/>'
        for i in range(5))
    # span bracket under the first four: the point recall runs out
    bracket = ('<path d="M 184 92 L 184 98 L 272 98 L 272 92"/>')
    # normal curve with the individual score placed on it
    bell = []
    for i in range(49):
        t = i / 48
        x = 180 + t * 156
        y = 178 - 54 * math.exp(-((x - 258) ** 2) / (2 * 30 ** 2))
        bell.append(("M" if i == 0 else "L") + f" {P(x, y)}")
    bell = " ".join(bell)
    tick_x = 288
    tick_y = 178 - 54 * math.exp(-((tick_x - 258) ** 2) / (2 * 30 ** 2))
    body = "\n".join([
        g(LINE, 2.1, f'        <path d="{HEAD}"/>\n        <path d="{SHOULDERS}"/>'),
        g(LINE, 2.1, f'        <rect x="168" y="42" width="180" height="150" rx="5" '
                     f'fill="{SOFT}"/>'),
        g(LINE, 2.1, f'        {chips}\n        {bracket}'),
        g(LINE, 1.8, f'        <path d="{bell}"/>\n        '
                     f'<path d="M 180 178 L 336 178"/>'),
        g(SIG, 2.5, f'        <path d="M {P(tick_x, 178)} L {P(tick_x, tick_y)}"/>'),
        f'        <circle cx="{tick_x}" cy="{tick_y:.2f}" r="3.6" fill="{SIG}"/>',
    ])
    return svg("A listener at a standardized cognitive test: a digit span of four items, "
               "and the resulting score placed against a normal distribution.", body)


# ============================ 2. acoustic and linguistic analysis of recorded speech
def fig_speech_analysis():
    rec = wiggle(24, 336, 62, 22, seed=5, gaps=((.30, .38), (.63, .70)))
    # acoustic: a pitch contour
    pitch = ("M 24 158 C 44 132 62 128 78 140 C 94 152 110 156 128 138 "
             "C 142 124 158 126 170 136")
    # linguistic: word tokens of unequal length
    toks = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="9" rx="4.5"/>'
        for x, y, w in ((196, 128, 44), (248, 128, 30), (286, 128, 50),
                        (196, 150, 34), (238, 150, 52), (298, 150, 38),
                        (196, 172, 46), (250, 172, 28)))
    body = "\n".join([
        g(SIG, 2.5, f'        <path d="{rec}"/>'),
        g(LINE, 1.6, '        <path d="M 24 100 L 336 100"/>\n'
                     '        <path d="M 180 112 L 180 194"/>'),
        g(LINE, 2.1, f'        <path d="{pitch}"/>\n'
                     '        <path d="M 24 178 L 62 178 M 82 178 L 122 178 '
                     'M 142 178 L 170 178"/>'),
        g(LINE, 2.1, f'        {toks}', fill=SOFT),
    ])
    return svg("A recorded speech waveform with two pauses, analysed into an acoustic "
               "pitch contour and a set of linguistic word tokens.", body)


# ================================ 3. machine-learning analysis of speech and neural data
def fig_ml():
    L1 = [(136, 74), (136, 110), (136, 146)]
    L2 = [(196, 56), (196, 92), (196, 128), (196, 164)]
    L3 = [(256, 92), (256, 128)]
    edges = "".join(
        f'<path d="M {P(a[0] + 7, a[1])} L {P(b[0] - 7, b[1])}"/>'
        for layer_a, layer_b in ((L1, L2), (L2, L3))
        for a in layer_a for b in layer_b)
    nodes = "".join(f'<circle cx="{x}" cy="{y}" r="7"/>' for x, y in L1 + L2 + L3)
    speech = wiggle(20, 100, 66, 16, seed=11)
    eeg = "\n        ".join(
        f'<path d="{wiggle(20, 100, 132 + i * 22, 8, seed=21 + i * 5)}"/>'
        for i in range(2))
    feeds = ("".join(f'<path d="M 106 {y} L 122 {n[1]}"/>'
                     for y, n in ((66, L1[0]), (132, L1[1]), (154, L1[2])))
             + "".join(f'<path d="M 263 {n[1]} L 292 {y}"/>'
                       for n, y in ((L3[0], 104), (L3[1], 132))))
    body = "\n".join([
        g(SIG, 2.5, f'        <path d="{speech}"/>'),
        g(SIG, 1.8, f'        {eeg}'),
        g(LINE, 1, f'        {edges}'),
        g(LINE, 1.4, f'        {feeds}'),
        g(LINE, 2.1, f'        {nodes}', fill=SOFT),
        g(LINE, 2.1, '        <rect x="296" y="98" width="48" height="13" rx="6.5"/>\n'
                     '        <rect x="296" y="126" width="48" height="13" rx="6.5"/>'),
        f'        <rect x="296" y="98" width="38" height="13" rx="6.5" fill="{SIG}"/>',
    ])
    return svg("Speech and EEG signals feeding a layered network, which outputs two "
               "class probabilities with the first clearly favoured.", body)


for name, fn in (("fig-cognitive.svg", fig_cognitive),
                 ("fig-speech-analysis.svg", fig_speech_analysis),
                 ("fig-ml.svg", fig_ml)):
    open(os.path.join(OUT, name), "w").write(fn())
    print("wrote", name)
