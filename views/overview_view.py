"""
AquaMitra Overview View Module
Renders Command-Center Dashboard with 8 KPI cards, structured analytics,
Farm Summary, and Daily Farm Brief. Strictly zero emojis. Bilingual (EN/TE).
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from utils.translations import t, tv
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
    get_expenses,
    get_sales
)


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_overview_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Dashboard", "డాష్‌బోర్డ్"),
        _lbl(lang, "Farm Summary", "ఫార్మ్ సారాంశం"),
        _lbl(lang, "Daily Brief", "రోజువారీ నివేదిక")
    ]
    tabs = st.tabs(subtabs)

    ponds = st.session_state.get("demo_ponds", [])
    stocks = get_fish_stocks()
    growths = get_growth_records()
    alerts = [a for a in st.session_state.get("demo_alerts", []) if not a.get("IsResolved")]
    expenses = get_expenses()
    sales = get_sales()
    feeds = get_feeding_records()
    mortality = st.session_state.get("demo_mortality", [])

    total_fish = sum(s.get("NumberOfFish", 0) for s in stocks)
    total_exp = sum(e.get("Amount", 0) for e in expenses)
    total_rev = sum(s.get("TotalRevenue", 0) for s in sales)
    net_diff = total_rev - total_exp
    active_p_count = len([p for p in ponds if p.get("Status") == "Active"])
    recent_dead = sum(m.get("NumberOfDead", 0) for m in mortality)
    today_feed = feeds[0].get("ActualFeedKg", 75.0) if feeds else 0.0
    kg_unit = _lbl(lang, "kg", "కేజీ")

    # 1. Command-Center Dashboard
    with tabs[0]:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_metric_card(
                _lbl(lang, "Active Ponds", "క్రియాశీల చెరువులు"),
                f"{active_p_count} / {len(ponds)}",
                _lbl(lang, "Operational Units", "నిర్వహణ యూనిట్లు")
            )
        with k2:
            render_metric_card(
                _lbl(lang, "Fish Stock", "చేపల నిల్వ"),
                f"{total_fish:,}",
                _lbl(lang, "Cultured Fingerlings", "సాగు చేప పిల్లలు")
            )
        with k3:
            render_metric_card(
                _lbl(lang, "Estimated Biomass", "అంచనా బయోమాస్"),
                f"10,340 {kg_unit}",
                _lbl(lang, "Farm Aggregate", "మొత్తం ఫార్మ్ అంచనా")
            )
        with k4:
            render_metric_card(
                _lbl(lang, "Today's Feed", "నేటి మేత"),
                f"{today_feed:,.1f} {kg_unit}",
                _lbl(lang, "Daily Application", "రోజువారీ వినియోగం")
            )

        k5, k6, k7, k8 = st.columns(4)
        with k5:
            render_metric_card(
                _lbl(lang, "Open Alerts", "క్రియాశీల అలర్ట్‌లు"),
                f"{len(alerts)}",
                _lbl(lang, "Unresolved Items", "పరిష్కరించని అంశాలు"),
                value_color="#DC2626" if alerts else "#059669"
            )
        with k6:
            fish_word = _lbl(lang, "Fish", "చేపలు")
            render_metric_card(
                _lbl(lang, "Recent Mortality", "ఇటీవలి మరణాలు"),
                f"{recent_dead} {fish_word}",
                _lbl(lang, "Last 7 Days Record", "గత 7 రోజుల రికార్డు"),
                value_color="#D97706" if recent_dead else "#0F172A"
            )
        with k7:
            render_metric_card(
                _lbl(lang, "Monthly Expenses", "నెలవారీ ఖర్చులు"),
                f"₹{total_exp:,.0f}",
                _lbl(lang, "All Input Costs", "మొత్తం పెట్టుబడి ఖర్చులు")
            )
        with k8:
            net_prefix = _lbl(lang, "Net", "నికర")
            render_metric_card(
                _lbl(lang, "Monthly Revenue", "నెలవారీ ఆదాయం"),
                f"₹{total_rev:,.0f}",
                f"{net_prefix}: +₹{net_diff:,.0f}",
                value_color="#059669"
            )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # AI Farm Intelligence Summary Banner
        ai_summary = generate_farm_summary(st.session_state, lang=lang)
        clean_text = ai_summary['text'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("📊", "").replace("💰", "").replace("💡", "").replace("🤖", "")
        clean_badge = ai_summary['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()

        st.markdown(
            f"""
            <div class="ai-banner">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div class="ai-banner-title">{_lbl(lang, 'AquaMitra AI — Farm Status Synthesis', 'ఆక్వామిత్ర AI — ఫార్మ్ స్థితి సారాంశం')}</div>
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
            st.markdown(f"##### {_lbl(lang, 'Pond Status Overview', 'చెరువుల స్థితి అవలోకనం')}")
            for p in ponds:
                snap = get_pond_health_snapshot(p["PondID"])
                render_pond_snapshot(snap)

            # Water Quality Trend Preview
            st.markdown(f"##### {_lbl(lang, 'Recent Water Quality Observations', 'ఇటీవలి నీటి నాణ్యత పరిశీలనలు')}")
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
                        title=_lbl(lang, "Dissolved Oxygen (mg/L) Trend Across Ponds", "చెరువుల వారీగా కరిగిన ఆక్సిజన్ (DO mg/L) ధోరణి"),
                        labels={
                            "ReadingDate": _lbl(lang, "Date", "తేదీ"),
                            "DissolvedOxygen": _lbl(lang, "DO (mg/L)", "కరిగిన ఆక్సిజన్ (mg/L)"),
                            "PondID": _lbl(lang, "Pond", "చెరువు")
                        }
                    )
                    fig_w.add_hline(
                        y=5.0,
                        line_dash="dash",
                        line_color="#D97706",
                        annotation_text=_lbl(lang, "Optimal Threshold (5.0 mg/L)", "ప్రమాణ స్థాయి (5.0 mg/L)")
                    )
                    fig_w.update_layout(height=260, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.2))
                    st.plotly_chart(fig_w, use_container_width=True)

            # Growth Trajectory Preview
            st.markdown(f"##### {_lbl(lang, 'Fish Weight Growth Trajectory', 'చేపల బరువు పెరుగుదల ధోరణి')}")
            if growths:
                df_g = pd.DataFrame(growths)
                fig_g = px.line(
                    df_g.sort_values("ObservationDate"),
                    x="ObservationDate",
                    y="AvgFishWeightGrams",
                    color="PondID",
                    markers=True,
                    labels={
                        "ObservationDate": _lbl(lang, "Sampling Date", "నమూనా తేదీ"),
                        "AvgFishWeightGrams": _lbl(lang, "Average Weight (g)", "సగటు బరువు (గ్రా.)"),
                        "PondID": _lbl(lang, "Pond", "చెరువు")
                    },
                    title=_lbl(lang, "Average Fish Weight (Grams) over Time", "కాలక్రమేణా సగటు చేపల బరువు (గ్రాములు)")
                )
                fig_g.update_layout(height=260, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.2))
                st.plotly_chart(fig_g, use_container_width=True)

        with c_right:
            st.markdown(f"##### {_lbl(lang, 'Active Decision-Support Alerts', 'క్రియాశీల నిర్ణయ-సహాయ అలర్ట్‌లు')}")
            if alerts:
                for a in alerts[:3]:
                    res = render_alert_card(a)
                    if res:
                        st.success(_lbl(lang, "Alert marked resolved.", "అలర్ట్ పరిష్కరించినట్లు గుర్తించబడింది."))
                        st.rerun()
            else:
                render_empty_state(
                    _lbl(lang, "Alerts", "అలర్ట్‌లు"),
                    _lbl(lang, "All Clear", "అన్నీ సాధారణంగా ఉన్నాయి"),
                    _lbl(lang, "No unresolved alerts detected.", "పరిష్కరించని అలర్ట్‌లు ఏవీ లేవు.")
                )

            st.markdown(f"##### {_lbl(lang, 'Recent Farm Activity Feed', 'ఇటీవలి ఫార్మ్ కార్యకలాపాలు')}")
            activities = get_unified_recent_activity(limit=6)
            render_activity_feed(activities)

    # 2. Farm Summary
    with tabs[1]:
        prof = st.session_state.get("demo_farm_profile", {})
        st.markdown(f"#### {prof.get('FarmName', _lbl(lang, 'Farm Profile', 'ఫార్మ్ ప్రొఫైల్'))}")
        st.caption(
            f"{_lbl(lang, 'Location', 'ప్రాంతం')}: {prof.get('Village')}, {prof.get('Mandal')}, {prof.get('District')} | "
            f"{_lbl(lang, 'Owner', 'యజమాని')}: {prof.get('OwnerName')} ({prof.get('MobileNumber')})"
        )

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            render_metric_card(
                _lbl(lang, "Total Farm Area", "మొత్తం ఫార్మ్ విస్తీర్ణం"),
                f"{prof.get('TotalFarmArea', 7.0)} {_lbl(lang, 'Acres', 'ఎకరాలు')}",
                f"{len(ponds)} {_lbl(lang, 'Configured Ponds', 'నమోదైన చెరువులు')}"
            )
        with f2:
            render_metric_card(
                _lbl(lang, "Estimated Total Biomass", "అంచనా మొత్తం బయోమాస్"),
                f"10,340 {kg_unit}",
                _lbl(lang, "Rohu, Catla, Tilapia", "రోహు, కట్లా, తిలాపియా")
            )
        with f3:
            render_metric_card(
                _lbl(lang, "Total Recorded Expenses", "మొత్తం నమోదైన ఖర్చులు"),
                f"₹{total_exp:,.0f}",
                _lbl(lang, "Operating Expenditures", "నిర్వహణ వ్యయాలు")
            )
        with f4:
            render_metric_card(
                _lbl(lang, "Harvest Sales Revenue", "పంట కోత అమ్మకాల ఆదాయం"),
                f"₹{total_rev:,.0f}",
                f"{_lbl(lang, 'Net', 'నికర')}: +₹{net_diff:,.0f}",
                value_color="#059669"
            )

        col_pie, col_bar = st.columns(2)
        with col_pie:
            st.markdown(f"##### {_lbl(lang, 'Stocked Species Distribution', 'నిల్వ చేసిన చేప జాతుల పంపిణీ')}")
            if stocks:
                df_s = pd.DataFrame(stocks)
                fig_pie = px.pie(
                    df_s,
                    names="Species",
                    values="NumberOfFish",
                    hole=0.45,
                    title=_lbl(lang, "Fish Population by Species", "జాతుల వారీగా చేపల సంఖ్య")
                )
                fig_pie.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar:
            st.markdown(f"##### {_lbl(lang, 'Operating Cost Breakdown', 'నిర్వహణ ఖర్చుల వివరణ')}")
            if expenses:
                df_e = pd.DataFrame(expenses)
                df_cat = df_e.groupby("Category")["Amount"].sum().reset_index()
                df_cat["CategoryDisplay"] = df_cat["Category"].apply(lambda c: tv(c, lang))
                fig_bar = px.bar(
                    df_cat,
                    x="CategoryDisplay",
                    y="Amount",
                    title=_lbl(lang, "Expenditure by Category (₹)", "విభాగం వారీగా ఖర్చులు (₹)"),
                    labels={"CategoryDisplay": _lbl(lang, "Category", "విభాగం"), "Amount": _lbl(lang, "Amount (₹)", "మొత్తం (₹)")}
                )
                fig_bar.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Daily Brief
    with tabs[2]:
        daily_brief = generate_daily_briefing(st.session_state, lang=lang)
        clean_brief_text = daily_brief["text"].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("📊", "").replace("💰", "").replace("💡", "").replace("🤖", "")
        clean_brief_badge = daily_brief["badge"].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()

        st.markdown(
            f"""
            <div class="saas-card" style="padding: 20px 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px;">
                    <h3 style="color: #0F2942; margin: 0; font-size: 1.2rem;">{_lbl(lang, 'Daily Operational Briefing & Advisory', 'రోజువారీ నిర్వహణ నివేదిక మరియు సూచనలు')}</h3>
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
