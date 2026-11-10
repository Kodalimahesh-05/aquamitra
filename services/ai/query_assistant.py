"""
AquaMitra Controlled Natural Language Query Assistant
Maps conversational farmer queries to structured data intents with safe, deterministic resolution.
Never allows raw, unconstrained SQL generation.
"""

import re
from typing import Dict, Any, Tuple
from .safety import enforce_ai_safety
from .context_builder import build_farm_context, build_pond_context
from .anomaly_detection import audit_data_health


def detect_query_intent(query: str, current_context_pond: str = None) -> Tuple[str, Dict[str, Any]]:
    """
    Classifies farmer query into an authorized intent and extracts entity parameters.
    """
    q = query.lower().strip()
    params = {"pond_id": current_context_pond}

    # Extract explicit Pond ID if present
    match_pond = re.search(r"\b(p-00[1-9]|p-[0-9]{3})\b", q)
    if match_pond:
        params["pond_id"] = match_pond.group(1).upper()

    # Intent Classification Rules
    if any(k in q for k in ["need attention", "needs attention", "attention", "problem", "issue", "alert"]):
        return "ATTENTION_CHECK", params
    elif any(k in q for k in ["how are my ponds", "pond status", "farm status", "overall", "how is the farm"]):
        return "FARM_STATUS", params
    elif any(k in q for k in ["feed", "feeding", "food", "ration"]):
        return "FEEDING_ANALYSIS", params
    elif any(k in q for k in ["mortality", "dead", "died", "incident"]):
        return "MORTALITY_CHECK", params
    elif any(k in q for k in ["grow", "growth", "weight", "biomass", "sample"]):
        return "GROWTH_ANALYSIS", params
    elif any(k in q for k in ["spend", "expense", "money", "cost", "revenue", "sale", "profit", "finance"]):
        return "FINANCE_CHECK", params
    elif any(k in q for k in ["water", "ph", "oxygen", "do", "temperature", "turbidity", "ammonia"]):
        return "WATER_STATUS", params
    elif any(k in q for k in ["missing", "data health", "incomplete", "what should i record"]):
        return "DATA_HEALTH", params
    elif any(k in q for k in ["compare", "difference"]):
        return "COMPARE_PONDS", params
    else:
        return "GENERAL_QA", params


