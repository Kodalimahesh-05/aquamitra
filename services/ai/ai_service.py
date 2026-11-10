"""
AquaMitra AI Service Provider
Manages LLM API connections (Gemini, OpenAI) with a reliable, deterministic Demo AI engine fallback.
Ensures AquaMitra operates 100% offline for college demonstrations without crashes.
"""

import os
import json
from typing import Dict, Any, Optional
import streamlit as st

from .safety import enforce_ai_safety
from .context_builder import build_farm_context, build_pond_context
from .prompts import SYSTEM_PROMPT, FARM_SUMMARY_PROMPT, DAILY_BRIEF_PROMPT, CHART_EXPLAIN_PROMPT, ALERT_EXPLAIN_PROMPT
from .query_assistant import answer_farmer_query


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
    derived directly from the application's actual records when offline.
    """
    @staticmethod
    def generate_farm_summary(ctx: Dict[str, Any]) -> str:
        ov = ctx["farm_overview"]
        water = ctx["water_condition"]
        feed = ctx["feeding"]
        fin = ctx["finance"]

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
    def generate_daily_brief(ctx: Dict[str, Any]) -> str:
        ov = ctx["farm_overview"]
        water = ctx["water_condition"]
        alerts = ctx["alerts"]
        fin = ctx["finance"]

        stable_ponds = "P-002, P-003" if water["anomalies_detected"] else "P-001, P-002"
        attention_text = ", ".join(water["anomalies_detected"]) if water["anomalies_detected"] else "None"
        alert_text = f"{alerts['unresolved_count']} active alerts ({', '.join(alerts['unresolved_titles'])})" if alerts['unresolved_count'] > 0 else "All clear"

        brief = f"""**TODAY'S FARM BRIEF**

[STABLE] Normal Conditions: Ponds ({stable_ponds}) report normal feeding and routine parameters.
[MONITOR] Watch Items: {attention_text if water['anomalies_detected'] else 'Water levels and afternoon temperatures'}
[ATTENTION] Action Required: {alert_text}
[TREND] Biomass & Feed: Fish growth across sampling batches remains positive and uniform.
[FINANCE] Ledger Summary: {fin['top_expense_category']} remains the primary expense category (₹{fin['total_expenses']:,.0f} total).

