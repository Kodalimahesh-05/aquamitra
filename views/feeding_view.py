"""
AquaMitra Feeding Management View Module
Provides Feeding Dashboard, Feeding Logger, History, Feed Inventory,
and Feed Cost Analytics with strictly zero emojis. Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.translations import tv, rename_df_for_display
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_feeding
from services.ai.ai_service import analyze_feeding
from database.queries import get_feeding_records


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_feeding_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Feeding Dashboard", "మేత డాష్‌బోర్డ్"),
        _lbl(lang, "Record Feeding", "మేత నమోదు"),
        _lbl(lang, "Feed History", "మేత చరిత్ర"),
        _lbl(lang, "Feed Inventory", "మేత నిల్వ (Inventory)"),
        _lbl(lang, "Feed Costs", "మేత ఖర్చులు")
    ]
    tabs = st.tabs(subtabs)

    feeds = get_feeding_records()
    inv = st.session_state.get("demo_feed_inventory", [])
    kg_unit = _lbl(lang, "kg", "కేజీ")

    # 1. Feeding Dashboard
    with tabs[0]:
        btn_c1, btn_c2 = st.columns([3, 1], vertical_alignment="center")
        with btn_c1:
            st.markdown(f"#### {_lbl(lang, 'Feed Management & Ration Dashboard', 'మేత నిర్వహణ మరియు రేషన్ డాష్‌బోర్డ్')}")
        with btn_c2:
            if st.button(_lbl(lang, "Analyze Feeding with AI", "AI తో మేత విశ్లేషణ"), type="secondary", use_container_width=True):
                st.session_state.show_feed_ai = True

        if st.session_state.get("show_feed_ai", False):
            f_ai = analyze_feeding(st.session_state)
            clean_obs = f_ai['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = f_ai['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = f_ai['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(
                f"**{_lbl(lang, 'Observation', 'పరిశీలన')}:** {clean_obs}\n\n"
                f"**{_lbl(lang, 'Trend', 'ధోరణి')}:** {clean_tr}\n\n"
                f"**{_lbl(lang, 'Suggested Check', 'సూచించిన తనిఖీ')}:** {clean_ck}"
            )

        # Metric cards
        today_kg = feeds[-1]["ActualFeedKg"] + (feeds[-2]["ActualFeedKg"] if len(feeds) >= 2 else 0) if feeds else 0
        total_cost = sum(f.get("TotalFeedCost", 0) for f in feeds)
        avg_feed = round(sum(f.get("ActualFeedKg", 0) for f in feeds) / len(feeds), 1) if feeds else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card(
                _lbl(lang, "Today's Feed Ration", "నేటి మేత రేషన్"),
                f"{today_kg} {kg_unit}",
                _lbl(lang, "Across Active Ponds", "క్రియాశీల చెరువులలో")
            )
        with c2:
            render_metric_card(
                _lbl(lang, "Average Daily Feed", "రోజువారీ సగటు మేత"),
                f"{avg_feed} {_lbl(lang, 'kg/day', 'కేజీ/రోజు')}",
                _lbl(lang, "14-Day Rolling Avg", "14-రోజుల సగటు")
            )
        with c3:
            render_metric_card(
                _lbl(lang, "Total Feed Cost", "మొత్తం మేత ఖర్చు"),
                f"₹{total_cost:,.0f}",
                _lbl(lang, "Recorded Operational Cost", "నమోదైన నిర్వహణ ఖర్చు")
            )
        with c4:
            rem_inv = sum(i.get("RemainingQuantityKg", 0) for i in inv)
            render_metric_card(
                _lbl(lang, "Warehouse Feed Stock", "గోదాం మేత నిల్వ"),
                f"{rem_inv:,.0f} {kg_unit}",
                f"{len(inv)} {_lbl(lang, 'Active Batches', 'క్రియాశీల బ్యాచ్‌లు')}"
            )

        st.markdown(f"##### {_lbl(lang, 'Daily Feed Distribution', 'రోజువారీ మేత పంపిణీ')}")
        if feeds:
            df_f = pd.DataFrame(feeds)
            fig_feed = px.bar(
                df_f,
                x="FeedingDate",
                y="ActualFeedKg",
                color="PondID",
                barmode="group",
                title=_lbl(lang, "Daily Feed Distributed (kg)", "రోజువారీ వేసిన మేత (కేజీ)"),
                labels={
                    "FeedingDate": _lbl(lang, "Feeding Date", "మేత తేదీ"),
                    "ActualFeedKg": _lbl(lang, "Feed Given (kg)", "వేసిన మేత (కేజీ)"),
                    "PondID": _lbl(lang, "Pond", "చెరువు")
                }
            )
            fig_feed.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_feed, use_container_width=True)

    # 2. Record Feeding
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Record Daily Feeding Log', 'రోజువారీ మేత లాగ్ నమోదు')}")
        st.caption(_lbl(lang, "Log daily feed rations, feed response, and feeding rates.", "రోజువారీ మేత రేషన్, చేపల స్పందన మరియు మేత రేట్లను నమోదు చేయండి."))
        if st.button(_lbl(lang, "Open Feeding Form", "మేత ఫారమ్ తెరవండి"), type="primary"):
            dialog_add_feeding()

    # 3. Feed History
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Farm Feeding History', 'ఫార్మ్ మేత చరిత్ర')}")
        if feeds:
            df_fh = pd.DataFrame(feeds)
            if "FeedingDate" in df_fh.columns:
                df_fh = df_fh.sort_values("FeedingDate", ascending=False)
            fh_cols = ["FeedingID", "PondID", "FeedingDate", "FeedType", "FeedBrand", "BiomassKg", "FeedingRatePercent", "RecommendedFeedKg", "ActualFeedKg", "TotalFeedCost", "FeedResponse", "Notes"]
            for col in fh_cols:
                if col not in df_fh.columns:
                    df_fh[col] = ""
            disp_fh = rename_df_for_display(df_fh[fh_cols], lang)
            if lang == "te":
                disp_fh = disp_fh.rename(columns={"FeedingRatePercent": "మేత రేటు (%)"})
            st.dataframe(disp_fh, use_container_width=True, hide_index=True)

            with st.expander(_lbl(lang, "Manage Feed Entries", "మేత ఎంట్రీలను నిర్వహించండి")):
                del_fid = st.selectbox(_lbl(lang, "Select Entry to Remove", "తొలగించాల్సిన ఎంట్రీని ఎంచుకోండి"), options=[f.get("FeedingID") for f in feeds])
                if st.button(_lbl(lang, "Delete Selected Feed Record", "ఎంచుకున్న మేత రికార్డును తొలగించండి"), type="secondary"):
                    st.session_state.demo_feeding = [f for f in st.session_state.demo_feeding if f.get("FeedingID") != del_fid]
                    st.success(_lbl(lang, "Entry removed successfully.", "ఎంట్రీ విజయవంతంగా తొలగించబడింది."))
                    st.rerun()
        else:
            render_empty_state(
                _lbl(lang, "Feeding", "మేత"),
                _lbl(lang, "No Feeding Records", "మేత రికార్డులు లేవు"),
                _lbl(lang, "Start logging daily feeding rations.", "రోజువారీ మేత రేషన్లను నమోదు చేయడం ప్రారంభించండి.")
            )

    # 4. Feed Inventory
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Feed Warehouse Inventory', 'మేత గోదాం నిల్వ')}")
        with st.expander(_lbl(lang, "Purchase / Add Feed Stock Batch", "కొత్త మేత నిల్వ బ్యాచ్‌ను జోడించండి")):
            with st.form("add_feed_inv_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    f_brand = st.text_input(_lbl(lang, "Brand *", "బ్రాండ్ *"), placeholder="e.g. Godrej Aquafeed")
                    f_type = st.selectbox(
                        _lbl(lang, "Feed Type", "మేత రకం"),
                        options=["Pellet (32% Protein)", "Floating Pellet (28%)", "Sinking Pellet (24%)", "Mash / Rice Bran Mix", "Other"],
                        format_func=lambda x: tv(x, lang)
                    )
                    batch = st.text_input(_lbl(lang, "Batch Number", "బ్యాచ్ నంబర్"), placeholder="e.g. GAF-2026-B1")
                    pur_date = st.date_input(_lbl(lang, "Purchase Date", "కొనుగోలు తేదీ"), value=date.today())
                with c2:
                    qty = st.number_input(_lbl(lang, "Purchased Quantity (kg) *", "కొనుగోలు చేసిన పరిమాణం (కేజీ) *"), min_value=50.0, value=1000.0, step=50.0)
                    cost_kg = st.number_input(_lbl(lang, "Unit Cost per kg (₹) *", "కేజీ ధర (₹) *"), min_value=10.0, value=48.0, step=1.0)
                    supplier = st.text_input(_lbl(lang, "Supplier / Dealer", "సరఫరాదారు / డీలర్"), placeholder="e.g. Royal Feeds Distributor")
                    storage = st.text_input(_lbl(lang, "Storage Location", "నిల్వ ప్రదేశం"), value="Main Feed Shed A")

                sub_inv = st.form_submit_button(_lbl(lang, "Save Feed Batch", "మేత బ్యాచ్‌ను సేవ్ చేయండి"), type="primary")
                if sub_inv:
                    if not f_brand:
                        st.error(_lbl(lang, "Brand is required.", "బ్రాండ్ పేరు తప్పనిసరి."))
                    else:
                        new_item = {
                            "InventoryID": len(inv) + 1,
                            "FeedType": f_type,
                            "Brand": f_brand.strip(),
                            "BatchNumber": batch.strip(),
                            "PurchaseDate": pur_date.strftime("%Y-%m-%d"),
                            "PurchasedQuantityKg": float(qty),
                            "UsedQuantityKg": 0.0,
                            "RemainingQuantityKg": float(qty),
                            "CostPerKg": float(cost_kg),
                            "Supplier": supplier.strip(),
                            "ExpiryDate": "2026-11-30",
                            "StorageLocation": storage.strip(),
                            "Notes": "New purchase logged."
                        }
                        st.session_state.demo_feed_inventory.append(new_item)
                        st.success(_lbl(lang, f"Added {qty:,.0f} kg {f_brand} to feed warehouse inventory.", f"{qty:,.0f} కేజీ {f_brand} గోదాం నిల్వకు జోడించబడింది."))
                        st.rerun()

        if inv:
            df_inv = pd.DataFrame(inv)
            inv_cols = ["InventoryID", "Brand", "FeedType", "BatchNumber", "PurchaseDate", "PurchasedQuantityKg", "UsedQuantityKg", "RemainingQuantityKg", "CostPerKg", "StorageLocation"]
            for c in inv_cols:
                if c not in df_inv.columns:
                    df_inv[c] = ""
            disp_inv = rename_df_for_display(df_inv[inv_cols], lang)
            if lang == "te":
                disp_inv = disp_inv.rename(columns={
                    "InventoryID": "నిల్వ ID",
                    "PurchasedQuantityKg": "కొనుగోలు పరిమాణం (కేజీ)",
                    "UsedQuantityKg": "వాడిన పరిమాణం (కేజీ)",
                    "RemainingQuantityKg": "మిగిలిన నిల్వ (కేజీ)",
                    "CostPerKg": "కేజీ ధర (₹)",
                    "StorageLocation": "నిల్వ స్థలం"
                })
            st.dataframe(disp_inv, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Inventory", "నిల్వ"),
                _lbl(lang, "No Feed in Stock", "మేత నిల్వ లేదు"),
                _lbl(lang, "Log purchased feed batches.", "కొనుగోలు చేసిన మేత బ్యాచ్‌లను నమోదు చేయండి.")
            )

    # 5. Feed Costs
    with tabs[4]:
        st.markdown(f"#### {_lbl(lang, 'Feed Expenditure Analytics', 'మేత ఖర్చుల విశ్లేషణ')}")
        if feeds:
            df_fc = pd.DataFrame(feeds)
            df_summary = df_fc.groupby("PondID")["TotalFeedCost"].sum().reset_index()
            fig_cost = px.bar(
                df_summary,
                x="PondID",
                y="TotalFeedCost",
                title=_lbl(lang, "Cumulative Feed Cost by Pond (₹)", "చెరువు వారీగా మొత్తం మేత ఖర్చు (₹)"),
                labels={"PondID": _lbl(lang, "Pond", "చెరువు"), "TotalFeedCost": _lbl(lang, "Total Feed Cost (₹)", "మొత్తం మేత ఖర్చు (₹)")}
            )
            fig_cost.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            render_empty_state(
                _lbl(lang, "Finance", "ఆర్థికం"),
                _lbl(lang, "No Cost Records", "ఖర్చు రికార్డులు లేవు"),
                _lbl(lang, "Log feed applications to view cost breakdowns.", "ఖర్చుల వివరాలను చూడటానికి మేత రికార్డులను నమోదు చేయండి.")
            )
