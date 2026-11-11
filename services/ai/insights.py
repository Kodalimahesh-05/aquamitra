"""
AquaMitra AI Insights Generator
Produces prioritized, evidence-based insights across farm modules with complete source transparency.
Fully bilingual (English / Telugu) with strictly zero emojis.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.translations import tv
from .anomaly_detection import detect_farm_anomalies, audit_data_health, _get_lang
from .context_builder import build_farm_context


def generate_farm_insights(session_state: Any, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generates actionable, evidence-based insights prioritized by severity.
    Includes source transparency linking each observation to underlying records.
    """
    lang = _get_lang(session_state)
    insights = []
    ctx = build_farm_context(session_state)
    now_str = datetime.now().strftime("%d %b %Y, %H:%M")

    # 1. Anomaly-Driven Insights (Water, Feeding, Mortality)
    anomalies = detect_farm_anomalies(session_state)
    for a in anomalies:
        sev_code = "HIGH ATTENTION" if a["severity"] == "HIGH" else "MONITOR"
        sev_label = (
            ("అధిక శ్రద్ధ అవసరం" if a["severity"] == "HIGH" else "పర్యవేక్షణ అవసరం")
            if lang == "te"
            else sev_code
        )
        insights.append({
            "id": f"ins_{a['id']}",
            "title": a["title"],
            "category": a["category"],
            "category_display": tv(a["category"], lang),
            "severity": sev_code,
            "severity_display": sev_label,
            "observation": a["observation"],
            "supporting_data": (
                f"ఆధారం: {a.get('source', 'ఫార్మ్ లాగ్‌లు')}"
                if lang == "te"
                else f"Based on: {a.get('source', 'Farm logs')}"
            ),
            "suggested_next_step": a["suggested_action"],
            "generated_at": now_str,
        })

    # 2. Fish Growth Insights
    growths = getattr(session_state, "demo_fish_growth", [])
    if growths:
        p1_growths = [g for g in growths if g.get("PondID") == "P-001"]
        if len(p1_growths) >= 2:
            start_w = p1_growths[0]["AvgFishWeightGrams"]
            curr_w = p1_growths[-1]["AvgFishWeightGrams"]
            gain = curr_w - start_w
            insights.append({
                "id": "ins_growth_p1",
                "title": (
                    "P-001 చెరువులో సానుకూల పెరుగుదల ధోరణి"
                    if lang == "te"
                    else "Positive Growth Trajectory in P-001"
                ),
                "category": "Growth",
                "category_display": tv("Growth", lang),
                "severity": "INFORMATION",
                "severity_display": "సమాచారం" if lang == "te" else "INFORMATION",
                "observation": (
                    f"నమూనా తనిఖీలలో చేపల సగటు బరువు {start_w}g నుండి {curr_w}g వరకు (+{gain}g) పెరిగింది."
                    if lang == "te"
                    else f"Average sampled fish weight grew from {start_w}g to {curr_w}g (+{gain}g) across sampling checks."
                ),
                "supporting_data": (
                    f"ఆధారం: P-001 లో {len(p1_growths)} నమూనా రికార్డులు"
                    if lang == "te"
                    else f"Based on: {len(p1_growths)} sampling records in P-001"
                ),
                "suggested_next_step": (
                    "ప్రస్తుత మేత రేషన్‌ను కొనసాగించండి మరియు 10-14 రోజుల్లో తదుపరి నమూనా తనిఖీ చేయండి."
                    if lang == "te"
                    else "Maintain current feeding ration and perform next periodic sample netting in 10-14 days."
                ),
                "generated_at": now_str,
            })

    # 3. Financial Spending Insights
    fin = ctx.get("finance", {})
    top_cat = fin.get("top_expense_category", "Feed")
    top_cat_disp = tv(top_cat, lang)
    total_exp = fin.get("total_expenses", 0)
    net_diff = fin.get("estimated_net_difference", 0)

    insights.append({
        "id": "ins_fin_top_cost",
        "title": (
            f"ప్రధాన ఖర్చు విభాగం: మొత్తం ఖర్చులలో {top_cat_disp} వాటా అధికం"
            if lang == "te"
            else f"Cost Driver: {top_cat} Represents Majority Spending"
        ),
        "category": "Finance",
        "category_display": tv("Finance", lang),
        "severity": "INFORMATION",
        "severity_display": "సమాచారం" if lang == "te" else "INFORMATION",
        "observation": (
            f"మొత్తం ఫార్మ్ ఖర్చులలో {top_cat_disp} విభాగం అత్యధిక వాటాను కలిగి ఉంది (మొత్తం ఖర్చులు: ₹{total_exp:,.0f})."
            if lang == "te"
            else f"{top_cat} accounts for the largest share of total farm expenditure (Total Expenses: ₹{total_exp:,.0f})."
        ),
        "supporting_data": (
            "ఆధారం: చారిత్రక ఫార్మ్ ఖర్చుల పట్టిక"
            if lang == "te"
            else "Based on: Historical categorized farm ledger entries"
        ),
        "suggested_next_step": (
            "ప్రతి కేజీ బరువు పెరుగుదలకు అయ్యే మేత ఖర్చును పర్యవేక్షించడానికి FCR సామర్థ్యాన్ని పరిశీలించండి."
            if lang == "te"
            else "Monitor feed conversion efficiency (FCR) to ensure optimal feed expenditure per kg weight gain."
        ),
        "generated_at": now_str,
    })

    if net_diff > 0:
        insights.append({
            "id": "ins_fin_net_diff",
            "title": (
                "అంచనా నికర సానుకూల ఫార్మ్ ఆదాయం"
                if lang == "te"
                else "Estimated Net Positive Farm Revenue"
            ),
            "category": "Finance",
            "category_display": tv("Finance", lang),
            "severity": "INFORMATION",
            "severity_display": "సమాచారం" if lang == "te" else "INFORMATION",
            "observation": (
                f"ప్రస్తుత పాక్షిక కోతల ద్వారా నమోదైన ఖర్చుల కంటే +₹{net_diff:,.0f} అంచనా నికర తేడా కనిపిస్తోంది."
                if lang == "te"
                else f"Current partial harvests have yielded an estimated net difference of +₹{net_diff:,.0f} over recorded operational expenses."
            ),
            "supporting_data": (
                "ఆధారం: ఫార్మ్ రిజిస్ట్రీలోని అమ్మకాలు మరియు ఖర్చుల ఎంట్రీలు"
                if lang == "te"
                else "Based on: Sales and expense entries in farm registry"
            ),
            "suggested_next_step": (
                "రాబోయే పంట కోత షెడ్యూల్‌ను ప్రస్తుత హోల్‌సేల్ మార్కెట్ ధరలకు అనుగుణంగా ప్రణాళిక చేయండి."
                if lang == "te"
                else "Ensure upcoming harvesting schedules align with prevailing wholesale market prices."
            ),
            "generated_at": now_str,
        })

    # 4. Data Quality & Completeness Insights
    health_issues = audit_data_health(session_state)
    for h in health_issues:
        sev_code = "MONITOR" if h["severity"] == "WARNING" else "INFORMATION"
        sev_label = (
            ("పర్యవేక్షణ అవసరం" if h["severity"] == "WARNING" else "సమాచారం")
            if lang == "te"
            else sev_code
        )
        insights.append({
            "id": f"ins_dq_{h['type']}",
            "title": f"డేటా ఆరోగ్యం: {h['title']}" if lang == "te" else f"Data Health: {h['title']}",
            "category": "Data Quality",
            "category_display": "డేటా నాణ్యత" if lang == "te" else "Data Quality",
            "severity": sev_code,
            "severity_display": sev_label,
            "observation": h["message"],
            "supporting_data": (
                "ఆధారం: స్వయంచాలక డేటా పూర్తిస్థాయి ఆడిట్"
                if lang == "te"
                else "Based on: Automated data completeness audit"
            ),
            "suggested_next_step": (
                f"అవసరమైన చర్య: {h['action']}."
                if lang == "te"
                else f"Action needed: {h['action']}."
            ),
            "generated_at": now_str,
        })

    # Filter by category if requested
    if category and category != "All":
        insights = [i for i in insights if i["category"].lower() == category.lower()]

    return insights
