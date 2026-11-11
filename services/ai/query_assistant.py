"""
AquaMitra Controlled Natural Language Query Assistant
Maps conversational farmer queries to structured data intents with safe, deterministic resolution.
Never allows raw, unconstrained SQL generation. Supports English & Telugu queries.
"""

import re
from typing import Dict, Any, Tuple
from .safety import enforce_ai_safety
from .context_builder import build_farm_context
from .anomaly_detection import audit_data_health, _get_lang


def detect_query_intent(query: str, current_context_pond: str = None) -> Tuple[str, Dict[str, Any]]:
    """
    Classifies farmer query into an authorized intent and extracts entity parameters.
    Supports both English and Telugu query phrases.
    """
    q = query.lower().strip()
    params = {"pond_id": current_context_pond}

    # Extract explicit Pond ID if present
    match_pond = re.search(r"\b(p-00[1-9]|p-[0-9]{3})\b", q)
    if match_pond:
        params["pond_id"] = match_pond.group(1).upper()

    # Intent Classification Rules (English + Telugu keywords)
    if any(k in q for k in [
        "need attention", "needs attention", "attention", "problem", "issue", "alert",
        "శ్రద్ధ", "సమస్య", "అలర్ట్", "జాగ్రత్త", "పర్యవేక్షణ"
    ]):
        return "ATTENTION_CHECK", params
    elif any(k in q for k in [
        "how are my ponds", "pond status", "farm status", "overall", "how is the farm",
        "చెరువులు ఎలా", "ఫార్మ్ స్థితి", "చెరువుల స్థితి", "సారాంశం"
    ]):
        return "FARM_STATUS", params
    elif any(k in q for k in [
        "feed", "feeding", "food", "ration",
        "మేత", "ఆహారం", "రేషన్"
    ]):
        return "FEEDING_ANALYSIS", params
    elif any(k in q for k in [
        "mortality", "dead", "died", "incident",
        "మరణ", "చనిపో", "సంఘటన"
    ]):
        return "MORTALITY_CHECK", params
    elif any(k in q for k in [
        "grow", "growth", "weight", "biomass", "sample",
        "పెరుగుదల", "బరువు", "బయోమాస్", "నమూనా"
    ]):
        return "GROWTH_ANALYSIS", params
    elif any(k in q for k in [
        "spend", "expense", "money", "cost", "revenue", "sale", "profit", "finance",
        "ఖర్చు", "ఆదాయం", "డబ్బు", "అమ్మకం", "ఆర్థిక"
    ]):
        return "FINANCE_CHECK", params
    elif any(k in q for k in [
        "water", "ph", "oxygen", "do", "temperature", "turbidity", "ammonia",
        "నీరు", "నీటి", "ఆక్సిజన్", "ఉష్ణోగ్రత", "అమోనియా"
    ]):
        return "WATER_STATUS", params
    elif any(k in q for k in [
        "missing", "data health", "incomplete", "what should i record",
        "డేటా", "నమోదు", "అసంపూర్ణ"
    ]):
        return "DATA_HEALTH", params
    elif any(k in q for k in ["compare", "difference", "పోల్చు", "తేడా"]):
        return "COMPARE_PONDS", params
    else:
        return "GENERAL_QA", params


