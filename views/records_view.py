"""
AquaMitra Records View Module
Provides Unified Recent Activity, All Records Master Search, and Data Health Audit.
Strictly zero emojis. Fully bilingual (EN/TE).
"""

import streamlit as st
import pandas as pd
from utils.translations import tv, rename_df_for_display
from utils.demo_data import get_unified_recent_activity
from components.cards import render_activity_feed, render_metric_card
from database.queries import (
    get_fish_stocks,
    get_water_quality,
    get_feeding_records,
    get_growth_records,
    get_incidents,
    get_expenses,
    get_sales,
    get_maintenance_records,
    get_data_health
)


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_records_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Recent Activity", "ఇటీవలి కార్యకలాపాలు"),
        _lbl(lang, "All Records", "అన్ని రికార్డులు"),
        _lbl(lang, "Data Health", "డేటా ఆరోగ్యం")
    ]
    tabs = st.tabs(subtabs)
    ponds = st.session_state.get("demo_ponds", [])

    rec_types_te = {
        "Water Quality Observations": "నీటి నాణ్యత పరిశీలనలు",
        "Daily Feeding Logs": "రోజువారీ మేత లాగ్‌లు",
        "Fish Growth Samplings": "చేపల పెరుగుదల నమూనాలు",
        "Fish Stocking Batches": "చేప పిల్లల నిల్వ బ్యాచ్‌లు",
        "Incidents & Health": "సంఘటనలు మరియు ఆరోగ్యం",
        "Expenses Ledger": "ఖర్చుల ఖాతా",
        "Sales Records": "అమ్మకాల రికార్డులు",
        "Maintenance Logs": "నిర్వహణ లాగ్‌లు",
    }

    # 1. Recent Activity
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Unified Chronological Farm Activity', 'సమగ్ర కాలక్రమానుసార ఫార్మ్ కార్యకలాపాలు')}")
        sel_p = st.selectbox(
            _lbl(lang, "Filter Activity Feed", "కార్యాచరణ ఫీడ్ వడపోత"),
            options=["All Ponds"] + [p["PondID"] for p in ponds],
            key="rec_act_sel",
            format_func=lambda x: tv(x, lang)
        )
        target_p = None if sel_p == "All Ponds" else sel_p
        acts = get_unified_recent_activity(pond_id=target_p, limit=25)
        render_activity_feed(acts)

    # 2. All Records Master Archive
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Centralized Records Search & Archive', 'కేంద్రీకృత రికార్డుల శోధన & ఆర్కైవ్')}")
        rec_type = st.selectbox(
            _lbl(lang, "Select Record Category", "రికార్డు విభాగాన్ని ఎంచుకోండి"),
            options=[
                "Water Quality Observations",
                "Daily Feeding Logs",
                "Fish Growth Samplings",
                "Fish Stocking Batches",
                "Incidents & Health",
                "Expenses Ledger",
                "Sales Records",
                "Maintenance Logs"
            ],
            format_func=lambda x: rec_types_te.get(x, x) if lang == "te" else x
        )

        if rec_type == "Water Quality Observations":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_water_quality()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Daily Feeding Logs":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_feeding_records()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Fish Growth Samplings":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_growth_records()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Fish Stocking Batches":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_fish_stocks()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Incidents & Health":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_incidents()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Expenses Ledger":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_expenses()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Sales Records":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_sales()), lang), use_container_width=True, hide_index=True)
        elif rec_type == "Maintenance Logs":
            st.dataframe(rename_df_for_display(pd.DataFrame(get_maintenance_records()), lang), use_container_width=True, hide_index=True)

    # 3. Data Health Section
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Data Health & Record Completeness Audit', 'డేటా ఆరోగ్యం మరియు రికార్డుల పూర్తిస్థాయి ఆడిట్')}")
        st.caption(_lbl(
            lang,
            "Evaluates documentation coverage across pond units. Does not judge biological health.",
            "చెరువు యూనిట్లలో రికార్డుల నమోదు శాతాన్ని పరిశీలిస్తుంది. ఇది జీవ ఆరోగ్య నిర్ధారణ కాదు."
        ))

        health_data = get_data_health()
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card(
                _lbl(lang, "Complete Documentation", "సంపూర్ణ నమోదు"),
                f"{health_data['complete_count']} / {health_data['total_ponds']}",
                _lbl(lang, "All 5 Core Domains Logged", "మొత్తం 5 ప్రధాన విభాగాలు నమోదయ్యాయి")
            )
        with c2:
            render_metric_card(
                _lbl(lang, "Partial Records", "పాక్షిక రికార్డులు"),
                f"{health_data['partial_count']}",
                _lbl(lang, "Active Observations Present", "క్రియాశీల పరిశీలనలు ఉన్నాయి"),
                value_color="#D97706"
            )
        with c3:
            render_metric_card(
                _lbl(lang, "Missing Records", "లోపించిన రికార్డులు"),
                f"{health_data['missing_count']}",
                _lbl(lang, "Gaps Requiring Entry", "నమోదు అవసరమైన అంశాలు"),
                value_color="#DC2626" if health_data['missing_count'] else "#059669"
            )

        st.markdown(f"##### {_lbl(lang, 'Pond Record Audit Breakdown', 'చెరువు వారీ రికార్డు ఆడిట్ వివరాలు')}")
        df_health = pd.DataFrame(health_data["pond_audits"])
        disp_h = rename_df_for_display(df_health[["PondID", "PondName", "Status", "RecordedItems", "TotalTracked", "MissingDomains"]], lang)
        if lang == "te":
            disp_h = disp_h.rename(columns={
                "RecordedItems": "నమోదైన అంశాలు",
                "TotalTracked": "మొత్తం ట్రాక్ చేసినవి",
                "MissingDomains": "లోపించిన విభాగాలు"
            })
        st.dataframe(disp_h, use_container_width=True, hide_index=True)
