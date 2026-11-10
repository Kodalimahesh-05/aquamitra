"""
AquaMitra - Automated Screenshot Capture Utility
Captures high-resolution screenshots of the 6 key application modules into the 'screenshots/' folder.
"""

import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOTS = [
    {
        "filename": "01_overview_dashboard.png",
        "url": "http://localhost:8501/?menu=overview",
        "expected_h1": "Farm Command Center",
        "title": "Overview Dashboard - Farm Command Center",
        "features": "8 KPI cards, 9-action Quick Actions Bar, AI Farm Status Synthesis, Pond Snapshots, Decision Alerts."
    },
    {
        "filename": "02_ponds_command_center.png",
        "url": "http://localhost:8501/?menu=ponds",
        "expected_h1": "Pond Management",
        "title": "Pond Management & Command Center",
        "features": "All Ponds Grid, health metrics (Stock, Biomass, Water, Feed, Incidents), status filters, and action buttons."
    },
    {
        "filename": "03_water_quality_matrix.png",
        "url": "http://localhost:8501/?menu=water",
        "expected_h1": "Water Quality Observations",
        "title": "Water Quality Matrix & Anomaly Detection",
        "features": "Physicochemical parameter matrix across ponds (pH, DO, Temp, Turbidity, Ammonia), status badges, and AI Water Analysis."
    },
    {
        "filename": "04_fish_growth_analytics.png",
        "url": "http://localhost:8501/?menu=fish",
        "expected_h1": "Fish Stock & Biology",
        "title": "Fish Stocking, Species Registry & Biomass",
        "features": "Active stocking batches, stocking density, calculated biomass (kg), hatchery sources, and species registry."
    },
    {
        "filename": "05_feeding_and_inventory.png",
        "url": "http://localhost:8501/?menu=feeding",
        "expected_h1": "Feeding & Nutrition",
        "title": "Feed Ration Management & Warehouse Inventory",
        "features": "Daily feed application tracking, biomass ration model variance, average daily consumption, and feed cost metrics."
    },
    {
        "filename": "06_ai_intelligence_center.png",
        "url": "http://localhost:8501/?menu=ai",
        "expected_h1": "AquaMitra AI Companion",
        "title": "AquaMitra AI Companion & Decision Support",
        "features": "Grounded AI chat companion, categorized anomaly insights, actionable recommendations ([Accept Action], [Ignore]), and Morning Brief."
    },
    {
        "filename": "07_financial_management.png",
        "url": "http://localhost:8501/?menu=finance",
        "expected_h1": "Farm Finances & Revenue",
        "title": "Farm Finances, Expenses & Sales Revenue",
        "features": "Total recorded revenue, operational expenditures, Estimated Net Difference, categorized spending, and sales ledger."
    }
]

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Using a crisp 1600x1100 viewport for clean enterprise dashboard presentation
        page = browser.new_page(viewport={"width": 1600, "height": 1100})

        for item in SCREENSHOTS:
            out_file = os.path.join(output_dir, item["filename"])
            print(f"Loading {item['title']} via {item['url']}...")
            
            page.goto(item["url"], wait_until="domcontentloaded")
            # Wait for header to match
            page.locator("h1").filter(has_text=item["expected_h1"]).first.wait_for(timeout=15000)
            # Give UI time to complete animations and charts
            page.wait_for_timeout(2500)
            
            page.screenshot(path=out_file, full_page=False)
            size_kb = os.path.getsize(out_file) / 1024
            print(f"-> Saved: {item['filename']} ({size_kb:.1f} KB)")

        browser.close()
        print("\nAll screenshots generated successfully!")

if __name__ == "__main__":
    main()
