"""
AquaMitra Assets View Module
Provides Equipment Registry, Machinery Maintenance Logs, and Document Management with strictly zero emojis.
"""

from datetime import date
import streamlit as st
import pandas as pd
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_maintenance
from database.queries import get_maintenance_records


def render_assets_view():
    subtabs = ["Equipment", "Maintenance", "Documents"]
    tabs = st.tabs(subtabs)

    equip = st.session_state.get("demo_equipment", [])
    maint = get_maintenance_records()
    docs = st.session_state.get("demo_documents", [])
    ponds = st.session_state.get("demo_ponds", [])

    # 1. Equipment Registry
    with tabs[0]:
        st.markdown("#### Farm Machinery & Equipment Registry")
        c1, c2 = st.columns(2)
        with c1:
            tot_val = sum(eq.get("PurchaseCost", 0) for eq in equip)
            render_metric_card("Total Equipment Asset Value", f"₹{tot_val:,.0f}", f"{len(equip)} Registered Assets")
        with c2:
            render_metric_card("Operational Condition", "100% Functional", "Aerators, Pumps, Optical DO Probe")

        with st.expander("Register New Equipment"):
            with st.form("add_equip_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    eq_name = st.text_input("Equipment Name *", placeholder="e.g. 2HP Submersible Pump")
                    eq_cat = st.selectbox("Category", options=["Aeration", "Pumps", "Testing Kit", "Feeding", "Power Generator", "Netting", "Other"])
                    eq_pond = st.selectbox("Assigned Pond", options=["All Ponds"] + [p["PondID"] for p in ponds])
                with col2:
                    eq_cost = st.number_input("Purchase Cost (₹) *", min_value=100.0, value=25000.0, step=1000.0)
                    eq_supp = st.text_input("Supplier", value="Godavari Aqua Machinery")
                    eq_cond = st.selectbox("Condition", options=["Excellent", "Good", "Needs Service"], index=1)

                eq_notes = st.text_input("Equipment Remarks", placeholder="2HP 3-phase motor with thermal overload relay.")
                eq_submit = st.form_submit_button("Save Equipment", type="primary")
                if eq_submit:
                    if not eq_name:
                        st.error("Equipment name is required.")
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
                        st.success(f"Equipment '{eq_name}' registered successfully.")
                        st.rerun()

        if equip:
            df_eq = pd.DataFrame(equip)
            eq_cols = ["EquipmentID", "EquipmentName", "Category", "PondID", "PurchaseCost", "Supplier", "Condition", "LastMaintenance", "NextMaintenance", "Warranty"]
            for col in eq_cols:
                if col not in df_eq.columns:
                    df_eq[col] = ""
            st.dataframe(df_eq[eq_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Equipment", "No Equipment Registered", "Add pumps, aerators, and testing meters.")

    # 2. Maintenance Logs
    with tabs[1]:
        st.markdown("#### Infrastructure & Equipment Maintenance History")
        m_top1, m_top2 = st.columns([3, 1])
        with m_top2:
            if st.button("Log Maintenance Record", type="primary", use_container_width=True):
                dialog_add_maintenance()

        if maint:
            df_m = pd.DataFrame(maint)
            m_cols = ["Date", "PondID", "Asset", "MaintenanceType", "Description", "Cost", "Person", "Status", "NextMaintenance"]
            for col in m_cols:
                if col not in df_m.columns:
                    df_m[col] = ""
            st.dataframe(df_m[m_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Maintenance", "No Maintenance Records", "Log equipment servicing, oiling, and pond repairs.")

    # 3. Documents
    with tabs[2]:
        st.markdown("#### Attached Records & Farm Documentation")
        st.caption("Centralized metadata repository for quarantine certificates, GST invoices, and inspection photographs.")
        
        with st.expander("Attach New Document Record"):
            doc_cat = st.selectbox("Document Category", options=["Hatchery Certificate", "Invoice", "Pond Photo", "Soil/Water Lab Report", "Equipment Manual"])
            doc_title = st.text_input("Document Title", placeholder="e.g. Lab Water Testing Report #102")
            doc_pond = st.selectbox("Related Pond", options=["All Ponds"] + [p["PondID"] for p in ponds], key="doc_p_sel")
            uploaded_file = st.file_uploader("Upload File (PDF / JPG / PNG)", type=["pdf", "png", "jpg", "jpeg"])
            if st.button("Save Document Record", type="primary"):
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
                    st.success("Document attached successfully.")
                    st.rerun()

        if docs:
            df_d = pd.DataFrame(docs)
            d_cols = ["DocID", "Date", "Category", "Title", "PondID", "FileName", "FileSize", "Notes"]
            for c in d_cols:
                if c not in df_d.columns:
                    df_d[c] = ""
            st.dataframe(df_d[d_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Documents", "No Documents Attached", "Attach testing certificates, purchase invoices, and receipts.")
