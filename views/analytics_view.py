"""
AquaMitra Analytics View Module
Provides interactive Plotly decision-support visual analytics across Farm, Pond,
Growth, Water, Feeding, Incidents, and Finance with 'Explain with AI' features.
Strictly zero emojis. Fully bilingual (EN/TE).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.translations import tv
from services.ai.ai_service import explain_chart_trend
from database.queries import (
    get_growth_records,
    get_water_quality,
    get_feeding_records,
    get_incidents,
    get_expenses,
    get_sales
)


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_analytics_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Farm Analytics", "ఫార్మ్ విశ్లేషణలు"),
        _lbl(lang, "Pond Analytics", "చెరువు విశ్లేషణలు"),
        _lbl(lang, "Growth Analytics", "పెరుగుదల విశ్లేషణలు"),
        _lbl(lang, "Water Analytics", "నీటి విశ్లేషణలు"),
        _lbl(lang, "Feeding Analytics", "మేత విశ్లేషణలు"),
        _lbl(lang, "Incident Analytics", "సంఘటన విశ్లేషణలు"),
        _lbl(lang, "Financial Analytics", "ఆర్థిక విశ్లేషణలు")
    ]
    tabs = st.tabs(subtabs)

    growths = get_growth_records()
    waters = get_water_quality()
    feeds = get_feeding_records()
    expenses = get_expenses()
    sales = get_sales()
    incidents = get_incidents()
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Farm Analytics
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Comprehensive Farm Performance Analytics', 'సమగ్ర ఫార్మ్ పనితీరు విశ్లేషణలు')}")
        if growths and feeds:
            c1, c2 = st.columns(2)
            with c1:
                df_g = pd.DataFrame(growths)
                fig_g = px.line(
                    df_g,
                    x="ObservationDate",
                    y="AvgFishWeightGrams",
                    color="PondID",
                    markers=True,
                    title=_lbl(lang, "Fish Growth Curves Across Ponds (g)", "చెరువుల వారీగా చేపల పెరుగుదల రేఖలు (గ్రా.)"),
                    labels={
                        "ObservationDate": _lbl(lang, "Sampling Date", "నమూనా తేదీ"),
                        "AvgFishWeightGrams": _lbl(lang, "Avg Weight (g)", "సగటు బరువు (గ్రా.)"),
                        "PondID": _lbl(lang, "Pond", "చెరువు")
                    }
                )
                fig_g.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_g, use_container_width=True)
                if st.button(_lbl(lang, "Explain Growth Trend with AI", "AI తో పెరుగుదల ధోరణిని వివరించండి"), key="ai_exp_farm_growth"):
                    p1_g = df_g[df_g["PondID"] == "P-001"]
                    metric_lbl = _lbl(lang, "Fish Growth", "చేపల పెరుగుదల")
                    clean_res = explain_chart_trend(
                        metric_lbl,
                        p1_g["AvgFishWeightGrams"].tolist(),
                        p1_g["ObservationDate"].tolist(),
                        lang=lang
                    ).replace("🤖", "").replace("📈", "").replace("💡", "").strip()
                    st.info(clean_res)

            with c2:
                df_f = pd.DataFrame(feeds)
                fig_f = px.bar(
                    df_f,
                    x="FeedingDate",
                    y="ActualFeedKg",
                    color="PondID",
                    barmode="stack",
                    title=_lbl(lang, "Total Daily Feed Distributed (kg)", "రోజువారీ వేసిన మొత్తం మేత (కేజీ)"),
                    labels={
                        "FeedingDate": _lbl(lang, "Feeding Date", "మేత తేదీ"),
                        "ActualFeedKg": _lbl(lang, "Feed Given (kg)", "వేసిన మేత (కేజీ)"),
                        "PondID": _lbl(lang, "Pond", "చెరువు")
                    }
                )
                fig_f.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_f, use_container_width=True)
                if st.button(_lbl(lang, "Explain Feed Trend with AI", "AI తో మేత ధోరణిని వివరించండి"), key="ai_exp_farm_feed"):
                    p1_f = df_f[df_f["PondID"] == "P-001"]
                    metric_lbl = _lbl(lang, "Feed Consumption", "మేత వినియోగం")
                    clean_res = explain_chart_trend(
                        metric_lbl,
                        p1_f["ActualFeedKg"].tolist(),
                        p1_f["FeedingDate"].tolist(),
                        lang=lang
                    ).replace("🤖", "").replace("📈", "").replace("💡", "").strip()
                    st.info(clean_res)

    # 2. Pond Analytics
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Pond-Level Comparative Analytics', 'చెరువు స్థాయి తులనాత్మక విశ్లేషణలు')}")
        sel_pid = st.selectbox(_lbl(lang, "Select Pond to Inspect", "పరిశీలించాల్సిన చెరువును ఎంచుకోండి"), options=[p["PondID"] for p in ponds], key="an_pond_sel")
        p_waters = [w for w in waters if w.get("PondID") == sel_pid]
        p_feeds = [f for f in feeds if f.get("PondID") == sel_pid]

        c1, c2 = st.columns(2)
        with c1:
            if p_waters:
                fig_pw = px.line(
                    pd.DataFrame(p_waters),
                    x="ReadingDate",
                    y="DissolvedOxygen",
                    markers=True,
                    title=f"{sel_pid} — {_lbl(lang, 'Dissolved Oxygen (mg/L)', 'కరిగిన ఆక్సిజన్ (mg/L)')}",
                    labels={"ReadingDate": _lbl(lang, "Date", "తేదీ"), "DissolvedOxygen": _lbl(lang, "DO (mg/L)", "కరిగిన ఆక్సిజన్ (mg/L)")}
                )
                fig_pw.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text=_lbl(lang, "Baseline Ref (5.0 mg/L)", "ప్రమాణ స్థాయి (5.0 mg/L)"))
                fig_pw.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_pw, use_container_width=True)
            else:
                st.caption(_lbl(lang, "No water records for selected pond.", "ఎంచుకున్న చెరువుకు నీటి రికార్డులు లేవు."))
        with c2:
            if p_feeds:
                fig_pf = px.line(
                    pd.DataFrame(p_feeds),
                    x="FeedingDate",
                    y=["ActualFeedKg", "RecommendedFeedKg"],
                    markers=True,
                    title=f"{sel_pid} — {_lbl(lang, 'Actual vs Recommended Feed (kg)', 'వేసిన vs సిఫార్సు మేత (కేజీ)')}",
                    labels={"FeedingDate": _lbl(lang, "Date", "తేదీ"), "value": _lbl(lang, "Feed (kg)", "మేత (కేజీ)")}
                )
                fig_pf.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.15))
                st.plotly_chart(fig_pf, use_container_width=True)
            else:
                st.caption(_lbl(lang, "No feeding records for selected pond.", "ఎంచుకున్న చెరువుకు మేత రికార్డులు లేవు."))

    # 3. Growth Analytics
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Fish Growth & Biomass Dynamics', 'చేపల పెరుగుదల మరియు బయోమాస్ గతిశీలత')}")
        if growths:
            df_gr = pd.DataFrame(growths)
            fig_bio = px.area(
                df_gr,
                x="ObservationDate",
                y="EstimatedBiomassKg",
                color="PondID",
                title=_lbl(lang, "Estimated Biomass Accumulation (kg)", "అంచనా బయోమాస్ పెరుగుదల (కేజీ)"),
                labels={
                    "ObservationDate": _lbl(lang, "Date", "తేదీ"),
                    "EstimatedBiomassKg": _lbl(lang, "Estimated Biomass (kg)", "అంచనా బయోమాస్ (కేజీ)"),
                    "PondID": _lbl(lang, "Pond", "చెరువు")
                }
            )
            fig_bio.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_bio, use_container_width=True)
        else:
            st.caption(_lbl(lang, "No growth sampling records available.", "పెరుగుదల నమూనా రికార్డులు అందుబాటులో లేవు."))

    # 4. Water Analytics
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Water Parameter Stability & Distribution', 'నీటి పారామితుల స్థిరత్వం మరియు పంపిణీ')}")
        if waters:
            df_w = pd.DataFrame(waters)
            fig_box = px.box(
                df_w,
                x="PondID",
                y="DissolvedOxygen",
                color="PondID",
                title=_lbl(lang, "Dissolved Oxygen Variance Across Ponds (mg/L)", "చెరువుల వారీగా కరిగిన ఆక్సిజన్ (DO) వ్యత్యాసం (mg/L)"),
                labels={"PondID": _lbl(lang, "Pond", "చెరువు"), "DissolvedOxygen": _lbl(lang, "DO (mg/L)", "కరిగిన ఆక్సిజన్ (mg/L)")}
            )
            fig_box.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.caption(_lbl(lang, "No water quality observations recorded.", "నీటి నాణ్యత పరిశీలనలు నమోదు కాలేదు."))

    # 5. Feeding Analytics
    with tabs[4]:
        st.markdown(f"#### {_lbl(lang, 'Feed Efficiency & Consumption Patterns', 'మేత సామర్థ్యం మరియు వినియోగ ధోరణులు')}")
        if feeds:
            df_fd = pd.DataFrame(feeds)
            fig_fd = px.scatter(
                df_fd,
                x="BiomassKg",
                y="ActualFeedKg",
                color="PondID",
                size="ActualFeedKg",
                title=_lbl(lang, "Feed Quantity (kg) vs Estimated Biomass (kg)", "మేత పరిమాణం (కేజీ) vs అంచనా బయోమాస్ (కేజీ)"),
                labels={
                    "BiomassKg": _lbl(lang, "Biomass (kg)", "బయోమాస్ (కేజీ)"),
                    "ActualFeedKg": _lbl(lang, "Feed Given (kg)", "వేసిన మేత (కేజీ)"),
                    "PondID": _lbl(lang, "Pond", "చెరువు")
                }
            )
            fig_fd.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_fd, use_container_width=True)
        else:
            st.caption(_lbl(lang, "No feeding records available.", "మేత రికార్డులు అందుబాటులో లేవు."))

    # 6. Incident Analytics
    with tabs[5]:
        st.markdown(f"#### {_lbl(lang, 'Incident Occurrence & Severity Distribution', 'సంఘటనల సంఖ్య మరియు తీవ్రత పంపిణీ')}")
        if incidents:
            df_inc = pd.DataFrame(incidents)
            df_inc["SeverityDisplay"] = df_inc["Severity"].apply(lambda s: tv(s, lang))
            fig_inc = px.bar(
                df_inc,
                x="Date",
                y="NumberAffected",
                color="SeverityDisplay",
                title=_lbl(lang, "Incident Affected Counts by Observation Date", "తేదీ వారీగా సంఘటన ప్రభావిత సంఖ్య"),
                labels={
                    "Date": _lbl(lang, "Date", "తేదీ"),
                    "NumberAffected": _lbl(lang, "Affected Count", "ప్రభావిత సంఖ్య"),
                    "SeverityDisplay": _lbl(lang, "Severity", "తీవ్రత")
                }
            )
            fig_inc.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_inc, use_container_width=True)
        else:
            st.caption(_lbl(lang, "No incidents recorded.", "సంఘటనలు నమోదు కాలేదు."))

    # 7. Financial Analytics
    with tabs[6]:
        st.markdown(f"#### {_lbl(lang, 'Financial Economics & Cash Realization', 'ఆర్థిక విశ్లేషణ మరియు నగదు రాబడి')}")
        if expenses and sales:
            df_e = pd.DataFrame(expenses)
            df_s = pd.DataFrame(sales)
            tot_e = df_e["Amount"].sum()
            tot_s = df_s["TotalRevenue"].sum()
            cat_col = _lbl(lang, "Category", "విభాగం")
            amt_col = _lbl(lang, "Amount (₹)", "మొత్తం (₹)")
            df_comp = pd.DataFrame({
                cat_col: [_lbl(lang, "Total Expenses", "మొత్తం ఖర్చులు"), _lbl(lang, "Total Revenue", "మొత్తం ఆదాయం")],
                amt_col: [tot_e, tot_s]
            })
            fig_fin = px.bar(
                df_comp,
                x=cat_col,
                y=amt_col,
                color=cat_col,
                title=_lbl(lang, "Expenditure vs Realized Revenue (₹)", "ఖర్చులు vs సాధించిన ఆదాయం (₹)")
            )
            fig_fin.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.caption(_lbl(lang, "Record financial transactions to generate cash flow comparisons.", "నగదు ప్రవాహ పోలికలను చూడటానికి ఆర్థిక లావాదేవీలను నమోదు చేయండి."))
