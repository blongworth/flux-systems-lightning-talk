"""Export the rendered revealjs deck to a PowerPoint file.

Each slide becomes a full-slide 1920x1080 picture, and its speaker notes are
copied into PowerPoint's notes field. The result can be inserted into another
presentation with Insert > Slides from > Other Presentation.

Usage:
    quarto render            # or leave `quarto preview` running
    uv run export_pptx.py    # writes export/flux-talk.pptx
"""

import argparse
import html
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).parent
DEFAULT_HTML = ROOT / "_site" / "index.html"
DEFAULT_OUT = ROOT / "export" / "flux-talk.pptx"
CHROME = os.environ.get(
    "CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
WIDTH, HEIGHT = 1920, 1080

# Hide on-screen navigation chrome in the screenshots.
EXPORT_CSS = """
<style>
  .slide-menu-button, .reveal .controls, .reveal .progress,
  .reveal .slide-number { display: none !important; }
</style>
"""


def top_level_sections(page: str) -> list[str]:
    """Return the HTML of each top-level <section> inside div.slides."""
    start = page.index('<div class="slides">')
    sections, depth, begin = [], 0, None
    for m in re.finditer(r"<section\b|</section>", page[start:]):
        pos = start + m.start()
        if m.group(0) == "</section>":
            depth -= 1
            if depth == 0:
                sections.append(page[begin : pos + len("</section>")])
        else:
            if depth == 0:
                begin = pos
            depth += 1
    return sections


def notes_text(section: str) -> str:
    """Extract speaker notes from a section as plain text."""
    m = re.search(r'<aside class="notes">(.*?)</aside>', section, re.DOTALL)
    if not m:
        return ""
    text = m.group(1)
    text = re.sub(r"<li[^>]*>", "• ", text)
    text = re.sub(r"</(p|li|ul|ol|div)>|<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    lines = [ln.strip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def screenshot(url: str, out: Path, profile: Path, timeout: float = 60) -> None:
    """Capture one slide with headless Chrome."""
    out.unlink(missing_ok=True)
    proc = subprocess.Popen(
        [
            CHROME,
            "--headless=new",
            f"--user-data-dir={profile}",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={WIDTH},{HEIGHT}",
            "--virtual-time-budget=8000",
            f"--screenshot={out}",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Headless Chrome sometimes writes the file but doesn't exit; don't wait on it.
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if out.exists() and out.stat().st_size > 0 and proc.poll() is not None:
            break
        if out.exists() and out.stat().st_size > 0:
            time.sleep(1)
            break
        time.sleep(0.25)
    if proc.poll() is None:
        proc.kill()
    if not out.exists():
        sys.exit(f"Screenshot failed for {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.html.exists():
        sys.exit(f"{args.html} not found; run `quarto render` first.")

    page = args.html.read_text(encoding="utf-8")
    sections = top_level_sections(page)
    print(f"Found {len(sections)} slides in {args.html}")

    # Copy of the deck with navigation hidden, next to the original so
    # relative asset paths still resolve.
    export_html = args.html.with_name("_export.html")
    export_html.write_text(page.replace("</head>", EXPORT_CSS + "</head>", 1))

    png_dir = args.out.parent / "slides"
    png_dir.mkdir(parents=True, exist_ok=True)

    prs = Presentation()
    prs.slide_width = Emu(12192000)  # 13.333 in, 16:9
    prs.slide_height = Emu(6858000)  # 7.5 in
    blank = prs.slide_layouts[6]

    try:
        with tempfile.TemporaryDirectory() as profile:
            for i, section in enumerate(sections):
                png = png_dir / f"slide-{i + 1:02d}.png"
                screenshot(f"{export_html.as_uri()}#/{i}", png, Path(profile))
                slide = prs.slides.add_slide(blank)
                slide.shapes.add_picture(
                    str(png), 0, 0, prs.slide_width, prs.slide_height
                )
                notes = notes_text(section)
                if notes:
                    slide.notes_slide.notes_text_frame.text = notes
                print(f"  slide {i + 1}: {png.name}, {len(notes)} chars of notes")
    finally:
        export_html.unlink(missing_ok=True)

    prs.save(args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
