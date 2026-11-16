"""
Capture High-DPI Screenshots from Live Flask Prototype and update Word Document.
Uses system Chrome via Playwright.
"""

import os
import sys
import time
import threading
from playwright.sync_api import sync_playwright

sys.path.insert(0, r"C:\Users\siriv\OneDrive\Desktop\sandya project")
from app import app
import build_full_ipr_doc

ASSETS_DIR = r"C:\Users\siriv\OneDrive\Desktop\sandya project\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)


def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)


def capture_all():
    # 1. Start Flask in background thread if not already running
    import urllib.request
    server_running = False
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:5000/", timeout=2)
        if resp.status == 200:
            server_running = True
    except Exception:
        server_running = False

    if not server_running:
        server_thread = threading.Thread(target=run_flask, daemon=True)
        server_thread.start()
        time.sleep(2)  # Give server time to bind

    print("Flask server verified running on http://127.0.0.1:5000")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
        page = context.new_page()

        # 1. Capture All 3 Screens (Figure A2.1 Wireframe replacement)
        page.goto("http://127.0.0.1:5000/all-screens")
        page.wait_for_selector("#showcase")
        time.sleep(1)

        figure_path = os.path.join(ASSETS_DIR, "figure_a2_1_live_prototype.png")
        page.locator("#showcase").screenshot(path=figure_path)
        print(f"Captured Figure A2.1 to: {figure_path}")

        # Also overwrite original asset image so any doc generator uses the live screenshot
        orig_fig_path = os.path.join(ASSETS_DIR, "c0d12457f56b4b37f50a1ccf1d353f8c220b9d3d.png")
        page.locator("#showcase").screenshot(path=orig_fig_path)
        print(f"Updated original asset at: {orig_fig_path}")

        # 2. Capture Unified Studio Application (Figure A2.2)
        page.goto("http://127.0.0.1:5000/")
        page.wait_for_selector("#studio-layout")
        time.sleep(1)
        unified_path = os.path.join(ASSETS_DIR, "figure_a2_2_unified_app.png")
        page.screenshot(path=unified_path, full_page=True)
        print(f"Captured Unified Application Figure A2.2 to: {unified_path}")

        # 3. Capture Screen A (Home)
        page.goto("http://127.0.0.1:5000/screen-a?stay=1")
        page.wait_for_selector("#frame-screen-a", timeout=8000)
        screen_a_path = os.path.join(ASSETS_DIR, "screen_a_home.png")
        page.locator("#frame-screen-a").screenshot(path=screen_a_path)
        print(f"Captured Screen A to: {screen_a_path}")

        # 4. Capture Screen B (Prompt)
        page.goto("http://127.0.0.1:5000/screen-b")
        page.wait_for_selector("#frame-screen-b", timeout=8000)
        screen_b_path = os.path.join(ASSETS_DIR, "screen_b_prompt.png")
        page.locator("#frame-screen-b").screenshot(path=screen_b_path)
        print(f"Captured Screen B to: {screen_b_path}")

        # 5. Capture Screen C (Caregiver)
        page.goto("http://127.0.0.1:5000/screen-c")
        page.wait_for_selector("#frame-screen-c", timeout=8000)
        screen_c_path = os.path.join(ASSETS_DIR, "screen_c_caregiver.png")
        page.locator("#frame-screen-c").screenshot(path=screen_c_path)
        print(f"Captured Screen C to: {screen_c_path}")

        browser.close()

    print("All screenshots successfully captured!")

    # Re-build Word document with the live captured prototype figure
    print("Re-compiling Word Document with live captured prototype screenshots...")
    build_full_ipr_doc.create_full_document()
    print("Document successfully re-compiled!")


if __name__ == "__main__":
    capture_all()