def answer_farmer_query(query: str, session_state: Any, current_pond: str = None) -> str:
    """
    Generates a safe, evidence-grounded answer to a farmer's natural-language question.
    Responds in Telugu when lang == 'te', otherwise in English.
    """
    lang = _get_lang(session_state)
    intent, params = detect_query_intent(query, current_pond)
    target_pid = params.get("pond_id")
    ctx = build_farm_context(session_state)

    # 1. Attention Check
    if intent == "ATTENTION_CHECK":
        anomalies = ctx["water_condition"]["anomalies_detected"]
        unresolved = ctx["alerts"]["unresolved_titles"]
        if anomalies or unresolved:
            if lang == "te":
                ans = "**శ్రద్ధ అవసరమైన చెరువులు:**\n\n"
                if anomalies:
                    ans += f"- **నీటి పరిశీలనలు:** {', '.join(anomalies)}\n"
                if unresolved:
                    ans += f"- **క్రియాశీల అలర్ట్‌లు:** {', '.join(unresolved)}\n\n"
                ans += "*సూచించిన చర్య: నీటి పారామితులను మళ్ళీ తనిఖీ చేసి ఏరేషన్ సరిగ్గా నడుస్తుందో నిర్ధారించండి.*"
                return enforce_ai_safety(ans)
            ans = "**Ponds Requiring Attention:**\n\n"
            if anomalies:
                ans += f"- **Water Observations:** {', '.join(anomalies)}\n"
            if unresolved:
                ans += f"- **Active Alerts:** {', '.join(unresolved)}\n\n"
            ans += "*Suggested Action: Recheck water readings and ensure aeration is running.*"
            return enforce_ai_safety(ans)
        else:
            if lang == "te":
                return "**అన్ని చెరువులు స్థిరంగా ఉన్నాయి:** తాజాగా నమోదైన అన్ని నీటి పారామితులు సాధారణ ప్రమాణ పరిధులలో ఉన్నాయి."
            return "**All Ponds Stable:** All latest recorded parameters are within configured baseline ranges."

    # 2. Farm Status
    elif intent == "FARM_STATUS":
        ov = ctx["farm_overview"]
        fin = ctx["finance"]
        if lang == "te":
            w_stat = "1 చెరువుపై శ్రద్ధ అవసరం" if ctx["water_condition"]["anomalies_detected"] else "స్థిరంగా ఉంది"
            return enforce_ai_safety(
                f"**ఈ రోజు ఫార్మ్ స్థితి అవలోకనం:**\n\n"
                f"- **చెరువులు:** {ov['active_ponds']} క్రియాశీల చెరువులు ({ov['total_area_acres']} ఎకరాలు)\n"
                f"- **చేపల నిల్వ:** సుమారు {ov['total_fish']:,} మొత్తం చేపలు\n"
                f"- **బయోమాస్:** అంచనా {ov['estimated_biomass_kg']:,.0f} కేజీ మొత్తం బయోమాస్\n"
                f"- **నీటి స్థితి:** {w_stat}\n"
                f"- **ఆర్థిక స్థితి:** ₹{fin['total_expenses']:,.0f} మొత్తం ఖర్చులు | ₹{fin['total_sales']:,.0f} అమ్మకాల ఆదాయం"
            )
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
            return (
                "దానికి సమాధానం ఇవ్వడానికి తగినంత మేత రికార్డులు ప్రస్తుతం లేవు."
                if lang == "te"
                else "I don't have enough recorded feeding data to answer that."
            )

        last_feed = feeds[-1]
        if lang == "te":
            return enforce_ai_safety(
                f"**మేత విశ్లేషణ:**\n\n"
                f"- **ఇటీవలి మేత నమోదు:** {last_feed.get('ActualFeedKg')} కేజీ ({last_feed.get('FeedType')})\n"
                f"- **సిఫార్సు రేషన్:** {last_feed.get('RecommendedFeedKg')} కేజీ\n"
                f"- **తేడా (Variance):** {feed_ctx['variance_kg']} కేజీ వ్యత్యాసం\n\n"
                f"*సూచన: మేత వేసిన 2 గంటల తర్వాత చెక్ ట్రేలను పరిశీలించి చేపలు మేతను పూర్తిగా తిన్నాయో లేదో చూడండి.*"
            )
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
            if lang == "te":
                return "**మరణాలు నమోదు కాలేదు:** ఎంచుకున్న కాలానికి చేపల మరణాల సంఘటనలు ఏవీ నమోదు కాలేదు."
            return "**No Mortality Recorded:** No fish mortality events are on record for the selected period."

        latest_m = mortalities[0]
        if lang == "te":
            return enforce_ai_safety(
                f"**ఇటీవలి మరణాల సంఘటనలు:**\n\n"
                f"- **చెరువు {latest_m.get('PondID')}:** {latest_m.get('IncidentDate')} న {latest_m.get('NumberOfDead')} చేపలు మృతి చెందాయి\n"
                f"- **గమనించిన ప్రవర్తన:** {latest_m.get('ObservedBehaviour')}\n"
                f"- **గమనికలు:** {latest_m.get('Remarks')}\n\n"
                f"*సూచించిన చర్య: నీటి పారామితులను తనిఖీ చేయండి; మరణాలు కొనసాగితే అర్హత గల మత్స్య నిపుణులను సంప్రదించండి.*"
            )
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
            if lang == "te":
                return "నమ్మకమైన పెరుగుదల ధోరణిని చూపడానికి కనీసం రెండు పెరుగుదల నమూనా రికార్డులు అవసరం."
            return "I don't have enough recorded growth sampling records to establish a reliable trend."

        start_w = p_growths[0]["AvgFishWeightGrams"]
        curr_w = p_growths[-1]["AvgFishWeightGrams"]
        pid_label = target_pid if target_pid else "P-001"
        if lang == "te":
            return enforce_ai_safety(
                f"**{pid_label} లో చేపల పెరుగుదల:**\n\n"
                f"- **మొదటి నమూనా:** {start_w}g ({p_growths[0]['ObservationDate']})\n"
                f"- **తాజా నమూనా:** {curr_w}g ({p_growths[-1]['ObservationDate']})\n"
                f"- **బరువు పెరుగుదల:** {len(p_growths)} నమూనా తనిఖీలలో +{curr_w - start_w}g\n\n"
                f"పెరుగుదల ధోరణి స్థిరంగా మరియు సానుకూలంగా ఉంది."
            )
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
        if lang == "te":
            return enforce_ai_safety(
                f"**ఆర్థిక సారాంశం:**\n\n"
                f"- **మొత్తం నిర్వహణ ఖర్చులు:** ₹{fin['total_expenses']:,.0f}\n"
                f"- **అత్యధిక ఖర్చు విభాగం:** {fin['top_expense_category']}\n"
                f"- **మొత్తం చేపల అమ్మకాల ఆదాయం:** ₹{fin['total_sales']:,.0f}\n"
                f"- **అంచనా నికర తేడా:** +₹{fin['estimated_net_difference']:,.0f}\n\n"
                f"*గమనిక: ఈ గణాంకాలు మీరు నమోదు చేసిన ఫార్మ్ రికార్డులపై ఆధారపడి ఉన్నాయి.*"
            )
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
            if lang == "te":
                return "సమాధానం ఇవ్వడానికి తగినంత నీటి నాణ్యత డేటా నమోదు కాలేదు."
            return "I don't have enough recorded water-quality data to answer that."

        anoms = ctx["water_condition"]["anomalies_detected"]
        if anoms:
            if lang == "te":
                return enforce_ai_safety(
                    f"**శ్రద్ధ అవసరమైన నీటి పరిశీలనలు:**\n\n"
                    f"- ప్రమాణ పరిధికి వెలుపల ఉన్న పరిశీలనలు: {', '.join(anoms)}\n\n"
                    f"*సూచించిన చర్య: మళ్ళీ నీటి పరీక్ష ద్వారా నిర్ధారించుకోండి మరియు ఏరేషన్ కొనసాగించండి.*"
                )
            return enforce_ai_safety(
                f"**Water Observations Requiring Attention:**\n\n"
                f"- Observations outside reference range: {', '.join(anoms)}\n\n"
                f"*Suggested Action: Verify with a follow-up test and maintain aeration.*"
            )
        else:
            if lang == "te":
                return "**నీటి నాణ్యత స్థిరంగా ఉంది:** అన్ని చెరువులలోని తాజా నీటి పరీక్షా ఫలితాలు సాధారణ ప్రమాణ పరిధులలో ఉన్నాయి."
            return "**Water Quality Stable:** Latest recorded observations across all ponds are within standard reference ranges."

    # 8. Data Health Audit
    elif intent == "DATA_HEALTH":
        issues = audit_data_health(session_state)
        if not issues:
            if lang == "te":
                return "**డేటా ఆరోగ్యం సంపూర్ణంగా ఉంది:** అన్ని క్రియాశీల చెరువులకు తాజా నీరు, మేత మరియు నిల్వ రికార్డులు ఉన్నాయి."
            return "**Data Health Complete:** All active ponds have recent water, feeding, and stocking records."

        ans = "**రికార్డుల పూర్తిస్థాయి ఆడిట్:**\n\n" if lang == "te" else "**Record Completeness Audit:**\n\n"
        for idx, iss in enumerate(issues[:3], 1):
            ans += f"{idx}. **{iss['title']}**: {iss['message']}\n"
        return ans

    # Default / General Fallback
    if lang == "te":
        return enforce_ai_safety(
            f"**ఆక్వామిత్ర AI:** మీ ప్రస్తుత ఫార్మ్ రికార్డులను పరిశీలించాను "
            f"({ctx['farm_overview']['active_ponds']} క్రియాశీల చెరువులు, {ctx['farm_overview']['total_fish']:,} చేపలు). "
            f"చెరువు నీటి నాణ్యత, మేత వినియోగం, చేపల పెరుగుదల, ఖర్చులు లేదా ఏ చెరువుకు శ్రద్ధ అవసరమో నన్ను అడగండి."
        )
    return enforce_ai_safety(
        f"**AquaMitra AI:** I have reviewed your current farm records ({ctx['farm_overview']['active_ponds']} active ponds, "
        f"{ctx['farm_overview']['total_fish']:,} fish). You can ask me about pond water quality, feed usage, "
        f"fish growth, expenses, or which pond needs attention today."
    )
