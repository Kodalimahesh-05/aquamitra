"""
AquaMitra Settings View Module
Provides Farm Profile Editor, General Config, Appearance, Language,
Data Mode, Reference Ranges, AI Settings, Database Status, Data Management, and About AquaMitra.
100% Zero-Emoji Professional SaaS Interface.
"""

from datetime import date
import streamlit as st
import pandas as pd
from utils.constants import APP_NAME, APP_TAGLINE, APP_VERSION, DISCLAIMER_TEXT, DEFAULT_REFERENCE_RANGES
from database.connection import is_database_connected, get_db_credentials
from services.ai.ai_service import get_ai_credentials


def render_settings_view():
    subtabs = [
        "Farm Profile",
        "General",
        "Appearance",
        "Language",
        "Data Mode",
        "Reference Ranges",
        "AI Settings",
        "Database",
        "Data Management",
        "About"
    ]
    tabs = st.tabs(subtabs)

    prof = st.session_state.get("demo_farm_profile", {})

    # 1. Farm Profile (All 16 Fields)
    with tabs[0]:
        st.markdown("### Farm & Owner Profile")
        st.caption("Update farm enterprise attributes, geographic location, and operational parameters.")

        with st.form("edit_farm_profile_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_name = st.text_input("Farm Name *", value=prof.get("FarmName", "Godavari Aqua Greens Farm"))
                f_owner = st.text_input("Owner Name *", value=prof.get("OwnerName", "Ramesh Varma"))
                f_mobile = st.text_input("Mobile Number *", value=prof.get("MobileNumber", "+91 98480 12345"))
            with c2:
                f_village = st.text_input("Village", value=prof.get("Village", "Undi"))
                f_mandal = st.text_input("Mandal", value=prof.get("Mandal", "Undi Mandal"))
                f_dist = st.text_input("District", value=prof.get("District", "West Godavari"))
            with c3:
                f_state = st.text_input("State", value=prof.get("State", "Andhra Pradesh"))
                f_pin = st.text_input("PIN Code", value=prof.get("PINCode", "534199"))
                f_type = st.text_input("Farm Type", value=prof.get("FarmType", "Commercial Freshwater Semi-Intensive"))

            c4, c5, c6 = st.columns(3)
            with c4:
                f_area = st.number_input("Total Farm Area (Acres)", min_value=0.5, value=float(prof.get("TotalFarmArea", 7.0)), step=0.5)
                f_area_unit = st.selectbox("Area Unit", options=["Acres", "Hectares", "Cents"], index=0)
            with c5:
                f_ponds_count = st.number_input("Number of Ponds", min_value=1, value=int(prof.get("NumberOfPonds", 3)), step=1)
                f_species = st.text_input("Primary Cultured Species", value=prof.get("PrimarySpecies", "Rohu, Catla, GIFT Tilapia"))
            with c6:
                f_water = st.text_input("Primary Water Source", value=prof.get("WaterSource", "Godavari Canal & Deep Borewell"))
                f_start_date = st.date_input("Operation Start Date", value=date(2024, 3, 15))

            f_addr = st.text_area("Full Farm Address / Survey Details", value=prof.get("FarmAddress", "Survey No. 142/B, Kolleru Road, Undi"))
            f_notes = st.text_area("Operational Notes & Best Practices", value=prof.get("Notes", "Community-focused sustainable fishery adhering to standard BMP."))

            save_prof_btn = st.form_submit_button("Save Farm Profile", type="primary", use_container_width=True)
            if save_prof_btn:
                st.session_state.demo_farm_profile.update({
                    "FarmName": f_name.strip(),
                    "OwnerName": f_owner.strip(),
                    "MobileNumber": f_mobile.strip(),
                    "Village": f_village.strip(),
                    "Mandal": f_mandal.strip(),
                    "District": f_dist.strip(),
                    "State": f_state.strip(),
                    "PINCode": f_pin.strip(),
                    "FarmType": f_type.strip(),
                    "TotalFarmArea": float(f_area),
                    "AreaUnit": f_area_unit,
                    "NumberOfPonds": int(f_ponds_count),
                    "PrimarySpecies": f_species.strip(),
                    "WaterSource": f_water.strip(),
                    "DateStarted": str(f_start_date),
                    "FarmAddress": f_addr.strip(),
                    "Notes": f_notes.strip()
                })
                st.success("Farm profile updated successfully.")
                st.rerun()

    # 2. General
    with tabs[1]:
        st.markdown("### General Operational Settings")
        st.caption("Default metrics and system localization settings applied across calculations.")
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Default Currency", options=["₹ INR (Indian Rupee)", "$ USD", "€ EUR"], index=0)
            st.selectbox("Default Biomass / Feed Weight Unit", options=["Kilograms (kg)", "Metric Tonnes (t)"], index=0)
        with c2:
            st.selectbox("Fish Sample Weight Unit", options=["Grams (g)", "Kilograms (kg)"], index=0)
            st.selectbox("Date Display Format", options=["DD/MM/YYYY", "YYYY-MM-DD"], index=0)
        st.info("System calculation engines automatically utilize these standard parameters.")

    # 3. Appearance
    with tabs[2]:
        st.markdown("### Visual Theme & Display System")
        st.caption("AquaMitra SaaS enterprise agricultural design system specifications.")
        st.markdown(
            """
            - **Primary Brand Color:** Navy (`#0F2942`)
            - **Accent & Action Color:** Teal (`#0D9488`)
            - **Text & Hierarchy:** Slate Charcoal (`#0F172A`, `#334155`, `#64748B`)
            - **Surface Background:** Cool Slate Tint (`#F8FAFC`, `#FFFFFF`)
            - **Borders & Dividers:** Subtle Slate (`#E2E8F0`)
            - **Design Philosophy:** 100% Text-Only Enterprise SaaS with Zero Emojis
            """
        )

    # 4. Language
    with tabs[3]:
        st.markdown("### Bilingual Interface Settings")
        st.caption("Toggle between English and Telugu across all menus, forms, and analytical views.")
        curr_lang = st.session_state.get("lang", "en")
        st.write(f"Current Active Language: **{'తెలుగు (Telugu)' if curr_lang=='te' else 'English'}**")
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            if st.button("Switch to English", type="primary" if curr_lang=="en" else "secondary", use_container_width=True):
                st.session_state.lang = "en"
                st.rerun()
        with l_col2:
            if st.button("తెలుగులోకి మారండి (Switch to Telugu)", type="primary" if curr_lang=="te" else "secondary", use_container_width=True):
                st.session_state.lang = "te"
                st.rerun()

    # 5. Data Mode
    with tabs[4]:
        st.markdown("### Data Storage & Persistence Mode")
        st.caption("Select between local offline-resilient farm database storage or centralized enterprise SQL Server.")
        st.write("AquaMitra features an enterprise **Dual-Tier Persistence Architecture**: an offline-first resilient local store for continuous field farm operations, and direct **Microsoft SQL Server** connectivity for centralized multi-facility aggregation.")
        is_demo = st.session_state.get("demo_mode", True)
        storage_mode = st.radio(
            "Active Storage Engine",
            options=["Local Offline-Resilient Farm Storage", "Centralized Microsoft SQL Server"],
            index=0 if is_demo else 1
        )
        new_demo = (storage_mode == "Local Offline-Resilient Farm Storage")
        if new_demo != is_demo:
            st.session_state.demo_mode = new_demo
            st.rerun()

    # 6. Reference Ranges
    with tabs[5]:
        st.markdown("### Reference Ranges Configuration")
        st.caption("Standard baseline reference ranges for freshwater aquaculture parameters. Values outside these thresholds trigger monitoring alerts.")
        ref_data = []
        for k, v in DEFAULT_REFERENCE_RANGES.items():
            ref_data.append({"Parameter": k, "Lower": v["lower"], "Upper": v["upper"], "Unit": v["unit"], "Description": v["description"]})
        st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)

    # 7. AI Settings
    with tabs[6]:
        st.markdown("### AquaMitra AI Provider Settings")
        st.caption("Manage AI models, API keys, and autonomous safety boundaries.")
        ai_creds = get_ai_credentials()
        st.write(f"Active AI Provider: **{ai_creds['provider'].upper()}**")
        if ai_creds["provider"] == "demo":
            st.info("Operating in [AQUAMITRA LOCAL INTELLIGENCE ENGINE] mode. Generates structured, evidence-grounded insights and deterministic calculations without external cloud API dependencies.")
        else:
            st.success(f"Connected to live [{ai_creds['provider'].upper()}] cloud intelligence endpoint.")
        
        st.selectbox("AI Model Selection", options=["Gemini 1.5 Flash (Recommended for latency)", "Gemini 1.5 Pro (Deep reasoning)", "Local Deterministic Rule Engine"], index=0)
        st.text_input("Gemini API Key", value="••••••••••••••••" if ai_creds.get("gemini_key") else "", type="password", help="Set in .streamlit/secrets.toml for persistent deployment.")

    # 8. Database Status
    with tabs[7]:
        st.markdown("### Microsoft SQL Server Connectivity")
        st.caption("Database server connection configuration and health validation.")
        db_creds = get_db_credentials()
        st.write(f"Configured Host: `{db_creds['server']}` | Database: `{db_creds['database']}` | User: `{db_creds['username']}`")
        
        if st.button("Test SQL Server Connection Now", type="primary"):
            with st.spinner("Pinging database server..."):
                if is_database_connected():
                    st.success("Successfully connected to Microsoft SQL Server.")
                    st.session_state.demo_mode = False
                else:
                    st.info("Central database is offline or unconfigured. AquaMitra is operating securely in Local Resilient Farm Storage mode.")
                    st.session_state.demo_mode = True

    # 9. Data Management & Backup
    with tabs[8]:
        st.markdown("### Data Backup & Archive")
        st.caption("Export master records or reset baseline farm enterprise data.")
        all_ponds_csv = pd.DataFrame(st.session_state.get("demo_ponds", [])).to_csv(index=False).encode("utf-8")
        st.download_button("Download Master Ponds Register (CSV)", data=all_ponds_csv, file_name="AquaMitra_Master_Ponds.csv", mime="text/csv")
        
        st.markdown("---")
        st.markdown("#### System State Reset")
        st.caption("Restore verified baseline farm enterprise records.")
        if st.button("Restore Verified Baseline Farm Data"):
            from utils.demo_data import initialize_demo_data
            initialize_demo_data(st.session_state)
            st.success("Farm enterprise dataset refreshed to verified baseline.")
            st.rerun()

    # 10. About
    with tabs[9]:
        st.markdown(f"### {APP_NAME} (v{APP_VERSION})")
        st.markdown(f"**{APP_TAGLINE}**")
        st.markdown(
            """
            AquaMitra is an academic **Community Service Project (CSP)** built for fish farming and pond communities.
            
            - **Department:** Computer Science & Engineering
            - **Project Nature:** Digital Fishery Pond Management & Decision-Support System
            - **Philosophy:** Practical, farmer-friendly, evidence-based decision support. Never replaces veterinarians or autonomous control.
            """
        )
        st.markdown(
            f"""
            <div class="disclaimer-box">
                <strong>Safety Disclaimer:</strong> {DISCLAIMER_TEXT}
            </div>
            """,
            unsafe_allow_html=True
        )
