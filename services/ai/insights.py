"""
AquaMitra AI Insights Generator
Produces prioritized, evidence-based insights across farm modules with complete source transparency.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .anomaly_detection import detect_farm_anomalies, audit_data_health
from .context_builder import build_farm_context


def generate_farm_insights(session_state: Any, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generates actionable, evidence-based insights prioritized by severity.
    Includes source transparency linking each observation to underlying records.
    """
    insights = []
    ctx = build_farm_context(session_state)
    now_str = datetime.now().strftime("%d %b %Y, %H:%M")

    # 1. Anomaly-Driven Insights (Water, Feeding, Mortality)
    anomalies = detect_farm_anomalies(session_state)
    for a in anomalies:
        sev = "HIGH ATTENTION" if a["severity"] == "HIGH" else "MONITOR"
        insights.append({
            "id": f"ins_{a['id']}",
            "title": a["title"],
            "category": a["category"],
            "severity": sev,
            "observation": a["observation"],
            "supporting_data": f"Based on: {a.get('source', 'Farm logs')}",
            "suggested_next_step": a["suggested_action"],
            "generated_at": now_str
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
                "title": "Positive Growth Trajectory in P-001",
                "category": "Growth",
                "severity": "INFORMATION",
                "observation": f"Average sampled fish weight grew from {start_w}g to {curr_w}g (+{gain}g) across sampling checks.",
                "supporting_data": f"Based on: {len(p1_growths)} sampling records in P-001",
                "suggested_next_step": "Maintain current feeding ration and perform next periodic sample netting in 10-14 days.",
                "generated_at": now_str
            })

    # 3. Financial Spending Insights
    fin = ctx.get("finance", {})
    top_cat = fin.get("top_expense_category", "Feed")
    total_exp = fin.get("total_expenses", 0)
    net_diff = fin.get("estimated_net_difference", 0)

    insights.append({
        "id": "ins_fin_top_cost",
        "title": f"Cost Driver: {top_cat} Represents Majority Spending",
        "category": "Finance",
        "severity": "INFORMATION",
        "observation": f"{top_cat} accounts for the largest share of total farm expenditure (Total Expenses: ₹{total_exp:,.0f}).",
        "supporting_data": "Based on: Historical categorized farm ledger entries",
        "suggested_next_step": "Monitor feed conversion efficiency (FCR) to ensure optimal feed expenditure per kg weight gain.",
        "generated_at": now_str
    })

    if net_diff > 0:
        insights.append({
            "id": "ins_fin_net_diff",
            "title": "Estimated Net Positive Farm Revenue",
            "category": "Finance",
            "severity": "INFORMATION",
            "observation": f"Current partial harvests have yielded an estimated net difference of +₹{net_diff:,.0f} over recorded operational expenses.",
            "supporting_data": "Based on: Sales and expense entries in farm registry",
            "suggested_next_step": "Ensure upcoming harvesting schedules align with prevailing wholesale market prices.",
            "generated_at": now_str
        })

    # 4. Data Quality & Completeness Insights
    health_issues = audit_data_health(session_state)
    for h in health_issues:
        insights.append({
            "id": f"ins_dq_{h['type']}",
            "title": f"Data Health: {h['title']}",
            "category": "Data Quality",
            "severity": "MONITOR" if h["severity"] == "WARNING" else "INFORMATION",
            "observation": h["message"],
            "supporting_data": "Based on: Automated data completeness audit",
            "suggested_next_step": f"Action needed: {h['action']}.",
            "generated_at": now_str
        })

    # Filter by category if requested
    if category and category != "All":
        insights = [i for i in insights if i["category"].lower() == category.lower()]

    # Sort: HIGH ATTENTION first, then MONITOR, then INFORMATION
    prio_order = {"HIGH ATTENTION": 0, "MONITOR": 1, "INFORMATION": 2}
    insights.sort(key=lambda x: prio_order.get(x["severity"], 3))

    return insights
