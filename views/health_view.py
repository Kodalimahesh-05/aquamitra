"""
AquaMitra Health & Incidents View Module
Provides Incident Management, Mortality Logger, Daily Behavioural Observations,
and Follow-ups with responsible, non-diagnostic AI analysis.
Strictly zero emojis.
"""

from datetime import date
import streamlit as st
import pandas as pd
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_incident
from services.ai.ai_service import analyze_incident
from database.queries import get_incidents
from utils.constants import DISCLAIMER_TEXT


def render_health_view():
    subtabs = ["Incidents", "Mortality", "Observations", "Follow-ups"]
    tabs = st.tabs(subtabs)

    incidents = get_incidents()
    mortalities = st.session_state.get("demo_mortality", [])
    ponds = st.session_state.get("demo_ponds", [])

    st.caption("Responsible record management for unexpected pond events. AquaMitra records observations and does not provide veterinary medical diagnosis.")

    # 1. Incidents
    with tabs[0]:
        st.markdown("#### Health Observations & Incident Registry")
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button("Log New Incident", type="primary", use_container_width=True):
                dialog_add_incident()

        if incidents:
            df_inc = pd.DataFrame(incidents)
            if "Date" in df_inc.columns:
                df_inc = df_inc.sort_values("Date", ascending=False)
            inc_cols = ["IncidentID", "PondID", "Date", "IncidentType", "NumberAffected", "Severity", "Description", "ActionTaken", "Status", "FollowUpDate"]
            for col in inc_cols:
                if col not in df_inc.columns:
                    df_inc[col] = ""
            st.dataframe(df_inc[inc_cols], use_container_width=True, hide_index=True)

            with st.expander("AI Incident Contextual Analysis"):
                sel_inc_id = st.selectbox("Select Incident to Analyze", options=[i.get("IncidentID") for i in incidents])
                if st.button("Analyze Selected Incident with AI", type="secondary"):
                    res = analyze_incident(sel_inc_id, st.session_state)
                    clean_obs = res['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                    clean_tr = res['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                    clean_ck = res['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                    st.info(f"**Observed:** {clean_obs}\n\n**Contextual Association:** {clean_tr}\n\n**Suggested Action:** {clean_ck}\n\n*{res['data_limitations']}*")
        else:
            render_empty_state("Health", "All Clear", "No unusual incidents have been recorded.", "Log Incident", "rec_inc_btn")

    # 2. Mortality
    with tabs[1]:
        st.markdown("#### Fish Mortality Observations")
        tot_dead = sum(m.get("NumberOfDead", 0) for m in mortalities)
        c1, c2 = st.columns(2)
        with c1:
            render_metric_card("Total Recorded Dead Fish", f"{tot_dead}", "Across Observed Batches")
        with c2:
            render_metric_card("Mortality Incident Count", f"{len(mortalities)}", "Logged in Incident Register")

        if mortalities:
            df_mort = pd.DataFrame(mortalities)
            mort_cols = ["IncidentID", "PondID", "IncidentDate", "NumberOfDead", "EstimatedMortalityPercent", "ObservedBehaviour", "VisibleSymptoms", "WaterCondition", "Remarks"]
            for col in mort_cols:
                if col not in df_mort.columns:
                    df_mort[col] = ""
            st.dataframe(df_mort[mort_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Health", "Zero Mortality", "No dead fish recorded in current observations.")

    # 3. Observations
    with tabs[2]:
        st.markdown("#### Daily Behavioural & Vitality Observations")
        obs_rows = []
        for i in incidents:
            obs_rows.append({
                "Date": i.get("Date"),
                "PondID": i.get("PondID"),
                "Observed Behaviour": i.get("ObservedBehaviour"),
                "Visible Symptoms": i.get("VisibleObservation"),
                "Water Appearance": i.get("WaterCondition"),
                "Weather": i.get("WeatherCondition")
            })
        if obs_rows:
            st.dataframe(pd.DataFrame(obs_rows), use_container_width=True, hide_index=True)
        else:
            render_empty_state("Observations", "No Behavioural Notes", "Daily vitality observations will appear here.")

    # 4. Follow-ups
    with tabs[3]:
        st.markdown("#### Pending Follow-ups & Monitoring Schedules")
        follow_rows = [i for i in incidents if i.get("Status") in ["Open", "Monitoring"]]
        if follow_rows:
            st.dataframe(pd.DataFrame(follow_rows)[["IncidentID", "PondID", "IncidentType", "Severity", "ActionTaken", "FollowUpDate", "Status"]], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Follow-ups", "All Follow-ups Cleared", "No incidents currently require pending review.")
