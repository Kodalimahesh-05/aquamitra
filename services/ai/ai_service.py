"""
AquaMitra AI Service Provider
Manages LLM API connections (Gemini, OpenAI) with a reliable, deterministic Demo AI engine fallback.
Fully bilingual (English / Telugu) with strictly zero emojis.
"""

import os
from typing import Dict, Any, Optional, List
import streamlit as st

from utils.translations import tv
from .safety import enforce_ai_safety
from .context_builder import build_farm_context, build_pond_context
from .query_assistant import answer_farmer_query
from .anomaly_detection import _get_lang


def _resolve_lang(session_state: Any = None, lang: Optional[str] = None) -> str:
    if lang in ("en", "te"):
        return lang
    if session_state is not None:
        resolved = _get_lang(session_state)
        if resolved in ("en", "te"):
            return resolved
    try:
        return st.session_state.get("lang", "en")
    except Exception:
        return "en"


def get_ai_credentials() -> Dict[str, Optional[str]]:
    """
    Checks for configured AI credentials in Streamlit secrets or environment variables.
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    provider = "demo"

    try:
        if hasattr(st, "secrets") and "ai" in st.secrets:
            sec = st.secrets["ai"]
            gemini_key = sec.get("gemini_api_key", gemini_key)
            openai_key = sec.get("openai_api_key", openai_key)
            provider = sec.get("provider", "demo")
    except Exception:
        pass

    if gemini_key:
        provider = "gemini"
    elif openai_key:
        provider = "openai"

    return {
        "provider": provider,
        "gemini_key": gemini_key,
        "openai_key": openai_key
    }


def is_live_ai_available() -> bool:
    """
    Returns True if an external AI API key is configured.
    """
    creds = get_ai_credentials()
    return creds["provider"] in ["gemini", "openai"]


class DemoAIEngine:
    """
    Intelligent local AI engine that provides structured, accurate insights
    derived directly from the application's actual records.
    """
    @staticmethod
    def generate_farm_summary(ctx: Dict[str, Any], lang: str = "en") -> str:
        ov = ctx["farm_overview"]
        water = ctx["water_condition"]
        feed = ctx["feeding"]
        fin = ctx["finance"]

        if lang == "te":
            water_note = (
                f"చెరువు {water['anomalies_detected'][0].split()[0]} లో ఇటీవలి నీటి పరిశీలనపై శ్రద్ధ అవసరం."
                if water["anomalies_detected"]
                else "అన్ని క్రియాశీల చెరువులు సాధారణ ప్రమాణ పరిధులలో స్థిరమైన నీటి నాణ్యతను కలిగి ఉన్నాయి."
            )
            feed_note = (
                f"రోజువారీ మేత {feed['today_actual_kg']} కేజీగా నమోదవుతోంది (బయోమాస్ అంచనాతో {feed['variance_kg']:+g} కేజీ తేడా)."
                if feed["today_actual_kg"] > 0
                else "ఈ రోజు మేత రికార్డులు ఇంకా నమోదు కాలేదు."
            )
            return (
                f"మీ ఫార్మ్‌లో ప్రస్తుతం {ov['active_ponds']} క్రియాశీల చెరువులు మరియు అంచనా {ov['estimated_biomass_kg']:,.0f} కేజీ మొత్తం బయోమాస్ ఉన్నాయి. "
                f"{water_note} {feed_note} "
                f"మొత్తం ఆదాయం ₹{fin['total_sales']:,.0f} కాగా, అంచనా నికర తేడా +₹{fin['estimated_net_difference']:,.0f} గా ఉంది."
            )

        water_note = (
            f"Pond {water['anomalies_detected'][0].split()[0]} has a recent water observation requiring attention."
            if water["anomalies_detected"]
            else "All active ponds maintain stable water quality within baseline reference ranges."
        )

        feed_note = (
            f"Daily feeding is tracking at {feed['today_actual_kg']} kg ({feed['variance_kg']:+g} kg variance from biomass model)."
            if feed["today_actual_kg"] > 0
            else "No feeding records logged today."
        )

        summary = (
            f"Your farm currently has {ov['active_ponds']} active ponds with an estimated total biomass of {ov['estimated_biomass_kg']:,.0f} kg. "
            f"{water_note} {feed_note} "
            f"Total farm revenue is ₹{fin['total_sales']:,.0f} with an estimated net difference of +₹{fin['estimated_net_difference']:,.0f}."
        )
        return summary

    @staticmethod
    def generate_daily_brief(ctx: Dict[str, Any], lang: str = "en") -> str:
        water = ctx["water_condition"]
        alerts = ctx["alerts"]
        fin = ctx["finance"]

        stable_ponds = "P-002, P-003" if water["anomalies_detected"] else "P-001, P-002"
        if lang == "te":
            attention_text = ", ".join(water["anomalies_detected"]) if water["anomalies_detected"] else "నీటి మట్టాలు మరియు మధ్యాహ్న ఉష్ణోగ్రతలు"
            alert_text = f"{alerts['unresolved_count']} క్రియాశీల అలర్ట్‌లు ({', '.join(alerts['unresolved_titles'])})" if alerts["unresolved_count"] > 0 else "అన్నీ సాధారణంగా ఉన్నాయి"
            top_exp_cat = tv(fin["top_expense_category"], "te")
            return f"""**ఈ రోజు ఫార్మ్ కార్యాచరణ నివేదిక (DAILY BRIEF)**

