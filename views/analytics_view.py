"""
AquaMitra Analytics View Module
Provides interactive Plotly decision-support visual analytics across Farm, Pond,
Growth, Water, Feeding, Incidents, and Finance with 'Explain with AI' features.
Strictly zero emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from services.ai.ai_service import explain_chart_trend
from database.queries import (
    get_fish_stocks,
    get_growth_records,
    get_water_quality,
    get_feeding_records,
    get_incidents,
    get_expenses,
    get_sales
)


def render_analytics_view():
    subtabs = ["Farm Analytics", "Pond Analytics", "Growth Analytics", "Water Analytics", "Feeding Analytics", "Incident Analytics", "Financial Analytics"]
    tabs = st.tabs(subtabs)

    growths = get_growth_records()
    waters = get_water_quality()
    feeds = get_feeding_records()
    expenses = get_expenses()
    sales = get_sales()
    incidents = get_incidents()
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Farm Analytics
    with tabs[0]:
        st.markdown("#### Comprehensive Farm Performance Analytics")
        if growths and feeds:
            c1, c2 = st.columns(2)
            with c1:
                df_g = pd.DataFrame(growths)
                fig_g = px.line(df_g, x="ObservationDate", y="AvgFishWeightGrams", color="PondID", markers=True, title="Fish Growth Curves Across Ponds (g)")
                fig_g.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_g, use_container_width=True)
                if st.button("Explain Growth Trend with AI", key="ai_exp_farm_growth"):
                    p1_g = df_g[df_g["PondID"] == "P-001"]
                    clean_res = explain_chart_trend("Fish Growth", p1_g["AvgFishWeightGrams"].tolist(), p1_g["ObservationDate"].tolist()).replace("🤖", "").replace("📈", "").replace("💡", "").strip()
                    st.info(clean_res)

            with c2:
                df_f = pd.DataFrame(feeds)
                fig_f = px.bar(df_f, x="FeedingDate", y="ActualFeedKg", color="PondID", barmode="stack", title="Total Daily Feed Distributed (kg)")
                fig_f.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_f, use_container_width=True)
                if st.button("Explain Feed Trend with AI", key="ai_exp_farm_feed"):
                    p1_f = df_f[df_f["PondID"] == "P-001"]
                    clean_res = explain_chart_trend("Feed Consumption", p1_f["ActualFeedKg"].tolist(), p1_f["FeedingDate"].tolist()).replace("🤖", "").replace("📈", "").replace("💡", "").strip()
                    st.info(clean_res)

    # 2. Pond Analytics
    with tabs[1]:
        st.markdown("#### Pond-Level Comparative Analytics")
        sel_pid = st.selectbox("Select Pond to Inspect", options=[p["PondID"] for p in ponds], key="an_pond_sel")
        p_growths = [g for g in growths if g.get("PondID") == sel_pid]
        p_waters = [w for w in waters if w.get("PondID") == sel_pid]
        p_feeds = [f for f in feeds if f.get("PondID") == sel_pid]

        c1, c2 = st.columns(2)
        with c1:
            if p_waters:
                fig_pw = px.line(pd.DataFrame(p_waters), x="ReadingDate", y="DissolvedOxygen", markers=True, title=f"{sel_pid} — Dissolved Oxygen (mg/L)")
                fig_pw.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Baseline Ref (5.0 mg/L)")
                fig_pw.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_pw, use_container_width=True)
            else:
                st.caption("No water records for selected pond.")
        with c2:
            if p_feeds:
                fig_pf = px.line(pd.DataFrame(p_feeds), x="FeedingDate", y=["ActualFeedKg", "RecommendedFeedKg"], markers=True, title=f"{sel_pid} — Actual vs Recommended Feed (kg)")
                fig_pf.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15), legend=dict(orientation="h", y=1.15))
                st.plotly_chart(fig_pf, use_container_width=True)
            else:
                st.caption("No feeding records for selected pond.")

    # 3. Growth Analytics
    with tabs[2]:
        st.markdown("#### Fish Growth & Biomass Dynamics")
        if growths:
            df_gr = pd.DataFrame(growths)
            fig_bio = px.area(df_gr, x="ObservationDate", y="EstimatedBiomassKg", color="PondID", title="Estimated Biomass Accumulation (kg)")
            fig_bio.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_bio, use_container_width=True)
        else:
            st.caption("No growth sampling records available.")

    # 4. Water Analytics
    with tabs[3]:
        st.markdown("#### Water Parameter Stability & Distribution")
        if waters:
            df_w = pd.DataFrame(waters)
            fig_box = px.box(df_w, x="PondID", y="DissolvedOxygen", color="PondID", title="Dissolved Oxygen Variance Across Ponds (mg/L)")
            fig_box.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.caption("No water quality observations recorded.")

    # 5. Feeding Analytics
    with tabs[4]:
        st.markdown("#### Feed Efficiency & Consumption Patterns")
        if feeds:
            df_fd = pd.DataFrame(feeds)
            fig_fd = px.scatter(df_fd, x="BiomassKg", y="ActualFeedKg", color="PondID", size="ActualFeedKg", title="Feed Quantity (kg) vs Estimated Biomass (kg)")
            fig_fd.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_fd, use_container_width=True)
        else:
            st.caption("No feeding records available.")

    # 6. Incident Analytics
    with tabs[5]:
        st.markdown("#### Incident Occurrence & Severity Distribution")
        if incidents:
            df_inc = pd.DataFrame(incidents)
            fig_inc = px.bar(df_inc, x="Date", y="NumberAffected", color="Severity", title="Incident Affected Counts by Observation Date")
            fig_inc.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_inc, use_container_width=True)
        else:
            st.caption("No incidents recorded.")

    # 7. Financial Analytics
    with tabs[6]:
        st.markdown("#### Financial Economics & Cash Realization")
        if expenses and sales:
            df_e = pd.DataFrame(expenses)
            df_s = pd.DataFrame(sales)
            tot_e = df_e["Amount"].sum()
            tot_s = df_s["TotalRevenue"].sum()
            df_comp = pd.DataFrame({
                "Category": ["Total Expenses", "Total Revenue"],
                "Amount (₹)": [tot_e, tot_s]
            })
            fig_fin = px.bar(df_comp, x="Category", y="Amount (₹)", color="Category", title="Expenditure vs Realized Revenue (₹)")
            fig_fin.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_fin, use_container_width=True)
        else:
            st.caption("Record financial transactions to generate cash flow comparisons.")
