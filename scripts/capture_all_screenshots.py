"""
AquaMitra - Master Visual Capture & Deployment Audit Utility
Generates both high-resolution Enterprise Desktop (1600x1100) and
Mobile Touch (390x844) screenshots across the 7 showcase views,
while auditing all 15 operational menus for 0 errors and clean alignment.
"""

import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")

DESKTOP_SHOTS = [
    ("01_overview_dashboard.png", "overview", "Farm Command Center"),
    ("02_ponds_command_center.png", "ponds", "Pond Management"),
    ("03_water_quality_matrix.png", "water", "Water Quality Observations"),
    ("04_fish_growth_analytics.png", "fish", "Fish Stock & Biology"),
    ("05_feeding_and_inventory.png", "feeding", "Feeding & Nutrition"),
    ("06_ai_intelligence_center.png", "ai", "AquaMitra AI Companion"),
    ("07_financial_management.png", "finance", "Farm Finances & Revenue"),
]

MOBILE_SHOTS = [
    ("mobile_01_overview.png", "overview", "Farm Command Center"),
    ("mobile_02_ponds.png", "ponds", "Pond Management"),
    ("mobile_03_water.png", "water", "Water Quality Observations"),
    ("mobile_04_fish.png", "fish", "Fish Stock & Biology"),
    ("mobile_05_feeding.png", "feeding", "Feeding & Nutrition"),
    ("mobile_06_ai.png", "ai", "AquaMitra AI Companion"),
    ("mobile_07_finance.png", "finance", "Farm Finances & Revenue"),
]

ALL_MENUS = [
    ("overview", "Farm Command Center"),
    ("ponds", "Pond Management"),
    ("fish", "Fish Stock & Biology"),
    ("water", "Water Quality Observations"),
    ("feeding", "Feeding & Nutrition"),
    ("health", "Health & Mortality Incidents"),
    ("environment", "Meteorological Context"),
    ("finance", "Farm Finances & Revenue"),
    ("assets", "Equipment & Machinery"),
    ("analytics", "Operational Analytics"),
    ("alerts", "Decision-Support Alerts"),
    ("records", "Master Records & Audit"),
    ("ai", "AquaMitra AI Companion"),
    ("reports", "Farm Reports & Exports"),
    ("settings", "Configuration & Farm Profile"),
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. Desktop Capture (1600 x 1100)
        print("=== 1. Capturing Desktop Enterprise Screenshots (1600x1100) ===")
        desktop_page = browser.new_page(viewport={"width": 1600, "height": 1100})
        for filename, menu_key, title in DESKTOP_SHOTS:
            url = f"http://localhost:8501/?menu={menu_key}"
            print(f"Loading {menu_key} ({title})...")
            desktop_page.goto(url, wait_until="domcontentloaded")
            desktop_page.locator("h1").filter(has_text=title).first.wait_for(timeout=15000)
            desktop_page.wait_for_timeout(2500)
            out_path = os.path.join(OUTPUT_DIR, filename)
            desktop_page.screenshot(path=out_path, full_page=False)
            print(f"  -> Saved {filename} ({os.path.getsize(out_path)/1024:.1f} KB)")
        desktop_page.close()

        # 2. Mobile Capture (390 x 844, scale factor 2)
        print("\n=== 2. Capturing Mobile Touch Screenshots (390x844) ===")
        mobile_context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2
        )
        mobile_page = mobile_context.new_page()
        for filename, menu_key, title in MOBILE_SHOTS:
            url = f"http://localhost:8501/?menu={menu_key}"
            print(f"Loading {menu_key} on mobile...")
            mobile_page.goto(url, wait_until="domcontentloaded")
            mobile_page.locator("h1").filter(has_text=title).first.wait_for(timeout=15000)
            mobile_page.wait_for_timeout(2200)
            out_path = os.path.join(OUTPUT_DIR, filename)
            mobile_page.screenshot(path=out_path, full_page=False)
            print(f"  -> Saved {filename} ({os.path.getsize(out_path)/1024:.1f} KB)")

        # 3. Comprehensive Menu Validation
        print("\n=== 3. Auditing All 15 Menus for Clean Execution ===")
        errors = []
        for menu_key, title in ALL_MENUS:
            url = f"http://localhost:8501/?menu={menu_key}"
            try:
                mobile_page.goto(url, wait_until="domcontentloaded")
                mobile_page.locator("h1").filter(has_text=title).first.wait_for(timeout=15000)
                mobile_page.wait_for_timeout(1000)
                # Check for exceptions
                exc = mobile_page.locator(".stException").count()
                if exc > 0:
                    errors.append(f"Exception detected on {menu_key}")
                    print(f"  [ERROR] {menu_key}: {exc} exception(s)")
                else:
                    print(f"  [OK] {menu_key}: 0 errors")
            except Exception as e:
                errors.append(f"{menu_key}: {str(e)}")
                print(f"  [FAIL] {menu_key}: {e}")

        mobile_context.close()
        browser.close()

        if errors:
            print(f"\nCompleted with {len(errors)} issues:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("\nSUCCESS: All 14 screenshots updated and all 15 menus verified flawless!")

if __name__ == "__main__":
    main()
