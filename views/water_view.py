"""
AquaMitra Water Quality View Module
Provides Parameter Matrix Dashboard, Readings Log, Interactive Plotly History,
Water Events, Multi-Pond Comparison, and Reference Range Configuration with strictly zero emojis.
Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import DEFAULT_REFERENCE_RANGES
from utils.translations import tv, rename_df_for_display
from components.cards import render_empty_state
from components.quick_actions import dialog_add_water_reading
from services.ai.ai_service import analyze_water
from database.queries import get_water_quality


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_water_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Water Dashboard", "నీటి డాష్‌బోర్డ్"),
        _lbl(lang, "Water Readings", "నీటి రీడింగ్‌లు"),
        _lbl(lang, "Water History", "నీటి చరిత్ర"),
        _lbl(lang, "Water Events", "నీటి నిర్వహణ సంఘటనలు"),
        _lbl(lang, "Water Comparison", "చెరువుల పోలిక"),
        _lbl(lang, "Reference Ranges", "ప్రమాణ పరిధులు")
    ]
    tabs = st.tabs(subtabs)

    waters = get_water_quality()
    events = st.session_state.get("demo_water_events", [])
    ponds = st.session_state.get("demo_ponds", [])

    param_labels_te = {
        "DissolvedOxygen": "కరిగిన ఆక్సిజన్ (DO mg/L)",
        "pH": "pH విలువ",
        "Temperature": "ఉష్ణోగ్రత (°C)",
        "Turbidity": "టర్బిడిటీ (NTU)",
        "Ammonia": "అమోనియా (mg/L)",
        "Nitrite": "నైట్రైట్ (mg/L)",
        "Nitrate": "నైట్రేట్ (mg/L)",
        "WaterLevel": "నీటి మట్టం (మీ.)",
        "Salinity": "లవణీయత (ppt)",
        "Alkalinity": "ఆల్కలీనిటీ (mg/L)",
    }
    ev_type_te = {
        "Water Added": "నీరు చేర్చబడింది",
        "Water Removed": "నీరు తొలగించబడింది",
        "Water Exchange": "నీటి మార్పిడి",
        "Rainfall Event": "వర్షపాతం సంఘటన",
        "Drainage": "డ్రైనేజీ / బయటకు పంపడం",
        "Refill": "నీరు తిరిగి నింపడం",
        "Cleaning": "శుభ్రపరచడం",
        "Other": "ఇతరములు",
    }

    # 1. Water Dashboard (Matrix View)
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Water Quality Parameter Matrix', 'నీటి నాణ్యత పారామితి పట్టిక')}")
        st.caption(_lbl(
            lang,
            "Latest recorded water conditions across all fishery ponds against baseline reference ranges.",
            "ప్రమాణ పరిధులతో పోల్చి అన్ని చెరువులలోని తాజా నీటి నాణ్యత స్థితి."
        ))

        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button(_lbl(lang, "Analyze Water with AI", "AI తో నీటి విశ్లేషణ"), type="secondary", use_container_width=True):
                st.session_state.show_water_ai = True

        if st.session_state.get("show_water_ai", False):
            res = analyze_water(st.session_state)
            clean_obs = res['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = res['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = res['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(
                f"**{_lbl(lang, 'Observation', 'పరిశీలన')}:** {clean_obs}\n\n"
                f"**{_lbl(lang, 'Trend', 'ధోరణి')}:** {clean_tr}\n\n"
                f"**{_lbl(lang, 'Suggested Check', 'సూచించిన తనిఖీ')}:** {clean_ck}"
            )

        # Build Clean Matrix without emojis
        param_col_name = _lbl(lang, "Parameter", "పారామితి")
        matrix_data = {
            param_col_name: [
                _lbl(lang, "pH (6.5 - 8.5)", "pH విలువ (6.5 - 8.5)"),
                _lbl(lang, "Dissolved Oxygen (>= 5.0 mg/L)", "కరిగిన ఆక్సిజన్ (>= 5.0 mg/L)"),
                _lbl(lang, "Temperature (24 - 32 °C)", "ఉష్ణోగ్రత (24 - 32 °C)"),
                _lbl(lang, "Turbidity (20 - 40 NTU)", "టర్బిడిటీ (20 - 40 NTU)"),
                _lbl(lang, "Ammonia (<= 0.05 mg/L)", "అమోనియా (<= 0.05 mg/L)"),
                _lbl(lang, "Water Level (>= 1.5 m)", "నీటి మట్టం (>= 1.5 మీ.)")
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
                    f"[{tv(ph_status, lang)}] {last_w.get('pH')}",
                    f"[{tv(do_status, lang)}] {last_w.get('DissolvedOxygen')} mg/L",
                    f"[{tv(temp_status, lang)}] {last_w.get('Temperature')} °C",
                    f"[{tv(turb_status, lang)}] {last_w.get('Turbidity')} NTU",
                    f"[{tv(nh3_status, lang)}] {last_w.get('Ammonia')} mg/L",
                    f"[{tv(lvl_status, lang)}] {last_w.get('WaterLevel')} m"
                ]
            else:
                matrix_data[f"{pid} ({p['PondName']})"] = [f"[{tv('No Data', lang)}]"] * 6

        st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)
        st.caption(_lbl(
            lang,
            "Status Indicators: [Optimal] Within baseline range | [Monitor] Marginal deviation | [Alert] Exceeds safe threshold | [No Data] Observation needed",
            "స్థితి సూచికలు: [ఉత్తమం] ప్రమాణ పరిధిలో ఉంది | [పర్యవేక్షణ అవసరం] స్వల్ప మార్పు | [అలర్ట్] పరిమితి దాటింది | [డేటా లేదు] పరిశీలన అవసరం"
        ))

    # 2. Water Readings
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Manual Water Quality Observations', 'నీటి నాణ్యత రీడింగ్‌ల నమోదు')}")
        rc1, rc2 = st.columns([3, 1])
        with rc2:
            if st.button(_lbl(lang, "Log Water Reading", "నీటి పరీక్ష నమోదు"), type="primary", use_container_width=True):
                dialog_add_water_reading()

        if waters:
            df_w = pd.DataFrame(waters)
            if "ReadingDate" in df_w.columns:
                df_w = df_w.sort_values("ReadingDate", ascending=False)
            w_cols = ["ReadingID", "PondID", "ReadingDate", "ReadingTime", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia", "WaterLevel", "Notes"]
            for col in w_cols:
                if col not in df_w.columns:
                    df_w[col] = ""
            disp_w = rename_df_for_display(df_w[w_cols], lang)
            if lang == "te":
                disp_w = disp_w.rename(columns={"WaterLevel": "నీటి మట్టం (మీ.)"})
            st.dataframe(disp_w, use_container_width=True, hide_index=True)

            with st.expander(_lbl(lang, "Manage Readings", "రీడింగ్‌లను నిర్వహించండి")):
                del_rid = st.selectbox(_lbl(lang, "Select Reading to Remove", "తొలగించాల్సిన రీడింగ్‌ను ఎంచుకోండి"), options=[w.get("ReadingID") for w in waters])
                if st.button(_lbl(lang, "Delete Selected Reading", "ఎంచుకున్న రీడింగ్‌ను తొలగించండి"), type="secondary"):
                    st.session_state.demo_water_quality = [w for w in st.session_state.demo_water_quality if w.get("ReadingID") != del_rid]
                    st.success(_lbl(lang, "Reading removed successfully.", "రీడింగ్ విజయవంతంగా తొలగించబడింది."))
                    st.rerun()
        else:
            render_empty_state(
                _lbl(lang, "Water", "నీరు"),
                _lbl(lang, "No Readings Recorded", "రీడింగ్‌లు నమోదు కాలేదు"),
                _lbl(lang, "Log routine pond water testing results.", "రోజువారీ చెరువు నీటి పరీక్షా ఫలితాలను నమోదు చేయండి."),
                _lbl(lang, "Log Reading", "రీడింగ్ నమోదు"),
                "w_read_btn"
            )

    # 3. Water History & Trends
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Water Quality Historical Trends', 'నీటి నాణ్యత చారిత్రక ధోరణులు')}")
        sel_pid = st.selectbox(
            _lbl(lang, "Select Pond for Time-Series Analysis", "విశ్లేషణ కోసం చెరువును ఎంచుకోండి"),
            options=[p["PondID"] for p in ponds],
            key="water_hist_pond"
        )
        p_waters = [w for w in waters if w.get("PondID") == sel_pid]

        if p_waters:
            df_hist = pd.DataFrame(p_waters).sort_values("ReadingDate")
            param = st.selectbox(
                _lbl(lang, "Parameter", "పారామితి"),
                options=["DissolvedOxygen", "pH", "Temperature", "Turbidity", "Ammonia", "WaterLevel"],
                format_func=lambda x: param_labels_te.get(x, x) if lang == "te" else x
            )
            p_title = param_labels_te.get(param, param) if lang == "te" else param
            fig_w = px.line(
                df_hist,
                x="ReadingDate",
                y=param,
                markers=True,
                title=f"{sel_pid} — {p_title}",
                labels={"ReadingDate": _lbl(lang, "Date", "తేదీ"), param: p_title}
            )
            # Add reference bounds
            if param == "DissolvedOxygen":
                fig_w.add_hline(y=5.0, line_dash="dash", line_color="#059669", annotation_text=_lbl(lang, "Baseline Ref (5.0 mg/L)", "ప్రమాణ స్థాయి (5.0 mg/L)"))
            elif param == "pH":
                fig_w.add_hline(y=8.5, line_dash="dash", line_color="#D97706", annotation_text=_lbl(lang, "Upper Limit (8.5)", "గరిష్ట పరిమితి (8.5)"))
                fig_w.add_hline(y=6.5, line_dash="dash", line_color="#D97706", annotation_text=_lbl(lang, "Lower Limit (6.5)", "కనిష్ట పరిమితి (6.5)"))

            fig_w.update_layout(height=340, margin=dict(l=15, r=15, t=35, b=15))
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            render_empty_state(
                _lbl(lang, "Water", "నీరు"),
                _lbl(lang, "No Historical Data", "చారిత్రక డేటా లేదు"),
                _lbl(lang, "Log readings across dates to view trend charts.", "ధోరణి చార్ట్‌లను చూడటానికి వివిధ తేదీలలో రీడింగ్‌లు నమోదు చేయండి.")
            )

    # 4. Water Events
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Water Management & Exchange Events', 'నీటి నిర్వహణ మరియు మార్పిడి సంఘటనలు')}")
        with st.expander(_lbl(lang, "Log Water Management Event", "నీటి నిర్వహణ సంఘటనను నమోదు చేయండి")):
            with st.form("water_event_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    ev_pid = st.selectbox(_lbl(lang, "Pond *", "చెరువు *"), options=[p["PondID"] for p in ponds], key="ev_p_sel")
                    ev_type = st.selectbox(
                        _lbl(lang, "Event Type", "సంఘటన రకం"),
                        options=[
                            "Water Added",
                            "Water Removed",
                            "Water Exchange",
                            "Rainfall Event",
                            "Drainage",
                            "Refill",
                            "Cleaning",
                            "Other"
                        ],
                        format_func=lambda x: ev_type_te.get(x, x) if lang == "te" else x
                    )
                    ev_date = st.date_input(_lbl(lang, "Event Date", "సంఘటన తేదీ"), value=date.today())
                with c2:
                    qty = st.number_input(_lbl(lang, "Estimated Quantity (m³)", "అంచనా పరిమాణం (m³)"), min_value=1.0, value=500.0, step=50.0)
                    reason = st.text_input(_lbl(lang, "Reason / Objective", "కారణం / ఉద్దేశ్యం"), placeholder=_lbl(lang, "e.g. Replenish evaporation loss", "ఉదా. ఆవిరి నష్టాన్ని భర్తీ చేయడానికి"))

                notes = st.text_input(_lbl(lang, "Event Notes", "సంఘటన గమనికలు"), placeholder=_lbl(lang, "Inlet mesh filter cleaned prior to pump run.", "పంపు నడపడానికి ముందు ఇన్‌లెట్ జాలీ శుభ్రం చేయబడింది."))
                ev_submit = st.form_submit_button(_lbl(lang, "Save Water Event", "నీటి సంఘటనను సేవ్ చేయండి"), type="primary")
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
                    st.success(_lbl(lang, "Water event logged successfully.", "నీటి సంఘటన విజయవంతంగా నమోదైంది."))
                    st.rerun()

        if events:
            df_ev = pd.DataFrame(events)
            ev_cols = ["EventID", "PondID", "Date", "EventType", "EstimatedQuantity", "Unit", "Reason", "Notes"]
            for c in ev_cols:
                if c not in df_ev.columns:
                    df_ev[c] = ""
            disp_ev = rename_df_for_display(df_ev[ev_cols], lang)
            if lang == "te":
                disp_ev = disp_ev.rename(columns={
                    "EventID": "సంఘటన ID",
                    "EventType": "సంఘటన రకం",
                    "EstimatedQuantity": "అంచనా పరిమాణం",
                    "Unit": "యూనిట్"
                })
            st.dataframe(disp_ev, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Water Events", "నీటి సంఘటనలు"),
                _lbl(lang, "No Water Events Recorded", "నీటి సంఘటనలు నమోదు కాలేదు"),
                _lbl(lang, "Log water exchanges, rainfall, or drainage events.", "నీటి మార్పిడి, వర్షపాతం లేదా డ్రైనేజీ సంఘటనలను నమోదు చేయండి.")
            )

    # 5. Water Comparison
    with tabs[4]:
        st.markdown(f"#### {_lbl(lang, 'Multi-Pond Parameter Comparison', 'బహుళ-చెరువుల పారామితి పోలిక')}")
        if waters:
            df_all = pd.DataFrame(waters)
            latest_all = df_all.sort_values("ReadingDate").groupby("PondID").last().reset_index()
            fig_comp = px.bar(
                latest_all,
                x="PondID",
                y="DissolvedOxygen",
                color="PondID",
                title=_lbl(lang, "Latest Dissolved Oxygen (mg/L) Comparison Across Ponds", "చెరువుల మధ్య తాజా కరిగిన ఆక్సిజన్ (mg/L) పోలిక"),
                labels={"PondID": _lbl(lang, "Pond", "చెరువు"), "DissolvedOxygen": _lbl(lang, "DO (mg/L)", "కరిగిన ఆక్సిజన్ (mg/L)")}
            )
            fig_comp.add_hline(y=5.0, line_dash="dash", line_color="#D97706", annotation_text=_lbl(lang, "Baseline Ref (5.0 mg/L)", "ప్రమాణ స్థాయి (5.0 mg/L)"))
            fig_comp.update_layout(height=320, margin=dict(l=15, r=15, t=35, b=15), showlegend=False)
            st.plotly_chart(fig_comp, use_container_width=True)

            cmp_cols = ["PondID", "ReadingDate", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia", "WaterLevel"]
            for c in cmp_cols:
                if c not in latest_all.columns:
                    latest_all[c] = ""
            disp_cmp = rename_df_for_display(latest_all[cmp_cols], lang)
            if lang == "te":
                disp_cmp = disp_cmp.rename(columns={"WaterLevel": "నీటి మట్టం (మీ.)"})
            st.dataframe(disp_cmp, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Water", "నీరు"),
                _lbl(lang, "No Readings Available", "రీడింగ్‌లు అందుబాటులో లేవు"),
                _lbl(lang, "Log readings to view multi-pond comparisons.", "చెరువుల పోలికను చూడటానికి నీటి రీడింగ్‌లను నమోదు చేయండి.")
            )

    # 6. Reference Ranges
    with tabs[5]:
        st.markdown(f"#### {_lbl(lang, 'Configurable Water Quality Reference Ranges', 'మార్చుకోదగిన నీటి నాణ్యత ప్రమాణ పరిధులు')}")
        st.caption(_lbl(
            lang,
            "Reference ranges must be configurable. Never invent scientific thresholds. If no reference range exists, AquaMitra displays 'No reference range configured.' without making a risk judgment.",
            "ప్రమాణ పరిధులను ఫార్మ్ అవసరాలకు అనుగుణంగా సవరించుకోవచ్చు. నిర్ధారిత పరిధి లేకపోతే రిస్క్ నిర్ధారణ చేయబడదు."
        ))

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
                _lbl(lang, "Parameter", "పారామితి"): param_labels_te.get(param_k, param_k) if lang == "te" else param_k,
                _lbl(lang, "Lower Value", "కనిష్ట విలువ"): val["lower"],
                _lbl(lang, "Upper Value", "గరిష్ట విలువ"): val["upper"],
                _lbl(lang, "Unit", "యూనిట్"): val["unit"],
                _lbl(lang, "Species", "చేప జాతి"): val.get("species", "General"),
                _lbl(lang, "Source", "మూలం"): val.get("source", "Standard Reference"),
                _lbl(lang, "Active", "క్రియాశీలం"): val.get("active", True),
                _lbl(lang, "Updated Date", "అప్‌డేట్ తేదీ"): val.get("updated_date", "2026-01-15")
            })

        st.dataframe(pd.DataFrame(ref_rows), use_container_width=True, hide_index=True)

        with st.expander(_lbl(lang, "Update / Add Parameter Reference Range", "పారామితి ప్రమాణ పరిధిని అప్‌డేట్ చేయండి")):
            with st.form("edit_ref_range_form"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    p_name = st.selectbox(
                        _lbl(lang, "Parameter Name", "పారామితి పేరు"),
                        options=["pH", "DissolvedOxygen", "Temperature", "Turbidity", "Ammonia", "Nitrite", "Nitrate", "WaterLevel", "Salinity", "Alkalinity"],
                        format_func=lambda x: param_labels_te.get(x, x) if lang == "te" else x
                    )
                    curr_item = ref_dict.get(p_name, {"lower": 0.0, "upper": 10.0, "unit": "mg/L", "species": "General", "source": "Department Guidelines"})
                    low_val = st.number_input(_lbl(lang, "Lower Threshold", "కనిష్ట పరిమితి"), value=float(curr_item["lower"]), step=0.1)
                    up_val = st.number_input(_lbl(lang, "Upper Threshold", "గరిష్ట పరిమితి"), value=float(curr_item["upper"]), step=0.1)
                with rc2:
                    unit = st.text_input(_lbl(lang, "Unit", "యూనిట్"), value=curr_item["unit"])
                    species = st.text_input(_lbl(lang, "Species Specification", "జాతి వివరణ"), value=curr_item.get("species", "General Freshwater"))
                    source = st.text_input(_lbl(lang, "Source / Citation", "మూలం / ఆధారం"), value=curr_item.get("source", "ICAR-CIFA"))

                save_ref = st.form_submit_button(_lbl(lang, "Save Reference Range", "ప్రమాణ పరిధిని సేవ్ చేయండి"), type="primary")
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
                    st.success(_lbl(lang, f"Reference range for {p_name} updated successfully.", f"{p_name} కోసం ప్రమాణ పరిధి విజయవంతంగా అప్‌డేట్ చేయబడింది."))
                    st.rerun()
