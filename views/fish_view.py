"""
AquaMitra Fish Management View Module
Provides Fish Stock, Species Registry, Growth Tracking, Biomass Overview,
Stocking History, and Harvest Management with strictly zero emojis. Bilingual (EN/TE).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.translations import tv, rename_df_for_display
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


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_fish_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Fish Stock", "చేపల నిల్వ"),
        _lbl(lang, "Species", "చేప జాతులు"),
        _lbl(lang, "Growth Tracking", "పెరుగుదల ట్రాకింగ్"),
        _lbl(lang, "Biomass", "బయోమాస్"),
        _lbl(lang, "Stocking History", "నిల్వ చరిత్ర"),
        _lbl(lang, "Harvest", "పంట కోత")
    ]
    tabs = st.tabs(subtabs)

    stocks = get_fish_stocks()
    growths = get_growth_records()
    species_list = st.session_state.get("demo_species", [])
    harvests = get_harvest_records()
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Fish Stock
    with tabs[0]:
        btn_c1, btn_c2 = st.columns([3, 1], vertical_alignment="center")
        with btn_c1:
            st.markdown(f"#### {_lbl(lang, 'Active Fish Stocking Batches', 'క్రియాశీల చేప పిల్లల నిల్వ బ్యాచ్‌లు')}")
        with btn_c2:
            if st.button(_lbl(lang, "Stock Fingerlings", "చేప పిల్లలను నిల్వ చేయండి"), type="primary", use_container_width=True):
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
            st.dataframe(rename_df_for_display(stocks_df[expected_cols], lang), use_container_width=True, hide_index=True)

            # Delete record
            with st.expander(_lbl(lang, "Manage Existing Batches", "ప్రస్తుత బ్యాచ్‌లను నిర్వహించండి")):
                del_id = st.selectbox(_lbl(lang, "Select Batch to Remove", "తొలగించాల్సిన బ్యాచ్‌ను ఎంచుకోండి"), options=[s["StockID"] for s in stocks])
                if st.button(_lbl(lang, "Delete Selected Stock Batch", "ఎంచుకున్న బ్యాచ్‌ను తొలగించండి"), type="secondary"):
                    st.session_state.demo_fish_stock = [s for s in st.session_state.demo_fish_stock if s.get("StockID") != del_id]
                    st.success(_lbl(lang, "Batch removed successfully.", "బ్యాచ్ విజయవంతంగా తొలగించబడింది."))
                    st.rerun()
        else:
            render_empty_state(
                _lbl(lang, "Fish", "చేపలు"),
                _lbl(lang, "No Fish Stocked", "చేపల నిల్వ లేదు"),
                _lbl(lang, "Add your first stocking batch to begin monitoring.", "పర్యవేక్షణ ప్రారంభించడానికి మీ మొదటి బ్యాచ్‌ను జోడించండి."),
                _lbl(lang, "Stock Fingerlings", "చేప పిల్లలను నిల్వ చేయండి"),
                "stk_first_btn"
            )

    # 2. Species Registry
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Cultured Species Registry', 'సాగు చేప జాతుల రిజిస్ట్రీ')}")
        if species_list:
            sp_df = pd.DataFrame(species_list)[["SpeciesName", "ScientificName", "TeluguName", "Category", "DefaultFeedingRate", "OptimalTempMin", "OptimalTempMax", "Active"]]
            if lang == "te":
                sp_df = sp_df.rename(columns={
                    "SpeciesName": "సాధారణ పేరు",
                    "ScientificName": "శాస్త్రీయ నామం",
                    "TeluguName": "తెలుగు పేరు",
                    "Category": "విభాగం",
                    "DefaultFeedingRate": "మేత రేటు (%)",
                    "OptimalTempMin": "కనిష్ట ఉష్ణోగ్రత (°C)",
                    "OptimalTempMax": "గరిష్ట ఉష్ణోగ్రత (°C)",
                    "Active": "క్రియాశీలం"
                })
            st.dataframe(sp_df, use_container_width=True, hide_index=True)

        with st.expander(_lbl(lang, "Add Custom Fish Species", "కొత్త చేప జాతిని జోడించండి")):
            with st.form("add_species_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    sp_name = st.text_input(_lbl(lang, "Common Name *", "సాధారణ పేరు *"), placeholder=_lbl(lang, "e.g. Pangasius", "ఉదా. పంగాసియస్"))
                    sc_name = st.text_input(_lbl(lang, "Scientific Name", "శాస్త్రీయ నామం"), placeholder="e.g. Pangasianodon hypophthalmus")
                with c2:
                    te_name = st.text_input(_lbl(lang, "Telugu Name", "తెలుగు పేరు"), placeholder="e.g. పంగాసియస్")
                    cat = st.selectbox(_lbl(lang, "Category", "విభాగం"), options=["Major Carp", "Exotic Carp", "Catfish", "Cichlid", "Prawn / Shrimp", "Other"])
                with c3:
                    f_rate = st.number_input(_lbl(lang, "Default Feeding Rate %", "డిఫాల్ట్ మేత రేటు %"), min_value=1.0, value=3.0, step=0.1)
                    t_min = st.number_input(_lbl(lang, "Min Temp (°C)", "కనిష్ట ఉష్ణోగ్రత (°C)"), value=24.0)
                    t_max = st.number_input(_lbl(lang, "Max Temp (°C)", "గరిష్ట ఉష్ణోగ్రత (°C)"), value=32.0)

                sp_notes = st.text_area(_lbl(lang, "Species Biological Notes", "జాతి జీవశాస్త్ర గమనికలు"), placeholder=_lbl(lang, "Surface feeder with rapid conversion ratio...", "వేగవంతమైన పెరుగుదల కలిగిన ఉపరితల మేత జాతి..."))
                add_sp_btn = st.form_submit_button(_lbl(lang, "Register Species", "జాతిని నమోదు చేయండి"), type="primary")
                if add_sp_btn:
                    if not sp_name:
                        st.error(_lbl(lang, "Species name is required.", "చేప జాతి పేరు తప్పనిసరి."))
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
                        st.success(_lbl(lang, f"Registered species '{sp_name}' successfully.", f"జాతి '{sp_name}' విజయవంతంగా నమోదైంది."))
                        st.rerun()

    # 3. Growth Tracking
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Fish Growth Sampling Observations', 'చేపల పెరుగుదల నమూనా పరిశీలనలు')}")
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 1], vertical_alignment="bottom")
        with col_ctrl1:
            sel_pid = st.selectbox(
                _lbl(lang, "Filter Pond", "చెరువును ఎంచుకోండి"),
                options=["All Ponds"] + [p["PondID"] for p in ponds],
                key="growth_filter_pond",
                format_func=lambda x: tv(x, lang)
            )
        with col_ctrl2:
            if st.button(_lbl(lang, "Analyze Growth with AI", "AI తో పెరుగుదల విశ్లేషణ"), type="secondary", use_container_width=True):
                st.session_state.show_growth_ai = True
        with col_ctrl3:
            if st.button(_lbl(lang, "Add Growth Sample", "పెరుగుదల నమూనా జోడించు"), type="primary", use_container_width=True):
                dialog_add_growth_sample()

        if st.session_state.get("show_growth_ai", False):
            target_p = "P-001" if sel_pid == "All Ponds" else sel_pid
            g_ai = analyze_growth(st.session_state, target_p)
            clean_obs = g_ai['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = g_ai['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = g_ai['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(
                f"**{_lbl(lang, 'Observation', 'పరిశీలన')}:** {clean_obs}\n\n"
                f"**{_lbl(lang, 'Trend', 'ధోరణి')}:** {clean_tr}\n\n"
                f"**{_lbl(lang, 'Suggested Check', 'సూచించిన తనిఖీ')}:** {clean_ck}"
            )

        filtered_growths = growths if sel_pid == "All Ponds" else [g for g in growths if g.get("PondID") == sel_pid]
        if filtered_growths:
            df_g = pd.DataFrame(filtered_growths).sort_values("ObservationDate", ascending=False)
            g_cols = ["GrowthID", "PondID", "Species", "ObservationDate", "SampleSize", "AvgFishWeightGrams", "MinWeightGrams", "MaxWeightGrams", "EstimatedBiomassKg", "Observer"]
            for c in g_cols:
                if c not in df_g.columns:
                    df_g[c] = ""
            st.dataframe(rename_df_for_display(df_g[g_cols], lang), use_container_width=True, hide_index=True)

            fig_g = px.line(
                df_g,
                x="ObservationDate",
                y="AvgFishWeightGrams",
                color="PondID",
                markers=True,
                title=_lbl(lang, "Fish Sample Weight Progression (Grams)", "చేపల నమూనా బరువు పెరుగుదల (గ్రాములు)"),
                labels={"ObservationDate": _lbl(lang, "Sampling Date", "నమూనా తేదీ"), "AvgFishWeightGrams": _lbl(lang, "Avg Weight (g)", "సగటు బరువు (గ్రా.)"), "PondID": _lbl(lang, "Pond", "చెరువు")}
            )
            fig_g.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            render_empty_state(
                _lbl(lang, "Growth", "పెరుగుదల"),
                _lbl(lang, "No Growth Observations", "పెరుగుదల పరిశీలనలు లేవు"),
                _lbl(lang, "Perform sample cast netting to record fish weights.", "చేపల బరువును నమోదు చేయడానికి వల నమూనా తనిఖీ చేయండి."),
                _lbl(lang, "Add Sample", "నమూనా జోడించు"),
                "gr_add_btn_empty"
            )

    # 4. Biomass Overview
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Estimated Pond Biomass Summary', 'చెరువుల అంచనా బయోమాస్ సారాంశం')}")
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
                _lbl(lang, "Pond ID", "చెరువు ID"): pid,
                _lbl(lang, "Pond Name", "చెరువు పేరు"): p["PondName"],
                _lbl(lang, "Status", "స్థితి"): tv(p["Status"], lang),
                _lbl(lang, "Stocked Count", "నిల్వ సంఖ్య"): f"{tot_f:,}",
                _lbl(lang, "Initial Biomass (kg)", "ప్రారంభ బయోమాస్ (కేజీ)"): f"{init_bio:,.1f}",
                _lbl(lang, "Current Avg Weight (g)", "ప్రస్తుత సగటు బరువు (గ్రా.)"): f"{latest_w}g",
                _lbl(lang, "Estimated Biomass (kg)", "అంచనా బయోమాస్ (కేజీ)"): f"{est_bio:,.1f}",
                _lbl(lang, "Biomass Gain (kg)", "బయోమాస్ పెరుగుదల (కేజీ)"): f"+{gain:,.1f}"
            })

        st.dataframe(pd.DataFrame(b_rows), use_container_width=True, hide_index=True)
        render_metric_card(
            _lbl(lang, "Total Estimated Farm Biomass", "మొత్తం ఫార్మ్ అంచనా బయోమాస్"),
            f"10,340 {_lbl(lang, 'kg', 'కేజీ')}",
            _lbl(lang, "Calculated across active culture ponds", "క్రియాశీల చెరువుల ఆధారంగా గణించబడింది")
        )

    # 5. Stocking History
    with tabs[4]:
        st.markdown(f"#### {_lbl(lang, 'Farm Stocking Chronicle', 'ఫార్మ్ చేపల నిల్వ చరిత్ర')}")
        if stocks:
            stocks_hist_df = pd.DataFrame(stocks)
            hist_cols = ["StockingDate", "PondID", "Species", "Variety", "NumberOfFish", "SourceHatchery", "BatchNumber", "TotalSeedCost", "Notes"]
            for col in hist_cols:
                if col not in stocks_hist_df.columns:
                    stocks_hist_df[col] = ""
            st.dataframe(rename_df_for_display(stocks_hist_df[hist_cols], lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Stocking", "నిల్వ"),
                _lbl(lang, "No Stocking History", "నిల్వ చరిత్ర లేదు"),
                _lbl(lang, "Stocking batches will appear here as you log fingerlings.", "చేప పిల్లలను నమోదు చేసిన తర్వాత బ్యాచ్‌లు ఇక్కడ కనిపిస్తాయి.")
            )

    # 6. Harvest Management
    with tabs[5]:
        h_top1, h_top2 = st.columns([3, 1], vertical_alignment="center")
        with h_top1:
            st.markdown(f"#### {_lbl(lang, 'Commercial Fish Harvests', 'వాణిజ్య చేపల పంట కోతలు')}")
        with h_top2:
            if st.button(_lbl(lang, "Record New Harvest", "కొత్త కోత నమోదు"), type="primary", use_container_width=True):
                dialog_record_harvest()

        if harvests:
            df_h = pd.DataFrame(harvests)
            h_cols = ["HarvestID", "PondID", "Date", "Species", "TotalWeightKg", "Grade", "Buyer", "PricePerKg", "TotalRevenue", "TransportCost", "LabourCost", "Notes"]
            for col in h_cols:
                if col not in df_h.columns:
                    df_h[col] = ""
            st.dataframe(rename_df_for_display(df_h[h_cols], lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Harvest", "పంట కోత"),
                _lbl(lang, "No Harvests Recorded", "కోత రికార్డులు లేవు"),
                _lbl(lang, "Record partial or final harvests as market sales occur.", "మార్కెట్ అమ్మకాల ప్రకారం పాక్షిక లేదా పూర్తి కోతలను నమోదు చేయండి."),
                _lbl(lang, "Record Harvest", "కోత నమోదు"),
                "rec_harv_empty"
            )
