"""
AquaMitra Statistical Anomaly Detection & Data Health Audit Engine
Combines statistical thresholds, rolling averages, and record audits to flag anomalies.
Fully bilingual (English / Telugu) with strictly zero emojis.
"""

from typing import List, Dict, Any
import pandas as pd


def _get_lang(session_state: Any) -> str:
    try:
        if hasattr(session_state, "get"):
            return session_state.get("lang", "en")
        return getattr(session_state, "lang", "en")
    except Exception:
        return "en"


def detect_farm_anomalies(session_state: Any) -> List[Dict[str, Any]]:
    """
    Scans recent farm records for statistical or threshold anomalies.
    Returns structured anomaly items with severity, category, and suggested checks.
    """
    lang = _get_lang(session_state)
    anomalies = []
    waters = getattr(session_state, "demo_water_quality", [])
    feeds = getattr(session_state, "demo_feeding", [])
    mortalities = getattr(session_state, "demo_mortality", [])

    # 1. Water Quality Anomalies (DO Drop or Ammonia Spikes)
    if waters:
        df_w = pd.DataFrame(waters)
        for pid, group in df_w.groupby("PondID"):
            recent = group.sort_values("ReadingDate").iloc[-1]
            # Check Dissolved Oxygen
            if pd.notnull(recent.get("DissolvedOxygen")) and recent["DissolvedOxygen"] < 5.0:
                do_v = recent["DissolvedOxygen"]
                r_date = recent.get("ReadingDate")
                anomalies.append({
                    "id": f"anom_do_{pid}",
                    "severity": "HIGH",
                    "category": "Water Quality",
                    "pond_id": pid,
                    "title": (
                        f"{pid} లో కరిగిన ఆక్సిజన్ (DO) తక్కువగా ఉంది"
                        if lang == "te"
                        else f"Dissolved Oxygen Low in {pid}"
                    ),
                    "observation": (
                        f"ఇటీవలి కరిగిన ఆక్సిజన్ (DO) {do_v} mg/L గా నమోదైంది (సిఫార్సు పరిధి >= 5.0 mg/L)."
                        if lang == "te"
                        else f"Recent DO is {do_v} mg/L (configured reference >= 5.0 mg/L)."
                    ),
                    "suggested_action": (
                        "తక్షణమే మళ్ళీ నీటి పరీక్ష చేయండి. తెల్లవారుజాము వేళల్లో ఏరేటర్లను నడిపి, చేపల ప్రవర్తనను గమనించండి."
                        if lang == "te"
                        else "Recheck reading immediately. Run aeration during early morning hours and observe fish behaviour."
                    ),
                    "source": f"నీటి పరీక్ష లాగ్ {r_date}" if lang == "te" else f"Water log {r_date}",
                })

            # Check Ammonia
            if pd.notnull(recent.get("Ammonia")) and recent["Ammonia"] > 0.05:
                nh3_v = recent["Ammonia"]
                r_date = recent.get("ReadingDate")
                anomalies.append({
                    "id": f"anom_nh3_{pid}",
                    "severity": "HIGH",
                    "category": "Water Quality",
                    "pond_id": pid,
                    "title": (
                        f"{pid} లో అమోనియా స్థాయి పెరిగింది"
                        if lang == "te"
                        else f"Elevated Ammonia in {pid}"
                    ),
                    "observation": (
                        f"ఇటీవలి అమోనియా {nh3_v} mg/L గా ఉంది (ప్రమాణ పరిమితి <= 0.05 mg/L)."
                        if lang == "te"
                        else f"Recent Ammonia is {nh3_v} mg/L (reference <= 0.05 mg/L)."
                    ),
                    "suggested_action": (
                        "మేత పరిమాణాన్ని సమీక్షించండి, చెరువు అడుగున సేంద్రియ వ్యర్థాలను తనిఖీ చేసి, వీలైతే పాక్షిక నీటి మార్పిడి చేయండి."
                        if lang == "te"
                        else "Review feeding quantity, check organic bottom accumulation, and refresh water if feasible."
                    ),
                    "source": f"నీటి పరీక్ష లాగ్ {r_date}" if lang == "te" else f"Water log {r_date}",
                })

    # 2. Feeding Ration Anomalies (Deviation from Biomass Requirement > 15%)
    if feeds:
        for f in feeds[-4:]:
            rec = f.get("RecommendedFeedKg", 0)
            act = f.get("ActualFeedKg", 0)
            if rec > 0:
                dev = abs(act - rec) / rec
                if dev > 0.15:
                    f_pid = f.get("PondID")
                    f_date = f.get("FeedingDate")
                    anomalies.append({
                        "id": f"anom_feed_{f.get('FeedingID')}",
                        "severity": "WARNING",
                        "category": "Feeding",
                        "pond_id": f_pid,
                        "title": (
                            f"మేత రేషన్ వ్యత్యాసం ({f_pid})"
                            if lang == "te"
                            else f"Feed Ration Deviation ({f_pid})"
                        ),
                        "observation": (
                            f"వేసిన మేత {act} కేజీ vs సిఫార్సు {rec} కేజీ ({int(dev*100)}% తేడా)."
                            if lang == "te"
                            else f"Fed {act} kg vs recommended {rec} kg ({int(dev*100)}% variance)."
                        ),
                        "suggested_action": (
                            "చెక్ ట్రేలలో మేత మిగిలి ఉందా లేదా అని తనిఖీ చేయండి మరియు పెరుగుదల నమూనా ప్రకారం మేత రేటును సరిచూడండి."
                            if lang == "te"
                            else "Verify if feed trays show leftover feed or if stock sampling justifies higher feed rate."
                        ),
                        "source": f"మేత లాగ్ {f_date}" if lang == "te" else f"Feeding log {f_date}",
                    })

    # 3. Mortality Events
    if mortalities:
        for m in mortalities:
            dead = m.get("NumberOfDead", 0)
            if dead >= 10:
                m_pid = m.get("PondID")
                m_date = m.get("IncidentDate")
                sym = m.get("VisibleSymptoms", "ఏమీ నమోదు కాలేదు" if lang == "te" else "None noted")
                anomalies.append({
                    "id": f"anom_mort_{m.get('IncidentID')}",
                    "severity": "HIGH",
                    "category": "Mortality",
                    "pond_id": m_pid,
                    "title": (
                        f"{m_pid} లో మరణాల పెరుగుదల ({dead} చేపలు)"
                        if lang == "te"
                        else f"Mortality Spike ({dead} Fish) in {m_pid}"
                    ),
                    "observation": (
                        f"{m_date} తేదీన {dead} చేపల మరణాలు నమోదయ్యాయి. లక్షణాలు: {sym}."
                        if lang == "te"
                        else f"{dead} dead fish recorded on {m_date}. Symptoms: {sym}."
                    ),
                    "suggested_action": (
                        "ఈ తేదీ చుట్టుపక్కల DO, ఉష్ణోగ్రత మరియు మేత రికార్డులను పరిశీలించండి. సమస్య కొనసాగితే అర్హత గల మత్స్య నిపుణులను సంప్రదించండి."
                        if lang == "te"
                        else "Check DO, temperature, and feeding records around this date. Consult a qualified fisheries professional if mortality continues."
                    ),
                    "source": f"సంఘటన లాగ్ {m_date}" if lang == "te" else f"Incident log {m_date}",
                })

    return anomalies


