"""
AquaMitra Overview View Module
Renders Command-Center Dashboard with 8 KPI cards, structured analytics,
Farm Summary, and Daily Farm Brief with strictly zero emojis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.translations import t
from utils.demo_data import get_pond_health_snapshot, get_unified_recent_activity
from components.cards import (
    render_metric_card,
    render_pond_snapshot,
    render_empty_state,
    render_activity_feed,
    render_alert_card
)
from services.ai.ai_service import generate_farm_summary, generate_daily_briefing
from database.queries import (
    get_fish_stocks,
    get_growth_records,
    get_water_quality,
    get_feeding_records,
    get_incidents,
    get_expenses,
    get_sales
)


def render_overview_view():
    lang = st.session_state.get("lang", "en")
    subtabs = ["Dashboard", "Farm Summary", "Daily Brief"]
    tabs = st.tabs(subtabs)

    ponds = st.session_state.get("demo_ponds", [])
    stocks = get_fish_stocks()
    growths = get_growth_records()
    alerts = [a for a in st.session_state.get("demo_alerts", []) if not a.get("IsResolved")]
    expenses = get_expenses()
    sales = get_sales()
    feeds = get_feeding_records()
    incidents = get_incidents()
    mortality = st.session_state.get("demo_mortality", [])

    total_fish = sum(s.get("NumberOfFish", 0) for s in stocks)
    total_exp = sum(e.get("Amount", 0) for e in expenses)
    total_rev = sum(s.get("TotalRevenue", 0) for s in sales)
    net_diff = total_rev - total_exp
    active_p_count = len([p for p in ponds if p.get("Status") == "Active"])
    recent_dead = sum(m.get("NumberOfDead", 0) for m in mortality)
    today_feed = feeds[0].get("ActualFeedKg", 75.0) if feeds else 0.0

    # 1. Command-Center Dashboard
    with tabs[0]:
        # Top 8 KPI Cards (Requirement 28)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_metric_card("Active Ponds", f"{active_p_count} / {len(ponds)}", "Operational Units")
        with k2:
            render_metric_card("Fish Stock", f"{total_fish:,}", "Cultured Fingerlings")
        with k3:
            render_metric_card("Estimated Biomass", "10,340 kg", "Farm Aggregate")
        with k4:
            render_metric_card("Today's Feed", f"{today_feed:,.1f} kg", "Daily Application")

        k5, k6, k7, k8 = st.columns(4)
        with k5:
            render_metric_card("Open Alerts", f"{len(alerts)}", "Unresolved Items", value_color="#DC2626" if alerts else "#059669")
        with k6:
            render_metric_card("Recent Mortality", f"{recent_dead} Fish", "Last 7 Days Record", value_color="#D97706" if recent_dead else "#0F172A")
        with k7:
            render_metric_card("Monthly Expenses", f"₹{total_exp:,.0f}", "All Input Costs")
        with k8:
            render_metric_card("Monthly Revenue", f"₹{total_rev:,.0f}", f"Net: +₹{net_diff:,.0f}", value_color="#059669")

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # AI Farm Intelligence Summary Banner
        ai_summary = generate_farm_summary(st.session_state)
        clean_text = ai_summary['text'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("📊", "").replace("💰", "").replace("💡", "").replace("🤖", "")
        clean_badge = ai_summary['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()

        st.markdown(
            f"""
            <div class="ai-banner">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div class="ai-banner-title">AquaMitra AI — Farm Status Synthesis</div>
                    <span style="background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 4px; font-size: 0.70rem; font-weight: 700; color: #38BDF8;">
                        {clean_badge}
                    </span>
                </div>
                <div class="ai-banner-content">
                    {clean_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Two-Column Dashboard Layout
        c_left, c_right = st.columns([3, 2])

        with c_left:
            st.markdown("##### Pond Status Overview")
            for p in ponds:
                snap = get_pond_health_snapshot(p["PondID"])
                render_pond_snapshot(snap)

            # Water Quality Trend Preview
            st.markdown("##### Recent Water Quality Observations")
            waters = get_water_quality()
            if waters:
                df_w = pd.DataFrame(waters)
                if "ReadingDate" in df_w.columns and "DissolvedOxygen" in df_w.columns:
                    fig_w = px.line(
                        df_w.sort_values("ReadingDate"),
                        x="ReadingDate",
                        y="DissolvedOxygen",
                        color="PondID",
                        markers=True,
                        title="Dissolved Oxygen (mg/L) Trend Across Ponds",
                        labels={"ReadingDate": "Date", "DissolvedOxygen": "DO (mg/L)"}
                    )
                    fig_w.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Optimal Threshold (5.0 mg/L)")
                    fig_w.update_layout(height=260, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.2))
                    st.plotly_chart(fig_w, use_container_width=True)

            # Growth Trajectory Preview
            st.markdown("##### Fish Weight Growth Trajectory")
            if growths:
                df_g = pd.DataFrame(growths)
                fig_g = px.line(
                    df_g.sort_values("ObservationDate"),
                    x="ObservationDate",
                    y="AvgFishWeightGrams",
                    color="PondID",
                    markers=True,
                    labels={"ObservationDate": "Sampling Date", "AvgFishWeightGrams": "Average Weight (g)"},
                    title="Average Fish Weight (Grams) over Time"
                )
                fig_g.update_layout(height=260, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.2))
                st.plotly_chart(fig_g, use_container_width=True)

        with c_right:
            st.markdown("##### Active Decision-Support Alerts")
            if alerts:
                for a in alerts[:3]:
                    res = render_alert_card(a)
                    if res:
                        st.success("Alert marked resolved.")
                        st.rerun()
            else:
                render_empty_state("Alerts", "All Clear", "No unresolved alerts detected.")

            st.markdown("##### Recent Farm Activity Feed")
            activities = get_unified_recent_activity(limit=6)
            render_activity_feed(activities)

    # 2. Farm Summary
    with tabs[1]:
        prof = st.session_state.get("demo_farm_profile", {})
        st.markdown(f"#### {prof.get('FarmName', 'Farm Profile')}")
        st.caption(f"Location: {prof.get('Village')}, {prof.get('Mandal')}, {prof.get('District')} | Owner: {prof.get('OwnerName')} ({prof.get('MobileNumber')})")

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            render_metric_card("Total Farm Area", f"{prof.get('TotalFarmArea', 7.0)} Acres", f"{len(ponds)} Configured Ponds")
        with f2:
            render_metric_card("Estimated Total Biomass", "10,340 kg", "Rohu, Catla, Tilapia")
        with f3:
            render_metric_card("Total Recorded Expenses", f"₹{total_exp:,.0f}", "Operating Expenditures")
        with f4:
            render_metric_card("Harvest Sales Revenue", f"₹{total_rev:,.0f}", f"Net: +₹{net_diff:,.0f}", value_color="#059669")

        col_pie, col_bar = st.columns(2)
        with col_pie:
            st.markdown("##### Stocked Species Distribution")
            if stocks:
                df_s = pd.DataFrame(stocks)
                fig_pie = px.pie(df_s, names="Species", values="NumberOfFish", hole=0.45, title="Fish Population by Species")
                fig_pie.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar:
            st.markdown("##### Operating Cost Breakdown")
            if expenses:
                df_e = pd.DataFrame(expenses)
                df_cat = df_e.groupby("Category")["Amount"].sum().reset_index()
                fig_bar = px.bar(df_cat, x="Category", y="Amount", title="Expenditure by Category (₹)")
                fig_bar.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Daily Brief
    with tabs[2]:
        daily_brief = generate_daily_briefing(st.session_state)
        clean_brief_text = daily_brief["text"].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("📊", "").replace("💰", "").replace("💡", "").replace("🤖", "")
        clean_brief_badge = daily_brief["badge"].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()

        st.markdown(
            f"""
            <div class="saas-card" style="padding: 20px 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px;">
                    <h3 style="color: #0F2942; margin: 0; font-size: 1.2rem;">Daily Operational Briefing & Advisory</h3>
                    <span style="font-size: 0.72rem; color: #0369A1; background: #E0F2FE; border: 1px solid #BAE6FD; padding: 3px 8px; border-radius: 4px; font-weight: 700;">
                        {clean_brief_badge}
                    </span>
                </div>
                <div style="font-size: 0.92rem; line-height: 1.6; color: #334155;">
            """,
            unsafe_allow_html=True
        )
        st.markdown(clean_brief_text)
        st.markdown("</div></div>", unsafe_allow_html=True)
