"""
AquaMitra Reports & Export View Module
Provides Farm, Pond, Water, Fish, Feeding, Incident, Financial, and Custom Reports
with real CSV export buttons and 'Generate AI Executive Summary' functionality.
100% Zero-Emoji Professional SaaS Interface.
"""

from datetime import date
import io
import streamlit as st
import pandas as pd
from services.ai.ai_service import generate_farm_summary


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_reports_view():
    subtabs = ["Farm Report", "Pond Report", "Water Report", "Fish Report", "Feeding Report", "Incident Report", "Financial Report", "Custom Report"]
    tabs = st.tabs(subtabs)

    ponds = st.session_state.get("demo_ponds", [])

    # 1. Farm Report
    with tabs[0]:
        st.markdown("### Comprehensive Farm Status Report")
        st.caption("Master summary of all farm units, dimensions, and operational ownership.")
        
        if st.button("Generate AI Executive Summary", key="ai_sum_farm_rep"):
            s = generate_farm_summary(st.session_state)
            clean_badge = s['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()
            clean_text = s['text'].replace("🟡", "").replace("🟢", "").replace("🔴", "").strip()
            st.info(f"**Executive AI Summary ([{clean_badge}]):**\n\n{clean_text}")

        df_fp = pd.DataFrame(ponds)
        p_cols = ["PondID", "PondName", "Location", "Area", "AreaUnit", "PondType", "WaterSource", "Status", "Owner", "Manager"]
        for col in p_cols:
            if col not in df_fp.columns:
                df_fp[col] = ""
        st.dataframe(df_fp[p_cols], use_container_width=True, hide_index=True)
        st.download_button(
            "Download Farm Report (CSV)",
            data=convert_df_to_csv(df_fp[p_cols]),
            file_name=f"AquaMitra_Farm_Report_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 2. Pond Report
    with tabs[1]:
        st.markdown("### Pond-Specific Comprehensive Report")
        st.caption("Deep-dive historical observations, feed consumption, and growth for an individual pond.")
        
        if ponds:
            sel_pid = st.selectbox("Select Pond", options=[p["PondID"] for p in ponds], key="rep_pond_sel")
            p_waters = [w for w in st.session_state.get("demo_water_quality", []) if w.get("PondID") == sel_pid]
            p_feeds = [f for f in st.session_state.get("demo_feeding", []) if f.get("PondID") == sel_pid]
            p_growths = [g for g in st.session_state.get("demo_fish_growth", []) if g.get("PondID") == sel_pid]

            st.markdown(f"#### Water Observations ({len(p_waters)} Records)")
            if p_waters:
                df_pw = pd.DataFrame(p_waters)
                pw_cols = ["ReadingDate", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia"]
                for col in pw_cols:
                    if col not in df_pw.columns:
                        df_pw[col] = ""
                st.dataframe(df_pw[pw_cols], use_container_width=True, hide_index=True)
                st.download_button("Download Pond Water Data (CSV)", data=convert_df_to_csv(df_pw[pw_cols]), file_name=f"AquaMitra_{sel_pid}_Water_{date.today()}.csv", mime="text/csv")
            else:
                st.info(f"No water quality records found for pond {sel_pid}.")

            st.markdown(f"#### Feeding Records ({len(p_feeds)} Records)")
            if p_feeds:
                df_pf = pd.DataFrame(p_feeds)
                st.dataframe(df_pf, use_container_width=True, hide_index=True)
                st.download_button("Download Pond Feeding Data (CSV)", data=convert_df_to_csv(df_pf), file_name=f"AquaMitra_{sel_pid}_Feeding_{date.today()}.csv", mime="text/csv")

            st.markdown(f"#### Growth Samplings ({len(p_growths)} Records)")
            if p_growths:
                df_pg = pd.DataFrame(p_growths)
                st.dataframe(df_pg, use_container_width=True, hide_index=True)
                st.download_button("Download Pond Growth Data (CSV)", data=convert_df_to_csv(df_pg), file_name=f"AquaMitra_{sel_pid}_Growth_{date.today()}.csv", mime="text/csv")
        else:
            st.info("No ponds currently registered.")

    # 3. Water Report
    with tabs[2]:
        st.markdown("### Farm-Wide Water Quality Report")
        st.caption("Consolidated register of all logged physicochemical observations across ponds.")
        df_w = pd.DataFrame(st.session_state.get("demo_water_quality", []))
        st.dataframe(df_w, use_container_width=True, hide_index=True)
        st.download_button("Download All Water Observations (CSV)", data=convert_df_to_csv(df_w), file_name=f"AquaMitra_Water_Observations_{date.today()}.csv", mime="text/csv", type="primary")

    # 4. Fish Report
    with tabs[3]:
        st.markdown("### Fish Stocking & Growth Report")
        st.caption("Complete inventory of stocked batches, stocking densities, and historical sampling weights.")
        df_s = pd.DataFrame(st.session_state.get("demo_fish_stock", []))
        df_g = pd.DataFrame(st.session_state.get("demo_fish_growth", []))
        st.markdown("#### Stocking Batches")
        st.dataframe(df_s, use_container_width=True, hide_index=True)
        st.markdown("#### Growth Samplings")
        st.dataframe(df_g, use_container_width=True, hide_index=True)
        st.download_button("Download Growth Data (CSV)", data=convert_df_to_csv(df_g), file_name=f"AquaMitra_Growth_Data_{date.today()}.csv", mime="text/csv", type="primary")

    # 5. Feeding Report
    with tabs[4]:
        st.markdown("### Feed Consumption & Cost Report")
        st.caption("Ledger of daily feeding disbursements, recommended rations, and feed expenditures.")
        df_f = pd.DataFrame(st.session_state.get("demo_feeding", []))
        st.dataframe(df_f, use_container_width=True, hide_index=True)
        st.download_button("Download Feeding Ledger (CSV)", data=convert_df_to_csv(df_f), file_name=f"AquaMitra_Feeding_Ledger_{date.today()}.csv", mime="text/csv", type="primary")

    # 6. Incident Report
    with tabs[5]:
        st.markdown("### Health Observations & Mortality Report")
        st.caption("Log of health incidents, abnormal fish behavior observations, and logged mortalities.")
        df_i = pd.DataFrame(st.session_state.get("demo_incidents", []))
        st.dataframe(df_i, use_container_width=True, hide_index=True)
        st.download_button("Download Incidents Log (CSV)", data=convert_df_to_csv(df_i), file_name=f"AquaMitra_Incidents_Log_{date.today()}.csv", mime="text/csv", type="primary")

    # 7. Financial Report
    with tabs[6]:
        st.markdown("### Financial Statement & Sales Summary")
        st.caption("Comprehensive statements of operating expenses, farm inputs, and fish harvest sales.")
        df_e = pd.DataFrame(st.session_state.get("demo_expenses", []))
        df_s = pd.DataFrame(st.session_state.get("demo_sales", []))
        st.markdown("#### Operational Expenses")
        st.dataframe(df_e, use_container_width=True, hide_index=True)
        st.markdown("#### Fish Sales & Revenue")
        st.dataframe(df_s, use_container_width=True, hide_index=True)
        st.download_button("Download Sales Records (CSV)", data=convert_df_to_csv(df_s), file_name=f"AquaMitra_Sales_Records_{date.today()}.csv", mime="text/csv", type="primary")

    # 8. Custom Report
    with tabs[7]:
        st.markdown("### Custom Report Builder")
        st.caption("Select specific data domains and pond filters to generate customized exports.")
        c1, c2 = st.columns(2)
        with c1:
            cust_type = st.selectbox("Select Data Domain", options=[
                "Water Quality",
                "Feeding",
                "Expenses",
                "Fish Stock",
                "Growth Samples",
                "Mortality Incidents",
                "Harvests",
                "Sales"
            ])
        with c2:
            cust_pond = st.selectbox("Filter Pond", options=["All Ponds"] + [p["PondID"] for p in ponds], key="cust_rep_pond")

        data_map = {
            "Water Quality": st.session_state.get("demo_water_quality", []),
            "Feeding": st.session_state.get("demo_feeding", []),
            "Expenses": st.session_state.get("demo_expenses", []),
            "Fish Stock": st.session_state.get("demo_fish_stock", []),
            "Growth Samples": st.session_state.get("demo_fish_growth", []),
            "Mortality Incidents": st.session_state.get("demo_mortality", []),
            "Harvests": st.session_state.get("demo_harvests", []),
            "Sales": st.session_state.get("demo_sales", [])
        }
        raw_list = data_map.get(cust_type, [])
        if cust_pond != "All Ponds":
            raw_list = [x for x in raw_list if x.get("PondID") == cust_pond]

        if raw_list:
            df_cust = pd.DataFrame(raw_list)
            st.dataframe(df_cust, use_container_width=True, hide_index=True)
            st.download_button(
                "Export Custom Selection (CSV)",
                data=convert_df_to_csv(df_cust),
                file_name=f"AquaMitra_Custom_{cust_type.replace(' ', '_')}_{date.today()}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No matching records found for this custom selection.")
