"""
AquaMitra Alerts View Module
Provides Active Alerts, All Alerts, and Resolved Alerts with strictly zero emojis.
"""

import streamlit as st
import pandas as pd
from components.cards import render_alert_card, render_empty_state
from services.ai.ai_service import explain_alert


def render_alerts_view():
    subtabs = ["Active Alerts", "All Alerts", "Resolved"]
    tabs = st.tabs(subtabs)

    alerts = st.session_state.get("demo_alerts", [])
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Active Alerts
    with tabs[0]:
        st.markdown("#### Active & Unresolved Decision-Support Alerts")
        active = [a for a in alerts if not a.get("IsResolved")]

        if active:
            for a in active:
                col_card, col_ai = st.columns([4, 1])
                with col_card:
                    res = render_alert_card(a, show_action=True)
                    if res:
                        a["IsResolved"] = True
                        st.success("Alert resolved.")
                        st.rerun()
                with col_ai:
                    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                    if st.button("Explain with AI", key=f"ai_exp_al_{a['AlertID']}", use_container_width=True):
                        st.session_state[f"exp_al_{a['AlertID']}"] = True

                if st.session_state.get(f"exp_al_{a['AlertID']}", False):
                    clean_exp = explain_alert(a).replace("🤖", "").replace("💡", "").replace("🔔", "").strip()
                    st.info(clean_exp)
        else:
            render_empty_state("Alerts", "All Clear", "Zero active alerts currently detected. All parameters within configured reference bounds.")

    # 2. All Alerts
    with tabs[1]:
        st.markdown("#### All Farm Alerts")
        c1, c2, c3 = st.columns(3)
        with c1:
            sev_f = st.selectbox("Filter Severity", options=["All", "HIGH", "WARNING", "INFO"])
        with c2:
            cat_f = st.selectbox("Filter Category", options=["All", "Water Quality", "Mortality", "Weather", "Feeding"])
        with c3:
            p_f = st.selectbox("Filter Pond", options=["All"] + [p["PondID"] for p in ponds])

        filt_alerts = alerts
        if sev_f != "All":
            filt_alerts = [a for a in filt_alerts if a.get("Severity") == sev_f]
        if cat_f != "All":
            filt_alerts = [a for a in filt_alerts if a.get("Category") == cat_f]
        if p_f != "All":
            filt_alerts = [a for a in filt_alerts if a.get("PondID") == p_f]

        if filt_alerts:
            df_fa = pd.DataFrame(filt_alerts)
            a_cols = ["AlertID", "Date", "Category", "PondID", "Severity", "Title", "Reason", "SuggestedAction", "IsResolved"]
            for col in a_cols:
                if col not in df_fa.columns:
                    df_fa[col] = ""
            st.dataframe(df_fa[a_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Alerts", "No Matching Alerts", "No alerts match the selected filters.")

    # 3. Resolved Alerts
    with tabs[2]:
        st.markdown("#### Resolved Alerts Archive")
        resolved = [a for a in alerts if a.get("IsResolved")]
        if resolved:
            df_res = pd.DataFrame(resolved)
            res_cols = ["AlertID", "Date", "Category", "PondID", "Title", "Reason", "SuggestedAction"]
            for col in res_cols:
                if col not in df_res.columns:
                    df_res[col] = ""
            st.dataframe(df_res[res_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Alerts", "No Resolved Alerts", "Resolved alerts will appear here.")
