"""
AquaMitra Assets View Module
Provides Equipment Registry, Machinery Maintenance Logs, and Document Management with strictly zero emojis.
Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
from utils.translations import tv, rename_df_for_display
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_maintenance
from database.queries import get_maintenance_records


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_assets_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Equipment", "పరికరాలు"),
        _lbl(lang, "Maintenance", "నిర్వహణ"),
        _lbl(lang, "Documents", "డాక్యుమెంట్లు")
    ]
    tabs = st.tabs(subtabs)

    equip = st.session_state.get("demo_equipment", [])
    maint = get_maintenance_records()
    docs = st.session_state.get("demo_documents", [])
    ponds = st.session_state.get("demo_ponds", [])

    eq_cat_te = {
        "Aeration": "ఏరేషన్ పరికరాలు",
        "Pumps": "పంపులు",
        "Testing Kit": "పరీక్షా కిట్",
        "Feeding": "మేత పరికరాలు",
        "Power Generator": "పవర్ జనరేటర్",
        "Netting": "వలలు",
        "Other": "ఇతరములు",
    }
    eq_cond_te = {
        "Excellent": "అత్యుత్తమం",
        "Good": "బాగుంది",
        "Needs Service": "సర్వీసింగ్ అవసరం",
    }
    doc_cat_te = {
        "Hatchery Certificate": "హేచరీ ధృవీకరణ పత్రం",
        "Invoice": "ఇన్‌వాయిస్ / బిల్లు",
        "Pond Photo": "చెరువు ఫోటో",
        "Soil/Water Lab Report": "మట్టి / నీటి ల్యాబ్ నివేదిక",
        "Equipment Manual": "పరికరాల మాన్యువల్",
    }

    # 1. Equipment Registry
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Farm Machinery & Equipment Registry', 'ఫార్మ్ యంత్రాలు మరియు పరికరాల రిజిస్ట్రీ')}")
        c1, c2 = st.columns(2)
        with c1:
            tot_val = sum(eq.get("PurchaseCost", 0) for eq in equip)
            render_metric_card(
                _lbl(lang, "Total Equipment Asset Value", "మొత్తం పరికరాల ఆస్తి విలువ"),
                f"₹{tot_val:,.0f}",
                f"{len(equip)} {_lbl(lang, 'Registered Assets', 'నమోదైన ఆస్తులు')}"
            )
        with c2:
            render_metric_card(
                _lbl(lang, "Operational Condition", "పనితీరు స్థితి"),
                _lbl(lang, "100% Functional", "100% పనితీరులో ఉన్నాయి"),
                _lbl(lang, "Aerators, Pumps, Optical DO Probe", "ఏరేటర్లు, పంపులు, DO ప్రోబ్")
            )

        with st.expander(_lbl(lang, "Register New Equipment", "కొత్త పరికరాన్ని నమోదు చేయండి")):
            with st.form("add_equip_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    eq_name = st.text_input(_lbl(lang, "Equipment Name *", "పరికరం పేరు *"), placeholder=_lbl(lang, "e.g. 2HP Submersible Pump", "ఉదా. 2HP సబ్‌మెర్సిబుల్ పంపు"))
                    eq_cat = st.selectbox(
                        _lbl(lang, "Category", "విభాగం"),
                        options=["Aeration", "Pumps", "Testing Kit", "Feeding", "Power Generator", "Netting", "Other"],
                        format_func=lambda x: eq_cat_te.get(x, x) if lang == "te" else x
                    )
                    eq_pond = st.selectbox(
                        _lbl(lang, "Assigned Pond", "కేటాయించిన చెరువు"),
                        options=["All Ponds"] + [p["PondID"] for p in ponds],
                        format_func=lambda x: tv(x, lang)
                    )
                with col2:
                    eq_cost = st.number_input(_lbl(lang, "Purchase Cost (₹) *", "కొనుగోలు ధర (₹) *"), min_value=100.0, value=25000.0, step=1000.0)
                    eq_supp = st.text_input(_lbl(lang, "Supplier", "సరఫరాదారు"), value="Godavari Aqua Machinery")
                    eq_cond = st.selectbox(
                        _lbl(lang, "Condition", "స్థితి"),
                        options=["Excellent", "Good", "Needs Service"],
                        index=1,
                        format_func=lambda x: eq_cond_te.get(x, x) if lang == "te" else x
                    )

                eq_notes = st.text_input(_lbl(lang, "Equipment Remarks", "పరికర గమనికలు"), placeholder=_lbl(lang, "2HP 3-phase motor with thermal overload relay.", "థర్మల్ ఓవర్‌లోడ్ రిలే తో 2HP 3-ఫేజ్ మోటార్."))
                eq_submit = st.form_submit_button(_lbl(lang, "Save Equipment", "పరికరాన్ని సేవ్ చేయండి"), type="primary")
                if eq_submit:
                    if not eq_name:
                        st.error(_lbl(lang, "Equipment name is required.", "పరికరం పేరు తప్పనిసరి."))
                    else:
                        new_eq = {
                            "EquipmentID": len(equip) + 1,
                            "EquipmentName": eq_name.strip(),
                            "Category": eq_cat,
                            "PondID": eq_pond,
                            "PurchaseDate": date.today().strftime("%Y-%m-%d"),
                            "PurchaseCost": float(eq_cost),
                            "Supplier": eq_supp.strip(),
                            "Condition": eq_cond,
                            "LastMaintenance": date.today().strftime("%Y-%m-%d"),
                            "NextMaintenance": "2026-12-31",
                            "Warranty": "1 Year",
                            "Notes": eq_notes.strip()
                        }
                        st.session_state.demo_equipment.append(new_eq)
                        st.success(_lbl(lang, f"Equipment '{eq_name}' registered successfully.", f"పరికరం '{eq_name}' విజయవంతంగా నమోదైంది."))
                        st.rerun()

        if equip:
            df_eq = pd.DataFrame(equip)
            eq_cols = ["EquipmentID", "EquipmentName", "Category", "PondID", "PurchaseCost", "Supplier", "Condition", "LastMaintenance", "NextMaintenance", "Warranty"]
            for col in eq_cols:
                if col not in df_eq.columns:
                    df_eq[col] = ""
            disp_eq = rename_df_for_display(df_eq[eq_cols], lang)
            if lang == "te":
                disp_eq = disp_eq.rename(columns={
                    "Supplier": "సరఫరాదారు",
                    "Condition": "స్థితి",
                    "LastMaintenance": "చివరి నిర్వహణ",
                    "Warranty": "వారంటీ"
                })
            st.dataframe(disp_eq, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Equipment", "పరికరాలు"),
                _lbl(lang, "No Equipment Registered", "పరికరాలు నమోదు కాలేదు"),
                _lbl(lang, "Add pumps, aerators, and testing meters.", "పంపులు, ఏరేటర్లు మరియు పరీక్షా మీటర్లను జోడించండి.")
            )

    # 2. Maintenance Logs
    with tabs[1]:
        m_top1, m_top2 = st.columns([3, 1], vertical_alignment="center")
        with m_top1:
            st.markdown(f"#### {_lbl(lang, 'Infrastructure & Equipment Maintenance History', 'మౌలిక సదుపాయాలు మరియు పరికరాల నిర్వహణ చరిత్ర')}")
        with m_top2:
            if st.button(_lbl(lang, "Log Maintenance Record", "నిర్వహణ రికార్డు నమోదు"), type="primary", use_container_width=True):
                dialog_add_maintenance()

        if maint:
            df_m = pd.DataFrame(maint)
            m_cols = ["Date", "PondID", "Asset", "MaintenanceType", "Description", "Cost", "Person", "Status", "NextMaintenance"]
            for col in m_cols:
                if col not in df_m.columns:
                    df_m[col] = ""
            disp_m = rename_df_for_display(df_m[m_cols], lang)
            if lang == "te":
                disp_m = disp_m.rename(columns={"Person": "నిపుణుడు / టెక్నీషియన్"})
            st.dataframe(disp_m, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Maintenance", "నిర్వహణ"),
                _lbl(lang, "No Maintenance Records", "నిర్వహణ రికార్డులు లేవు"),
                _lbl(lang, "Log equipment servicing, oiling, and pond repairs.", "పరికరాల సర్వీసింగ్ మరియు చెరువు మరమ్మతులను నమోదు చేయండి.")
            )

    # 3. Documents
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Attached Records & Farm Documentation', 'జతచేసిన రికార్డులు మరియు ఫార్మ్ డాక్యుమెంట్లు')}")
        st.caption(_lbl(
            lang,
            "Centralized metadata repository for quarantine certificates, GST invoices, and inspection photographs.",
            "క్వారంటైన్ సర్టిఫికెట్లు, GST ఇన్‌వాయిస్‌లు మరియు తనిఖీ ఫోటోల కోసం కేంద్రీకృత రిపోజిటరీ."
        ))

        with st.expander(_lbl(lang, "Attach New Document Record", "కొత్త డాక్యుమెంట్ రికార్డును జతచేయండి")):
            doc_cat = st.selectbox(
                _lbl(lang, "Document Category", "డాక్యుమెంట్ విభాగం"),
                options=["Hatchery Certificate", "Invoice", "Pond Photo", "Soil/Water Lab Report", "Equipment Manual"],
                format_func=lambda x: doc_cat_te.get(x, x) if lang == "te" else x
            )
            doc_title = st.text_input(_lbl(lang, "Document Title", "డాక్యుమెంట్ శీర్షిక"), placeholder=_lbl(lang, "e.g. Lab Water Testing Report #102", "ఉదా. నీటి పరీక్ష ల్యాబ్ నివేదిక #102"))
            doc_pond = st.selectbox(
                _lbl(lang, "Related Pond", "సంబంధిత చెరువు"),
                options=["All Ponds"] + [p["PondID"] for p in ponds],
                key="doc_p_sel",
                format_func=lambda x: tv(x, lang)
            )
            uploaded_file = st.file_uploader(_lbl(lang, "Upload File (PDF / JPG / PNG)", "ఫైల్‌ను అప్‌లోడ్ చేయండి (PDF / JPG / PNG)"), type=["pdf", "png", "jpg", "jpeg"])
            if st.button(_lbl(lang, "Save Document Record", "డాక్యుమెంట్ రికార్డును సేవ్ చేయండి"), type="primary"):
                if doc_title:
                    fname = uploaded_file.name if uploaded_file else "Attached_Record.pdf"
                    st.session_state.demo_documents.append({
                        "DocID": len(docs) + 1,
                        "PondID": doc_pond,
                        "Category": doc_cat,
                        "Title": doc_title.strip(),
                        "Date": date.today().strftime("%Y-%m-%d"),
                        "FileName": fname,
                        "FileSize": "1.2 MB",
                        "Notes": "Uploaded via web interface"
                    })
                    st.success(_lbl(lang, "Document attached successfully.", "డాక్యుమెంట్ విజయవంతంగా జతచేయబడింది."))
                    st.rerun()

        if docs:
            df_d = pd.DataFrame(docs)
            d_cols = ["DocID", "Date", "Category", "Title", "PondID", "FileName", "FileSize", "Notes"]
            for c in d_cols:
                if c not in df_d.columns:
                    df_d[c] = ""
            disp_d = rename_df_for_display(df_d[d_cols], lang)
            if lang == "te":
                disp_d = disp_d.rename(columns={
                    "DocID": "డాక్యుమెంట్ ID",
                    "FileName": "ఫైల్ పేరు",
                    "FileSize": "ఫైల్ పరిమాణం"
                })
            st.dataframe(disp_d, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Documents", "డాక్యుమెంట్లు"),
                _lbl(lang, "No Documents Attached", "డాక్యుమెంట్లు ఏవీ జతచేయబడలేదు"),
                _lbl(lang, "Attach testing certificates, purchase invoices, and receipts.", "పరీక్షా ధృవీకరణ పత్రాలు మరియు బిల్లులను జతచేయండి.")
            )