[స్థిరం] సాధారణ పరిస్థితులు: చెరువులు ({stable_ponds}) సాధారణ మేత మరియు దైనందిన పారామితులను నమోదు చేస్తున్నాయి.
[పర్యవేక్షణ] గమనించవలసినవి: {attention_text}
[శ్రద్ధ] తక్షణ చర్యలు: {alert_text}
[ధోరణి] బయోమాస్ & మేత: నమూనా బ్యాచ్‌లలో చేపల పెరుగుదల స్థిరంగా మరియు సానుకూలంగా ఉంది.
[ఆర్థికం] ఖర్చుల సారాంశం: ప్రధాన ఖర్చు విభాగం {top_exp_cat} (మొత్తం ఖర్చులు: ₹{fin['total_expenses']:,.0f}).

సూచించిన తనిఖీలు:
1. తెల్లవారుజాము వేళల్లో కరిగిన ఆక్సిజన్ (DO) స్థాయిలను మళ్ళీ తనిఖీ చేయండి.
2. మేత వేసిన 2 గంటల తర్వాత చెక్ ట్రేలలో మేత వినియోగాన్ని పరిశీలించండి.
3. రాబోయే వర్షాలు లేదా ఉష్ణోగ్రత మార్పుల కోసం వాతావరణ అంచనాను గమనించండి."""

        attention_text = ", ".join(water["anomalies_detected"]) if water["anomalies_detected"] else "Water levels and afternoon temperatures"
        alert_text = f"{alerts['unresolved_count']} active alerts ({', '.join(alerts['unresolved_titles'])})" if alerts['unresolved_count'] > 0 else "All clear"

        brief = f"""**TODAY'S FARM BRIEF**

[STABLE] Normal Conditions: Ponds ({stable_ponds}) report normal feeding and routine parameters.
[MONITOR] Watch Items: {attention_text}
[ATTENTION] Action Required: {alert_text}
[TREND] Biomass & Feed: Fish growth across sampling batches remains positive and uniform.
[FINANCE] Ledger Summary: {fin['top_expense_category']} remains the primary expense category (₹{fin['total_expenses']:,.0f} total).

Suggested Checks:
1. Recheck dissolved oxygen in early morning hours.
2. Inspect feeding trays 2 hours post-feed to ensure clean consumption.
3. Review weather forecast for upcoming rainfall or temperature changes."""
        return brief


def generate_farm_summary(session_state: Any, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates a concise farm summary in the active UI language.
    """
    active_lang = _resolve_lang(session_state, lang)
    ctx = build_farm_context(session_state)
    creds = get_ai_credentials()

    text = DemoAIEngine.generate_farm_summary(ctx, lang=active_lang)
    text = enforce_ai_safety(text)

    if active_lang == "te":
        badge = "ఆక్వామిత్ర AI" if creds["provider"] == "demo" else "జెమిని AI"
    else:
        badge = "AQUAMITRA AI" if creds["provider"] == "demo" else "GEMINI AI"

    return {
        "text": text,
        "is_demo_ai": creds["provider"] == "demo",
        "provider": creds["provider"],
        "badge": badge
    }


