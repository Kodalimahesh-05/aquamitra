"""
AquaMitra Pond Management View Module
Provides All Ponds Grid, Add Pond Form, Pond Command Center (10 Sub-tabs), Activity Timeline,
and Maintenance Scheduler with strictly zero emojis. Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import POND_STATUSES, POND_TYPES, AREA_UNITS, WATER_SOURCES
from utils.translations import t, tv, rename_df_for_display
from utils.demo_data import get_pond_health_snapshot, get_unified_recent_activity
from components.cards import (
    render_pond_snapshot,
    render_empty_state,
    render_activity_feed
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


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_ponds_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "All Ponds", "అన్ని చెరువులు"),
        _lbl(lang, "Add Pond", "చెరువు జోడించు"),
        _lbl(lang, "Pond Profiles", "చెరువు ప్రొఫైల్స్"),
        _lbl(lang, "Pond Activity", "చెరువు కార్యకలాపాలు"),
        _lbl(lang, "Pond Maintenance", "చెరువు నిర్వహణ")
    ]
    tabs = st.tabs(subtabs)
    ponds = st.session_state.get("demo_ponds", [])

    # 1. All Ponds Grid & Management
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Registered Aquaculture Ponds', 'నమోదైన చేపల చెరువులు')}")
        col_f1, col_f2, col_f3, col_add = st.columns([3, 2, 2, 2])
        with col_f1:
            p_search = st.text_input(
                _lbl(lang, "Search Ponds", "చెరువులను వెతకండి"),
                placeholder=_lbl(lang, "Search by name, ID or location...", "పేరు, ID లేదా ప్రాంతం ద్వారా వెతకండి..."),
                label_visibility="collapsed"
            )
        with col_f2:
            status_filter = st.selectbox(
                _lbl(lang, "Filter Status", "స్థితి వడపోత"),
                options=["All"] + POND_STATUSES,
                index=0,
                format_func=lambda x: tv(x, lang)
            )
        with col_f3:
            type_filter = st.selectbox(
                _lbl(lang, "Filter Type", "రకం వడపోత"),
                options=["All"] + POND_TYPES,
                index=0,
                format_func=lambda x: tv(x, lang)
            )
        with col_add:
            if st.button(_lbl(lang, "Register New Pond", "కొత్త చెరువు నమోదు"), type="primary", use_container_width=True):
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
            render_empty_state(
                _lbl(lang, "Ponds", "చెరువులు"),
                _lbl(lang, "No Ponds Found", "చెరువులు కనుగొనబడలేదు"),
                _lbl(lang, "No ponds match the selected criteria.", "ఎంచుకున్న ప్రమాణాలకు సరిపోలే చెరువులు లేవు."),
                t("qa_add_pond", lang),
                "all_p_add_btn"
            )
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered):
                pid = p["PondID"]
                snap = get_pond_health_snapshot(pid)
                with cols[idx % 2]:
                    render_pond_snapshot(snap)
                    b1, b2, b3 = st.columns([2, 1, 1])
                    with b1:
                        if st.button(f"{_lbl(lang, 'Command Center', 'నిర్వహణ కేంద్రం')} ({pid})", key=f"open_pond_{pid}", use_container_width=True):
                            st.session_state.active_profile_pond = pid
                            st.rerun()
                    with b2:
                        if st.button(_lbl(lang, "Edit", "సవరించు"), key=f"edit_pond_{pid}", use_container_width=True):
                            dialog_edit_pond(pid)
                    with b3:
                        if st.button(_lbl(lang, "Delete", "తొలగించు"), key=f"del_pond_{pid}", use_container_width=True):
                            st.session_state[f"confirm_del_{pid}"] = True

                    if st.session_state.get(f"confirm_del_{pid}", False):
                        st.warning(_lbl(
                            lang,
                            f"Confirm deleting {p.get('PondName')} ({pid})?",
                            f"{p.get('PondName')} ({pid}) ను తొలగించాలని నిర్ధారిస్తున్నారా?"
                        ))
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button(_lbl(lang, "Yes, Delete", "అవును, తొలగించు"), key=f"yes_del_{pid}", type="primary", use_container_width=True):
                                delete_pond_record(pid)
                                st.session_state[f"confirm_del_{pid}"] = False
                                st.success(_lbl(lang, "Pond deleted successfully.", "చెరువు విజయవంతంగా తొలగించబడింది."))
                                st.rerun()
                        with c2:
                            if st.button(_lbl(lang, "Cancel", "రద్దు చేయండి"), key=f"cancel_del_{pid}", use_container_width=True):
                                st.session_state[f"confirm_del_{pid}"] = False
                                st.rerun()

    # 2. Add Pond Form
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Register New Pond', 'కొత్త చెరువును నమోదు చేయండి')}")
        with st.form("main_add_pond_form", clear_on_submit=True):
            st.markdown(f"##### {_lbl(lang, 'Basic Information', 'ప్రాథమిక సమాచారం')}")
            c1, c2, c3 = st.columns(3)
            with c1:
                p_id = st.text_input(_lbl(lang, "Pond ID *", "చెరువు ID *"), value=f"P-00{len(ponds)+1}")
                p_name = st.text_input(_lbl(lang, "Pond Name *", "చెరువు పేరు *"), placeholder=_lbl(lang, "e.g. Varun Aquaculture Pond 1", "ఉదా. వరుణ్ ఆక్వా చెరువు 1"))
            with c2:
                location = st.text_input(_lbl(lang, "Location / Sector *", "ప్రాంతం / సెక్టార్ *"), placeholder=_lbl(lang, "e.g. Bhimavaram, Block 2", "ఉదా. భీమవరం, బ్లాక్ 2"))
                area = st.number_input(_lbl(lang, "Pond Area *", "చెరువు విస్తీర్ణం *"), min_value=0.1, value=2.0, step=0.1)
            with c3:
                area_unit = st.selectbox(_lbl(lang, "Area Unit", "విస్తీర్ణ ప్రమాణం"), options=AREA_UNITS, index=0, format_func=lambda x: tv(x, lang))
                status = st.selectbox(_lbl(lang, "Operational Status", "నిర్వహణ స్థితి"), options=POND_STATUSES, index=0, format_func=lambda x: tv(x, lang))

            st.markdown(f"##### {_lbl(lang, 'Dimensions & Physical Characteristics', 'కొలతలు మరియు భౌతిక లక్షణాలు')}")
            c4, c5, c6 = st.columns(3)
            with c4:
                length_m = st.number_input(_lbl(lang, "Length (meters)", "పొడవు (మీటర్లు)"), min_value=1.0, value=110.0, step=5.0)
                width_m = st.number_input(_lbl(lang, "Width (meters)", "వెడల్పు (మీటర్లు)"), min_value=1.0, value=40.0, step=5.0)
            with c5:
                avg_depth = st.number_input(_lbl(lang, "Average Water Depth (meters)", "సగటు నీటి లోతు (మీటర్లు)"), min_value=0.5, value=1.6, step=0.1)
                max_depth = st.number_input(_lbl(lang, "Maximum Depth (meters)", "గరిష్ట లోతు (మీటర్లు)"), min_value=0.5, value=2.1, step=0.1)
            with c6:
                p_type = st.selectbox(_lbl(lang, "Pond Construction Type", "చెరువు నిర్మాణ రకం"), options=POND_TYPES, index=0, format_func=lambda x: tv(x, lang))
                water_src = st.selectbox(_lbl(lang, "Water Source Type", "నీటి వనరు రకం"), options=WATER_SOURCES, index=0, format_func=lambda x: tv(x, lang))

            soil = st.text_input(_lbl(lang, "Soil Texture / Quality", "నేల స్వభావం / నాణ్యత"), value="Clayey Loam (High water retention)")
            notes = st.text_area(_lbl(lang, "Initial Operational Notes", "ప్రారంభ నిర్వహణ గమనికలు"), placeholder=_lbl(lang, "De-silted and limed with 200 kg agricultural lime.", "పూడిక తీయబడింది మరియు 200 కేజీ సున్నం చల్లబడింది."))

            submitted = st.form_submit_button(_lbl(lang, "Register Pond", "చెరువును నమోదు చేయండి"), type="primary", use_container_width=True)
            if submitted:
                if not p_name or not p_id:
                    st.error(_lbl(lang, "Pond ID and Pond Name are required.", "చెరువు ID మరియు పేరు తప్పనిసరి."))
                elif any(p["PondID"] == p_id.strip() for p in ponds):
                    st.error(_lbl(lang, f"Pond ID '{p_id}' already exists.", f"చెరువు ID '{p_id}' ఇప్పటికే ఉంది."))
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
                    st.success(_lbl(lang, f"Registered Pond {p_id} ({p_name}) successfully.", f"చెరువు {p_id} ({p_name}) విజయవంతంగా నమోదైంది."))
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
            selected_label = st.selectbox(_lbl(lang, "Select Pond Profile", "చెరువు ప్రొఫైల్‌ను ఎంచుకోండి"), options=pond_opts, index=curr_idx)
            selected_pid = pid_map[selected_label]
            st.session_state.active_profile_pond = selected_pid
        with col_edit:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button(_lbl(lang, "Edit Pond", "సవరించండి"), use_container_width=True):
                dialog_edit_pond(selected_pid)
        with col_ai:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button(_lbl(lang, "Analyze Pond", "AI విశ్లేషణ"), type="primary", use_container_width=True):
                st.session_state[f"show_ai_analysis_{selected_pid}"] = True

        p_obj = next((p for p in ponds if p["PondID"] == selected_pid), None)
        if p_obj:
            status_lvl = "optimal" if p_obj.get("Status") == "Active" else "monitor"
            badge = get_status_badge_html(tv(p_obj.get("Status", "Active"), lang), status_lvl)
            st.markdown(
                f"""
                <div class="saas-card" style="margin-top: 12px; border-left: 4px solid #0F2942;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div>
                            <h2 style="color: #0F2942; margin: 0; font-size: 1.4rem; font-weight: 700;">{p_obj['PondID']}: {p_obj['PondName']}</h2>
                            <div style="color: #64748B; font-size: 0.84rem; margin-top: 4px;">
                                {_lbl(lang, 'Location', 'ప్రాంతం')}: {p_obj['Location']} | {_lbl(lang, 'Area', 'విస్తీర్ణం')}: {p_obj['Area']} {tv(p_obj['AreaUnit'], lang)} | {_lbl(lang, 'Water Source', 'నీటి వనరు')}: {tv(p_obj['WaterSource'], lang)} | {_lbl(lang, 'Type', 'రకం')}: {tv(p_obj['PondType'], lang)}
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
                if st.button(_lbl(lang, "+ Water", "+ నీరు"), key=f"cmd_w_{selected_pid}", use_container_width=True):
                    dialog_add_water_reading()
            with q2:
                if st.button(_lbl(lang, "+ Fish", "+ చేపలు"), key=f"cmd_f_{selected_pid}", use_container_width=True):
                    dialog_add_fish_stock()
            with q3:
                if st.button(_lbl(lang, "+ Growth", "+ పెరుగుదల"), key=f"cmd_g_{selected_pid}", use_container_width=True):
                    dialog_add_growth_sample()
            with q4:
                if st.button(_lbl(lang, "+ Feed", "+ మేత"), key=f"cmd_fd_{selected_pid}", use_container_width=True):
                    dialog_add_feeding()
            with q5:
                if st.button(_lbl(lang, "+ Incident", "+ సంఘటన"), key=f"cmd_i_{selected_pid}", use_container_width=True):
                    dialog_add_incident()
            with q6:
                if st.button(_lbl(lang, "+ Expense", "+ ఖర్చు"), key=f"cmd_e_{selected_pid}", use_container_width=True):
                    dialog_add_expense()
            with q7:
                if st.button(_lbl(lang, "+ Sale", "+ అమ్మకం"), key=f"cmd_s_{selected_pid}", use_container_width=True):
                    dialog_add_sale()
            with q8:
                if st.button(_lbl(lang, "+ Harvest", "+ కోత"), key=f"cmd_h_{selected_pid}", use_container_width=True):
                    dialog_record_harvest()
            with q9:
                if st.button(_lbl(lang, "+ Maint", "+ నిర్వహణ"), key=f"cmd_m_{selected_pid}", use_container_width=True):
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
                        <h4 style="color: #065F46; margin: 0 0 8px 0;">{_lbl(lang, f'AquaMitra AI — Pond Evaluation ({selected_pid})', f'ఆక్వామిత్ర AI — చెరువు విశ్లేషణ ({selected_pid})')}</h4>
                        <p style="font-size: 0.86rem; color: #1E293B; margin: 4px 0;"><strong>{_lbl(lang, 'Observation', 'పరిశీలన')}:</strong> {clean_obs}</p>
                        <p style="font-size: 0.86rem; color: #1E293B; margin: 4px 0;"><strong>{_lbl(lang, 'Trend', 'ధోరణి')}:</strong> {clean_trend}</p>
                        <p style="font-size: 0.86rem; color: #92400E; margin: 4px 0;"><strong>{_lbl(lang, 'Attention Area', 'శ్రద్ధ వహించాల్సిన అంశం')}:</strong> {clean_att}</p>
                        <p style="font-size: 0.86rem; color: #0F2942; margin: 4px 0;"><strong>{_lbl(lang, 'Suggested Check', 'సూచించిన తనిఖీ')}:</strong> {clean_chk}</p>
                        <div style="font-size: 0.72rem; color: #64748B; margin-top: 8px;">{res['data_limitations']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # 10 Pond Command Subtabs
            sub_tabs = st.tabs([
                _lbl(lang, "Pond Information", "చెరువు సమాచారం"),
                _lbl(lang, "Fish Stock", "చేపల నిల్వ"),
                _lbl(lang, "Water Quality", "నీటి నాణ్యత"),
                _lbl(lang, "Feeding History", "మేత చరిత్ర"),
                _lbl(lang, "Growth Sampling", "పెరుగుదల నమూనా"),
                _lbl(lang, "Mortality & Incidents", "మరణాలు & సంఘటనలు"),
                _lbl(lang, "Finances", "ఆర్థిక వివరాలు"),
                _lbl(lang, "Maintenance", "నిర్వహణ"),
                _lbl(lang, "Activity History", "కార్యాచరణ చరిత్ర"),
                _lbl(lang, "Pond Analytics", "చెరువు విశ్లేషణలు")
            ])

            # Tab 1: Info
            with sub_tabs[0]:
                i1, i2, i3 = st.columns(3)
                with i1:
                    st.write(f"**{_lbl(lang, 'Pond ID', 'చెరువు ID')}:** {p_obj['PondID']}")
                    st.write(f"**{_lbl(lang, 'Pond Code', 'చెరువు కోడ్')}:** {p_obj.get('PondCode', 'N/A')}")
                    st.write(f"**{_lbl(lang, 'Area', 'విస్తీర్ణం')}:** {p_obj['Area']} {tv(p_obj['AreaUnit'], lang)}")
                    st.write(f"**{_lbl(lang, 'Water Volume', 'నీటి పరిమాణం')}:** {p_obj.get('WaterVolumeM3', 0):,} m³")
                with i2:
                    st.write(f"**{_lbl(lang, 'Dimensions', 'కొలతలు')}:** {p_obj.get('LengthMeters', 0)}m × {p_obj.get('WidthMeters', 0)}m")
                    st.write(f"**{_lbl(lang, 'Depth (Avg / Max)', 'లోతు (సగటు / గరిష్ట)')}:** {p_obj.get('AvgDepthMeters', 0)}m / {p_obj.get('MaxDepthMeters', 0)}m")
                    st.write(f"**{_lbl(lang, 'Soil Type', 'నేల రకం')}:** {tv(p_obj.get('SoilType', 'N/A'), lang)}")
                    st.write(f"**{_lbl(lang, 'Lining Type', 'లైనింగ్ రకం')}:** {p_obj.get('LiningType', 'N/A')}")
                with i3:
                    st.write(f"**{_lbl(lang, 'Water Source', 'నీటి వనరు')}:** {tv(p_obj.get('WaterSource', 'N/A'), lang)}")
                    st.write(f"**{_lbl(lang, 'Inlet / Outlet', 'ఇన్‌లెట్ / అవుట్‌లెట్')}:** {p_obj.get('WaterInlet', 'N/A')} / {p_obj.get('WaterOutlet', 'N/A')}")
                    st.write(f"**{_lbl(lang, 'Owner / Manager', 'యజమాని / మేనేజర్')}:** {p_obj.get('Owner', 'N/A')} / {p_obj.get('Manager', 'N/A')}")
                    st.write(f"**{_lbl(lang, 'Date Added', 'నమోదు తేదీ')}:** {p_obj.get('DateAdded', 'N/A')}")
                st.info(f"**{_lbl(lang, 'Operational Notes', 'నిర్వహణ గమనికలు')}:** {p_obj.get('Notes', _lbl(lang, 'No notes recorded.', 'గమనికలు లేవు.'))}")

            # Tab 2: Fish Stock
            with sub_tabs[1]:
                p_stocks = get_fish_stocks(pond_id=selected_pid)
                if p_stocks:
                    df = pd.DataFrame(p_stocks)
                    expected_cols = ["StockID", "Species", "Variety", "StockingDate", "NumberOfFish", "AvgInitialWeightGrams", "TotalInitialBiomassKg", "SourceHatchery"]
                    for col in expected_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(rename_df_for_display(df[expected_cols], lang), use_container_width=True, hide_index=True)
                else:
                    render_empty_state(
                        _lbl(lang, "Fish", "చేపలు"),
                        _lbl(lang, "No Fish Stocked", "చేపల నిల్వ లేదు"),
                        _lbl(lang, "This pond currently has no stocked fish batches.", "ఈ చెరువులో ప్రస్తుతం చేపల బ్యాచ్‌లు నిల్వ చేయబడలేదు."),
                        _lbl(lang, "Stock Fingerlings", "చేప పిల్లలను నిల్వ చేయండి"),
                        f"stk_btn_{selected_pid}"
                    )

            # Tab 3: Water Quality
            with sub_tabs[2]:
                p_water = get_water_quality(pond_id=selected_pid)
                if p_water:
                    df = pd.DataFrame(p_water)
                    w_cols = ["ReadingID", "ReadingDate", "ReadingTime", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia", "WaterLevel", "Notes"]
                    for col in w_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(rename_df_for_display(df[w_cols], lang), use_container_width=True, hide_index=True)
                else:
                    render_empty_state(
                        _lbl(lang, "Water", "నీరు"),
                        _lbl(lang, "No Water Readings", "నీటి రీడింగ్‌లు లేవు"),
                        _lbl(lang, "No water observations recorded for this pond.", "ఈ చెరువుకు నీటి పరిశీలనలు నమోదు కాలేదు."),
                        _lbl(lang, "Log Reading", "రీడింగ్ నమోదు"),
                        f"w_btn_{selected_pid}"
                    )

            # Tab 4: Feeding History
            with sub_tabs[3]:
                p_feed = get_feeding_records(pond_id=selected_pid)
                if p_feed:
                    df = pd.DataFrame(p_feed)
                    f_cols = ["FeedingDate", "FeedType", "FeedBrand", "ActualFeedKg", "FeedCostPerKg", "TotalFeedCost", "FeedResponse", "Notes"]
                    for col in f_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(rename_df_for_display(df[f_cols], lang), use_container_width=True, hide_index=True)
                else:
                    render_empty_state(
                        _lbl(lang, "Feeding", "మేత"),
                        _lbl(lang, "No Feeding Records", "మేత రికార్డులు లేవు"),
                        _lbl(lang, "No feed logs recorded for this pond.", "ఈ చెరువుకు మేత లాగ్‌లు నమోదు కాలేదు."),
                        t("qa_log_feed", lang),
                        f"fd_btn_{selected_pid}"
                    )

            # Tab 5: Growth Sampling
            with sub_tabs[4]:
                p_growth = get_growth_records(pond_id=selected_pid)
                if p_growth:
                    df = pd.DataFrame(p_growth)
                    g_cols = ["GrowthID", "ObservationDate", "Species", "SampleSize", "AvgFishWeightGrams", "EstimatedBiomassKg", "SamplingMethod", "Notes"]
                    for col in g_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(rename_df_for_display(df[g_cols], lang), use_container_width=True, hide_index=True)
                else:
                    render_empty_state(
                        _lbl(lang, "Growth", "పెరుగుదల"),
                        _lbl(lang, "No Growth Records", "పెరుగుదల రికార్డులు లేవు"),
                        _lbl(lang, "No sampling recorded for this pond.", "ఈ చెరువుకు నమూనాలు నమోదు కాలేదు."),
                        _lbl(lang, "Add Sample", "నమూనా జోడించు"),
                        f"gr_btn_{selected_pid}"
                    )

            # Tab 6: Mortality & Incidents
            with sub_tabs[5]:
                p_inc = get_incidents(pond_id=selected_pid)
                if p_inc:
                    df = pd.DataFrame(p_inc)
                    i_cols = ["IncidentID", "Date", "IncidentType", "NumberAffected", "ObservedBehaviour", "Severity", "Status", "ActionTaken"]
                    for col in i_cols:
                        if col not in df.columns:
                            df[col] = ""
                    st.dataframe(rename_df_for_display(df[i_cols], lang), use_container_width=True, hide_index=True)
                else:
                    render_empty_state(
                        _lbl(lang, "Health", "ఆరోగ్యం"),
                        _lbl(lang, "All Clear", "అన్నీ సాధారణంగా ఉన్నాయి"),
                        _lbl(lang, "No health or mortality incidents recorded for this pond.", "ఈ చెరువుకు ఆరోగ్య లేదా మరణాల సంఘటనలు నమోదు కాలేదు."),
                        t("qa_log_incident", lang),
                        f"inc_btn_{selected_pid}"
                    )

            # Tab 7: Finances
            with sub_tabs[6]:
                p_exp = get_expenses(pond_id=selected_pid)
                p_sal = get_sales(pond_id=selected_pid)
                c_e, c_s = st.columns(2)
                with c_e:
                    st.markdown(f"##### {_lbl(lang, 'Pond Expenses', 'చెరువు ఖర్చులు')}")
                    if p_exp:
                        df_e = pd.DataFrame(p_exp)
                        e_cols = ["ExpenseDate", "Category", "Description", "Amount"]
                        for col in e_cols:
                            if col not in df_e.columns:
                                df_e[col] = ""
                        st.dataframe(rename_df_for_display(df_e[e_cols], lang), use_container_width=True, hide_index=True)
                    else:
                        st.caption(_lbl(lang, "No expenses recorded.", "ఖర్చులు నమోదు కాలేదు."))
                with c_s:
                    st.markdown(f"##### {_lbl(lang, 'Pond Sales & Harvest Revenue', 'చెరువు అమ్మకాలు & కోత ఆదాయం')}")
                    if p_sal:
                        df_s = pd.DataFrame(p_sal)
                        s_cols = ["SaleDate", "Species", "QuantitySoldKg", "PricePerKg", "TotalRevenue", "PaymentStatus"]
                        for col in s_cols:
                            if col not in df_s.columns:
                                df_s[col] = ""
                        st.dataframe(rename_df_for_display(df_s[s_cols], lang), use_container_width=True, hide_index=True)
                    else:
                        st.caption(_lbl(lang, "No sales recorded.", "అమ్మకాలు నమోదు కాలేదు."))

            # Tab 8: Maintenance
            with sub_tabs[7]:
                p_maint = get_maintenance_records(pond_id=selected_pid)
                btn_m1, btn_m2 = st.columns([3, 1])
                with btn_m2:
                    if st.button(_lbl(lang, "Log Maintenance", "నిర్వహణ నమోదు"), key=f"maint_btn_tab_{selected_pid}", type="primary", use_container_width=True):
                        dialog_add_maintenance()
                if p_maint:
                    df_m = pd.DataFrame(p_maint)
                    m_cols = ["Date", "Asset", "MaintenanceType", "Description", "Cost", "Status", "NextMaintenance"]
                    for col in m_cols:
                        if col not in df_m.columns:
                            df_m[col] = ""
                    st.dataframe(rename_df_for_display(df_m[m_cols], lang), use_container_width=True, hide_index=True)
                else:
                    render_empty_state(
                        _lbl(lang, "Maintenance", "నిర్వహణ"),
                        _lbl(lang, "No Maintenance Records", "నిర్వహణ రికార్డులు లేవు"),
                        _lbl(lang, "All equipment and pond structures are operating normally.", "అన్ని పరికరాలు మరియు చెరువు నిర్మాణాలు సాధారణంగా పనిచేస్తున్నాయి."),
                        t("qa_add_maintenance", lang),
                        f"add_m_btn_{selected_pid}"
                    )

            # Tab 9: Activity History
            with sub_tabs[8]:
                acts = get_unified_recent_activity(pond_id=selected_pid, limit=10)
                render_activity_feed(acts)

            # Tab 10: Pond Analytics
            with sub_tabs[9]:
                st.markdown(f"##### {_lbl(lang, 'Pond Parameter Trends', 'చెరువు పారామితి ధోరణులు')}")
                p_w = get_water_quality(pond_id=selected_pid)
                if p_w:
                    df_w = pd.DataFrame(p_w).sort_values("ReadingDate")
                    if "ReadingDate" in df_w.columns and "DissolvedOxygen" in df_w.columns:
                        fig = px.line(
                            df_w,
                            x="ReadingDate",
                            y=["DissolvedOxygen", "pH", "Temperature"],
                            markers=True,
                            title=_lbl(lang, f"Water Parameters for {selected_pid}", f"{selected_pid} కోసం నీటి పారామితులు"),
                            labels={"ReadingDate": _lbl(lang, "Date", "తేదీ"), "value": _lbl(lang, "Value", "విలువ")}
                        )
                        fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20), legend=dict(orientation="h", y=1.15))
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(_lbl(lang, "Log water observations to unlock parameter trend charts.", "పారామితి ధోరణి చార్ట్‌లను చూడటానికి నీటి పరిశీలనలను నమోదు చేయండి."))

    # 4. Pond Activity Timeline
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Chronological Activity History', 'కాలక్రమానుసార కార్యకలాపాల చరిత్ర')}")
        filter_p = st.selectbox(
            _lbl(lang, "Filter Activity by Pond", "చెరువు వారీగా కార్యకలాపాలను వడపోయండి"),
            options=["All Ponds"] + [p["PondID"] for p in ponds],
            index=0,
            format_func=lambda x: tv(x, lang)
        )
        p_filter = None if filter_p == "All Ponds" else filter_p
        acts = get_unified_recent_activity(pond_id=p_filter, limit=20)
        render_activity_feed(acts)

    # 5. Pond Maintenance Scheduler
    with tabs[4]:
        st.markdown(f"#### {_lbl(lang, 'Equipment & Pond Maintenance Log', 'పరికరాలు మరియు చెరువు నిర్వహణ లాగ్')}")
        m_top1, m_top2 = st.columns([3, 1])
        with m_top2:
            if st.button(_lbl(lang, "Add Maintenance Log", "నిర్వహణ లాగ్ జోడించు"), type="primary", use_container_width=True):
                dialog_add_maintenance()

        maints = get_maintenance_records()
        if maints:
            df_m = pd.DataFrame(maints)
            expected_m = ["Date", "PondID", "Asset", "MaintenanceType", "Description", "Cost", "Status", "NextMaintenance", "Notes"]
            for col in expected_m:
                if col not in df_m.columns:
                    df_m[col] = ""
            st.dataframe(rename_df_for_display(df_m[expected_m], lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Maintenance", "నిర్వహణ"),
                _lbl(lang, "No Maintenance Scheduled", "నిర్వహణ షెడ్యూల్ లేదు"),
                _lbl(lang, "Equipment and aerators are in routine operational condition.", "పరికరాలు మరియు ఏరేటర్లు సాధారణ పనితీరులో ఉన్నాయి.")
            )
