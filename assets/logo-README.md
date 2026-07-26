# STC Lab logo

The mark is a speech envelope in SDSU red with one arch missing from the signal
and redrawn in slate. Red is what reaches the ear; slate is what the listener
supplies. That gap is the lab's question in all three programs — a target voice
dug out of babble, a percept with no source at all, and the cognition doing the
filling in.

## Which file to use

| File | Use it for |
| --- | --- |
| `logo-lockup.svg` | Slides, posters, letterhead, email signatures — the default |
| `logo-mark.svg` | The mark alone, where the lab name already appears nearby |
| `logo-tile.svg` | Favicon, Twitter/Bluesky avatar, any square slot |
| `logo-mark-mono.svg` | One colour: print, embroidery, stamps, fax-grade repro |
| `*-dark.svg` | Dark backgrounds |
| `*.png` | Anywhere SVG is not accepted (some journal portals, Word) |

The PNGs are transparent: `logo-lockup.png` 1600×222, `logo-mark.png` 1024×603,
`logo-tile.png` 1024×1024. Regenerate at other sizes from the SVGs rather than
scaling the PNGs up.

## Colours

| Role | Light | Dark |
| --- | --- | --- |
| Signal (red) | `#a6192e` | `#ef6076` |
| Inferred (slate) | `#98a0ae` | `#6d7686` |
| Wordmark | `#1a1a1a` | `#e9eaee` |
| Affiliation line | `#5c5f66` | `#a3a8b2` |

## Rules that matter

Keep clear space around the mark equal to the height of its tallest arch.

Never recolour the slate arch to red. The two-tone contrast *is* the logo — a
single-colour version already exists as `logo-mark-mono.svg`, and it drops the
arch entirely rather than filling it in.

Do not stretch. The wordmark in `logo-lockup.svg` is converted to outlines, so it
needs no fonts installed and will not reflow, but it also cannot be re-typed —
edit `build_logo.py` and regenerate if the lab name changes.

Below about 24 px the slate arch stops being legible. That is expected; the
silhouette still carries. Use `logo-tile.svg` for anything smaller.

## Regenerating

`logo-build.py`, in this folder, redraws every SVG here:

```
pip install --user fonttools brotli uharfbuzz
python3 logo-build.py
```

It draws the wave from the six-value `AMPS` envelope at the top of the file and
outlines the wordmark from the `.woff2` files in `fonts/`. Change the lab name or
the envelope there, not in the SVGs. It emits vectors only — the PNGs were
exported from the SVGs separately.
