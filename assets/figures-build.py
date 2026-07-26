#!/usr/bin/env python3
"""Method figures for the STC Lab research page: behavioural testing and EEG.

Same head in both frames — one listener, two conditions. Slate carries the
apparatus, red carries the signal, matching the hero figure on the homepage.
"""
import os, math, random

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 360, 220

SLATE = "var(--fig-line, #98a0ae)"
RED = "var(--fig-sig, #a6192e)"
SOFT = "var(--fig-soft, #f7f7f8)"
SWS, SWR = 2.1, 2.5

CX, CY, R = 88, 88, 38          # shared head geometry


def P(*v):
    return " ".join(f"{x:.2f}" for x in v)


# ------------------------------------------------------------------ anatomy
def head(cx=CX, cy=CY, r=R):
    """Profile facing right: crown, forehead, brow, nose, lips, chin, jaw."""
    return (
        f"M {P(cx, cy - r)} "
        f"C {P(cx + 0.50*r, cy - 1.01*r, cx + 0.86*r, cy - 0.78*r, cx + 0.89*r, cy - 0.38*r)} "
        f"C {P(cx + 0.90*r, cy - 0.26*r, cx + 0.88*r, cy - 0.17*r, cx + 0.93*r, cy - 0.09*r)} "
        f"C {P(cx + 1.03*r, cy + 0.03*r, cx + 1.12*r, cy + 0.08*r, cx + 1.10*r, cy + 0.18*r)} "
        f"C {P(cx + 1.08*r, cy + 0.25*r, cx + 0.98*r, cy + 0.23*r, cx + 0.90*r, cy + 0.27*r)} "
        f"C {P(cx + 0.96*r, cy + 0.35*r, cx + 0.94*r, cy + 0.42*r, cx + 0.86*r, cy + 0.47*r)} "
        f"C {P(cx + 0.83*r, cy + 0.60*r, cx + 0.72*r, cy + 0.70*r, cx + 0.52*r, cy + 0.76*r)} "
        f"C {P(cx + 0.28*r, cy + 0.83*r, cx - 0.34*r, cy + 0.80*r, cx - 0.70*r, cy + 0.50*r)} "
        f"C {P(cx - 0.96*r, cy + 0.26*r, cx - 1.00*r, cy - 0.44*r, cx - 0.60*r, cy - 0.78*r)} "
        f"C {P(cx - 0.40*r, cy - 0.95*r, cx - 0.21*r, cy - r, cx, cy - r)} Z")


def body(cx=CX, cy=CY, r=R):
    """Short neck, then shoulders running off the bottom edge — a portrait crop."""
    ny = cy + 0.74 * r
    return (
        # back of neck -> back / shoulder, exits bottom
        f"M {P(cx - 0.30*r, ny)} C {P(cx - 0.34*r, ny + 0.28*r, cx - 0.42*r, ny + 0.44*r, cx - 0.60*r, ny + 0.60*r)} "
        f"C {P(cx - 1.15*r, ny + 0.90*r, cx - 1.55*r, H - 22, cx - 1.62*r, H)} "
        # front of neck -> chest, exits bottom
        f"M {P(cx + 0.40*r, ny)} C {P(cx + 0.44*r, ny + 0.30*r, cx + 0.50*r, ny + 0.46*r, cx + 0.66*r, ny + 0.60*r)} "
        f"C {P(cx + 1.10*r, ny + 0.86*r, cx + 1.26*r, H - 26, cx + 1.28*r, H)}")


def ear_pos(cx=CX, cy=CY, r=R):
    return cx - 0.06 * r, cy + 0.14 * r


def arcs(x, y, n=3, r0=7, step=6.5, sweep=54, facing=-1):
    """Concentric arcs at the earcup — sound arriving at the ear."""
    out = []
    for i in range(n):
        rr = r0 + i * step
        a = math.radians(sweep)
        sf = 0 if facing < 0 else 1
        out.append(f'<path d="M {P(x + facing*rr*math.cos(a), y - rr*math.sin(a))} '
                   f'A {P(rr, rr)} 0 0 {sf} {P(x + facing*rr*math.cos(a), y + rr*math.sin(a))}"/>')
    return "".join(out)


def trace(x0, x1, y, amp, seed, pts=110):
    """Smooth pseudo-random line with an alpha burst — one EEG channel."""
    rng = random.Random(seed)
    c = [rng.uniform(-1, 1) for _ in range(7)]
    d = []
    for i in range(pts + 1):
        t = i / pts
        v = sum(ci * math.sin((k + 1) * math.pi * t * 2.6 + ci * 4) / (k * 0.7 + 1.5)
                for k, ci in enumerate(c))
        v += 0.55 * math.sin(t * math.pi * 30) * math.exp(-((t - 0.58) ** 2) / 0.010)
        v *= math.sin(math.pi * min(1, t / 0.08)) if t < 0.08 else 1   # ease in from the lead
        d.append(("M" if i == 0 else "L") + f" {P(x0 + (x1 - x0) * t, y + v * amp)}")
    return " ".join(d)


