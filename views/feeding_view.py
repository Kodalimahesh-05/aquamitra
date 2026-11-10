"""
AquaMitra Feeding Management View Module
Provides Feeding Dashboard, Feeding Logger, History, Feed Inventory,
and Feed Cost Analytics with strictly zero emojis.
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_feeding
from services.ai.ai_service import analyze_feeding
from database.queries import get_feeding_records


def render_feeding_view():
    subtabs = ["Feeding Dashboard", "Record Feeding", "Feed History", "Feed Inventory", "Feed Costs"]
    tabs = st.tabs(subtabs)

    feeds = get_feeding_records()
    inv = st.session_state.get("demo_feed_inventory", [])
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Feeding Dashboard
    with tabs[0]:
        st.markdown("#### Feed Management & Ration Dashboard")
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button("Analyze Feeding with AI", type="secondary", use_container_width=True):
                st.session_state.show_feed_ai = True

        if st.session_state.get("show_feed_ai", False):
            f_ai = analyze_feeding(st.session_state)
            clean_obs = f_ai['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = f_ai['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = f_ai['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(f"**Observation:** {clean_obs}\n\n**Trend:** {clean_tr}\n\n**Suggested Check:** {clean_ck}")

        # Metric cards
        today_kg = feeds[-1]["ActualFeedKg"] + (feeds[-2]["ActualFeedKg"] if len(feeds) >= 2 else 0) if feeds else 0
        total_cost = sum(f.get("TotalFeedCost", 0) for f in feeds)
        avg_feed = round(sum(f.get("ActualFeedKg", 0) for f in feeds) / len(feeds), 1) if feeds else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Today's Feed Ration", f"{today_kg} kg", "Across Active Ponds")
        with c2:
            render_metric_card("Average Daily Feed", f"{avg_feed} kg/day", "14-Day Rolling Avg")
        with c3:
            render_metric_card("Total Feed Cost", f"₹{total_cost:,.0f}", "Recorded Operational Cost")
        with c4:
            rem_inv = sum(i.get("RemainingQuantityKg", 0) for i in inv)
            render_metric_card("Warehouse Feed Stock", f"{rem_inv:,.0f} kg", f"{len(inv)} Active Batches")

        st.markdown("##### Daily Feed Distribution")
        if feeds:
            df_f = pd.DataFrame(feeds)
            fig_feed = px.bar(
                df_f,
                x="FeedingDate",
                y="ActualFeedKg",
                color="PondID",
                barmode="group",
                title="Daily Feed Distributed (kg)"
            )
            fig_feed.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_feed, use_container_width=True)

    # 2. Record Feeding
    with tabs[1]:
        st.markdown("#### Record Daily Feeding Log")
        st.caption("Log daily feed rations, feed response, and feeding rates.")
        if st.button("Open Feeding Form", type="primary"):
            dialog_add_feeding()

    # 3. Feed History
    with tabs[2]:
        st.markdown("#### Farm Feeding History")
        if feeds:
            df_fh = pd.DataFrame(feeds)
            if "FeedingDate" in df_fh.columns:
                df_fh = df_fh.sort_values("FeedingDate", ascending=False)
            fh_cols = ["FeedingID", "PondID", "FeedingDate", "FeedType", "FeedBrand", "BiomassKg", "FeedingRatePercent", "RecommendedFeedKg", "ActualFeedKg", "TotalFeedCost", "FeedResponse", "Notes"]
            for col in fh_cols:
                if col not in df_fh.columns:
                    df_fh[col] = ""
            st.dataframe(df_fh[fh_cols], use_container_width=True, hide_index=True)
            
            with st.expander("Manage Feed Entries"):
                del_fid = st.selectbox("Select Entry to Remove", options=[f.get("FeedingID") for f in feeds])
                if st.button("Delete Selected Feed Record", type="secondary"):
                    st.session_state.demo_feeding = [f for f in st.session_state.demo_feeding if f.get("FeedingID") != del_fid]
                    st.success("Entry removed successfully.")
                    st.rerun()
        else:
            render_empty_state("Feeding", "No Feeding Records", "Start logging daily feeding rations.")

    # 4. Feed Inventory
    with tabs[3]:
        st.markdown("#### Feed Warehouse Inventory")
        with st.expander("Purchase / Add Feed Stock Batch"):
            with st.form("add_feed_inv_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    f_brand = st.text_input("Brand *", placeholder="e.g. Godrej Aquafeed")
                    f_type = st.selectbox("Feed Type", options=["Pellet (32% Protein)", "Floating Pellet (28%)", "Sinking Pellet (24%)", "Mash / Rice Bran Mix", "Other"])
                    batch = st.text_input("Batch Number", placeholder="e.g. GAF-2026-B1")
                    pur_date = st.date_input("Purchase Date", value=date.today())
                with c2:
                    qty = st.number_input("Purchased Quantity (kg) *", min_value=50.0, value=1000.0, step=50.0)
                    cost_kg = st.number_input("Unit Cost per kg (₹) *", min_value=10.0, value=48.0, step=1.0)
                    supplier = st.text_input("Supplier / Dealer", placeholder="e.g. Royal Feeds Distributor")
                    storage = st.text_input("Storage Location", value="Main Feed Shed A")

                sub_inv = st.form_submit_button("Save Feed Batch", type="primary")
                if sub_inv:
                    if not f_brand:
                        st.error("Brand is required.")
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
                        st.success(f"Added {qty:,.0f} kg {f_brand} to feed warehouse inventory.")
                        st.rerun()

        if inv:
            df_inv = pd.DataFrame(inv)
            inv_cols = ["InventoryID", "Brand", "FeedType", "BatchNumber", "PurchaseDate", "PurchasedQuantityKg", "UsedQuantityKg", "RemainingQuantityKg", "CostPerKg", "StorageLocation"]
            for c in inv_cols:
                if c not in df_inv.columns:
                    df_inv[c] = ""
            st.dataframe(df_inv[inv_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Inventory", "No Feed in Stock", "Log purchased feed batches.")

    # 5. Feed Costs
    with tabs[4]:
        st.markdown("#### Feed Expenditure Analytics")
        if feeds:
            df_fc = pd.DataFrame(feeds)
            df_summary = df_fc.groupby("PondID")["TotalFeedCost"].sum().reset_index()
            fig_cost = px.bar(df_summary, x="PondID", y="TotalFeedCost", title="Cumulative Feed Cost by Pond (₹)")
            fig_cost.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            render_empty_state("Finance", "No Cost Records", "Log feed applications to view cost breakdowns.")