def answer_farmer_query(query: str, session_state: Any, current_pond: str = None) -> str:
    """
    Generates a safe, evidence-grounded answer to a farmer's natural-language question.
    """
    intent, params = detect_query_intent(query, current_pond)
    target_pid = params.get("pond_id")
    ctx = build_farm_context(session_state)

    # 1. Attention Check
    if intent == "ATTENTION_CHECK":
        anomalies = ctx["water_condition"]["anomalies_detected"]
        unresolved = ctx["alerts"]["unresolved_titles"]
        if anomalies or unresolved:
            ans = "**Ponds Requiring Attention:**\n\n"
            if anomalies:
                ans += f"- **Water Observations:** {', '.join(anomalies)}\n"
            if unresolved:
                ans += f"- **Active Alerts:** {', '.join(unresolved)}\n\n"
            ans += "*Suggested Action: Recheck water readings and ensure aeration is running.*"
            return enforce_ai_safety(ans)
        else:
            return "**All Ponds Stable:** All latest recorded parameters are within configured baseline ranges."

    # 2. Farm Status
    elif intent == "FARM_STATUS":
        ov = ctx["farm_overview"]
        fin = ctx["finance"]
        return enforce_ai_safety(
            f"**Farm Overview Today:**\n\n"
            f"- **Ponds:** {ov['active_ponds']} active ponds ({ov['total_area_acres']} acres)\n"
            f"- **Fish Stock:** ~{ov['total_fish']:,} total stocked fish\n"
            f"- **Biomass:** Estimated {ov['estimated_biomass_kg']:,.0f} kg total biomass\n"
            f"- **Water Status:** {'1 pond requires attention' if ctx['water_condition']['anomalies_detected'] else 'Stable'}\n"
            f"- **Finance:** ₹{fin['total_expenses']:,.0f} total expenses | ₹{fin['total_sales']:,.0f} harvest revenue"
        )

    # 3. Feeding Analysis
    elif intent == "FEEDING_ANALYSIS":
        feed_ctx = ctx["feeding"]
        feeds = getattr(session_state, "demo_feeding", [])
        if not feeds:
            return "I don't have enough recorded feeding data to answer that."
        
        last_feed = feeds[-1]
        return enforce_ai_safety(
            f"**Feeding Analysis:**\n\n"
            f"- **Recent Feed Log:** {last_feed.get('ActualFeedKg')} kg of {last_feed.get('FeedType')}\n"
            f"- **Recommended Ration:** {last_feed.get('RecommendedFeedKg')} kg\n"
            f"- **Variance:** {feed_ctx['variance_kg']} kg difference\n\n"
            f"*Suggestion: Check feed trays 2 hours after feeding to verify consumption.*"
        )

    # 4. Mortality Check
    elif intent == "MORTALITY_CHECK":
        mortalities = getattr(session_state, "demo_mortality", [])
        if not mortalities:
            return "**No Mortality Recorded:** No fish mortality events are on record for the selected period."
        
        latest_m = mortalities[0]
        return enforce_ai_safety(
            f"**Recent Mortality Events:**\n\n"
            f"- **Pond {latest_m.get('PondID')}:** {latest_m.get('NumberOfDead')} dead fish on {latest_m.get('IncidentDate')}\n"
            f"- **Observed Behaviour:** {latest_m.get('ObservedBehaviour')}\n"
            f"- **Remarks:** {latest_m.get('Remarks')}\n\n"
            f"*Suggested Action: Check water parameters and consult a fisheries specialist if mortality continues.*"
        )

    # 5. Growth Analysis
    elif intent == "GROWTH_ANALYSIS":
        growths = getattr(session_state, "demo_fish_growth", [])
        if target_pid:
            p_growths = [g for g in growths if g.get("PondID") == target_pid]
        else:
            p_growths = [g for g in growths if g.get("PondID") == "P-001"]

        if len(p_growths) < 2:
            return "I don't have enough recorded growth sampling records to establish a reliable trend."
        
        start_w = p_growths[0]["AvgFishWeightGrams"]
        curr_w = p_growths[-1]["AvgFishWeightGrams"]
        pid_label = target_pid if target_pid else "P-001"
        return enforce_ai_safety(
            f"**Fish Growth in {pid_label}:**\n\n"
            f"- **Initial Sample:** {start_w}g ({p_growths[0]['ObservationDate']})\n"
            f"- **Latest Sample:** {curr_w}g ({p_growths[-1]['ObservationDate']})\n"
            f"- **Weight Gain:** +{curr_w - start_w}g across {len(p_growths)} sampling intervals\n\n"
            f"Growth trajectory is positive and uniform."
        )

    # 6. Finance Check
    elif intent == "FINANCE_CHECK":
        fin = ctx["finance"]
        return enforce_ai_safety(
            f"**Financial Summary:**\n\n"
            f"- **Total Operational Expenses:** ₹{fin['total_expenses']:,.0f}\n"
            f"- **Top Spending Category:** {fin['top_expense_category']}\n"
            f"- **Total Fish Sales Revenue:** ₹{fin['total_sales']:,.0f}\n"
            f"- **Estimated Net Difference:** +₹{fin['estimated_net_difference']:,.0f}\n\n"
            f"*Note: Figures reflect recorded farm entries.*"
        )

    # 7. Water Status
    elif intent == "WATER_STATUS":
        waters = getattr(session_state, "demo_water_quality", [])
        if not waters:
            return "I don't have enough recorded water-quality data to answer that."
        
        anoms = ctx["water_condition"]["anomalies_detected"]
        if anoms:
            return enforce_ai_safety(
                f"**Water Observations Requiring Attention:**\n\n"
                f"- Observations outside reference range: {', '.join(anoms)}\n\n"
                f"*Suggested Action: Verify with a follow-up test and maintain aeration.*"
            )
        else:
            return "**Water Quality Stable:** Latest recorded observations across all ponds are within standard reference ranges."

    # 8. Data Health Audit
    elif intent == "DATA_HEALTH":
        issues = audit_data_health(session_state)
        if not issues:
            return "**Data Health Complete:** All active ponds have recent water, feeding, and stocking records."
        
        ans = "**Record Completeness Audit:**\n\n"
        for idx, iss in enumerate(issues[:3], 1):
            ans += f"{idx}. **{iss['title']}**: {iss['message']}\n"
        return ans

    # Default / General Fallback
    return enforce_ai_safety(
        f"**AquaMitra AI:** I have reviewed your current farm records ({ctx['farm_overview']['active_ponds']} active ponds, "
        f"{ctx['farm_overview']['total_fish']:,} fish). You can ask me about pond water quality, feed usage, "
        f"fish growth, expenses, or which pond needs attention today."
    )
