"""
Record the dashboard demo video (docs/dashboard-demo.mp4) with Playwright.

1. Start the Panel app in another terminal:   panel serve dashboard_app.py --port 5007
2. Run:                                        python docs/record_demo.py

The Plotly map dashboards (Dashboard_1.html, Dashboard_2.html, World_Electricity.html,
World_Energy.html) are opened from the repo.
Needs: pip install playwright && playwright install chromium, plus ffmpeg on PATH.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
W, H = 1280, 720
PANEL_URL = "http://localhost:5007/dashboard_app"

CAPTION_JS = """(text) => {
  let el = document.getElementById('__cap');
  if (!el) {
    el = document.createElement('div'); el.id = '__cap';
    el.style.cssText = 'position:fixed;left:0;right:0;bottom:0;padding:14px 28px;background:rgba(13,17,23,.92);' +
      'color:#f0f6fc;font:600 20px Inter,Arial,sans-serif;z-index:99999;border-left:6px solid #3987e5';
    document.body.appendChild(el);
  }
  el.textContent = text;
}"""


def sweep(page, x0, x1, y, secs, steps=60):
    page.mouse.move(x0, y)
    for i in range(steps + 1):
        page.mouse.move(x0 + (x1 - x0) * i / steps, y, steps=2)
        page.wait_for_timeout(int(secs * 1000 / steps))


def main(route_installer=None):
    tmp = OUT / "_video_tmp"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(tmp),
                                  record_video_size={"width": W, "height": H})
        page = ctx.new_page()
        if route_installer:
            route_installer(page)

        # 1. Panel dashboard (live)
        page.goto(PANEL_URL)
        page.wait_for_selector("canvas", timeout=30000)
        page.wait_for_timeout(1500)
        page.evaluate(CAPTION_JS, "Panel dashboard: Ireland vs EU average energy use per person, 1960 to 2022")
        page.wait_for_timeout(2500)
        box = page.locator("canvas").first.bounding_box()
        page.evaluate(CAPTION_JS, "Hover to compare Ireland and the EU average for any year")
        sweep(page, box["x"] + 70, box["x"] + 570, box["y"] + 60, secs=7)
        page.mouse.move(box["x"] + 408 - 10, box["y"] + 57, steps=10)  # Ireland's 2001 peak
        page.evaluate(CAPTION_JS, "Ireland's energy use peaked in 2001 and has fallen about 29% since")
        page.wait_for_timeout(3000)
        page.evaluate(CAPTION_JS, "Switch metric: electricity use per person (kWh)")
        page.locator("select").first.select_option(index=1)
        page.wait_for_timeout(2500)
        sweep(page, box["x"] + 70, box["x"] + 570, box["y"] + 120, secs=6)
        page.evaluate(CAPTION_JS, "Ireland caught up with the EU average around 2000 and has tracked just below it since")
        page.wait_for_timeout(3000)

        # 2. Plotly animated maps
        for name, cap in [
            ("Dashboard_1.html", "Animated map: electricity use per person across the EU, 1960 to 2022"),
            ("Dashboard_2.html", "Animated map: energy use per person across the EU, 1960 to 2022"),
            ("World_Electricity.html", "World view: electricity use per person, 1960 to 2022"),
            ("World_Energy.html", "World view: energy use per person, 1960 to 2022"),
        ]:
            page.goto((ROOT / name).as_uri())
            page.wait_for_selector(".updatemenu-button", timeout=30000)
            page.wait_for_timeout(1200)
            page.evaluate(CAPTION_JS, cap)
            page.wait_for_timeout(1500)
            # same as pressing play, but stepping every third year so 1960 to 2022 fits in a few seconds
            page.evaluate("""() => { const gd = document.querySelector('.plotly-graph-div');
                const names = gd._transitionData._frames.map(f => f.name);
                const pick = names.filter((n, i) => i % 3 === 0 || i === names.length - 1);
                return Plotly.animate(gd, pick, {frame: {duration: 150, redraw: true},
                                                 transition: {duration: 0}, mode: 'immediate'}); }""")
            page.wait_for_timeout(2000)

        video = page.video.path()
        ctx.close()
        browser.close()

    raw = OUT / "raw-demo.webm"
    shutil.move(video, raw)
    shutil.rmtree(tmp, ignore_errors=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "22", "-preset", "slow", "-movflags", "+faststart", "-an",
                    str(OUT / "dashboard-demo.mp4")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-vf",
                    "fps=8,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];"
                    "[b][p]paletteuse=dither=none:diff_mode=rectangle", str(OUT / "dashboard-demo.gif")], check=True)
    raw.unlink()
    print("Saved", OUT / "dashboard-demo.mp4", "and", OUT / "dashboard-demo.gif")


if __name__ == "__main__":
    installer = None
    if len(sys.argv) > 1:  # optional: path to a module that serves CDN files locally (offline recording)
        sys.path.insert(0, sys.argv[1])
        from routes import install as installer
    main(installer)
