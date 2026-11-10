"""
AquaMitra Statistical Anomaly Detection & Data Health Audit Engine
Combines statistical thresholds, rolling averages, and record audits to flag anomalies.
"""

from typing import List, Dict, Any
from datetime import date, timedelta
import pandas as pd


def detect_farm_anomalies(session_state: Any) -> List[Dict[str, Any]]:
    """
    Scans recent farm records for statistical or threshold anomalies.
    Returns structured anomaly items with severity, category, and suggested checks.
    """
    anomalies = []
    waters = getattr(session_state, "demo_water_quality", [])
    feeds = getattr(session_state, "demo_feeding", [])
    mortalities = getattr(session_state, "demo_mortality", [])
    expenses = getattr(session_state, "demo_expenses", [])

    # 1. Water Quality Anomalies (DO Drop or Ammonia Spikes)
    if waters:
        df_w = pd.DataFrame(waters)
        for pid, group in df_w.groupby("PondID"):
            recent = group.sort_values("ReadingDate").iloc[-1]
            # Check Dissolved Oxygen
            if pd.notnull(recent.get("DissolvedOxygen")) and recent["DissolvedOxygen"] < 5.0:
                anomalies.append({
                    "id": f"anom_do_{pid}",
                    "severity": "HIGH",
                    "category": "Water Quality",
                    "pond_id": pid,
                    "title": f"Dissolved Oxygen Low in {pid}",
                    "observation": f"Recent DO is {recent['DissolvedOxygen']} mg/L (configured reference >= 5.0 mg/L).",
                    "suggested_action": "Recheck reading immediately. Run aeration during early morning hours and observe fish behaviour.",
                    "source": f"Water log {recent.get('ReadingDate')}"
                })

            # Check Ammonia
            if pd.notnull(recent.get("Ammonia")) and recent["Ammonia"] > 0.05:
                anomalies.append({
                    "id": f"anom_nh3_{pid}",
                    "severity": "HIGH",
                    "category": "Water Quality",
                    "pond_id": pid,
                    "title": f"Elevated Ammonia in {pid}",
                    "observation": f"Recent Ammonia is {recent['Ammonia']} mg/L (reference <= 0.05 mg/L).",
                    "suggested_action": "Review feeding quantity, check organic bottom accumulation, and refresh water if feasible.",
                    "source": f"Water log {recent.get('ReadingDate')}"
                })

    # 2. Feeding Ration Anomalies (Deviation from Biomass Requirement > 15%)
    if feeds:
        for f in feeds[-4:]:
            rec = f.get("RecommendedFeedKg", 0)
            act = f.get("ActualFeedKg", 0)
            if rec > 0:
                dev = abs(act - rec) / rec
                if dev > 0.15:
                    anomalies.append({
                        "id": f"anom_feed_{f.get('FeedingID')}",
                        "severity": "WARNING",
                        "category": "Feeding",
                        "pond_id": f.get("PondID"),
                        "title": f"Feed Ration Deviation ({f.get('PondID')})",
                        "observation": f"Fed {act} kg vs recommended {rec} kg ({int(dev*100)}% variance).",
                        "suggested_action": "Verify if feed trays show leftover feed or if stock sampling justifies higher feed rate.",
                        "source": f"Feeding log {f.get('FeedingDate')}"
                    })

    # 3. Mortality Events
    if mortalities:
        for m in mortalities:
            dead = m.get("NumberOfDead", 0)
            if dead >= 10:
                anomalies.append({
                    "id": f"anom_mort_{m.get('IncidentID')}",
                    "severity": "HIGH",
                    "category": "Mortality",
                    "pond_id": m.get("PondID"),
                    "title": f"Mortality Spike ({dead} Fish) in {m.get('PondID')}",
                    "observation": f"{dead} dead fish recorded on {m.get('IncidentDate')}. Symptoms: {m.get('VisibleSymptoms', 'None noted')}.",
                    "suggested_action": "Check DO, temperature, and feeding records around this date. Consult a qualified fisheries professional if mortality continues.",
                    "source": f"Incident log {m.get('IncidentDate')}"
                })

    return anomalies


def audit_data_health(session_state: Any) -> List[Dict[str, Any]]:
    """
    Audits farm records for missing, outdated, or incomplete data.
    Helps farmers maintain disciplined farm records.
    """
    issues = []
    ponds = getattr(session_state, "demo_ponds", [])
    waters = getattr(session_state, "demo_water_quality", [])
    stocks = getattr(session_state, "demo_fish_stock", [])
    growths = getattr(session_state, "demo_fish_growth", [])
    feeds = getattr(session_state, "demo_feeding", [])

    # 1. Ponds with no water observations
    water_pids = {w["PondID"] for w in waters}
    for p in ponds:
        if p["Status"] == "Active" and p["PondID"] not in water_pids:
            issues.append({
                "type": "missing_water",
                "severity": "WARNING",
                "title": f"No Water Readings: {p['PondName']} ({p['PondID']})",
                "message": "This active pond has no recorded water observations. Regular water tests are essential for health tracking.",
                "action": "Log Water Reading"
            })

    # 2. Stocked ponds without recent growth observations
    growth_pids = {g["PondID"] for g in growths}
    for s in stocks:
        if s["PondID"] not in growth_pids:
            issues.append({
                "type": "missing_growth",
                "severity": "INFO",
                "title": f"No Growth Samples: {s['PondID']}",
                "message": f"Fish stocked on {s.get('StockingDate')} have no sampling observations. Sample weight needed for accurate biomass estimation.",
                "action": "Record Growth Sample"
            })

    # 3. Feeding records with missing costs
    zero_cost_feeds = [f for f in feeds if not f.get("FeedCostPerKg")]
    if zero_cost_feeds:
        issues.append({
            "type": "missing_feed_cost",
            "severity": "INFO",
            "title": f"{len(zero_cost_feeds)} Feed Records Missing Cost",
            "message": "Some feed entries do not include feed cost/kg, which affects total farm financial analytics.",
            "action": "Update Feed Costs"
        })

    return issues
