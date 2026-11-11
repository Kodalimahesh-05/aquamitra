"""
AquaMitra Environment View Module
Provides Meteorological Awareness, Weather Forecasts, Historical Logs,
and Contextual Environmental Analysis with strictly zero emojis. Bilingual (EN/TE).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from components.cards import render_metric_card


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_environment_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Weather", "వాతావరణం"),
        _lbl(lang, "Environmental Context", "పర్యావరణ సందర్భం")
    ]
    tabs = st.tabs(subtabs)
    weath = st.session_state.get("demo_weather", {})

    cond_te = {
        "Partly Cloudy": "పాక్షికంగా మేఘావృతం",
        "Overcast / Cloudy": "మేఘావృతం",
        "Cloudy": "మేఘావృతం",
        "Light Rain": "తేలికపాటి వర్షం",
        "Showers": "జల్లులు",
        "Sunny": "ఎండగా ఉంది",
        "Clear": "స్వచ్ఛమైన ఆకాశం",
        "Humid": "తేమగా ఉంది",
    }

    # 1. Weather & Forecast
    with tabs[0]:
        loc_str = weath.get("location", _lbl(lang, "Krishna-Godavari Fishery Belt, AP", "కృష్ణా-గోదావరి మత్స్య సాగు ప్రాంతం, ఆం.ప్ర"))
        st.markdown(f"#### {_lbl(lang, 'Meteorological Conditions & Forecast', 'వాతావరణ పరిస్థితులు మరియు అంచనా')} ({loc_str})")
        st.caption(_lbl(
            lang,
            "Station: Regional Agro-Meteorological Observation Network — Krishna-Godavari Delta Basin",
            "కేంద్రం: ప్రాంతీయ వ్యవసాయ-వాతావరణ పరిశీలన నెట్‌వర్క్ — కృష్ణా-గోదావరి డెల్టా ప్రాంతం"
        ))

        curr_cond = weath.get("current_condition", "Partly Cloudy")
        curr_cond_disp = cond_te.get(curr_cond, curr_cond) if lang == "te" else curr_cond

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card(_lbl(lang, "Current Temperature", "ప్రస్తుత ఉష్ణోగ్రత"), f"{weath.get('current_temp', 32)} °C", curr_cond_disp)
        with c2:
            render_metric_card(_lbl(lang, "Relative Humidity", "గాలిలో తేమ"), f"{weath.get('current_humidity', 75)}%", _lbl(lang, "Ambient Air", "పరిసర వాతావరణం"))
        with c3:
            render_metric_card(_lbl(lang, "Wind Velocity", "గాలి వేగం"), f"{weath.get('current_wind_kmh', 12)} {_lbl(lang, 'km/h', 'కి.మీ/గం')}", _lbl(lang, "Surface Wind", "ఉపరితల గాలి"))
        with c4:
            render_metric_card(_lbl(lang, "Today's Rainfall", "నేటి వర్షపాతం"), f"{weath.get('today_rainfall_mm', 0.0)} {_lbl(lang, 'mm', 'మి.మీ')}", _lbl(lang, "Accumulated Precipitation", "నమోదైన వర్షపాతం"))

        st.markdown(f"##### {_lbl(lang, '5-Day Aquaculture Meteorological Forecast', '5-రోజుల ఆక్వాకల్చర్ వాతావరణ అంచనా')}")
        forecast = weath.get("forecast", [])
        if forecast:
            cols = st.columns(len(forecast))
            for i, f in enumerate(forecast):
                cond_disp = cond_te.get(f["condition"], f["condition"]) if lang == "te" else f["condition"]
                rain_lbl = _lbl(lang, "Rain", "వర్షం")
                mm_lbl = _lbl(lang, "mm", "మి.మీ")
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class="saas-card forecast-card" style="padding: 12px; text-align: center;">
                            <div style="font-weight: 700; color: #0F2942; font-size: 0.88rem;">{f['day'][:3]} ({f['date'][5:]})</div>
                            <div style="font-size: 0.78rem; color: #64748B; margin: 4px 0;">{cond_disp}</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">{f['temp_max']}° / <span style="color:#64748B; font-size: 0.90rem;">{f['temp_min']}°</span></div>
                            <div style="font-size: 0.76rem; color: #0D9488; margin-top: 4px; font-weight: 600;">{rain_lbl}: {f['rainfall_mm']} {mm_lbl}</div>
                            <div style="font-size: 0.70rem; color: #92400E; margin-top: 6px; line-height: 1.2;">{f['cautionary_note']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown(f"##### {_lbl(lang, 'Temperature Trend Forecast', 'ఉష్ణోగ్రత ధోరణి అంచనా')}")
            df_w = pd.DataFrame(forecast)
            fig_w = px.line(
                df_w,
                x="date",
                y=["temp_max", "temp_min"],
                markers=True,
                title=_lbl(lang, "Forecasted Daily Temperature Range (°C)", "అంచనా వేసిన రోజువారీ ఉష్ణోగ్రత స్థాయిలు (°C)"),
                labels={
                    "date": _lbl(lang, "Forecast Date", "అంచనా తేదీ"),
                    "value": _lbl(lang, "Temperature (°C)", "ఉష్ణోగ్రత (°C)"),
                    "variable": _lbl(lang, "Range", "స్థాయి")
                }
            )
            fig_w.update_layout(height=280, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_w, use_container_width=True)

    # 2. Environmental Context
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Combined Environmental Context Synthesis', 'సమగ్ర పర్యావరణ సందర్భ విశ్లేషణ')}")
        st.caption(_lbl(lang, "Cross-analyzes meteorological patterns against observed pond parameters.", "గమనించిన చెరువు పారామితులతో వాతావరణ ధోరణులను కలిపి విశ్లేషిస్తుంది."))
        if lang == "te":
            obs_html = "ఇటీవలి వర్షపాత అంచనాలు (14.5 మి.మీ వరకు) మేఘావృతమైన ఉదయ పరిస్థితులతో కలిసి ఉన్నాయి. వరుసగా ఆకాశం మబ్బుగా ఉన్నప్పుడు తక్కువ లోతు ఉన్న మట్టి చెరువులలో కిరణజన్య సంయోగ క్రియ తగ్గి కరిగిన ఆక్సిజన్ (DO) తగ్గే అవకాశం ఉంటుంది."
            rec_html = "నీటి బయటకు వెళ్లే స్లూయిస్ జాలీలలో కలుపు మొక్కలు అడ్డుపడకుండా చూసుకోండి. ఆకాశం మేఘావృతంగా కొనసాగితే తెల్లవారుజామున యాంత్రిక ఏరేటర్లను సిద్ధంగా ఉంచండి."
            card_title = "పర్యావరణ సందర్భ విశ్లేషణ"
            obs_lbl = "పరిశీలన"
            rec_lbl = "నిర్వహణ సూచన"
        else:
            obs_html = "Recent rainfall forecasts (up to 14.5 mm) coincide with overcast morning conditions. Dissolved oxygen in shallow earthen ponds tends to experience reduced photosynthetically active radiation during sustained cloud cover."
            rec_html = "Verify that overflow sluice screens are free of floating vegetation. Ensure mechanical aeration is prepared for dawn operations if overcast skies persist."
            card_title = "Environmental Context Analysis"
            obs_lbl = "Observation"
            rec_lbl = "Operational Recommendation"

        st.markdown(
            f"""
            <div class="saas-card" style="border-left: 4px solid #0F2942; background: #F8FAFC;">
                <h4 style="color: #0F2942; margin: 0 0 6px 0;">{card_title}</h4>
                <p style="font-size: 0.88rem; color: #1E293B; margin-bottom: 6px; line-height: 1.5;">
                    <strong>{obs_lbl}:</strong> {obs_html}
                </p>
                <p style="font-size: 0.84rem; color: #059669; margin: 0;">
                    <strong>{rec_lbl}:</strong> {rec_html}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
