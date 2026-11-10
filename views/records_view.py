"""
AquaMitra Records View Module
Provides Unified Recent Activity, All Records Master Search, and Data Health Audit.
Strictly zero emojis.
"""

import streamlit as st
import pandas as pd
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


def render_records_view():
    subtabs = ["Recent Activity", "All Records", "Data Health"]
    tabs = st.tabs(subtabs)
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Recent Activity
    with tabs[0]:
        st.markdown("#### Unified Chronological Farm Activity")
        sel_p = st.selectbox("Filter Activity Feed", options=["All Ponds"] + [p["PondID"] for p in ponds], key="rec_act_sel")
        target_p = None if sel_p == "All Ponds" else sel_p
        acts = get_unified_recent_activity(pond_id=target_p, limit=25)
        render_activity_feed(acts)

    # 2. All Records Master Archive
    with tabs[1]:
        st.markdown("#### Centralized Records Search & Archive")
        rec_type = st.selectbox(
            "Select Record Category",
            options=[
                "Water Quality Observations",
                "Daily Feeding Logs",
                "Fish Growth Samplings",
                "Fish Stocking Batches",
                "Incidents & Health",
                "Expenses Ledger",
                "Sales Records",
                "Maintenance Logs"
            ]
        )

        if rec_type == "Water Quality Observations":
            st.dataframe(pd.DataFrame(get_water_quality()), use_container_width=True, hide_index=True)
        elif rec_type == "Daily Feeding Logs":
            st.dataframe(pd.DataFrame(get_feeding_records()), use_container_width=True, hide_index=True)
        elif rec_type == "Fish Growth Samplings":
            st.dataframe(pd.DataFrame(get_growth_records()), use_container_width=True, hide_index=True)
        elif rec_type == "Fish Stocking Batches":
            st.dataframe(pd.DataFrame(get_fish_stocks()), use_container_width=True, hide_index=True)
        elif rec_type == "Incidents & Health":
            st.dataframe(pd.DataFrame(get_incidents()), use_container_width=True, hide_index=True)
        elif rec_type == "Expenses Ledger":
            st.dataframe(pd.DataFrame(get_expenses()), use_container_width=True, hide_index=True)
        elif rec_type == "Sales Records":
            st.dataframe(pd.DataFrame(get_sales()), use_container_width=True, hide_index=True)
        elif rec_type == "Maintenance Logs":
            st.dataframe(pd.DataFrame(get_maintenance_records()), use_container_width=True, hide_index=True)

    # 3. Data Health Section (Requirement 32)
    with tabs[2]:
        st.markdown("#### Data Health & Record Completeness Audit")
        st.caption("Evaluates documentation coverage across pond units. Does not judge biological health.")

        health_data = get_data_health()
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card("Complete Documentation", f"{health_data['complete_count']} / {health_data['total_ponds']}", "All 5 Core Domains Logged")
        with c2:
            render_metric_card("Partial Records", f"{health_data['partial_count']}", "Active Observations Present", value_color="#D97706")
        with c3:
            render_metric_card("Missing Records", f"{health_data['missing_count']}", "Gaps Requiring Entry", value_color="#DC2626" if health_data['missing_count'] else "#059669")

        st.markdown("##### Pond Record Audit Breakdown")
        df_health = pd.DataFrame(health_data["pond_audits"])
        st.dataframe(df_health[["PondID", "PondName", "Status", "RecordedItems", "TotalTracked", "MissingDomains"]], use_container_width=True, hide_index=True)