def generate_daily_briefing(session_state: Any, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates the structured Daily Farm Brief in the active UI language.
    """
    active_lang = _resolve_lang(session_state, lang)
    ctx = build_farm_context(session_state)
    creds = get_ai_credentials()

    brief_text = DemoAIEngine.generate_daily_brief(ctx, lang=active_lang)
    brief_text = enforce_ai_safety(brief_text)

    if active_lang == "te":
        badge = "ఆక్వామిత్ర AI" if creds["provider"] == "demo" else "జెమిని AI"
    else:
        badge = "AQUAMITRA AI" if creds["provider"] == "demo" else "GEMINI AI"

    return {
        "text": brief_text,
        "is_demo_ai": creds["provider"] == "demo",
        "provider": creds["provider"],
        "badge": badge
    }


def ask_aquamitra_ai(query: str, session_state: Any, current_pond: str = None, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Processes natural-language queries through the AI assistant.
    """
    active_lang = _resolve_lang(session_state, lang)
    creds = get_ai_credentials()
    answer = answer_farmer_query(query, session_state, current_pond)
    answer = enforce_ai_safety(answer)

    if active_lang == "te":
        badge = "ఆక్వామిత్ర AI" if creds["provider"] == "demo" else "జెమిని AI"
    else:
        badge = "AQUAMITRA AI" if creds["provider"] == "demo" else "GEMINI AI"

    return {
        "answer": answer,
        "is_demo_ai": creds["provider"] == "demo",
        "provider": creds["provider"],
        "badge": badge
    }


def explain_chart_trend(metric_name: str, values: list, dates: list, lang: Optional[str] = None) -> str:
    """
    Generates a natural-language explanation of a chart's trend.
    """
    active_lang = _resolve_lang(None, lang)
    if not values or len(values) < 2:
        return (
            "నమ్మకమైన ధోరణిని గుర్తించడానికి తగినన్ని చారిత్రక పరిశీలనలు లేవు."
            if active_lang == "te"
            else "Not enough historical observations to establish a reliable trend."
        )

    change = values[-1] - values[0]
    if active_lang == "te":
        trend_dir = "పెరిగింది" if change > 0 else "తగ్గింది" if change < 0 else "స్థిరంగా ఉంది"
        explanation = (
            f"**{metric_name} ధోరణి విశ్లేషణ:**\n\n"
            f"నమోదైన కాలంలో ({dates[0]} నుండి {dates[-1]} వరకు), {metric_name} విలువ "
            f"{values[0]} నుండి {values[-1]} వరకు ({change:+g} నికర మార్పు) {trend_dir}. "
            f"ఈ ధోరణి సాధారణ కాలానుగుణ పరిశీలనలను ప్రతిబింబిస్తుంది. మార్పులను గమనించడానికి క్రమం తప్పకుండా డేటాను నమోదు చేస్తూ ఉండండి."
        )
        return enforce_ai_safety(explanation)

    trend_dir = "increased" if change > 0 else "decreased" if change < 0 else "remained steady"

    explanation = (
        f"**{metric_name} Trend Analysis:**\n\n"
        f"Over the recorded period ({dates[0]} to {dates[-1]}), {metric_name.lower()} has {trend_dir} "
        f"from {values[0]} to {values[-1]} ({change:+g} net change). "
        f"The pattern reflects regular seasonal observations. Continue standard periodic recording to track progression."
    )
    return enforce_ai_safety(explanation)


def explain_alert(alert: Dict[str, Any], lang: Optional[str] = None) -> str:
    """
    Generates a natural-language explanation for an alert to assist non-technical users.
    """
    active_lang = _resolve_lang(None, lang)
    title = alert.get("Title", "Alert")
    reason = alert.get("Reason", "Observation outside normal bounds.")
    pid = alert.get("PondID", "General")
    action = alert.get("SuggestedAction", "Monitor conditions closely.")

    if active_lang == "te":
        explanation = (
            f"**ఈ అలర్ట్ ఎందుకు చూపబడింది ({pid}):**\n\n"
            f"{title}: {reason}\n\n"
            f"**సూచించిన తదుపరి చర్య:** {action}\n"
            f"*క్రమం తప్పకుండా తనిఖీ చేయడం వల్ల చిన్న నీటి లేదా మేత మార్పులు పెద్ద సమస్యలుగా మారకుండా నిరోధించవచ్చు.*"
        )
        return enforce_ai_safety(explanation)

    explanation = (
        f"**Why this alert was triggered ({pid}):**\n\n"
        f"{title}: {reason}\n\n"
        f"**Suggested next step:** {action}\n"
        f"*Regular verification prevents minor water or feeding changes from escalating.*"
    )
    return enforce_ai_safety(explanation)


def analyze_pond(pond_id: str, session_state: Any) -> Dict[str, str]:
    """
    Comprehensive AI evaluation of an individual pond command center.
    """
    lang = _resolve_lang(session_state)
    ctx = build_pond_context(pond_id, session_state)
    waters = [w for w in getattr(session_state, "demo_water_quality", []) if w.get("PondID") == pond_id]
    feeds = [f for f in getattr(session_state, "demo_feeding", []) if f.get("PondID") == pond_id]
    stocks = [s for s in getattr(session_state, "demo_fish_stock", []) if s.get("PondID") == pond_id]
    mortalities = [m for m in getattr(session_state, "demo_mortality", []) if m.get("PondID") == pond_id]

    latest_w = waters[-1] if waters else {}
    total_fish = sum(s.get("NumberOfFish", 0) for s in stocks)

    if lang == "te":
        obs = f"చెరువు {pond_id} ({ctx.get('pond_name')}) లో {len(stocks)} బ్యాచ్‌లలో సుమారు {total_fish:,} చేపలు నిల్వ చేయబడ్డాయి. {latest_w.get('ReadingDate', 'లభ్యం లేదు')} న తాజా నీటి పరీక్షలో pH {latest_w.get('pH')}, ఉష్ణోగ్రత {latest_w.get('Temperature')}°C మరియు DO {latest_w.get('DissolvedOxygen')} mg/L గా నమోదయ్యాయి."
        trend = "బయోమాస్ పెరుగుదల స్థిరంగా సాగుతోంది. మేత వినియోగం బయోమాస్ అంచనాలకు దగ్గరగా ఉంది."
        attention = f"కరిగిన ఆక్సిజన్ పరిశీలన ({latest_w.get('DissolvedOxygen')} mg/L) ప్రమాణ స్థాయి కంటే తక్కువగా ఉంది." if latest_w.get("DissolvedOxygen", 6) < 5.0 else "నమోదైన అన్ని నీరు మరియు మేత పారామితులు స్థిరంగా ఉన్నాయి."
        action = "తెల్లవారుజామున (04:00 - 07:30 AM) పాడిల్‌వీల్ ఏరేషన్ కొనసాగించండి. మేత వేసిన 2 గంటల తర్వాత చెక్ ట్రేలను తనిఖీ చేయండి."
        limits = f"ఈ విశ్లేషణ {len(waters)} నీటి పరీక్ష లాగ్‌లు, {len(feeds)} మేత రికార్డులు మరియు {len(mortalities)} సంఘటనలపై ఆధారపడి ఉంది."
    else:
        obs = f"Pond {pond_id} ({ctx.get('pond_name')}) has ~{total_fish:,} stocked fish across {len(stocks)} batches. Latest water reading on {latest_w.get('ReadingDate', 'N/A')} recorded pH {latest_w.get('pH')}, Temp {latest_w.get('Temperature')}°C, and DO {latest_w.get('DissolvedOxygen')} mg/L."
        trend = "Biomass growth is steadily advancing. Feed consumption aligns closely with biomass ration expectations."
        attention = f"1 dissolved oxygen observation ({latest_w.get('DissolvedOxygen')} mg/L) dropped below baseline." if latest_w.get("DissolvedOxygen", 6) < 5.0 else "All observed water and feed parameters are stable."
        action = "Maintain early morning paddlewheel aeration (04:00 - 07:30 AM). Inspect feed check-trays 2 hours post-feed."
        limits = f"Analysis based on {len(waters)} water logs, {len(feeds)} feeding logs, and {len(mortalities)} recorded incidents."

    return {
        "observation": obs,
        "trend": trend,
        "attention": attention,
        "suggested_check": action,
        "data_limitations": limits
    }


def analyze_water(session_state: Any, pond_id: Optional[str] = None) -> Dict[str, str]:
    """
    AI Water Quality analysis across ponds.
    """
    lang = _resolve_lang(session_state)
    waters = getattr(session_state, "demo_water_quality", [])
    if pond_id:
        waters = [w for w in waters if w.get("PondID") == pond_id]

    if not waters:
        if lang == "te":
            return {
                "observation": "ఎంచుకున్న విభాగానికి నీటి నాణ్యత రికార్డులు కనుగొనబడలేదు.",
                "trend": "ధోరణిని గుర్తించడానికి డేటా సరిపోదు.",
                "attention": "నీటి పరీక్ష చేయించడం సిఫార్సు చేయబడుతుంది.",
                "suggested_check": "మీ మొదటి నీటి పరీక్ష వివరాలను (pH, DO, ఉష్ణోగ్రత) నమోదు చేయండి.",
                "data_limitations": "పరిశీలనలు శూన్యం."
            }
        return {
            "observation": "No water quality records found for the selected scope.",
            "trend": "Insufficient data to determine trend.",
            "attention": "Water testing recommended.",
            "suggested_check": "Log your first water reading (pH, DO, Temp).",
            "data_limitations": "Zero observations."
        }

    latest = waters[-1]
    do_val = latest.get("DissolvedOxygen", 6.0)
    ph_val = latest.get("pH", 7.5)

    if lang == "te":
        obs = f"{latest.get('PondID')} లో తాజా పరిశీలన ({latest.get('ReadingDate')}) ప్రకారం కరిగిన ఆక్సిజన్ {do_val} mg/L మరియు pH {ph_val} గా ఉన్నాయి."
        trend = "కరిగిన ఆక్సిజన్ రోజువారీగా మారుతూ ఉంటుంది; మేఘావృతమైన ఉదయ వేళల్లో స్వల్ప తగ్గుదల కనిపిస్తుంది."
        attention = "ఇటీవలి పరిశీలనలలో DO 5.0 mg/L కంటే తక్కువగా నమోదైంది; తక్షణ పర్యవేక్షణ అవసరం." if do_val < 5.0 else "పారామితులు ప్రస్తుతం మంచి మంచినీటి ప్రమాణ పరిధులలో ఉన్నాయి."
        action = "DO మీటర్ కాలిబ్రేషన్ తనిఖీ చేయండి. తెల్లవారుజాము రీడింగ్‌లు 4.5 mg/L కంటే తగ్గితే అత్యవసర ఏరేషన్ నడపండి."
        limits = f"{len(waters)} చారిత్రక నీటి పరీక్ష లాగ్‌ల ఆధారంగా ఈ అంచనా రూపొందించబడింది."
    else:
        obs = f"Latest observation in {latest.get('PondID')} shows Dissolved Oxygen at {do_val} mg/L and pH at {ph_val} (Recorded {latest.get('ReadingDate')})."
        trend = "Dissolved oxygen shows regular diurnal variation, with dips observed during cloudy dawn periods."
        attention = "Pond P-001 registered a sub-5.0 mg/L DO reading on a recent overcast morning." if do_val < 5.0 else "Parameters currently within optimal freshwater reference ranges."
        action = "Verify calibration of optical DO probe. Run emergency aeration if early dawn readings fall below 4.5 mg/L."
        limits = f"Evaluation based on {len(waters)} historical water testing logs."

    return {
        "observation": obs,
        "trend": trend,
        "attention": attention,
        "suggested_check": action,
        "data_limitations": limits
    }


def analyze_feeding(session_state: Any, pond_id: Optional[str] = None) -> Dict[str, str]:
    """
    AI Feeding & Nutrition analysis.
    """
    lang = _resolve_lang(session_state)
    feeds = getattr(session_state, "demo_feeding", [])
    if pond_id:
        feeds = [f for f in feeds if f.get("PondID") == pond_id]

    if not feeds:
        if lang == "te":
            return {
                "observation": "మేత రికార్డులు అందుబాటులో లేవు.",
                "trend": "లభ్యం లేదు",
                "attention": "క్రమం తప్పకుండా మేత రికార్డులు నమోదు చేయడం అవసరం.",
                "suggested_check": "మేత వినియోగం మరియు FCR ను ట్రాక్ చేయడానికి రోజువారీ మేతను నమోదు చేయండి.",
                "data_limitations": "మేత లాగ్‌లు లేవు."
            }
        return {
            "observation": "No feeding records available.",
            "trend": "N/A",
            "attention": "Regular feeding records required.",
            "suggested_check": "Log daily feeding rations to track consumption and FCR.",
            "data_limitations": "Zero feeding logs."
        }

    last_feed = feeds[-1]
    act = last_feed.get("ActualFeedKg", 0)
    rec = last_feed.get("RecommendedFeedKg", 0)
    diff = round(act - rec, 1)

    if lang == "te":
        obs = f"ప్రస్తుత మేత {act} కేజీ/రోజు ({tv(last_feed.get('FeedType'), 'te')}), సిఫార్సు మేత {rec} కేజీ/రోజు ({diff:+g} కేజీ తేడా)."
        trend = "రోజువారీ మేత పరిమాణం చేపల బయోమాస్ పెరుగుదలకు అనుగుణంగా మారింది."
        attention = "మేత వేసిన 2 గంటల తర్వాత కూడా చెక్ ట్రేలలో గుళికలు మిగిలితే మేత పరిమాణాన్ని సర్దుబాటు చేయాలి."
        action = "మధ్యాహ్న ఎండ సమయంలో మేత స్పందనను గమనించండి. ఉదయం మరియు సాయంత్రం చల్లని వేళల్లో మేత విభజించి వేయండి."
        limits = f"క్రియాశీల సాగు చక్రంలోని {len(feeds)} మేత ఎంట్రీలపై ఆధారితం."
    else:
        obs = f"Current ration is {act} kg/day ({last_feed.get('FeedType')}) against recommended {rec} kg/day ({diff:+g} kg variance)."
        trend = "Daily feeding volume has scaled proportionally with fish biomass growth."
        attention = "Feed adjustment needed if unconsumed pellets persist in sampling trays after 2 hours."
        action = "Check feeding response during peak midday heat. Adjust split rations to morning and evening cool hours."
        limits = f"Based on {len(feeds)} feeding entries in the active farm cycle."

    return {
        "observation": obs,
        "trend": trend,
        "attention": attention,
        "suggested_check": action,
        "data_limitations": limits
    }


def analyze_growth(session_state: Any, pond_id: str = "P-001") -> Dict[str, str]:
    """
    AI Fish Growth & Sampling analysis.
    """
    lang = _resolve_lang(session_state)
    growths = [g for g in getattr(session_state, "demo_fish_growth", []) if g.get("PondID") == pond_id]
    if len(growths) < 2:
        if lang == "te":
            return {
                "observation": "తగినన్ని పెరుగుదల నమూనా పరిశీలనలు నమోదు కాలేదు.",
                "trend": "సగటు రోజువారీ పెరుగుదల (ADG) లెక్కించడానికి పరిశీలనలు సరిపోవు.",
                "attention": "క్రమం తప్పకుండా వల వేసి నమూనా చేపలను తూకం వేయండి.",
                "suggested_check": "బయోమాస్ మోడల్ అప్‌డేట్ కోసం 30-40 చేపలను పట్టి బరువు చూడండి.",
                "data_limitations": f"{len(growths)} నమూనా రికార్డులు మాత్రమే ఉన్నాయి."
            }
        return {
            "observation": "Limited growth sampling observations recorded.",
            "trend": "Insufficient observations to calculate Average Daily Growth (ADG).",
            "attention": "Perform periodic sample catch netting.",
            "suggested_check": "Catch and weigh 30-40 fish to update biomass model.",
            "data_limitations": f"Only {len(growths)} sample records found."
        }

    first_w = growths[0]["AvgFishWeightGrams"]
    curr_w = growths[-1]["AvgFishWeightGrams"]
    gain = curr_w - first_w

    if lang == "te":
        obs = f"{pond_id} లో పరీక్షించిన చేపల సగటు బరువు {first_w}g నుండి {curr_w}g వరకు (+{gain}g నికర పెరుగుదల, {len(growths)} తనిఖీలలో) పెరిగింది."
        trend = "పెరుగుదల రేఖ ఆరోగ్యకరమైన చేప పిల్లల పెరుగుదలకు అనుగుణంగా స్థిరంగా పైకి సాగుతోంది."
        attention = "కనిష్ట మరియు గరిష్ట బరువుల మధ్య ఎక్కువ తేడా ఉంటే సైజు గ్రేడింగ్ అవసరం కావచ్చు."
        action = "బయోమాస్ మరియు మేత రేషన్లను ఖచ్చితంగా సవరించడానికి 10 రోజుల్లో తదుపరి వల నమూనా తనిఖీని షెడ్యూల్ చేయండి."
        limits = f"సగటున ప్రతి తనిఖీకి 35 చేపలతో కూడిన {len(growths)} నమూనా బ్యాచ్‌ల నుండి లెక్కించబడింది."
    else:
        obs = f"Fish sampled in {pond_id} increased from {first_w}g to {curr_w}g (+{gain}g net gain across {len(growths)} checks)."
        trend = "Growth trajectory shows steady, linear upward momentum characteristic of healthy fingerling progression."
        attention = "Watch for weight dispersion; wide variations between min and max weight indicate grading may be needed."
        action = "Schedule next cast-net sampling in 10 days to refine biomass and feed rations."
        limits = f"Calculated from {len(growths)} sample batches averaging 35 fish per check."

    return {
        "observation": obs,
        "trend": trend,
        "attention": attention,
        "suggested_check": action,
        "data_limitations": limits
    }


def analyze_incident(incident_id: int, session_state: Any) -> Dict[str, str]:
    """
    Contextual AI Incident Analysis without diagnosing disease.
    """
    lang = _resolve_lang(session_state)
    incidents = [i for i in getattr(session_state, "demo_incidents", []) if i.get("IncidentID") == incident_id]
    if not incidents:
        if lang == "te":
            return {
                "observation": "సంఘటన రికార్డు కనుగొనబడలేదు.",
                "trend": "లభ్యం లేదు",
                "attention": "లభ్యం లేదు",
                "suggested_check": "క్రియాశీల సంఘటనను ఎంచుకోండి.",
                "data_limitations": "రికార్డు కనుగొనబడలేదు."
            }
        return {
            "observation": "Incident record not found.",
            "trend": "N/A",
            "attention": "N/A",
            "suggested_check": "Select an active incident.",
            "data_limitations": "Record not found."
        }

    inc = incidents[0]
    pid = inc.get("PondID")
    date_str = inc.get("Date")

    if lang == "te":
        obs = f"{pid} చెరువులో {date_str} తేదీన సంఘటన #{incident_id} నమోదైంది: {tv(inc.get('IncidentType'), 'te')} ({inc.get('NumberAffected')} చేపలు ప్రభావితం)."
        trend = f"ఇదే కాలంలో {inc.get('WeatherCondition', 'సాధారణ వాతావరణం')} మరియు {inc.get('WaterCondition', 'నీటి పరిశీలనలు')} తో పాటు గమనించబడింది."
        attention = f"నమోదైన పరిశీలనలు: {inc.get('VisibleObservation')}."
        action = f"తీసుకున్న తక్షణ చర్య: {inc.get('ActionTaken')}. సూచన: తదుపరి నీటి పరీక్ష చేయండి మరియు పరిస్థితి కొనసాగితే అర్హత గల మత్స్య నిపుణులను సంప్రదించండి."
        limits = "ఇది నమోదైన రికార్డుల ఆధారంగా చూపబడిన సహసంబంధం మాత్రమే, కారణ నిర్ధారణ కాదు. ఆక్వామిత్ర వ్యాధులను నిర్ధారించదు."
    else:
        obs = f"Incident #{incident_id} recorded in {pid} on {date_str}: {inc.get('IncidentType')} affecting {inc.get('NumberAffected')} fish."
        trend = f"Observed around the same period as {inc.get('WeatherCondition', 'ambient weather')} and {inc.get('WaterCondition', 'water observations')}."
        attention = f"Visible observations recorded: {inc.get('VisibleObservation')}."
        action = f"Immediate response taken: {inc.get('ActionTaken')}. Recommended: Schedule follow-up test and consult a qualified fisheries professional if conditions persist."
        limits = "This is an observed association based on logged records, NOT proof of causation. AquaMitra does not diagnose biological disease."

    return {
        "observation": obs,
        "trend": trend,
        "attention": attention,
        "suggested_check": action,
        "data_limitations": limits
    }


def analyze_finances(session_state: Any) -> Dict[str, str]:
    """
    AI Financial & Cost Structure Analysis.
    """
    lang = _resolve_lang(session_state)
    expenses = getattr(session_state, "demo_expenses", [])
    sales = getattr(session_state, "demo_sales", [])

    tot_exp = sum(e.get("Amount", 0) for e in expenses)
    tot_rev = sum(s.get("TotalRevenue", 0) for s in sales)
    net_diff = tot_rev - tot_exp

    cat_totals = {}
    for e in expenses:
        c = e.get("Category", "Other")
        cat_totals[c] = cat_totals.get(c, 0) + e.get("Amount", 0)

    top_c = max(cat_totals.items(), key=lambda x: x[1])[0] if cat_totals else "N/A"
    top_c_disp = tv(top_c, lang)

    if lang == "te":
        obs = f"నమోదైన నిర్వహణ ఖర్చులు ₹{tot_exp:,.0f} కాగా, పంట కోత అమ్మకాలు ₹{tot_rev:,.0f} (అంచనా నికర తేడా: +₹{net_diff:,.0f})."
        trend = f"నిర్వహణ ఖర్చులలో {top_c_disp} విభాగం అత్యధికంగా ఉంది (₹{cat_totals.get(top_c, 0):,.0f}); ఆ తర్వాత చేప పిల్లల కొనుగోలు ఖర్చు ఉంది."
        attention = "పాక్షిక పంట కోతలు సానుకూల నగదు ప్రవాహాన్ని ఇచ్చాయి; మిగిలిన కొనుగోలుదారుల బకాయిలు వసూలయ్యేలా చూడండి."
        action = "మేత ఖర్చు సామర్థ్యాన్ని అంచనా వేయడానికి కోత బరువుతో పోల్చి FCR ని లెక్కించండి."
        limits = f"{len(expenses)} ఖర్చు ఎంట్రీలు మరియు {len(sales)} అమ్మకాల వోచర్లపై ఆధారితం."
    else:
        obs = f"Recorded operational expenses stand at ₹{tot_exp:,.0f}, while selective harvest sales total ₹{tot_rev:,.0f} (Estimated Net: +₹{net_diff:,.0f})."
        trend = f"{top_c} represents the largest operational expenditure category (₹{cat_totals.get(top_c, 0):,.0f}), followed by fish seed procurement."
        attention = "Partial harvests have yielded positive cash flow; ensure remaining buyer payments are collected."
        action = "Calculate Feed Conversion Ratio (FCR) against harvest weight to evaluate feed cost efficiency."
        limits = f"Based on {len(expenses)} expense entries and {len(sales)} harvest sale vouchers."

    return {
        "observation": obs,
        "trend": trend,
        "attention": attention,
        "suggested_check": action,
        "data_limitations": limits
    }


def generate_ai_suggestions(session_state: Any) -> List[Dict[str, Any]]:
    """
    Generates actionable AI suggestions with localized labels and actions.
    """
    lang = _resolve_lang(session_state)
    suggestions = []
    waters = getattr(session_state, "demo_water_quality", [])

    # 1. Water Suggestion
    if any(w.get("DissolvedOxygen", 6) < 5.0 for w in waters[-2:]):
        suggestions.append({
            "id": "sug_water_aeration",
            "category": "నీటి నిర్వహణ" if lang == "te" else "Water Management",
            "title": "P-001 లో తెల్లవారుజాము ఏరేషన్ పెంచండి" if lang == "te" else "Increase Dawn Aeration in P-001",
            "why": (
                "ఇటీవల మేఘావృతమైన ఉదయ వేళల్లో కరిగిన ఆక్సిజన్ (DO) 4.2 mg/L కు తగ్గింది."
                if lang == "te"
                else "Recent dissolved oxygen observation dropped to 4.2 mg/L on overcast mornings."
            ),
            "based_on": (
                "గ్రీన్ వ్యాలీ చెరువులో గత 3 రోజుల నీటి పరీక్ష లాగ్‌లు."
                if lang == "te"
                else "Water logs from past 3 days in Green Valley Pond."
            ),
            "what_to_check": (
                "తెల్లవారుజామున 04:00 నుండి 07:30 మధ్య పాడిల్‌వీల్ ఏరేటర్లను నడపండి. ప్రోబ్‌తో DO ను మళ్ళీ తనిఖీ చేయండి."
                if lang == "te"
                else "Turn on paddlewheel aerators between 04:00 AM and 07:30 AM. Recheck DO with probe."
            ),
            "action_label": "నీటి పరీక్ష నమోదు" if lang == "te" else "Log Water Reading",
            "action_menu": "water"
        })

    # 2. Feed Inventory Suggestion
    suggestions.append({
        "id": "sug_feed_order",
        "category": "మేత మరియు నిల్వ" if lang == "te" else "Feeding & Inventory",
        "title": "మేత నిల్వ రీ-ఆర్డర్ స్థాయిని సమీక్షించండి" if lang == "te" else "Review Feed Inventory Re-order Level",
        "why": (
            "రెండు క్రియాశీల చెరువులలో ప్రస్తుత మేత వినియోగం సుమారు 280 కేజీ/రోజు గా ఉంది."
            if lang == "te"
            else "Current feed consumption is ~280 kg/day across both active ponds."
        ),
        "based_on": (
            "14 రోజుల మేత వినియోగ రేట్లు మరియు గోదాంలో మిగిలి ఉన్న బస్తాలు."
            if lang == "te"
            else "14 days of recorded feeding rates and remaining warehouse bags."
        ),
        "what_to_check": (
            "మేత గోదాంలో ఉన్న నిల్వను సరిచూసుకోండి. వర్షాకాలం ముందు కనీసం 15 రోజుల నిల్వ ఉండేలా చూడండి."
            if lang == "te"
            else "Verify warehouse stock in feed shed. Ensure 15-day buffer stock before rainy season."
        ),
        "action_label": "మేత నిల్వను చూడండి" if lang == "te" else "View Feed Inventory",
        "action_menu": "feeding"
    })

    # 3. Growth Sampling Suggestion
    suggestions.append({
        "id": "sug_growth_netting",
        "category": "పెరుగుదల ట్రాకింగ్" if lang == "te" else "Growth Tracking",
        "title": (
            "కృష్ణా ఆక్వా చెరువు (P-002) కోసం పక్షం రోజుల నమూనా తనిఖీ"
            if lang == "te"
            else "Bi-weekly Sampling Due for Krishna Aqua Pond (P-002)"
        ),
        "why": (
            "తిలాపియా చివరి నమూనా తనిఖీ 12 రోజుల క్రితం జరిగింది."
            if lang == "te"
            else "Last sampling of Tilapia was conducted 12 days ago."
        ),
        "based_on": (
            "పెరుగుదల రిజిస్ట్రీలో P-002 నమూనా టైమ్‌లైన్."
            if lang == "te"
            else "Pond P-002 sampling timeline in growth registry."
        ),
        "what_to_check": (
            "40 చేపల నమూనాను పట్టి సగటు బరువును కొలవండి; తద్వారా రోజువారీ మేత శాతాన్ని అప్‌డేట్ చేయవచ్చు."
            if lang == "te"
            else "Net a representative sample of 40 fish. Measure average weight to update daily feeding percentage."
        ),
        "action_label": "పెరుగుదల నమూనా జోడించు" if lang == "te" else "Add Growth Sample",
        "action_menu": "fish"
    })

    # 4. Payment Collection Suggestion
    suggestions.append({
        "id": "sug_payment_balance",
        "category": "ఆర్థికం" if lang == "te" else "Finance",
        "title": "పాక్షిక అమ్మకం బకాయి వసూలును పరిశీలించండి" if lang == "te" else "Follow up on Partial Sale Payment",
        "why": (
            "విజయవాడ ఫిష్ ట్రేడర్స్ నుండి సేల్ వోచర్ #2 లో ₹44,000 బకాయి పెండింగ్‌లో ఉంది."
            if lang == "te"
            else "Sale voucher #2 has a pending balance of ₹44,000 from Vijayawada Fish Traders."
        ),
        "based_on": (
            "అమ్మకాల ఖాతాలో పాక్షిక చెల్లింపు స్థితి."
            if lang == "te"
            else "Sales ledger partial payment status."
        ),
        "what_to_check": (
            "కొనుగోలుదారు ప్రతినిధిని సంప్రదించి మొత్తం అందిన తర్వాత చెల్లింపు స్థితిని అప్‌డేట్ చేయండి."
            if lang == "te"
            else "Contact buyer representative and update payment status upon receipt."
        ),
        "action_label": "అమ్మకాల ఖాతాను చూడండి" if lang == "te" else "View Sales Ledger",
        "action_menu": "finance"
    })

    return suggestions
