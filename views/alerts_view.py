"""
AquaMitra Alerts View Module
Provides Active Alerts, All Alerts, and Resolved Alerts with strictly zero emojis.
Fully bilingual (EN/TE).
"""

import streamlit as st
import pandas as pd
from utils.translations import tv, rename_df_for_display
from components.cards import render_alert_card, render_empty_state
from services.ai.ai_service import explain_alert


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_alerts_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Active Alerts", "క్రియాశీల అలర్ట్‌లు"),
        _lbl(lang, "All Alerts", "అన్ని అలర్ట్‌లు"),
        _lbl(lang, "Resolved", "పరిష్కరించబడినవి")
    ]
    tabs = st.tabs(subtabs)

    alerts = st.session_state.get("demo_alerts", [])
    ponds = st.session_state.get("demo_ponds", [])

    def _fmt_opt(val: str) -> str:
        if val == "Weather" and lang == "te":
            return "వాతావరణం"
        return tv(val, lang)

    # 1. Active Alerts
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Active & Unresolved Decision-Support Alerts', 'క్రియాశీల మరియు పరిష్కరించని నిర్ణయ-సహాయ అలర్ట్‌లు')}")
        active = [a for a in alerts if not a.get("IsResolved")]

        if active:
            for a in active:
                col_card, col_ai = st.columns([4, 1], vertical_alignment="center")
                with col_card:
                    res = render_alert_card(a, show_action=True)
                    if res:
                        a["IsResolved"] = True
                        st.success(_lbl(lang, "Alert resolved.", "అలర్ట్ పరిష్కరించబడింది."))
                        st.rerun()
                with col_ai:
                    if st.button(_lbl(lang, "Explain with AI", "AI తో వివరించండి"), key=f"ai_exp_al_{a['AlertID']}", use_container_width=True):
                        st.session_state[f"exp_al_{a['AlertID']}"] = True

                if st.session_state.get(f"exp_al_{a['AlertID']}", False):
                    clean_exp = explain_alert(a, lang=lang).replace("🤖", "").replace("💡", "").replace("🔔", "").strip()
                    st.info(clean_exp)
        else:
            render_empty_state(
                _lbl(lang, "Alerts", "అలర్ట్‌లు"),
                _lbl(lang, "All Clear", "అన్నీ సాధారణంగా ఉన్నాయి"),
                _lbl(lang, "Zero active alerts currently detected. All parameters within configured reference bounds.", "ప్రస్తుతం క్రియాశీల అలర్ట్‌లు లేవు. అన్ని పారామితులు సాధారణ పరిధులలో ఉన్నాయి.")
            )

    # 2. All Alerts
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'All Farm Alerts', 'అన్ని ఫార్మ్ అలర్ట్‌లు')}")
        c1, c2, c3 = st.columns(3)
        with c1:
            sev_f = st.selectbox(_lbl(lang, "Filter Severity", "తీవ్రత వడపోత"), options=["All", "HIGH", "WARNING", "INFO"], format_func=_fmt_opt)
        with c2:
            cat_f = st.selectbox(_lbl(lang, "Filter Category", "విభాగం వడపోత"), options=["All", "Water Quality", "Mortality", "Weather", "Feeding"], format_func=_fmt_opt)
        with c3:
            p_f = st.selectbox(_lbl(lang, "Filter Pond", "చెరువు వడపోత"), options=["All"] + [p["PondID"] for p in ponds], format_func=_fmt_opt)

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
            st.dataframe(rename_df_for_display(df_fa[a_cols], lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Alerts", "అలర్ట్‌లు"),
                _lbl(lang, "No Matching Alerts", "సరిపోలిన అలర్ట్‌లు లేవు"),
                _lbl(lang, "No alerts match the selected filters.", "ఎంచుకున్న ఫిల్టర్లకు సరిపోయే అలర్ట్‌లు లేవు.")
            )

    # 3. Resolved Alerts
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Resolved Alerts Archive', 'పరిష్కరించిన అలర్ట్‌ల ఆర్కైవ్')}")
        resolved = [a for a in alerts if a.get("IsResolved")]
        if resolved:
            df_res = pd.DataFrame(resolved)
            res_cols = ["AlertID", "Date", "Category", "PondID", "Title", "Reason", "SuggestedAction"]
            for col in res_cols:
                if col not in df_res.columns:
                    df_res[col] = ""
            st.dataframe(rename_df_for_display(df_res[res_cols], lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Alerts", "అలర్ట్‌లు"),
                _lbl(lang, "No Resolved Alerts", "పరిష్కరించిన అలర్ట్‌లు లేవు"),
                _lbl(lang, "Resolved alerts will appear here.", "పరిష్కరించిన అలర్ట్‌లు ఇక్కడ కనిపిస్తాయి.")
            )
