"""
AquaMitra Pond Management View Module
Provides All Ponds Grid, Add Pond Form, Pond Command Center (10 Sub-tabs), Activity Timeline,
and Maintenance Scheduler with strictly zero emojis.
"""

from datetime import date, datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import POND_STATUSES, POND_TYPES, AREA_UNITS, WATER_SOURCES
from utils.translations import t
from utils.demo_data import get_pond_health_snapshot, get_unified_recent_activity
from components.cards import (
    render_metric_card,
    render_pond_snapshot,
    render_empty_state,
    render_activity_feed,
    render_alert_card
)
from services.ai.ai_service import analyze_pond
from components.quick_actions import (
    dialog_add_pond,
    dialog_edit_pond,
    dialog_add_water_reading,
    dialog_add_fish_stock,
    dialog_add_growth_sample,
    dialog_add_feeding,
    dialog_add_incident,
    dialog_add_expense,
    dialog_add_sale,
    dialog_record_harvest,
    dialog_add_maintenance
)
from database.queries import (
    get_fish_stocks,
    get_growth_records,
    get_water_quality,
    get_feeding_records,
    get_incidents,
    get_expenses,
    get_sales,
    get_maintenance_records,
    delete_pond_record
)
from components.theme import get_status_badge_html


def render_ponds_view():
    lang = st.session_state.get("lang", "en")
    subtabs = ["All Ponds", "Add Pond", "Pond Profiles", "Pond Activity", "Pond Maintenance"]
    tabs = st.tabs(subtabs)
    ponds = st.session_state.get("demo_ponds", [])

    # 1. All Ponds Grid & Management
    with tabs[0]:
        st.markdown("#### Registered Aquaculture Ponds")
        col_f1, col_f2, col_f3, col_add = st.columns([3, 2, 2, 2])
        with col_f1:
            p_search = st.text_input("Search Ponds", placeholder="Search by name, ID or location...", label_visibility="collapsed")
        with col_f2:
            status_filter = st.selectbox("Filter Status", options=["All"] + POND_STATUSES, index=0)
        with col_f3:
            type_filter = st.selectbox("Filter Type", options=["All"] + POND_TYPES, index=0)
        with col_add:
            if st.button("Register New Pond", type="primary", use_container_width=True):
                dialog_add_pond()

        # Filter logic
        filtered = ponds
        if p_search:
            q = p_search.lower().strip()
            filtered = [p for p in filtered if q in p.get("PondName", "").lower() or q in p.get("PondID", "").lower() or q in p.get("Location", "").lower()]
        if status_filter != "All":
            filtered = [p for p in filtered if p.get("Status") == status_filter]
        if type_filter != "All":
            filtered = [p for p in filtered if p.get("PondType") == type_filter]

        if not filtered:
            render_empty_state("Ponds", "No Ponds Found", "No ponds match the selected criteria.", "Add Pond", "all_p_add_btn")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered):
                pid = p["PondID"]
                snap = get_pond_health_snapshot(pid)
                with cols[idx % 2]:
                    render_pond_snapshot(snap)
                    b1, b2, b3 = st.columns([2, 1, 1])
                    with b1:
                        if st.button(f"Command Center ({pid})", key=f"open_pond_{pid}", use_container_width=True):
                            st.session_state.active_profile_pond = pid
                            st.rerun()
                    with b2:
                        if st.button("Edit", key=f"edit_pond_{pid}", use_container_width=True):
                            dialog_edit_pond(pid)
                    with b3:
                        if st.button("Delete", key=f"del_pond_{pid}", use_container_width=True):
                            st.session_state[f"confirm_del_{pid}"] = True

                    if st.session_state.get(f"confirm_del_{pid}", False):
                        st.warning(f"Confirm deleting {p.get('PondName')} ({pid})?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Yes, Delete", key=f"yes_del_{pid}", type="primary", use_container_width=True):
                                delete_pond_record(pid)
                                st.session_state[f"confirm_del_{pid}"] = False
                                st.success("Pond deleted successfully.")
                                st.rerun()
                        with c2:
                            if st.button("Cancel", key=f"cancel_del_{pid}", use_container_width=True):
                                st.session_state[f"confirm_del_{pid}"] = False
                                st.rerun()

    # 2. Add Pond Form
    with tabs[1]:
        st.markdown("#### Register New Pond")
        with st.form("main_add_pond_form", clear_on_submit=True):
            st.markdown("##### Basic Information")
            c1, c2, c3 = st.columns(3)
            with c1:
                p_id = st.text_input("Pond ID *", value=f"P-00{len(ponds)+1}")
                p_name = st.text_input("Pond Name *", placeholder="e.g. Varun Aquaculture Pond 1")
            with c2:
                location = st.text_input("Location / Sector *", placeholder="e.g. Bhimavaram, Block 2")
                area = st.number_input("Pond Area *", min_value=0.1, value=2.0, step=0.1)
            with c3:
                area_unit = st.selectbox("Area Unit", options=AREA_UNITS, index=0)
                status = st.selectbox("Operational Status", options=POND_STATUSES, index=0)

            st.markdown("##### Dimensions & Physical Characteristics")
            c4, c5, c6 = st.columns(3)
            with c4:
                length_m = st.number_input("Length (meters)", min_value=1.0, value=110.0, step=5.0)
                width_m = st.number_input("Width (meters)", min_value=1.0, value=40.0, step=5.0)
            with c5:
                avg_depth = st.number_input("Average Water Depth (meters)", min_value=0.5, value=1.6, step=0.1)
                max_depth = st.number_input("Maximum Depth (meters)", min_value=0.5, value=2.1, step=0.1)
            with c6:
                p_type = st.selectbox("Pond Construction Type", options=POND_TYPES, index=0)
                water_src = st.selectbox("Water Source Type", options=WATER_SOURCES, index=0)

            soil = st.text_input("Soil Texture / Quality", value="Clayey Loam (High water retention)")
            notes = st.text_area("Initial Operational Notes", placeholder="De-silted and limed with 200 kg agricultural lime.")

            submitted = st.form_submit_button("Register Pond", type="primary", use_container_width=True)
            if submitted:
                if not p_name or not p_id:
                    st.error("Pond ID and Pond Name are required.")
                elif any(p["PondID"] == p_id.strip() for p in ponds):
                    st.error(f"Pond ID '{p_id}' already exists.")
                else:
                    new_p = {
                        "PondID": p_id.strip().upper(),
                        "PondName": p_name.strip(),
                        "PondCode": f"{p_id.strip().upper()}-01",
                        "Status": status,
                        "Location": location.strip(),
                        "Area": float(area),
                        "AreaUnit": area_unit,
                        "LengthMeters": float(length_m),
                        "WidthMeters": float(width_m),
                        "AvgDepthMeters": float(avg_depth),
                        "MaxDepthMeters": float(max_depth),
                        "WaterVolumeM3": round(float(area) * 4046.86 * float(avg_depth), 0),
                        "PondType": p_type,
                        "WaterSource": water_src,
                        "WaterInlet": "PVC Sluice with Mesh Filter",
                        "WaterOutlet": "Bottom Monk Drain",
                        "WaterExchangeMethod": "Gravity / Pump",
                        "SoilType": soil.strip(),
                        "LiningType": "Compacted Clay",
                        "EmbankmentCondition": "Good",
                        "BottomCondition": "Limed and prepared",
                        "Owner": "Ramesh Varma",
                        "Manager": "K. Satyanarayana",
                        "DateAdded": date.today().strftime("%Y-%m-%d"),
                        "LastRenovation": date.today().strftime("%Y-%m-%d"),
                        "Notes": notes.strip()
                    }
                    st.session_state.demo_ponds.append(new_p)
                    st.success(f"Registered Pond {p_id} ({p_name}) successfully.")
                    st.rerun()

    # 3. Pond Profiles Command Center
    with tabs[2]:
        active_pid = st.session_state.get("active_profile_pond", ponds[0]["PondID"] if ponds else "P-001")
        pond_opts = [f"{p['PondID']} - {p['PondName']}" for p in ponds]
        pid_map = {f"{p['PondID']} - {p['PondName']}": p["PondID"] for p in ponds}

        curr_idx = 0
        for i, opt in enumerate(pond_opts):
            if pid_map[opt] == active_pid:
                curr_idx = i
                break

        col_sel, col_edit, col_ai = st.columns([3, 1, 1])
        with col_sel:
            selected_label = st.selectbox("Select Pond Profile", options=pond_opts, index=curr_idx)
            selected_pid = pid_map[selected_label]
            st.session_state.active_profile_pond = selected_pid
        with col_edit:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Edit Pond", use_container_width=True):
                dialog_edit_pond(selected_pid)
        with col_ai:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Analyze Pond", type="primary", use_container_width=True):
                st.session_state[f"show_ai_analysis_{selected_pid}"] = True

        p_obj = next((p for p in ponds if p["PondID"] == selected_pid), None)
        if p_obj:
            status_lvl = "optimal" if p_obj.get("Status") == "Active" else "monitor"
            badge = get_status_badge_html(p_obj.get("Status", "Active"), status_lvl)
            st.markdown(
                f"""
                <div class="saas-card" style="margin-top: 12px; border-left: 4px solid #0F2942;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h2 style="color: #0F2942; margin: 0; font-size: 1.4rem; font-weight: 700;">{p_obj['PondID']}: {p_obj['PondName']}</h2>
                            <div style="color: #64748B; font-size: 0.84rem; margin-top: 4px;">
                                Location: {p_obj['Location']} | Area: {p_obj['Area']} {p_obj['AreaUnit']} | Water Source: {p_obj['WaterSource']} | Type: {p_obj['PondType']}
                            </div>
                        </div>
                        <div>{badge}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Pond Action Row (All 9 Workflows)
            q1, q2, q3, q4, q5, q6, q7, q8, q9 = st.columns(9)
            with q1:
                if st.button("+ Water", key=f"cmd_w_{selected_pid}", use_container_width=True):
                    dialog_add_water_reading()
            with q2:
                if st.button("+ Fish", key=f"cmd_f_{selected_pid}", use_container_width=True):
                    dialog_add_fish_stock()
            with q3:
                if st.button("+ Growth", key=f"cmd_g_{selected_pid}", use_container_width=True):
                    dialog_add_growth_sample()
            with q4:
                if st.button("+ Feed", key=f"cmd_fd_{selected_pid}", use_container_width=True):
                    dialog_add_feeding()
            with q5:
                if st.button("+ Incident", key=f"cmd_i_{selected_pid}", use_container_width=True):
                    dialog_add_incident()
            with q6:
                if st.button("+ Expense", key=f"cmd_e_{selected_pid}", use_container_width=True):
                    dialog_add_expense()
            with q7:
                if st.button("+ Sale", key=f"cmd_s_{selected_pid}", use_container_width=True):
                    dialog_add_sale()
            with q8:
                if st.button("+ Harvest", key=f"cmd_h_{selected_pid}", use_container_width=True):
                    dialog_record_harvest()
            with q9:
                if st.button("+ Maint", key=f"cmd_m_{selected_pid}", use_container_width=True):
                    dialog_add_maintenance()

            # AI Analysis Box
            if st.session_state.get(f"show_ai_analysis_{selected_pid}", False):
                res = analyze_pond(selected_pid, st.session_state)
                clean_obs = res['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                clean_trend = res['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                clean_att = res['attention'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
                clean_chk = res['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()

                st.markdown(
                    f"""
                    <div class="saas-card" style="border-left: 4px solid #059669; background: #F0FDF4; margin: 14px 0;">
                        <h4 style="color: #065F46; margin: 0 0 8px 0;">AquaMitra AI — Pond Evaluation ({selected_pid})</h4>
                        <p style="font-size: 0.86rem; color: #1E293B; margin: 4px 0;"><strong>Observation:</strong> {clean_obs}</p>
                        <p style="font-size: 0.86rem; color: #1E293B; margin: 4px 0;"><strong>Trend:</strong> {clean_trend}</p>
                        <p style="font-size: 0.86rem; color: #92400E; margin: 4px 0;"><strong>Attention Area:</strong> {clean_att}</p>
                        <p style="font-size: 0.86rem; color: #0F2942; margin: 4px 0;"><strong>Suggested Check:</strong> {clean_chk}</p>
                        <div style="font-size: 0.72rem; color: #64748B; margin-top: 8px;">{res['data_limitations']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # 10 Pond Command Subtabs (Requirement 13)
            sub_tabs = st.tabs([
                "Pond Information",
                "Fish Stock",
                "Water Quality",
                "Feeding History",
                "Growth Sampling",
                "Mortality & Incidents",
                "Finances",
                "Maintenance",
                "Activity History",
                "Pond Analytics"
            ])

            # Tab 1: Info
            with sub_tabs[0]:
                i1, i2, i3 = st.columns(3)
                with i1:
                    st.write(f"**Pond ID:** {p_obj['PondID']}")
                    st.write(f"**Pond Code:** {p_obj.get('PondCode', 'N/A')}")
                    st.write(f"**Area:** {p_obj['Area']} {p_obj['AreaUnit']}")
                    st.write(f"**Water Volume:** {p_obj.get('WaterVolumeM3', 'N/A'):,} m³")
                with i2:
                    st.write(f"**Dimensions:** {p_obj.get('LengthMeters', 0)}m × {p_obj.get('WidthMeters', 0)}m")
                    st.write(f"**Depth (Avg / Max):** {p_obj.get('AvgDepthMeters', 0)}m / {p_obj.get('MaxDepthMeters', 0)}m")
                    st.write(f"**Soil Type:** {p_obj.get('SoilType', 'N/A')}")
                    st.write(f"**Lining Type:** {p_obj.get('LiningType', 'N/A')}")
                with i3:
                    st.write(f"**Water Source:** {p_obj.get('WaterSource', 'N/A')}")
                    st.write(f"**Inlet / Outlet:** {p_obj.get('WaterInlet', 'N/A')} / {p_obj.get('WaterOutlet', 'N/A')}")
                    st.write(f"**Owner / Manager:** {p_obj.get('Owner', 'N/A')} / {p_obj.get('Manager', 'N/A')}")
                    st.write(f"**Date Added:** {p_obj.get('DateAdded', 'N/A')}")
                st.info(f"**Operational Notes:** {p_obj.get('Notes', 'No notes recorded.')}")

            # Tab 2: Fish Stock
            with sub_tabs[1]:
                p_stocks = get_fish_stocks(pond_id=selected_pid)
                if p_stocks:
                    df = pd.DataFrame(p_stocks)
                    expected_cols = ["StockID", "Species", "Variety", "StockingDate", "NumberOfFish", "AvgInitialWeightGrams", "TotalInitialBiomassKg", "SourceHatchery"]
                    for col in expected_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(df[expected_cols], use_container_width=True, hide_index=True)
                else:
                    render_empty_state("Fish", "No Fish Stocked", "This pond currently has no stocked fish batches.", "Stock Fingerlings", f"stk_btn_{selected_pid}")

            # Tab 3: Water Quality
            with sub_tabs[2]:
                p_water = get_water_quality(pond_id=selected_pid)
                if p_water:
                    df = pd.DataFrame(p_water)
                    w_cols = ["ReadingID", "ReadingDate", "ReadingTime", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia", "WaterLevel", "Notes"]
                    for col in w_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(df[w_cols], use_container_width=True, hide_index=True)
                else:
                    render_empty_state("Water", "No Water Readings", "No water observations recorded for this pond.", "Log Reading", f"w_btn_{selected_pid}")

            # Tab 4: Feeding History
            with sub_tabs[3]:
                p_feed = get_feeding_records(pond_id=selected_pid)
                if p_feed:
                    df = pd.DataFrame(p_feed)
                    f_cols = ["FeedingDate", "FeedType", "FeedBrand", "ActualFeedKg", "FeedCostPerKg", "TotalFeedCost", "FeedResponse", "Notes"]
                    for col in f_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(df[f_cols], use_container_width=True, hide_index=True)
                else:
                    render_empty_state("Feeding", "No Feeding Records", "No feed logs recorded for this pond.", "Log Feed", f"fd_btn_{selected_pid}")

            # Tab 5: Growth Sampling
            with sub_tabs[4]:
                p_growth = get_growth_records(pond_id=selected_pid)
                if p_growth:
                    df = pd.DataFrame(p_growth)
                    g_cols = ["GrowthID", "ObservationDate", "Species", "SampleSize", "AvgFishWeightGrams", "EstimatedBiomassKg", "SamplingMethod", "Notes"]
                    for col in g_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(df[g_cols], use_container_width=True, hide_index=True)
                else:
                    render_empty_state("Growth", "No Growth Records", "No sampling recorded for this pond.", "Add Sample", f"gr_btn_{selected_pid}")

            # Tab 6: Mortality & Incidents
            with sub_tabs[5]:
                p_inc = get_incidents(pond_id=selected_pid)
                if p_inc:
                    df = pd.DataFrame(p_inc)
                    i_cols = ["IncidentID", "Date", "IncidentType", "NumberAffected", "ObservedBehaviour", "Severity", "Status", "ActionTaken"]
                    for col in i_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(df[i_cols], use_container_width=True, hide_index=True)
                else:
                    render_empty_state("Health", "All Clear", "No health or mortality incidents recorded for this pond.", "Log Incident", f"inc_btn_{selected_pid}")

            # Tab 7: Finances
            with sub_tabs[6]:
                p_exp = get_expenses(pond_id=selected_pid)
                p_sal = get_sales(pond_id=selected_pid)
                c_e, c_s = st.columns(2)
                with c_e:
                    st.markdown("##### Pond Expenses")
                    if p_exp:
                        df_e = pd.DataFrame(p_exp)
                        e_cols = ["ExpenseDate", "Category", "Description", "Amount"]
                        for col in e_cols:
                            if col not in df_e.columns:
                                df_e[col] = ""
                        st.dataframe(df_e[e_cols], use_container_width=True, hide_index=True)
                    else:
                        st.caption("No expenses recorded.")
                with c_s:
                    st.markdown("##### Pond Sales & Harvest Revenue")
                    if p_sal:
                        df_s = pd.DataFrame(p_sal)
                        s_cols = ["SaleDate", "Species", "QuantitySoldKg", "PricePerKg", "TotalRevenue", "PaymentStatus"]
                        for col in s_cols:
                            if col not in df_s.columns:
                                df_s[col] = ""
                        st.dataframe(df_s[s_cols], use_container_width=True, hide_index=True)
                    else:
                        st.caption("No sales recorded.")

            # Tab 8: Maintenance
            with sub_tabs[7]:
                p_maint = get_maintenance_records(pond_id=selected_pid)
                btn_m1, btn_m2 = st.columns([3, 1])
                with btn_m2:
                    if st.button("Log Maintenance", key=f"maint_btn_tab_{selected_pid}", type="primary", use_container_width=True):
                        dialog_add_maintenance()
                if p_maint:
                    df_m = pd.DataFrame(p_maint)
                    m_cols = ["Date", "Asset", "MaintenanceType", "Description", "Cost", "Status", "NextMaintenance"]
                    for col in m_cols:
                        if col not in df_m.columns:
                            df_m[col] = ""
                    st.dataframe(df_m[m_cols], use_container_width=True, hide_index=True)
                else:
                    render_empty_state("Maintenance", "No Maintenance Records", "All equipment and pond structures are operating normally.", "Add Maintenance", f"add_m_btn_{selected_pid}")

            # Tab 9: Activity History
            with sub_tabs[8]:
                acts = get_unified_recent_activity(pond_id=selected_pid, limit=10)
                render_activity_feed(acts)

            # Tab 10: Pond Analytics
            with sub_tabs[9]:
                st.markdown("##### Pond Parameter Trends")
                p_w = get_water_quality(pond_id=selected_pid)
                if p_w:
                    df_w = pd.DataFrame(p_w).sort_values("ReadingDate")
                    if "ReadingDate" in df_w.columns and "DissolvedOxygen" in df_w.columns:
                        fig = px.line(df_w, x="ReadingDate", y=["DissolvedOxygen", "pH", "Temperature"], markers=True, title=f"Water Parameters for {selected_pid}")
                        fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=1.15))
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Log water observations to unlock parameter trend charts.")

    # 4. Pond Activity Timeline
    with tabs[3]:
        st.markdown("#### Chronological Activity History")
        filter_p = st.selectbox("Filter Activity by Pond", options=["All Ponds"] + [p["PondID"] for p in ponds], index=0)
        p_filter = None if filter_p == "All Ponds" else filter_p
        acts = get_unified_recent_activity(pond_id=p_filter, limit=20)
        render_activity_feed(acts)

    # 5. Pond Maintenance Scheduler
    with tabs[4]:
        st.markdown("#### Equipment & Pond Maintenance Log")
        m_top1, m_top2 = st.columns([3, 1])
        with m_top2:
            if st.button("Add Maintenance Log", type="primary", use_container_width=True):
                dialog_add_maintenance()

        maints = get_maintenance_records()
        if maints:
            df_m = pd.DataFrame(maints)
            expected_m = ["Date", "PondID", "Asset", "MaintenanceType", "Description", "Cost", "Status", "NextMaintenance", "Notes"]
            for col in expected_m:
                if col not in df_m.columns:
                    df_m[col] = ""
            st.dataframe(df_m[expected_m], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Maintenance", "No Maintenance Scheduled", "Equipment and aerators are in routine operational condition.")
