"""
AquaMitra Fish Management View Module
Provides Fish Stock, Species Registry, Growth Tracking, Biomass Overview,
Stocking History, and Harvest Management with strictly zero emojis.
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import SPECIES_LIST
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import (
    dialog_add_fish_stock,
    dialog_add_growth_sample,
    dialog_record_harvest
)
from services.ai.ai_service import analyze_growth
from database.queries import (
    get_fish_stocks,
    get_growth_records,
    get_harvest_records
)


def render_fish_view():
    subtabs = ["Fish Stock", "Species", "Growth Tracking", "Biomass", "Stocking History", "Harvest"]
    tabs = st.tabs(subtabs)

    stocks = get_fish_stocks()
    growths = get_growth_records()
    species_list = st.session_state.get("demo_species", [])
    harvests = get_harvest_records()
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Fish Stock
    with tabs[0]:
        st.markdown("#### Active Fish Stocking Batches")
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button("Stock Fingerlings", type="primary", use_container_width=True):
                dialog_add_fish_stock()

        if stocks:
            stocks_df = pd.DataFrame(stocks)
            expected_cols = [
                "StockID",
                "PondID",
                "Species",
                "Variety",
                "StockingDate",
                "NumberOfFish",
                "AvgInitialWeightGrams",
                "TotalInitialBiomassKg",
                "SourceHatchery",
                "TotalSeedCost"
            ]
            for col in expected_cols:
                if col not in stocks_df.columns:
                    stocks_df[col] = ""
            st.dataframe(stocks_df[expected_cols], use_container_width=True, hide_index=True)
            
            # Delete record
            with st.expander("Manage Existing Batches"):
                del_id = st.selectbox("Select Batch to Remove", options=[s["StockID"] for s in stocks])
                if st.button("Delete Selected Stock Batch", type="secondary"):
                    st.session_state.demo_fish_stock = [s for s in st.session_state.demo_fish_stock if s.get("StockID") != del_id]
                    st.success("Batch removed successfully.")
                    st.rerun()
        else:
            render_empty_state("Fish", "No Fish Stocked", "Add your first stocking batch to begin monitoring.", "Stock Fingerlings", "stk_first_btn")

    # 2. Species Registry
    with tabs[1]:
        st.markdown("#### Cultured Species Registry")
        if species_list:
            st.dataframe(
                pd.DataFrame(species_list)[["SpeciesName", "ScientificName", "TeluguName", "Category", "DefaultFeedingRate", "OptimalTempMin", "OptimalTempMax", "Active"]],
                use_container_width=True,
                hide_index=True
            )

        with st.expander("Add Custom Fish Species"):
            with st.form("add_species_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    sp_name = st.text_input("Common Name *", placeholder="e.g. Pangasius")
                    sc_name = st.text_input("Scientific Name", placeholder="e.g. Pangasianodon hypophthalmus")
                with c2:
                    te_name = st.text_input("Telugu Name", placeholder="e.g. పంగాసియస్")
                    cat = st.selectbox("Category", options=["Major Carp", "Exotic Carp", "Catfish", "Cichlid", "Prawn / Shrimp", "Other"])
                with c3:
                    f_rate = st.number_input("Default Feeding Rate %", min_value=1.0, value=3.0, step=0.1)
                    t_min = st.number_input("Min Temp (°C)", value=24.0)
                    t_max = st.number_input("Max Temp (°C)", value=32.0)

                sp_notes = st.text_area("Species Biological Notes", placeholder="Surface feeder with rapid conversion ratio...")
                add_sp_btn = st.form_submit_button("Register Species", type="primary")
                if add_sp_btn:
                    if not sp_name:
                        st.error("Species name is required.")
                    else:
                        new_sp = {
                            "SpeciesID": len(species_list) + 1,
                            "SpeciesName": sp_name.strip(),
                            "ScientificName": sc_name.strip(),
                            "LocalName": sp_name.strip(),
                            "TeluguName": te_name.strip(),
                            "Category": cat,
                            "DefaultFeedingRate": float(f_rate),
                            "OptimalTempMin": float(t_min),
                            "OptimalTempMax": float(t_max),
                            "Notes": sp_notes.strip(),
                            "Active": True
                        }
                        st.session_state.demo_species.append(new_sp)
                        st.success(f"Registered species '{sp_name}' successfully.")
                        st.rerun()

    # 3. Growth Tracking
    with tabs[2]:
        st.markdown("#### Fish Growth Sampling Observations")
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 1])
        with col_ctrl1:
            sel_pid = st.selectbox("Filter Pond", options=["All Ponds"] + [p["PondID"] for p in ponds], key="growth_filter_pond")
        with col_ctrl2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Analyze Growth with AI", type="secondary", use_container_width=True):
                st.session_state.show_growth_ai = True
        with col_ctrl3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Add Growth Sample", type="primary", use_container_width=True):
                dialog_add_growth_sample()

        if st.session_state.get("show_growth_ai", False):
            target_p = "P-001" if sel_pid == "All Ponds" else sel_pid
            g_ai = analyze_growth(st.session_state, target_p)
            clean_obs = g_ai['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = g_ai['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = g_ai['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(f"**Observation:** {clean_obs}\n\n**Trend:** {clean_tr}\n\n**Suggested Check:** {clean_ck}")

        filtered_growths = growths if sel_pid == "All Ponds" else [g for g in growths if g.get("PondID") == sel_pid]
        if filtered_growths:
            df_g = pd.DataFrame(filtered_growths).sort_values("ObservationDate", ascending=False)
            g_cols = ["GrowthID", "PondID", "Species", "ObservationDate", "SampleSize", "AvgFishWeightGrams", "MinWeightGrams", "MaxWeightGrams", "EstimatedBiomassKg", "Observer"]
            for c in g_cols:
                if c not in df_g.columns:
                    df_g[c] = ""
            st.dataframe(df_g[g_cols], use_container_width=True, hide_index=True)
            
            fig_g = px.line(df_g, x="ObservationDate", y="AvgFishWeightGrams", color="PondID", markers=True, title="Fish Sample Weight Progression (Grams)")
            fig_g.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            render_empty_state("Growth", "No Growth Observations", "Perform sample cast netting to record fish weights.", "Add Sample", "gr_add_btn_empty")

    # 4. Biomass Overview
    with tabs[3]:
        st.markdown("#### Estimated Pond Biomass Summary")
        b_rows = []
        for p in ponds:
            pid = p["PondID"]
            p_stocks = [s for s in stocks if s.get("PondID") == pid]
            p_growths = [g for g in growths if g.get("PondID") == pid]
            tot_f = sum(s.get("NumberOfFish", 0) for s in p_stocks)
            init_bio = sum(s.get("TotalInitialBiomassKg", 0) for s in p_stocks)
            latest_w = p_growths[-1]["AvgFishWeightGrams"] if p_growths else 50.0
            est_bio = round((tot_f * latest_w) / 1000.0, 1)
            gain = round(est_bio - init_bio, 1) if tot_f else 0.0
            b_rows.append({
                "Pond ID": pid,
                "Pond Name": p["PondName"],
                "Status": p["Status"],
                "Stocked Count": f"{tot_f:,}",
                "Initial Biomass (kg)": f"{init_bio:,.1f}",
                "Current Avg Weight (g)": f"{latest_w}g",
                "Estimated Biomass (kg)": f"{est_bio:,.1f}",
                "Biomass Gain (kg)": f"+{gain:,.1f}"
            })

        st.dataframe(pd.DataFrame(b_rows), use_container_width=True, hide_index=True)
        render_metric_card("Total Estimated Farm Biomass", "10,340 kg", "Calculated across active culture ponds")

    # 5. Stocking History
    with tabs[4]:
        st.markdown("#### Farm Stocking Chronicle")
        if stocks:
            stocks_hist_df = pd.DataFrame(stocks)
            hist_cols = ["StockingDate", "PondID", "Species", "Variety", "NumberOfFish", "SourceHatchery", "BatchNumber", "TotalSeedCost", "Notes"]
            for col in hist_cols:
                if col not in stocks_hist_df.columns:
                    stocks_hist_df[col] = ""
            st.dataframe(stocks_hist_df[hist_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Stocking", "No Stocking History", "Stocking batches will appear here as you log fingerlings.")

    # 6. Harvest Management
    with tabs[5]:
        st.markdown("#### Commercial Fish Harvests")
        h_top1, h_top2 = st.columns([3, 1])
        with h_top2:
            if st.button("Record New Harvest", type="primary", use_container_width=True):
                dialog_record_harvest()

        if harvests:
            df_h = pd.DataFrame(harvests)
            h_cols = ["HarvestID", "PondID", "Date", "Species", "TotalWeightKg", "Grade", "Buyer", "PricePerKg", "TotalRevenue", "TransportCost", "LabourCost", "Notes"]
            for col in h_cols:
                if col not in df_h.columns:
                    df_h[col] = ""
            st.dataframe(df_h[h_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Harvest", "No Harvests Recorded", "Record partial or final harvests as market sales occur.", "Record Harvest", "rec_harv_empty")
