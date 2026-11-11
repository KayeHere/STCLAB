"""Fill the ASCII portraits on people.html.

Ports avatarToAscii() from github.com/jeantimex/neofetch-profile (api/index.js):
contain the photo in a character grid whose cells are half as wide as they are
tall, sample one pixel per character, apply contrast 1.2, and index the
luminance into the same 92-character ramp; transparent pixels become spaces.

Changes for this site:
  * the background is cut away with macOS Vision person segmentation
    (tools/person-mask.swift), since the repo's removeBackground only handles
    flat colours and lab photos have real backgrounds;
  * luminance is stretched to the 2nd-98th percentile inside the mask, and
    masked pixels never map to a blank, so the silhouette reads on the page;
  * no inversion of dark photos, because the page is always dark.

Usage (macOS, from the repo root):  python3 tools/neofetch-ascii.py
Every <pre data-ascii="slug" data-cols="N"> is regenerated from assets/slug.jpg.
To add a person, add their card to people.html and rerun.
"""
import html, os, re, subprocess, tempfile
from PIL import Image

RAMP = ' `.-\':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@'
CONTRAST = 1.2
FLOOR = 2          # lowest ramp index inside the person
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = tempfile.gettempdir()


def mask_tool():
    exe = os.path.join(TMP, 'stc-person-mask')
    src = os.path.join(ROOT, 'tools', 'person-mask.swift')
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        subprocess.run(['swiftc', '-O', src, '-o', exe], check=True)
    return exe


def to_ascii(photo, cols):
    rows = round(cols * 0.5)                       # square photo, cells 1:2
    mask = os.path.join(TMP, 'stc-mask.png')
    subprocess.run([mask_tool(), photo, mask], check=True, stdout=subprocess.DEVNULL)
    px = Image.open(photo).convert('L').resize((cols, rows), Image.LANCZOS).load()
    mk = Image.open(mask).convert('L').resize((cols, rows), Image.LANCZOS).load()
    inside = sorted(px[x, y] for y in range(rows) for x in range(cols) if mk[x, y] >= 128)
    lo, hi = inside[len(inside) // 50], inside[-len(inside) // 50 - 1]
    lines = []
    for y in range(rows):
        line = ''
        for x in range(cols):
            if mk[x, y] < 128:
                line += ' '
                continue
            l = (px[x, y] - lo) / max(1, hi - lo) * 255
            l = min(255, max(0, (l - 128) * CONTRAST + 128))
            line += RAMP[FLOOR + int(l / 255 * (len(RAMP) - 1 - FLOOR))]
        lines.append(line.rstrip())
    return '\n'.join(lines)


def main():
    path = os.path.join(ROOT, 'people.html')
    page = open(path).read()
    pat = re.compile(r'(<pre class="nf-ascii" data-ascii="([\w-]+)" data-cols="(\d+)"[^>]*>)(.*?)(</pre>)', re.S)

    def fill(m):
        art = to_ascii(os.path.join(ROOT, 'assets', m[2] + '.jpg'), int(m[3]))
        print('filled', m[2])
        return m[1] + html.escape(art, quote=False) + m[5]

    open(path, 'w').write(pat.sub(fill, page))


if __name__ == '__main__':
    main()
