"""
AquaMitra Reports & Export View Module
Provides Farm, Pond, Water, Fish, Feeding, Incident, Financial, and Custom Reports
with real CSV export buttons and 'Generate AI Executive Summary' functionality.
100% Zero-Emoji Professional SaaS Interface. Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
from utils.translations import tv, rename_df_for_display
from services.ai.ai_service import generate_farm_summary


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def render_reports_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Farm Report", "ఫార్మ్ నివేదిక"),
        _lbl(lang, "Pond Report", "చెరువు నివేదిక"),
        _lbl(lang, "Water Report", "నీటి నివేదిక"),
        _lbl(lang, "Fish Report", "చేపల నివేదిక"),
        _lbl(lang, "Feeding Report", "మేత నివేదిక"),
        _lbl(lang, "Incident Report", "సంఘటన నివేదిక"),
        _lbl(lang, "Financial Report", "ఆర్థిక నివేదిక"),
        _lbl(lang, "Custom Report", "కస్టమ్ నివేదిక")
    ]
    tabs = st.tabs(subtabs)

    ponds = st.session_state.get("demo_ponds", [])

    domain_te = {
        "Water Quality": "నీటి నాణ్యత",
        "Feeding": "మేత",
        "Expenses": "ఖర్చులు",
        "Fish Stock": "చేపల నిల్వ",
        "Growth Samples": "పెరుగుదల నమూనాలు",
        "Mortality Incidents": "మరణాల సంఘటనలు",
        "Harvests": "పంట కోతలు",
        "Sales": "అమ్మకాలు",
    }

    # 1. Farm Report
    with tabs[0]:
        st.markdown(f"### {_lbl(lang, 'Comprehensive Farm Status Report', 'సమగ్ర ఫార్మ్ స్థితి నివేదిక')}")
        st.caption(_lbl(lang, "Master summary of all farm units, dimensions, and operational ownership.", "అన్ని చెరువు యూనిట్లు, కొలతలు మరియు యాజమాన్య వివరాల ప్రధాన సారాంశం."))

        if st.button(_lbl(lang, "Generate AI Executive Summary", "AI కార్యనిర్వాహక సారాంశాన్ని రూపొందించండి"), key="ai_sum_farm_rep"):
            s = generate_farm_summary(st.session_state, lang=lang)
            clean_badge = s['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()
            clean_text = s['text'].replace("🟡", "").replace("🟢", "").replace("🔴", "").strip()
            sum_lbl = _lbl(lang, "Executive AI Summary", "కార్యనిర్వాహక AI సారాంశం")
            st.info(f"**{sum_lbl} ([{clean_badge}]):**\n\n{clean_text}")

        df_fp = pd.DataFrame(ponds)
        p_cols = ["PondID", "PondName", "Location", "Area", "AreaUnit", "PondType", "WaterSource", "Status", "Owner", "Manager"]
        for col in p_cols:
            if col not in df_fp.columns:
                df_fp[col] = ""
        disp_fp = rename_df_for_display(df_fp[p_cols], lang)
        if lang == "te":
            disp_fp = disp_fp.rename(columns={"Manager": "మేనేజర్"})
        st.dataframe(disp_fp, use_container_width=True, hide_index=True)
        st.download_button(
            _lbl(lang, "Download Farm Report (CSV)", "ఫార్మ్ నివేదిక డౌన్‌లోడ్ (CSV)"),
            data=convert_df_to_csv(df_fp[p_cols]),
            file_name=f"AquaMitra_Farm_Report_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 2. Pond Report
    with tabs[1]:
        st.markdown(f"### {_lbl(lang, 'Pond-Specific Comprehensive Report', 'చెరువు వారీ సమగ్ర నివేదిక')}")
        st.caption(_lbl(lang, "Deep-dive historical observations, feed consumption, and growth for an individual pond.", "ఒక్కో చెరువు కోసం చారిత్రక నీటి పరిశీలనలు, మేత వినియోగం మరియు పెరుగుదల నివేదిక."))

        if ponds:
            sel_pid = st.selectbox(_lbl(lang, "Select Pond", "చెరువును ఎంచుకోండి"), options=[p["PondID"] for p in ponds], key="rep_pond_sel")
            p_waters = [w for w in st.session_state.get("demo_water_quality", []) if w.get("PondID") == sel_pid]
            p_feeds = [f for f in st.session_state.get("demo_feeding", []) if f.get("PondID") == sel_pid]
            p_growths = [g for g in st.session_state.get("demo_fish_growth", []) if g.get("PondID") == sel_pid]
            rec_word = _lbl(lang, "Records", "రికార్డులు")

            st.markdown(f"#### {_lbl(lang, 'Water Observations', 'నీటి పరిశీలనలు')} ({len(p_waters)} {rec_word})")
            if p_waters:
                df_pw = pd.DataFrame(p_waters)
                pw_cols = ["ReadingDate", "pH", "Temperature", "DissolvedOxygen", "Turbidity", "Ammonia"]
                for col in pw_cols:
                    if col not in df_pw.columns:
                        df_pw[col] = ""
                st.dataframe(rename_df_for_display(df_pw[pw_cols], lang), use_container_width=True, hide_index=True)
                st.download_button(
                    _lbl(lang, "Download Pond Water Data (CSV)", "చెరువు నీటి డేటా డౌన్‌లోడ్ (CSV)"),
                    data=convert_df_to_csv(df_pw[pw_cols]),
                    file_name=f"AquaMitra_{sel_pid}_Water_{date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.info(_lbl(lang, f"No water quality records found for pond {sel_pid}.", f"{sel_pid} చెరువుకు నీటి నాణ్యత రికార్డులు లేవు."))

            st.markdown(f"#### {_lbl(lang, 'Feeding Records', 'మేత రికార్డులు')} ({len(p_feeds)} {rec_word})")
            if p_feeds:
                df_pf = pd.DataFrame(p_feeds)
                st.dataframe(rename_df_for_display(df_pf, lang), use_container_width=True, hide_index=True)
                st.download_button(
                    _lbl(lang, "Download Pond Feeding Data (CSV)", "చెరువు మేత డేటా డౌన్‌లోడ్ (CSV)"),
                    data=convert_df_to_csv(df_pf),
                    file_name=f"AquaMitra_{sel_pid}_Feeding_{date.today()}.csv",
                    mime="text/csv"
                )

            st.markdown(f"#### {_lbl(lang, 'Growth Samplings', 'పెరుగుదల నమూనాలు')} ({len(p_growths)} {rec_word})")
            if p_growths:
                df_pg = pd.DataFrame(p_growths)
                st.dataframe(rename_df_for_display(df_pg, lang), use_container_width=True, hide_index=True)
                st.download_button(
                    _lbl(lang, "Download Pond Growth Data (CSV)", "చెరువు పెరుగుదల డేటా డౌన్‌లోడ్ (CSV)"),
                    data=convert_df_to_csv(df_pg),
                    file_name=f"AquaMitra_{sel_pid}_Growth_{date.today()}.csv",
                    mime="text/csv"
                )
        else:
            st.info(_lbl(lang, "No ponds currently registered.", "ప్రస్తుతం చెరువులు ఏవీ నమోదు కాలేదు."))

    # 3. Water Report
    with tabs[2]:
        st.markdown(f"### {_lbl(lang, 'Farm-Wide Water Quality Report', 'ఫార్మ్ మొత్తం నీటి నాణ్యత నివేదిక')}")
        st.caption(_lbl(lang, "Consolidated register of all logged physicochemical observations across ponds.", "అన్ని చెరువులలో నమోదైన నీటి పరీక్షా పరిశీలనల ఏకీకృత రిజిస్టర్."))
        df_w = pd.DataFrame(st.session_state.get("demo_water_quality", []))
        st.dataframe(rename_df_for_display(df_w, lang), use_container_width=True, hide_index=True)
        st.download_button(
            _lbl(lang, "Download All Water Observations (CSV)", "అన్ని నీటి పరిశీలనలు డౌన్‌లోడ్ (CSV)"),
            data=convert_df_to_csv(df_w),
            file_name=f"AquaMitra_Water_Observations_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 4. Fish Report
    with tabs[3]:
        st.markdown(f"### {_lbl(lang, 'Fish Stocking & Growth Report', 'చేపల నిల్వ మరియు పెరుగుదల నివేదిక')}")
        st.caption(_lbl(lang, "Complete inventory of stocked batches, stocking densities, and historical sampling weights.", "నిల్వ చేసిన బ్యాచ్‌లు మరియు చారిత్రక నమూనా బరువుల పూర్తి జాబితా."))
        df_s = pd.DataFrame(st.session_state.get("demo_fish_stock", []))
        df_g = pd.DataFrame(st.session_state.get("demo_fish_growth", []))
        st.markdown(f"#### {_lbl(lang, 'Stocking Batches', 'చేపల నిల్వ బ్యాచ్‌లు')}")
        st.dataframe(rename_df_for_display(df_s, lang), use_container_width=True, hide_index=True)
        st.markdown(f"#### {_lbl(lang, 'Growth Samplings', 'పెరుగుదల నమూనాలు')}")
        st.dataframe(rename_df_for_display(df_g, lang), use_container_width=True, hide_index=True)
        st.download_button(
            _lbl(lang, "Download Growth Data (CSV)", "పెరుగుదల డేటా డౌన్‌లోడ్ (CSV)"),
            data=convert_df_to_csv(df_g),
            file_name=f"AquaMitra_Growth_Data_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 5. Feeding Report
    with tabs[4]:
        st.markdown(f"### {_lbl(lang, 'Feed Consumption & Cost Report', 'మేత వినియోగం మరియు ఖర్చుల నివేదిక')}")
        st.caption(_lbl(lang, "Ledger of daily feeding disbursements, recommended rations, and feed expenditures.", "రోజువారీ మేత పంపిణీ, సిఫార్సు రేషన్ మరియు మేత ఖర్చుల పట్టిక."))
        df_f = pd.DataFrame(st.session_state.get("demo_feeding", []))
        st.dataframe(rename_df_for_display(df_f, lang), use_container_width=True, hide_index=True)
        st.download_button(
            _lbl(lang, "Download Feeding Ledger (CSV)", "మేత ఖాతా డౌన్‌లోడ్ (CSV)"),
            data=convert_df_to_csv(df_f),
            file_name=f"AquaMitra_Feeding_Ledger_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 6. Incident Report
    with tabs[5]:
        st.markdown(f"### {_lbl(lang, 'Health Observations & Mortality Report', 'ఆరోగ్య పరిశీలనలు మరియు మరణాల నివేదిక')}")
        st.caption(_lbl(lang, "Log of health incidents, abnormal fish behavior observations, and logged mortalities.", "ఆరోగ్య సంఘటనలు, అసాధారణ ప్రవర్తన మరియు మరణాల లాగ్."))
        df_i = pd.DataFrame(st.session_state.get("demo_incidents", []))
        st.dataframe(rename_df_for_display(df_i, lang), use_container_width=True, hide_index=True)
        st.download_button(
            _lbl(lang, "Download Incidents Log (CSV)", "సంఘటనల లాగ్ డౌన్‌లోడ్ (CSV)"),
            data=convert_df_to_csv(df_i),
            file_name=f"AquaMitra_Incidents_Log_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 7. Financial Report
    with tabs[6]:
        st.markdown(f"### {_lbl(lang, 'Financial Statement & Sales Summary', 'ఆర్థిక నివేదిక మరియు అమ్మకాల సారాంశం')}")
        st.caption(_lbl(lang, "Comprehensive statements of operating expenses, farm inputs, and fish harvest sales.", "నిర్వహణ ఖర్చులు, ఫార్మ్ పెట్టుబడులు మరియు చేపల అమ్మకాల సమగ్ర ప్రకటన."))
        df_e = pd.DataFrame(st.session_state.get("demo_expenses", []))
        df_s = pd.DataFrame(st.session_state.get("demo_sales", []))
        st.markdown(f"#### {_lbl(lang, 'Operational Expenses', 'నిర్వహణ ఖర్చులు')}")
        st.dataframe(rename_df_for_display(df_e, lang), use_container_width=True, hide_index=True)
        st.markdown(f"#### {_lbl(lang, 'Fish Sales & Revenue', 'చేపల అమ్మకాలు & ఆదాయం')}")
        st.dataframe(rename_df_for_display(df_s, lang), use_container_width=True, hide_index=True)
        st.download_button(
            _lbl(lang, "Download Sales Records (CSV)", "అమ్మకాల రికార్డుల డౌన్‌లోడ్ (CSV)"),
            data=convert_df_to_csv(df_s),
            file_name=f"AquaMitra_Sales_Records_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

    # 8. Custom Report
    with tabs[7]:
        st.markdown(f"### {_lbl(lang, 'Custom Report Builder', 'కస్టమ్ నివేదిక బిల్డర్')}")
        st.caption(_lbl(lang, "Select specific data domains and pond filters to generate customized exports.", "మీకు కావలసిన డేటా విభాగాలు మరియు చెరువులను ఎంచుకుని నివేదికలను ఎగుమతి చేయండి."))
        c1, c2 = st.columns(2)
        with c1:
            cust_type = st.selectbox(
                _lbl(lang, "Select Data Domain", "డేటా విభాగాన్ని ఎంచుకోండి"),
                options=[
                    "Water Quality",
                    "Feeding",
                    "Expenses",
                    "Fish Stock",
                    "Growth Samples",
                    "Mortality Incidents",
                    "Harvests",
                    "Sales"
                ],
                format_func=lambda x: domain_te.get(x, x) if lang == "te" else x
            )
        with c2:
            cust_pond = st.selectbox(
                _lbl(lang, "Filter Pond", "చెరువు వడపోత"),
                options=["All Ponds"] + [p["PondID"] for p in ponds],
                key="cust_rep_pond",
                format_func=lambda x: tv(x, lang)
            )

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
            st.dataframe(rename_df_for_display(df_cust, lang), use_container_width=True, hide_index=True)
            st.download_button(
                _lbl(lang, "Export Custom Selection (CSV)", "ఎంచుకున్న నివేదిక ఎగుమతి (CSV)"),
                data=convert_df_to_csv(df_cust),
                file_name=f"AquaMitra_Custom_{cust_type.replace(' ', '_')}_{date.today()}.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info(_lbl(lang, "No matching records found for this custom selection.", "ఈ ఎంపికకు సరిపోయే రికార్డులు కనుగొనబడలేదు."))
