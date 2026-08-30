#!/usr/bin/env python3
"""
Render every .svg in a directory to .png with headless Chromium.

Called by generate_diagrams.py; the intermediate SVGs live in a temp directory and
are not committed -- only the PNGs are.

    python3 scripts/svg_to_png.py <svg_dir> <png_dir> [scale]

Reports, per file, whether any text overflows the SVG viewBox. That check is the
reason this step exists as its own script: text overflow is invisible in the SVG
source and only shows up once rendered.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

BG = "#0d1117"


def main(svg_dir, png_dir, scale=2):
    svg_dir, png_dir = pathlib.Path(svg_dir), pathlib.Path(png_dir)
    png_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(svg_dir.glob("*.svg"))
    problems = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for f in files:
            svg = f.read_text(encoding="utf-8")
            page = browser.new_page(device_scale_factor=scale)
            page.set_content(
                f'<html><body style="margin:0;background:{BG}">{svg}</body></html>',
                wait_until="load")
            page.wait_for_timeout(120)

            # does anything stick out of the viewBox?
            over = page.evaluate("""() => {
                const svg = document.querySelector('svg');
                const vb = svg.viewBox.baseVal;
                const bad = [];
                for (const el of svg.querySelectorAll('text, rect, line, polyline, circle')) {
                    let b; try { b = el.getBBox(); } catch (e) { continue; }
                    if (b.width === 0 && b.height === 0) continue;
                    if (b.x < -0.5 || b.y < -0.5 ||
                        b.x + b.width > vb.width + 0.5 || b.y + b.height > vb.height + 0.5) {
                        bad.push((el.textContent || el.tagName).trim().slice(0, 48));
                    }
                }
                const texts = [...svg.querySelectorAll('text')].map(el => {
                    const b = el.getBBox();
                    return {t: el.textContent.trim(), x: b.x, y: b.y, w: b.width, h: b.height};
                }).filter(o => o.w > 0);
                for (let i = 0; i < texts.length; i++)
                    for (let j = i + 1; j < texts.length; j++) {
                        const a = texts[i], c = texts[j];
                        const ox = Math.min(a.x + a.w, c.x + c.w) - Math.max(a.x, c.x);
                        const oy = Math.min(a.y + a.h, c.y + c.h) - Math.max(a.y, c.y);
                        if (ox > 1.5 && oy > 1.5)
                            bad.push(`OVERLAP "${a.t.slice(0,26)}" / "${c.t.slice(0,26)}"`);
                    }
                return bad;
            }""")
            el = page.query_selector("svg")
            el.screenshot(path=str(png_dir / f"{f.stem}.png"))
            box = el.bounding_box()
            page.close()

            flag = ""
            if over:
                problems.append((f.stem, over))
                flag = f"   <-- {len(over)} element(s) layout problem(s)"
            print(f"  {f.stem:34s} {int(box['width'])}×{int(box['height'])} px{flag}")
        browser.close()

    if problems:
        print("\nLAYOUT REPORT")
        for name, items in problems:
            print(f"  {name}: {items}")
        return 1
    print("\nclean: nothing outside the viewBox, no overlapping labels")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2],
                  int(sys.argv[3]) if len(sys.argv) > 3 else 2))
