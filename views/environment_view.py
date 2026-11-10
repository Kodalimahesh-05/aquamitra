"""
AquaMitra Environment View Module
Provides Meteorological Awareness, Weather Forecasts, Historical Logs,
and Contextual Environmental Analysis with strictly zero emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from components.cards import render_metric_card


def render_environment_view():
    subtabs = ["Weather", "Environmental Context"]
    tabs = st.tabs(subtabs)
    weath = st.session_state.get("demo_weather", {})

    # 1. Weather & Forecast
    with tabs[0]:
        st.markdown(f"#### Meteorological Conditions & Forecast ({weath.get('location', 'Krishna-Godavari Fishery Belt, AP')})")
        st.caption("Station: Regional Agro-Meteorological Observation Network — Krishna-Godavari Delta Basin")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Current Temperature", f"{weath.get('current_temp', 32)} °C", weath.get("current_condition", "Partly Cloudy"))
        with c2:
            render_metric_card("Relative Humidity", f"{weath.get('current_humidity', 75)}%", "Ambient Air")
        with c3:
            render_metric_card("Wind Velocity", f"{weath.get('current_wind_kmh', 12)} km/h", "Surface Wind")
        with c4:
            render_metric_card("Today's Rainfall", f"{weath.get('today_rainfall_mm', 0.0)} mm", "Accumulated Precipitation")

        st.markdown("##### 5-Day Aquaculture Meteorological Forecast")
        forecast = weath.get("forecast", [])
        if forecast:
            cols = st.columns(len(forecast))
            for i, f in enumerate(forecast):
                with cols[i]:
                    st.markdown(
                        f"""
                        <div class="saas-card" style="padding: 12px; text-align: center;">
                            <div style="font-weight: 700; color: #0F2942; font-size: 0.88rem;">{f['day'][:3]} ({f['date'][5:]})</div>
                            <div style="font-size: 0.78rem; color: #64748B; margin: 4px 0;">{f['condition']}</div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">{f['temp_max']}° / <span style="color:#64748B; font-size: 0.90rem;">{f['temp_min']}°</span></div>
                            <div style="font-size: 0.76rem; color: #0D9488; margin-top: 4px; font-weight: 600;">Rain: {f['rainfall_mm']} mm</div>
                            <div style="font-size: 0.70rem; color: #92400E; margin-top: 6px; line-height: 1.2;">{f['cautionary_note']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("##### Temperature Trend Forecast")
            df_w = pd.DataFrame(forecast)
            fig_w = px.line(
                df_w,
                x="date",
                y=["temp_max", "temp_min"],
                markers=True,
                title="Forecasted Daily Temperature Range (°C)",
                labels={"date": "Forecast Date", "value": "Temperature (°C)", "variable": "Range"}
            )
            fig_w.update_layout(height=280, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.15))
            st.plotly_chart(fig_w, use_container_width=True)

    # 2. Environmental Context
    with tabs[1]:
        st.markdown("#### Combined Environmental Context Synthesis")
        st.caption("Cross-analyzes meteorological patterns against observed pond parameters.")
        st.markdown(
            """
            <div class="saas-card" style="border-left: 4px solid #0F2942; background: #F8FAFC;">
                <h4 style="color: #0F2942; margin: 0 0 6px 0;">Environmental Context Analysis</h4>
                <p style="font-size: 0.88rem; color: #1E293B; margin-bottom: 6px; line-height: 1.5;">
                    <strong>Observation:</strong> Recent rainfall forecasts (up to 14.5 mm) coincide with overcast morning conditions. 
                    Dissolved oxygen in shallow earthen ponds tends to experience reduced photosynthetically active radiation during sustained cloud cover.
                </p>
                <p style="font-size: 0.84rem; color: #059669; margin: 0;">
                    <strong>Operational Recommendation:</strong> Verify that overflow sluice screens are free of floating vegetation. 
                    Ensure mechanical aeration is prepared for dawn operations if overcast skies persist.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