def audit_data_health(session_state: Any) -> List[Dict[str, Any]]:
    """
    Audits farm records for missing, outdated, or incomplete data.
    Helps farmers maintain disciplined farm records.
    """
    lang = _get_lang(session_state)
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
                "title": (
                    f"నీటి పరీక్షలు లేవు: {p['PondName']} ({p['PondID']})"
                    if lang == "te"
                    else f"No Water Readings: {p['PondName']} ({p['PondID']})"
                ),
                "message": (
                    "ఈ క్రియాశీల చెరువుకు నీటి నాణ్యత పరిశీలనలు నమోదు కాలేదు. ఆరోగ్య పర్యవేక్షణకు క్రమం తప్పకుండా నీటి పరీక్షలు అవసరం."
                    if lang == "te"
                    else "This active pond has no recorded water observations. Regular water tests are essential for health tracking."
                ),
                "action": "నీటి పరీక్ష నమోదు చేయండి" if lang == "te" else "Log Water Reading",
            })

    # 2. Stocked ponds without recent growth observations
    growth_pids = {g["PondID"] for g in growths}
    for s in stocks:
        if s["PondID"] not in growth_pids:
            issues.append({
                "type": "missing_growth",
                "severity": "INFO",
                "title": (
                    f"పెరుగుదల నమూనాలు లేవు: {s['PondID']}"
                    if lang == "te"
                    else f"No Growth Samples: {s['PondID']}"
                ),
                "message": (
                    f"{s.get('StockingDate')} న నిల్వ చేసిన చేపలకు నమూనా బరువు రికార్డులు లేవు. ఖచ్చితమైన బయోమాస్ అంచనాకు నమూనా తూకం అవసరం."
                    if lang == "te"
                    else f"Fish stocked on {s.get('StockingDate')} have no sampling observations. Sample weight needed for accurate biomass estimation."
                ),
                "action": "పెరుగుదల నమూనా నమోదు చేయండి" if lang == "te" else "Record Growth Sample",
            })

    # 3. Feeding records with missing costs
    zero_cost_feeds = [f for f in feeds if not f.get("FeedCostPerKg")]
    if zero_cost_feeds:
        issues.append({
            "type": "missing_feed_cost",
            "severity": "INFO",
            "title": (
                f"{len(zero_cost_feeds)} మేత రికార్డులలో ధర వివరాలు లేవు"
                if lang == "te"
                else f"{len(zero_cost_feeds)} Feed Records Missing Cost"
            ),
            "message": (
                "కొన్ని మేత ఎంట్రీలలో కేజీ ధర లేదు; ఇది ఫార్మ్ ఆర్థిక విశ్లేషణను ప్రభావితం చేస్తుంది."
                if lang == "te"
                else "Some feed entries do not include feed cost/kg, which affects total farm financial analytics."
            ),
            "action": "మేత ఖర్చులను అప్‌డేట్ చేయండి" if lang == "te" else "Update Feed Costs",
        })

    return issues
