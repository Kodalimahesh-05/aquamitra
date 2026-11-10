"""
AquaMitra AI Context Builder
Extracts, aggregates, and sanitizes application records into a compact structured context.
Keeps token count low (< 1,000 tokens) and excludes all credentials and sensitive data.
"""

from typing import Dict, Any, List, Optional
from datetime import date, timedelta


def build_farm_context(session_state: Any) -> Dict[str, Any]:
    """
    Builds a structured, sanitized summary context for the entire farm.
    """
    ponds = getattr(session_state, "demo_ponds", [])
    stocks = getattr(session_state, "demo_fish_stock", [])
    growths = getattr(session_state, "demo_fish_growth", [])
    waters = getattr(session_state, "demo_water_quality", [])
    feeds = getattr(session_state, "demo_feeding", [])
    mortalities = getattr(session_state, "demo_mortality", [])
    expenses = getattr(session_state, "demo_expenses", [])
    sales = getattr(session_state, "demo_sales", [])
    alerts = getattr(session_state, "demo_alerts", [])
    weather = getattr(session_state, "demo_weather", {})

    # Pond summary
    total_ponds = len(ponds)
    active_ponds = len([p for p in ponds if p.get("Status") == "Active"])
    total_area = sum(float(p.get("Area", 0)) for p in ponds)

    # Stock & Biomass
    total_fish = sum(s.get("NumberOfFish", 0) for s in stocks)
    species_counts = {}
    for s in stocks:
        sp = s.get("Species", "Unknown")
        species_counts[sp] = species_counts.get(sp, 0) + s.get("NumberOfFish", 0)

    # Approximate current biomass based on latest sampling
    total_biomass_kg = 0.0
    for p in ponds:
        pid = p["PondID"]
        p_stocks = [s for s in stocks if s.get("PondID") == pid]
        p_growths = [g for g in growths if g.get("PondID") == pid]
        if p_stocks:
            p_fish = sum(s.get("NumberOfFish", 0) for s in p_stocks)
            avg_w = p_growths[-1].get("AvgFishWeightGrams", 50.0) if p_growths else 50.0
            total_biomass_kg += (p_fish * avg_w) / 1000.0

    # Latest water quality condition
    water_anomalies = []
    latest_by_pond = {}
    for w in sorted(waters, key=lambda x: x.get("ReadingDate", "")):
        latest_by_pond[w["PondID"]] = w

    for pid, w in latest_by_pond.items():
        issues = []
        if w.get("DissolvedOxygen") is not None and w.get("DissolvedOxygen") < 5.0:
            issues.append(f"Low DO: {w['DissolvedOxygen']} mg/L")
        if w.get("pH") is not None and (w.get("pH") < 6.5 or w.get("pH") > 8.5):
            issues.append(f"pH: {w['pH']}")
        if issues:
            water_anomalies.append(f"{pid} ({', '.join(issues)})")

    # Feeding summary
    recent_feeds = feeds[-6:] if feeds else []
    today_feed_kg = sum(f.get("ActualFeedKg", 0) for f in feeds[-2:]) if feeds else 0.0
    recommended_feed_kg = sum(f.get("RecommendedFeedKg", 0) for f in feeds[-2:]) if feeds else 0.0

    # Mortality summary (last 7 days)
    recent_dead = sum(m.get("NumberOfDead", 0) for m in mortalities)
    unresolved_alerts = [a for a in alerts if not a.get("IsResolved")]

    # Financial summary
    total_expenses = sum(e.get("Amount", 0) for e in expenses)
    total_sales = sum(s.get("TotalRevenue", 0) for s in sales)
    net_diff = total_sales - total_expenses

    # Top expense category
    cat_expenses = {}
    for e in expenses:
        c = e.get("Category", "Other")
        cat_expenses[c] = cat_expenses.get(c, 0) + e.get("Amount", 0)
    top_cat = max(cat_expenses.items(), key=lambda x: x[1])[0] if cat_expenses else "N/A"

    return {
        "farm_overview": {
            "total_ponds": total_ponds,
            "active_ponds": active_ponds,
            "total_area_acres": round(total_area, 2),
            "total_fish": total_fish,
            "estimated_biomass_kg": round(total_biomass_kg, 1),
            "species_breakdown": species_counts
        },
        "water_condition": {
            "anomalies_detected": water_anomalies,
            "ponds_with_attention_needed": len(water_anomalies)
        },
        "feeding": {
            "today_actual_kg": round(today_feed_kg, 1),
            "today_recommended_kg": round(recommended_feed_kg, 1),
            "variance_kg": round(today_feed_kg - recommended_feed_kg, 1)
        },
        "health_incidents": {
            "recent_dead_fish": recent_dead,
            "total_incidents": len(mortalities)
        },
        "alerts": {
            "unresolved_count": len(unresolved_alerts),
            "unresolved_titles": [f"{a.get('PondID')}: {a.get('Title')}" for a in unresolved_alerts[:3]]
        },
        "finance": {
            "total_expenses": total_expenses,
            "total_sales": total_sales,
            "estimated_net_difference": net_diff,
            "top_expense_category": top_cat
        },
        "weather": {
            "current_temp": weather.get("current_temp", 32.0),
            "condition": weather.get("current_condition", "Partly Cloudy")
        }
    }


def build_pond_context(pond_id: str, session_state: Any) -> Dict[str, Any]:
    """
    Builds a focused context for an individual pond.
    """
    farm_ctx = build_farm_context(session_state)
    ponds = {p.get("PondID", ""): p for p in getattr(session_state, "demo_ponds", [])}
    pond = ponds.get(pond_id, {"PondID": pond_id, "PondName": f"Pond {pond_id}"})

    stocks = [s for s in getattr(session_state, "demo_fish_stock", []) if s.get("PondID") == pond_id]
    waters = [w for w in getattr(session_state, "demo_water_quality", []) if w.get("PondID") == pond_id]
    feeds = [f for f in getattr(session_state, "demo_feeding", []) if f.get("PondID") == pond_id]
    mortalities = [m for m in getattr(session_state, "demo_mortality", []) if m.get("PondID") == pond_id]

    latest_water = waters[-1] if waters else {}
    latest_feed = feeds[-1] if feeds else {}

    return {
        "pond_id": pond_id,
        "pond_name": pond.get("PondName"),
        "status": pond.get("Status"),
        "area": pond.get("Area"),
        "stock": stocks,
        "latest_water": {
            "pH": latest_water.get("pH"),
            "temperature": latest_water.get("Temperature"),
            "dissolved_oxygen": latest_water.get("DissolvedOxygen"),
            "turbidity": latest_water.get("Turbidity"),
            "ammonia": latest_water.get("Ammonia"),
            "date": latest_water.get("ReadingDate")
        },
        "latest_feeding": {
            "actual_feed_kg": latest_feed.get("ActualFeedKg"),
            "recommended_feed_kg": latest_feed.get("RecommendedFeedKg"),
            "feed_type": latest_feed.get("FeedType")
        },
        "mortality_events_count": len(mortalities)
    }