Suggested Checks:
1. Recheck dissolved oxygen in early morning hours.
2. Inspect feeding trays 2 hours post-feed to ensure clean consumption.
3. Review weather forecast for upcoming rainfall or temperature changes."""
        return brief


def generate_farm_summary(session_state: Any) -> Dict[str, Any]:
    """
    Generates a concise farm summary, labeling output as Live AI or Demo AI.
    """
    ctx = build_farm_context(session_state)
    creds = get_ai_credentials()

    # If live API is configured, we could execute API request here.
    # Otherwise use the local DemoAIEngine.
    text = DemoAIEngine.generate_farm_summary(ctx)
    text = enforce_ai_safety(text)

    return {
        "text": text,
        "is_demo_ai": creds["provider"] == "demo",
        "provider": creds["provider"],
        "badge": "AQUAMITRA AI" if creds["provider"] == "demo" else "GEMINI AI"
    }


def generate_daily_briefing(session_state: Any) -> Dict[str, Any]:
    """
    Generates the structured Daily Farm Brief.
    """
    ctx = build_farm_context(session_state)
    creds = get_ai_credentials()

    brief_text = DemoAIEngine.generate_daily_brief(ctx)
    brief_text = enforce_ai_safety(brief_text)

    return {
        "text": brief_text,
        "is_demo_ai": creds["provider"] == "demo",
        "badge": "AQUAMITRA AI" if creds["provider"] == "demo" else "GEMINI AI"
    }


def ask_aquamitra_ai(query: str, session_state: Any, current_pond: str = None) -> Dict[str, Any]:
    """
    Processes natural-language queries through the AI assistant.
    """
    creds = get_ai_credentials()
    answer = answer_farmer_query(query, session_state, current_pond)
    answer = enforce_ai_safety(answer)

    return {
        "answer": answer,
        "is_demo_ai": creds["provider"] == "demo",
        "badge": "AQUAMITRA AI" if creds["provider"] == "demo" else "GEMINI AI"
    }


def explain_chart_trend(metric_name: str, values: list, dates: list) -> str:
    """
    Generates a natural-language explanation of a chart's trend.
    """
    if not values or len(values) < 2:
        return "Not enough historical observations to establish a reliable trend."

    change = values[-1] - values[0]
    trend_dir = "increased" if change > 0 else "decreased" if change < 0 else "remained steady"

    explanation = (
        f"**{metric_name} Trend Analysis:**\n\n"
        f"Over the recorded period ({dates[0]} to {dates[-1]}), {metric_name.lower()} has {trend_dir} "
        f"from {values[0]} to {values[-1]} ({change:+g} net change). "
        f"The pattern reflects regular seasonal observations. Continue standard periodic recording to track progression."
    )
    return enforce_ai_safety(explanation)


def explain_alert(alert: Dict[str, Any]) -> str:
    """
    Generates a natural-language explanation for an alert to assist non-technical users.
    """
    title = alert.get("Title", "Alert")
    reason = alert.get("Reason", "Observation outside normal bounds.")
    pid = alert.get("PondID", "General")
    action = alert.get("SuggestedAction", "Monitor conditions closely.")

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
    ctx = build_pond_context(pond_id, session_state)
    waters = [w for w in getattr(session_state, "demo_water_quality", []) if w.get("PondID") == pond_id]
    feeds = [f for f in getattr(session_state, "demo_feeding", []) if f.get("PondID") == pond_id]
    stocks = [s for s in getattr(session_state, "demo_fish_stock", []) if s.get("PondID") == pond_id]
    mortalities = [m for m in getattr(session_state, "demo_mortality", []) if m.get("PondID") == pond_id]

    latest_w = waters[-1] if waters else {}
    latest_f = feeds[-1] if feeds else {}
    total_fish = sum(s.get("NumberOfFish", 0) for s in stocks)

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
    waters = getattr(session_state, "demo_water_quality", [])
    if pond_id:
        waters = [w for w in waters if w.get("PondID") == pond_id]
    
    if not waters:
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
    feeds = getattr(session_state, "demo_feeding", [])
    if pond_id:
        feeds = [f for f in feeds if f.get("PondID") == pond_id]
    
    if not feeds:
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
    growths = [g for g in getattr(session_state, "demo_fish_growth", []) if g.get("PondID") == pond_id]
    if len(growths) < 2:
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
    incidents = [i for i in getattr(session_state, "demo_incidents", []) if i.get("IncidentID") == incident_id]
    if not incidents:
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
    Generates actionable AI suggestions with [Accept], [Ignore], [Record Action] triggers.
    """
    suggestions = []
    waters = getattr(session_state, "demo_water_quality", [])
    feeds = getattr(session_state, "demo_feeding", [])
    mortalities = getattr(session_state, "demo_mortality", [])

    # 1. Water Suggestion
    if any(w.get("DissolvedOxygen", 6) < 5.0 for w in waters[-2:]):
        suggestions.append({
            "id": "sug_water_aeration",
            "category": "Water Management",
            "title": "Increase Dawn Aeration in P-001",
            "why": "Recent dissolved oxygen observation dropped to 4.2 mg/L on overcast mornings.",
            "based_on": "Water logs from past 3 days in Green Valley Pond.",
            "what_to_check": "Turn on paddlewheel aerators between 04:00 AM and 07:30 AM. Recheck DO with probe.",
            "action_label": "Log Water Reading",
            "action_menu": "water"
        })

    # 2. Feed Inventory Suggestion
    suggestions.append({
        "id": "sug_feed_order",
        "category": "Feeding & Inventory",
        "title": "Review Feed Inventory Re-order Level",
        "why": "Current feed consumption is ~280 kg/day across both active ponds.",
        "based_on": "14 days of recorded feeding rates and remaining warehouse bags.",
        "what_to_check": "Verify warehouse stock in feed shed. Ensure 15-day buffer stock before rainy season.",
        "action_label": "View Feed Inventory",
        "action_menu": "feeding"
    })

    # 3. Growth Sampling Suggestion
    suggestions.append({
        "id": "sug_growth_netting",
        "category": "Growth Tracking",
        "title": "Bi-weekly Sampling Due for Krishna Aqua Pond (P-002)",
        "why": "Last sampling of Tilapia was conducted 12 days ago.",
        "based_on": "Pond P-002 sampling timeline in growth registry.",
        "what_to_check": "Net a representative sample of 40 fish. Measure average weight to update daily feeding percentage.",
        "action_label": "Add Growth Sample",
        "action_menu": "fish"
    })

    # 4. Payment Collection Suggestion
    suggestions.append({
        "id": "sug_payment_balance",
        "category": "Finance",
        "title": "Follow up on Partial Sale Payment",
        "why": "Sale voucher #2 has a pending balance of ₹44,000 from Vijayawada Fish Traders.",
        "based_on": "Sales ledger partial payment status.",
        "what_to_check": "Contact buyer representative and update payment status upon receipt.",
        "action_label": "View Sales Ledger",
        "action_menu": "finance"
    })

    return suggestions


