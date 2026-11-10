"""
AquaMitra Water Quality View Module
Provides Parameter Matrix Dashboard, Readings Log, Interactive Plotly History,
Water Events, Multi-Pond Comparison, and Reference Range Configuration with strictly zero emojis.
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import DEFAULT_REFERENCE_RANGES
from components.cards import render_empty_state
from components.quick_actions import dialog_add_water_reading
from services.ai.ai_service import analyze_water
from database.queries import get_water_quality


def render_water_view():
    subtabs = ["Water Dashboard", "Water Readings", "Water History", "Water Events", "Water Comparison", "Reference Ranges"]
    tabs = st.tabs(subtabs)

    waters = get_water_quality()
    events = st.session_state.get("demo_water_events", [])
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Water Dashboard (Matrix View)
    with tabs[0]:
        st.markdown("#### Water Quality Parameter Matrix")
        st.caption("Latest recorded water conditions across all fishery ponds against baseline reference ranges.")
        
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button("Analyze Water with AI", type="secondary", use_container_width=True):
                st.session_state.show_water_ai = True

        if st.session_state.get("show_water_ai", False):
            res = analyze_water(st.session_state)
            clean_obs = res['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = res['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = res['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(f"**Observation:** {clean_obs}\n\n**Trend:** {clean_tr}\n\n**Suggested Check:** {clean_ck}")

        # Build Clean Matrix without emojis
        matrix_data = {
            "Parameter": [
                "pH (6.5 - 8.5)",
                "Dissolved Oxygen (>= 5.0 mg/L)",
                "Temperature (24 - 32 °C)",
                "Turbidity (20 - 40 NTU)",
                "Ammonia (<= 0.05 mg/L)",
                "Water Level (>= 1.5 m)"
            ]
        }

        for p in ponds:
            pid = p["PondID"]
            p_w = [w for w in waters if w.get("PondID") == pid]
            if p_w:
                last_w = p_w[-1]
                ph_status = "Optimal" if 6.5 <= last_w.get("pH", 7) <= 8.5 else "Monitor"
                do_val = last_w.get("DissolvedOxygen", 6)
                do_status = "Optimal" if do_val >= 5.0 else ("Alert" if do_val < 4.5 else "Monitor")
                temp_status = "Optimal" if 24.0 <= last_w.get("Temperature", 28) <= 32.0 else "Monitor"
                turb_status = "Optimal" if 20.0 <= last_w.get("Turbidity", 30) <= 40.0 else "Monitor"
                nh3_status = "Optimal" if last_w.get("Ammonia", 0) <= 0.05 else "Alert"
                lvl_status = "Optimal" if last_w.get("WaterLevel", 1.6) >= 1.5 else "Monitor"

                matrix_data[f"{pid} ({p['PondName']})"] = [
                    f"[{ph_status}] {last_w.get('pH')}",
                    f"[{do_status}] {last_w.get('DissolvedOxygen')} mg/L",
                    f"[{temp_status}] {last_w.get('Temperature')} °C",
                    f"[{turb_status}] {last_w.get('Turbidity')} NTU",
                    f"[{nh3_status}] {last_w.get('Ammonia')} mg/L",
                    f"[{lvl_status}] {last_w.get('WaterLevel')} m"
                ]
            else:
                matrix_data[f"{pid} ({p['PondName']})"] = ["[No Data]"] * 6

        st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)
        st.caption("Status Indicators: [Optimal] Within baseline range | [Monitor] Marginal deviation | [Alert] Exceeds safe threshold | [No Data] Observation needed")

    # 2. Water Readings
    with tabs[1]:
        st.markdown("#### Manual Water Quality Observations")
        rc1, rc2 = st.columns([3, 1])
        with rc2:
            if st.button("Log Water Reading", type="primary", use_container_width=True):
                dialog_add_water_reading()

        if waters:
            df_w = pd.DataFrame(waters)
            if "ReadingDate" in df_w.columns:
                df_w = df_w.sort_values("ReadingDate", ascending=False)
            w_cols = ["ReadingID", "PondID", "ReadingDate", "ReadingTime", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia", "WaterLevel", "Notes"]
            for col in w_cols:
                if col not in df_w.columns:
                    df_w[col] = ""
            st.dataframe(df_w[w_cols], use_container_width=True, hide_index=True)
            
            with st.expander("Manage Readings"):
                del_rid = st.selectbox("Select Reading to Remove", options=[w.get("ReadingID") for w in waters])
                if st.button("Delete Selected Reading", type="secondary"):
                    st.session_state.demo_water_quality = [w for w in st.session_state.demo_water_quality if w.get("ReadingID") != del_rid]
                    st.success("Reading removed successfully.")
                    st.rerun()
        else:
            render_empty_state("Water", "No Readings Recorded", "Log routine pond water testing results.", "Log Reading", "w_read_btn")

    # 3. Water History & Trends
    with tabs[2]:
        st.markdown("#### Water Quality Historical Trends")
        sel_pid = st.selectbox("Select Pond for Time-Series Analysis", options=[p["PondID"] for p in ponds], key="water_hist_pond")
        p_waters = [w for w in waters if w.get("PondID") == sel_pid]

        if p_waters:
            df_hist = pd.DataFrame(p_waters).sort_values("ReadingDate")
            param = st.selectbox("Parameter", options=["DissolvedOxygen", "pH", "Temperature", "Turbidity", "Ammonia", "WaterLevel"])
            fig_w = px.line(
                df_hist,
                x="ReadingDate",
                y=param,
                markers=True,
                title=f"{sel_pid} — {param} Over Time"
            )
            # Add reference bounds
            if param == "DissolvedOxygen":
                fig_w.add_hline(y=5.0, line_dash="dash", line_color="#059669", annotation_text="Baseline Ref (5.0 mg/L)")
            elif param == "pH":
                fig_w.add_hline(y=8.5, line_dash="dash", line_color="#D97706", annotation_text="Upper Limit (8.5)")
                fig_w.add_hline(y=6.5, line_dash="dash", line_color="#D97706", annotation_text="Lower Limit (6.5)")

            fig_w.update_layout(height=340, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            render_empty_state("Water", "No Historical Data", "Log readings across dates to view trend charts.")

    # 4. Water Events
    with tabs[3]:
        st.markdown("#### Water Management & Exchange Events")
        with st.expander("Log Water Management Event"):
            with st.form("water_event_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    ev_pid = st.selectbox("Pond *", options=[p["PondID"] for p in ponds], key="ev_p_sel")
                    ev_type = st.selectbox("Event Type", options=[
                        "Water Added",
                        "Water Removed",
                        "Water Exchange",
                        "Rainfall Event",
                        "Drainage",
                        "Refill",
                        "Cleaning",
                        "Other"
                    ])
                    ev_date = st.date_input("Event Date", value=date.today())
                with c2:
                    qty = st.number_input("Estimated Quantity (m³)", min_value=1.0, value=500.0, step=50.0)
                    reason = st.text_input("Reason / Objective", placeholder="e.g. Replenish evaporation loss")

                notes = st.text_input("Event Notes", placeholder="Inlet mesh filter cleaned prior to pump run.")
                ev_submit = st.form_submit_button("Save Water Event", type="primary")
                if ev_submit:
                    new_ev = {
                        "EventID": len(events) + 1,
                        "PondID": ev_pid,
                        "Date": ev_date.strftime("%Y-%m-%d"),
                        "EventType": ev_type,
                        "EstimatedQuantity": float(qty),
                        "Unit": "m³",
                        "Reason": reason.strip(),
                        "Notes": notes.strip()
                    }
                    st.session_state.demo_water_events.append(new_ev)
                    st.success("Water event logged successfully.")
                    st.rerun()

        if events:
            df_ev = pd.DataFrame(events)
            ev_cols = ["EventID", "PondID", "Date", "EventType", "EstimatedQuantity", "Unit", "Reason", "Notes"]
            for c in ev_cols:
                if c not in df_ev.columns:
                    df_ev[c] = ""
            st.dataframe(df_ev[ev_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Water Events", "No Water Events Recorded", "Log water exchanges, rainfall, or drainage events.")

    # 5. Water Comparison
    with tabs[4]:
        st.markdown("#### Multi-Pond Parameter Comparison")
        if waters:
            df_all = pd.DataFrame(waters)
            latest_all = df_all.sort_values("ReadingDate").groupby("PondID").last().reset_index()
            fig_comp = px.bar(latest_all, x="PondID", y="DissolvedOxygen", color="PondID", title="Latest Dissolved Oxygen (mg/L) Comparison Across Ponds")
            fig_comp.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text="Baseline Ref (5.0 mg/L)")
            fig_comp.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_comp, use_container_width=True)

            cmp_cols = ["PondID", "ReadingDate", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia", "WaterLevel"]
            for c in cmp_cols:
                if c not in latest_all.columns:
                    latest_all[c] = ""
            st.dataframe(latest_all[cmp_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Water", "No Readings Available", "Log readings to view multi-pond comparisons.")

    # 6. Reference Ranges
    with tabs[5]:
        st.markdown("#### Configurable Water Quality Reference Ranges")
        st.caption("Reference ranges must be configurable. Never invent scientific thresholds. If no reference range exists, AquaMitra displays 'No reference range configured.' without making a risk judgment.")
        
        # Initialize configurable ranges in session state if not present
        if "custom_reference_ranges" not in st.session_state:
            st.session_state.custom_reference_ranges = {
                k: {
                    "lower": v["lower"],
                    "upper": v["upper"],
                    "unit": v["unit"],
                    "species": "Freshwater Carps / Mixed",
                    "source": "ICAR-CIFA / NFDB Guidelines",
                    "active": True,
                    "updated_date": "2026-01-15"
                }
                for k, v in DEFAULT_REFERENCE_RANGES.items()
            }

        ref_dict = st.session_state.custom_reference_ranges
        ref_rows = []
        for param_k, val in ref_dict.items():
            ref_rows.append({
                "Parameter": param_k,
                "Lower Value": val["lower"],
                "Upper Value": val["upper"],
                "Unit": val["unit"],
                "Species": val.get("species", "General"),
                "Source": val.get("source", "Standard Reference"),
                "Active": val.get("active", True),
                "Updated Date": val.get("updated_date", "2026-01-15")
            })

        st.dataframe(pd.DataFrame(ref_rows), use_container_width=True, hide_index=True)

        with st.expander("Update / Add Parameter Reference Range"):
            with st.form("edit_ref_range_form"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    p_name = st.selectbox("Parameter Name", options=["pH", "DissolvedOxygen", "Temperature", "Turbidity", "Ammonia", "Nitrite", "Nitrate", "WaterLevel", "Salinity", "Alkalinity"])
                    curr_item = ref_dict.get(p_name, {"lower": 0.0, "upper": 10.0, "unit": "mg/L", "species": "General", "source": "Department Guidelines"})
                    low_val = st.number_input("Lower Threshold", value=float(curr_item["lower"]), step=0.1)
                    up_val = st.number_input("Upper Threshold", value=float(curr_item["upper"]), step=0.1)
                with rc2:
                    unit = st.text_input("Unit", value=curr_item["unit"])
                    species = st.text_input("Species Specification", value=curr_item.get("species", "General Freshwater"))
                    source = st.text_input("Source / Citation", value=curr_item.get("source", "ICAR-CIFA"))

                save_ref = st.form_submit_button("Save Reference Range", type="primary")
                if save_ref:
                    st.session_state.custom_reference_ranges[p_name] = {
                        "lower": float(low_val),
                        "upper": float(up_val),
                        "unit": unit.strip(),
                        "species": species.strip(),
                        "source": source.strip(),
                        "active": True,
                        "updated_date": date.today().strftime("%Y-%m-%d")
                    }
                    st.success(f"Reference range for {p_name} updated successfully.")
                    st.rerun()
