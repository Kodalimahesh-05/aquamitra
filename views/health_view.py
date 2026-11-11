"""
AquaMitra Health & Incidents View Module
Provides Incident Management, Mortality Logger, Daily Behavioural Observations,
and Follow-ups with responsible, non-diagnostic AI analysis.
Strictly zero emojis. Fully bilingual (EN/TE).
"""

import streamlit as st
import pandas as pd
from utils.translations import rename_df_for_display
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_incident
from services.ai.ai_service import analyze_incident
from database.queries import get_incidents


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_health_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Incidents", "సంఘటనలు"),
        _lbl(lang, "Mortality", "మరణాలు"),
        _lbl(lang, "Observations", "పరిశీలనలు"),
        _lbl(lang, "Follow-ups", "తదుపరి తనిఖీలు")
    ]
    tabs = st.tabs(subtabs)

    incidents = get_incidents()
    mortalities = st.session_state.get("demo_mortality", [])

    st.caption(_lbl(
        lang,
        "Responsible record management for unexpected pond events. AquaMitra records observations and does not provide veterinary medical diagnosis.",
        "అనూహ్య చెరువు సంఘటనల బాధ్యతాయుత రికార్డు నిర్వహణ. ఆక్వామిత్ర పరిశీలనలను మాత్రమే నమోదు చేస్తుంది మరియు పశువైద్య నిర్ధారణ చేయదు."
    ))

    # 1. Incidents
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Health Observations & Incident Registry', 'ఆరోగ్య పరిశీలనలు మరియు సంఘటనల రిజిస్ట్రీ')}")
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button(_lbl(lang, "Log New Incident", "కొత్త సంఘటన నమోదు"), type="primary", use_container_width=True):
                dialog_add_incident()

        if incidents:
            df_inc = pd.DataFrame(incidents)
            if "Date" in df_inc.columns:
                df_inc = df_inc.sort_values("Date", ascending=False)
            inc_cols = ["IncidentID", "PondID", "Date", "IncidentType", "NumberAffected", "Severity", "Description", "ActionTaken", "Status", "FollowUpDate"]
            for col in inc_cols:
                if col not in df_inc.columns:
                    df_inc[col] = ""
            st.dataframe(rename_df_for_display(df_inc[inc_cols], lang), use_container_width=True, hide_index=True)

            with st.expander(_lbl(lang, "AI Incident Contextual Analysis", "AI సంఘటన సందర్భ విశ్లేషణ")):
                sel_inc_id = st.selectbox(_lbl(lang, "Select Incident to Analyze", "విశ్లేషించాల్సిన సంఘటనను ఎంచుకోండి"), options=[i.get("IncidentID") for i in incidents])
                if st.button(_lbl(lang, "Analyze Selected Incident with AI", "ఎంచుకున్న సంఘటనను AI తో విశ్లేషించండి"), type="secondary"):
                    res = analyze_incident(sel_inc_id, st.session_state)
                    clean_obs = res['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                    clean_tr = res['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                    clean_ck = res['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                    st.info(
                        f"**{_lbl(lang, 'Observed', 'గమనించినది')}:** {clean_obs}\n\n"
                        f"**{_lbl(lang, 'Contextual Association', 'సందర్భ సంబంధం')}:** {clean_tr}\n\n"
                        f"**{_lbl(lang, 'Suggested Action', 'సూచించిన చర్య')}:** {clean_ck}\n\n"
                        f"*{res['data_limitations']}*"
                    )
        else:
            render_empty_state(
                _lbl(lang, "Health", "ఆరోగ్యం"),
                _lbl(lang, "All Clear", "అన్నీ సాధారణంగా ఉన్నాయి"),
                _lbl(lang, "No unusual incidents have been recorded.", "అసాధారణ సంఘటనలు ఏవీ నమోదు కాలేదు."),
                _lbl(lang, "Log Incident", "సంఘటన నమోదు"),
                "rec_inc_btn"
            )

    # 2. Mortality
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Fish Mortality Observations', 'చేపల మరణాల పరిశీలనలు')}")
        tot_dead = sum(m.get("NumberOfDead", 0) for m in mortalities)
        c1, c2 = st.columns(2)
        with c1:
            render_metric_card(
                _lbl(lang, "Total Recorded Dead Fish", "మొత్తం నమోదైన చేపల మరణాలు"),
                f"{tot_dead}",
                _lbl(lang, "Across Observed Batches", "పరిశీలించిన బ్యాచ్‌ల అంతటా")
            )
        with c2:
            render_metric_card(
                _lbl(lang, "Mortality Incident Count", "మరణ సంఘటనల సంఖ్య"),
                f"{len(mortalities)}",
                _lbl(lang, "Logged in Incident Register", "సంఘటన రిజిస్టర్‌లో నమోదైనవి")
            )

        if mortalities:
            df_mort = pd.DataFrame(mortalities)
            mort_cols = ["IncidentID", "PondID", "IncidentDate", "NumberOfDead", "EstimatedMortalityPercent", "ObservedBehaviour", "VisibleSymptoms", "WaterCondition", "Remarks"]
            for col in mort_cols:
                if col not in df_mort.columns:
                    df_mort[col] = ""
            disp_m = rename_df_for_display(df_mort[mort_cols], lang)
            if lang == "te":
                disp_m = disp_m.rename(columns={
                    "NumberOfDead": "చనిపోయిన సంఖ్య",
                    "EstimatedMortalityPercent": "అంచనా మరణ శాతం (%)",
                    "VisibleSymptoms": "కనిపించే లక్షణాలు",
                    "WaterCondition": "నీటి స్థితి",
                    "Remarks": "వ్యాఖ్యలు"
                })
            st.dataframe(disp_m, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Health", "ఆరోగ్యం"),
                _lbl(lang, "Zero Mortality", "మరణాలు లేవు"),
                _lbl(lang, "No dead fish recorded in current observations.", "ప్రస్తుత పరిశీలనలలో చేపల మరణాలు నమోదు కాలేదు.")
            )

    # 3. Observations
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Daily Behavioural & Vitality Observations', 'రోజువారీ ప్రవర్తన మరియు చురుకుదనం పరిశీలనలు')}")
        obs_rows = []
        for i in incidents:
            obs_rows.append({
                _lbl(lang, "Date", "తేదీ"): i.get("Date"),
                "PondID": i.get("PondID"),
                _lbl(lang, "Observed Behaviour", "గమనించిన ప్రవర్తన"): i.get("ObservedBehaviour"),
                _lbl(lang, "Visible Symptoms", "కనిపించే లక్షణాలు"): i.get("VisibleObservation"),
                _lbl(lang, "Water Appearance", "నీటి రూపం"): i.get("WaterCondition"),
                _lbl(lang, "Weather", "వాతావరణం"): i.get("WeatherCondition")
            })
        if obs_rows:
            st.dataframe(rename_df_for_display(pd.DataFrame(obs_rows), lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Observations", "పరిశీలనలు"),
                _lbl(lang, "No Behavioural Notes", "ప్రవర్తన గమనికలు లేవు"),
                _lbl(lang, "Daily vitality observations will appear here.", "రోజువారీ చురుకుదనం పరిశీలనలు ఇక్కడ కనిపిస్తాయి.")
            )

    # 4. Follow-ups
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Pending Follow-ups & Monitoring Schedules', 'పెండింగ్ తదుపరి తనిఖీలు మరియు షెడ్యూల్‌లు')}")
        follow_rows = [i for i in incidents if i.get("Status") in ["Open", "Monitoring"]]
        if follow_rows:
            f_df = pd.DataFrame(follow_rows)[["IncidentID", "PondID", "IncidentType", "Severity", "ActionTaken", "FollowUpDate", "Status"]]
            st.dataframe(rename_df_for_display(f_df, lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Follow-ups", "తదుపరి తనిఖీలు"),
                _lbl(lang, "All Follow-ups Cleared", "అన్ని తనిఖీలు పూర్తయ్యాయి"),
                _lbl(lang, "No incidents currently require pending review.", "ప్రస్తుతం పెండింగ్ సమీక్ష అవసరమైన సంఘటనలు లేవు.")
            )