# --------------------------------------------------------- figure 1: behaviour
def fig_behaviour():
    ex, ey = ear_pos()
    cup_w, cup_h = 0.60 * R, 0.76 * R

    # band hugs the skull: leaves the top of the cup and clears the crown without dipping
    band = (f"M {P(ex - 0.22*R, ey - 0.44*R)} "
            f"C {P(CX - 0.78*R, CY - 0.52*R, CX - 0.66*R, CY - 1.10*R, CX + 0.02*R, CY - 1.18*R)} "
            f"C {P(CX + 0.62*R, CY - 1.16*R, CX + 0.90*R, CY - 0.84*R, CX + 0.96*R, CY - 0.48*R)}")

    desk_y = 178
    mx, mw, my, mh = 214, 118, 60, 82        # monitor
    kx, kw = 148, 52                          # keyboard

    # cable: earcup -> down the chest -> along the desk to the monitor
    cable = (f"M {P(ex - 0.12*R, ey + 0.40*R)} C {P(CX - 0.10*R, CY + 1.30*R, CX + 1.30*R, CY + 1.70*R, kx - 6, desk_y - 3)}")

    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="A listener wearing headphones responds to a two-choice speech task on a computer.">
  <g fill="none" stroke="{SLATE}" stroke-width="{SWS}" stroke-linecap="round" stroke-linejoin="round">
    <path d="{head()}"/>
    <path d="{body()}"/>
    <path d="{band}"/>
    <rect x="{ex-cup_w/2:.1f}" y="{ey-cup_h/2:.1f}" width="{cup_w:.1f}" height="{cup_h:.1f}" rx="9"/>
  </g>
  <g fill="none" stroke="{SLATE}" stroke-width="1.6" stroke-linecap="round">
    <path d="{cable}"/>
  </g>
  <g fill="none" stroke="{SLATE}" stroke-width="{SWS}" stroke-linecap="round" stroke-linejoin="round">
    <line x1="140" y1="{desk_y}" x2="{W-14}" y2="{desk_y}"/>
    <rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="5" fill="{SOFT}"/>
    <path d="M {P(mx+mw/2, my+mh)} v 12 M {P(mx+mw/2-20, desk_y)} L {P(mx+mw/2-7, my+mh+12)}
             M {P(mx+mw/2+20, desk_y)} L {P(mx+mw/2+7, my+mh+12)}"/>
    <path d="M {P(kx, desk_y-3)} h {kw} l -7 -7 h -{kw-14} Z" fill="{SOFT}"/>
    <path d="M {P(mx+20, my+22)} h 30 M {P(mx+20, my+32)} h 52"/>
    <rect x="{mx+20}" y="{my+48}" width="36" height="19" rx="9.5"/>
  </g>

  <g fill="none" stroke="{RED}" stroke-width="{SWR}" stroke-linecap="round">
    {arcs(ex - 0.46*R, ey, n=3, r0=8, step=6.5)}
    <rect x="{mx+64}" y="{my+48}" width="36" height="19" rx="9.5" stroke-width="{SWR}"/>
  </g>
  <circle cx="{mx+82}" cy="{my+57.5}" r="3.6" fill="{RED}"/>
</svg>'''


# ------------------------------------------------------------- figure 2: EEG
def fig_eeg():
    capr = R * 1.16
    # cap shell across the crown, ending just above the ear on both sides
    cap = (f"M {P(CX - 0.97*capr, CY + 0.16*capr)} "
           f"C {P(CX - 1.00*capr, CY - 0.56*capr, CX - 0.56*capr, CY - 1.00*capr, CX + 0.07*capr, CY - 1.00*capr)} "
           f"C {P(CX + 0.64*capr, CY - 1.00*capr, CX + 0.95*capr, CY - 0.60*capr, CX + 0.97*capr, CY - 0.12*capr)}")
    # chin strap
    strap = (f"M {P(CX - 0.97*capr, CY + 0.16*capr)} "
             f"C {P(CX - 0.90*capr, CY + 0.42*capr, CX - 0.74*capr, CY + 0.52*capr, CX - 0.60*capr, CY + 0.56*capr)}")

    # electrodes sit ON the dome only, in two concentric rows
    els_outer = [(CX + capr * 0.97 * math.cos(math.radians(a)),
                  CY + capr * 0.97 * math.sin(math.radians(a)))
                 for a in range(190, 360, 26)]
    els_inner = [(CX + capr * 0.62 * math.cos(math.radians(a)),
                  CY + capr * 0.62 * math.sin(math.radians(a)))
                 for a in range(206, 350, 34)]
    el_svg = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6"/>' for x, y in els_outer + els_inner)

    # Three electrodes hand off to three traces: grey hardware, red signal. The
    # bundle arcs over the crown rather than across the face — and echoes the
    # headphone band in the companion figure.
    TY = [70, 108, 146]
    TX0, TX1 = 208, W - 14
    sources = [els_outer[2], els_outer[3], els_outer[4]]
    leads = "".join(
        f'<path d="M {P(sx, sy)} C {P(sx + 10, sy - 26 - i*7, TX0 - 74, 26 + i*10, TX0 - 2, ty)}"/>'
        for i, ((sx, sy), ty) in enumerate(zip(sources, TY)))
    traces = "".join(f'<path d="{trace(TX0, TX1, ty, 12, seed=13 + i*9)}"/>'
                     for i, ty in enumerate(TY))

    return f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="A listener wearing an EEG cap; three electrodes hand off to three neural traces.">
  <g fill="none" stroke="{SLATE}" stroke-width="{SWS}" stroke-linecap="round" stroke-linejoin="round">
    <path d="{head()}"/>
    <path d="{body()}"/>
    <path d="{cap}"/>
    <path d="{strap}"/>
  </g>
  <g fill="none" stroke="{SLATE}" stroke-width="1.6" stroke-linecap="round">
    {leads}
  </g>
  <g fill="{SLATE}" stroke="none">{el_svg}</g>
  <g fill="none" stroke="{RED}" stroke-width="{SWR}" stroke-linecap="round" stroke-linejoin="round">
    {traces}
  </g>
</svg>'''


open(os.path.join(OUT, "fig-behaviour.svg"), "w").write(fig_behaviour())
open(os.path.join(OUT, "fig-eeg.svg"), "w").write(fig_eeg())
print("wrote both figures")
