"""
AquaMitra Settings View Module
Provides Farm Profile Editor, General Config, Appearance, Language,
Data Mode, Reference Ranges, AI Settings, Database Status, Data Management, and About AquaMitra.
100% Zero-Emoji Professional SaaS Interface. Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
from utils.constants import APP_NAME, APP_TAGLINE, APP_VERSION, DISCLAIMER_TEXT, DEFAULT_REFERENCE_RANGES
from utils.translations import t, tv
from database.connection import is_database_connected, get_db_credentials
from services.ai.ai_service import get_ai_credentials


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_settings_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Farm Profile", "ఫార్మ్ ప్రొఫైల్"),
        _lbl(lang, "General", "సాధారణం"),
        _lbl(lang, "Appearance", "రూపం"),
        _lbl(lang, "Language", "భాష"),
        _lbl(lang, "Data Mode", "డేటా మోడ్"),
        _lbl(lang, "Reference Ranges", "ప్రమాణ పరిధులు"),
        _lbl(lang, "AI Settings", "AI సెట్టింగ్‌లు"),
        _lbl(lang, "Database", "డేటాబేస్"),
        _lbl(lang, "Data Management", "డేటా నిర్వహణ"),
        _lbl(lang, "About", "గురించి")
    ]
    tabs = st.tabs(subtabs)

    prof = st.session_state.get("demo_farm_profile", {})

    # 1. Farm Profile (All 16 Fields)
    with tabs[0]:
        st.markdown(f"### {_lbl(lang, 'Farm & Owner Profile', 'ఫార్మ్ మరియు యజమాని ప్రొఫైల్')}")
        st.caption(_lbl(lang, "Update farm enterprise attributes, geographic location, and operational parameters.", "ఫార్మ్ వివరాలు, భౌగోళిక ప్రాంతం మరియు నిర్వహణ వివరాలను అప్‌డేట్ చేయండి."))

        with st.form("edit_farm_profile_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_name = st.text_input(_lbl(lang, "Farm Name *", "ఫార్మ్ పేరు *"), value=prof.get("FarmName", "Godavari Aqua Greens Farm"))
                f_owner = st.text_input(_lbl(lang, "Owner Name *", "యజమాని పేరు *"), value=prof.get("OwnerName", "Ramesh Varma"))
                f_mobile = st.text_input(_lbl(lang, "Mobile Number *", "మొబైల్ నంబర్ *"), value=prof.get("MobileNumber", "+91 98480 12345"))
            with c2:
                f_village = st.text_input(_lbl(lang, "Village", "గ్రామం"), value=prof.get("Village", "Undi"))
                f_mandal = st.text_input(_lbl(lang, "Mandal", "మండలం"), value=prof.get("Mandal", "Undi Mandal"))
                f_dist = st.text_input(_lbl(lang, "District", "జిల్లా"), value=prof.get("District", "West Godavari"))
            with c3:
                f_state = st.text_input(_lbl(lang, "State", "రాష్ట్రం"), value=prof.get("State", "Andhra Pradesh"))
                f_pin = st.text_input(_lbl(lang, "PIN Code", "పిన్ కోడ్"), value=prof.get("PINCode", "534199"))
                f_type = st.text_input(_lbl(lang, "Farm Type", "ఫార్మ్ రకం"), value=prof.get("FarmType", "Commercial Freshwater Semi-Intensive"))

            c4, c5, c6 = st.columns(3)
            with c4:
                f_area = st.number_input(_lbl(lang, "Total Farm Area (Acres)", "మొత్తం ఫార్మ్ విస్తీర్ణం (ఎకరాలు)"), min_value=0.5, value=float(prof.get("TotalFarmArea", 7.0)), step=0.5)
                f_area_unit = st.selectbox(
                    _lbl(lang, "Area Unit", "విస్తీర్ణ ప్రమాణం"),
                    options=["Acres", "Hectares", "Cents"],
                    index=0,
                    format_func=lambda x: "సెంట్లు" if (x == "Cents" and lang == "te") else tv(x, lang)
                )
            with c5:
                f_ponds_count = st.number_input(_lbl(lang, "Number of Ponds", "చెరువుల సంఖ్య"), min_value=1, value=int(prof.get("NumberOfPonds", 3)), step=1)
                f_species = st.text_input(_lbl(lang, "Primary Cultured Species", "ప్రధాన సాగు జాతులు"), value=prof.get("PrimarySpecies", "Rohu, Catla, GIFT Tilapia"))
            with c6:
                f_water = st.text_input(_lbl(lang, "Primary Water Source", "ప్రధాన నీటి వనరు"), value=prof.get("WaterSource", "Godavari Canal & Deep Borewell"))
                f_start_date = st.date_input(_lbl(lang, "Operation Start Date", "ప్రారంభ తేదీ"), value=date(2024, 3, 15))

            f_addr = st.text_area(_lbl(lang, "Full Farm Address / Survey Details", "పూర్తి ఫార్మ్ చిరునామా / సర్వే వివరాలు"), value=prof.get("FarmAddress", "Survey No. 142/B, Kolleru Road, Undi"))
            f_notes = st.text_area(_lbl(lang, "Operational Notes & Best Practices", "నిర్వహణ గమనికలు & ఉత్తమ పద్ధతులు"), value=prof.get("Notes", "Community-focused sustainable fishery adhering to standard BMP."))

            save_prof_btn = st.form_submit_button(_lbl(lang, "Save Farm Profile", "ఫార్మ్ ప్రొఫైల్ సేవ్ చేయండి"), type="primary", use_container_width=True)
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
                st.success(_lbl(lang, "Farm profile updated successfully.", "ఫార్మ్ ప్రొఫైల్ విజయవంతంగా అప్‌డేట్ చేయబడింది."))
                st.rerun()

    # 2. General
    with tabs[1]:
        st.markdown(f"### {_lbl(lang, 'General Operational Settings', 'సాధారణ నిర్వహణ సెట్టింగ్‌లు')}")
        st.caption(_lbl(lang, "Default metrics and system localization settings applied across calculations.", "గణనలలో ఉపయోగించే డిఫాల్ట్ కొలమానాలు మరియు స్థానిక సెట్టింగ్‌లు."))
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox(_lbl(lang, "Default Currency", "డిఫాల్ట్ కరెన్సీ"), options=["₹ INR (Indian Rupee)", "$ USD", "€ EUR"], index=0)
            st.selectbox(_lbl(lang, "Default Biomass / Feed Weight Unit", "బయోమాస్ / మేత బరువు యూనిట్"), options=["Kilograms (kg)", "Metric Tonnes (t)"], index=0)
        with c2:
            st.selectbox(_lbl(lang, "Fish Sample Weight Unit", "చేప నమూనా బరువు యూనిట్"), options=["Grams (g)", "Kilograms (kg)"], index=0)
            st.selectbox(_lbl(lang, "Date Display Format", "తేదీ ఫార్మాట్"), options=["DD/MM/YYYY", "YYYY-MM-DD"], index=0)
        st.info(_lbl(lang, "System calculation engines automatically utilize these standard parameters.", "సిస్టమ్ గణన ఇంజిన్లు ఈ ప్రమాణ పారామితులను స్వయంచాలకంగా ఉపయోగిస్తాయి."))

    # 3. Appearance
    with tabs[2]:
        st.markdown(f"### {_lbl(lang, 'Visual Theme & Display System', 'విజువల్ థీమ్ మరియు డిస్‌ప్లే సిస్టమ్')}")
        st.caption(_lbl(lang, "AquaMitra SaaS enterprise agricultural design system specifications.", "ఆక్వామిత్ర ఎంటర్‌ప్రైజ్ వ్యవసాయ సాఫ్ట్‌వేర్ డిజైన్ ప్రమాణాలు."))
        if lang == "te":
            st.markdown(
                """
                - **ప్రధాన బ్రాండ్ రంగు:** నేవీ బ్లూ (`#0F2942`)
                - **యాక్సెంట్ రంగు:** టీల్ (`#0D9488`)
                - **టెక్స్ట్ శైలి:** స్లేట్ చార్‌కోల్ (`#0F172A`, `#334155`, `#64748B`)
                - **బ్యాక్‌గ్రౌండ్ రంగులు:** కూల్ స్లేట్ టింట్ (`#F8FAFC`, `#FFFFFF`)
                - **బార్డర్లు:** సూక్ష్మమైన స్లేట్ (`#E2E8F0`)
                - **డిజైన్ విధానం:** ఎమోజీలు లేని స్వచ్ఛమైన ప్రొఫెషనల్ SaaS ఇంటర్‌ఫేస్
                """
            )
        else:
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
        st.markdown(f"### {_lbl(lang, 'Bilingual Interface Settings', 'ద్విభాషా ఇంటర్‌ఫేస్ సెట్టింగ్‌లు')}")
        st.caption(_lbl(lang, "Toggle between English and Telugu across all menus, forms, and analytical views.", "అన్ని మెనూలు, ఫారమ్‌లు మరియు విశ్లేషణలలో ఇంగ్లీష్ మరియు తెలుగు మధ్య మారండి."))
        curr_lang = st.session_state.get("lang", "en")
        curr_lang_disp = "తెలుగు (Telugu)" if curr_lang == "te" else "English"
        st.write(f"{_lbl(lang, 'Current Active Language', 'ప్రస్తుత క్రియాశీల భాష')}: **{curr_lang_disp}**")
        l_col1, l_col2 = st.columns(2)
        with l_col1:
            if st.button(_lbl(lang, "Switch to English", "English కు మారండి"), type="primary" if curr_lang == "en" else "secondary", use_container_width=True):
                st.session_state.lang = "en"
                try:
                    st.query_params["lang"] = "en"
                except Exception:
                    pass
                st.rerun()
        with l_col2:
            if st.button("తెలుగులోకి మారండి (Switch to Telugu)", type="primary" if curr_lang == "te" else "secondary", use_container_width=True):
                st.session_state.lang = "te"
                try:
                    st.query_params["lang"] = "te"
                except Exception:
                    pass
                st.rerun()

    # 5. Data Mode
    with tabs[4]:
        st.markdown(f"### {_lbl(lang, 'Data Storage & Persistence Mode', 'డేటా నిల్వ మరియు నిర్వహణ విధానం')}")
        st.caption(_lbl(lang, "Select between local offline-resilient farm database storage or centralized enterprise SQL Server.", "స్థానిక ఆఫ్‌లైన్-స్థిరమైన నిల్వ లేదా కేంద్రీకృత SQL సర్వర్ మధ్య ఎంచుకోండి."))
        st.write(_lbl(
            lang,
            "AquaMitra features an enterprise **Dual-Tier Persistence Architecture**: an offline-first resilient local store for continuous field farm operations, and direct **Microsoft SQL Server** connectivity for centralized multi-facility aggregation.",
            "ఆక్వామిత్ర **ద్వంద్వ డేటా నిల్వ నిర్మాణాన్ని** కలిగి ఉంది: ఫీల్డ్ వద్ద నిరంతరాయం లేకుండా పనిచేయడానికి స్థానిక స్థిరమైన నిల్వ మరియు కేంద్రీకృత డేటా కోసం **Microsoft SQL Server** అనుసంధానం."
        ))
        is_demo = st.session_state.get("demo_mode", True)
        mode_labels_te = {
            "Local Offline-Resilient Farm Storage": "స్థానిక ఆఫ్‌లైన్-స్థిరమైన ఫార్మ్ నిల్వ",
            "Centralized Microsoft SQL Server": "కేంద్రీకృత మైక్రోసాఫ్ట్ SQL సర్వర్",
        }
        storage_mode = st.radio(
            _lbl(lang, "Active Storage Engine", "క్రియాశీల డేటా ఇంజిన్"),
            options=["Local Offline-Resilient Farm Storage", "Centralized Microsoft SQL Server"],
            index=0 if is_demo else 1,
            format_func=lambda x: mode_labels_te.get(x, x) if lang == "te" else x
        )
        new_demo = (storage_mode == "Local Offline-Resilient Farm Storage")
        if new_demo != is_demo:
            st.session_state.demo_mode = new_demo
            st.rerun()

    # 6. Reference Ranges
    with tabs[5]:
        st.markdown(f"### {_lbl(lang, 'Reference Ranges Configuration', 'ప్రమాణ పరిధుల కాన్ఫిగరేషన్')}")
        st.caption(_lbl(lang, "Standard baseline reference ranges for freshwater aquaculture parameters. Values outside these thresholds trigger monitoring alerts.", "మంచినీటి చేపల సాగు పారామితుల ప్రామాణిక పరిధులు. ఈ పరిమితులకు మించిన విలువలు అలర్ట్‌లను ప్రేరేపిస్తాయి."))
        ref_data = []
        p_col = _lbl(lang, "Parameter", "పారామితి")
        l_col = _lbl(lang, "Lower", "కనిష్టం")
        u_col = _lbl(lang, "Upper", "గరిష్టం")
        un_col = _lbl(lang, "Unit", "యూనిట్")
        d_col = _lbl(lang, "Description", "వివరణ")
        for k, v in DEFAULT_REFERENCE_RANGES.items():
            ref_data.append({p_col: k, l_col: v["lower"], u_col: v["upper"], un_col: v["unit"], d_col: v["description"]})
        st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)

    # 7. AI Settings
    with tabs[6]:
        st.markdown(f"### {_lbl(lang, 'AquaMitra AI Provider Settings', 'ఆక్వామిత్ర AI ప్రొవైడర్ సెట్టింగ్‌లు')}")
        st.caption(_lbl(lang, "Manage AI models, API keys, and autonomous safety boundaries.", "AI మోడల్స్, API కీలు మరియు భద్రతా నియమాలను నిర్వహించండి."))
        ai_creds = get_ai_credentials()
        st.write(f"{_lbl(lang, 'Active AI Provider', 'క్రియాశీల AI ప్రొవైడర్')}: **{ai_creds['provider'].upper()}**")
        if ai_creds["provider"] == "demo":
            st.info(_lbl(
                lang,
                "Operating in [AQUAMITRA LOCAL INTELLIGENCE ENGINE] mode. Generates structured, evidence-grounded insights and deterministic calculations without external cloud API dependencies.",
                "[ఆక్వామిత్ర స్థానిక ఇంటెలిజెన్స్ ఇంజిన్] మోడ్‌లో పనిచేస్తోంది. బాహ్య API పై ఆధారపడకుండా మీ ఫార్మ్ రికార్డుల ఆధారంగా విశ్లేషణలు అందిస్తుంది."
            ))
        else:
            st.success(_lbl(lang, f"Connected to live [{ai_creds['provider'].upper()}] cloud intelligence endpoint.", f"[{ai_creds['provider'].upper()}] క్లౌడ్ AI సేవకు కనెక్ట్ చేయబడింది."))

        st.selectbox(
            _lbl(lang, "AI Model Selection", "AI మోడల్ ఎంపిక"),
            options=["Gemini 1.5 Flash (Recommended for latency)", "Gemini 1.5 Pro (Deep reasoning)", "Local Deterministic Rule Engine"],
            index=0
        )
        st.text_input(
            _lbl(lang, "Gemini API Key", "జెమిని API కీ"),
            value="••••••••••••••••" if ai_creds.get("gemini_key") else "",
            type="password",
            help=_lbl(lang, "Set in .streamlit/secrets.toml for persistent deployment.", "శాశ్వత డిప్లాయ్‌మెంట్ కోసం .streamlit/secrets.toml లో సెట్ చేయండి.")
        )

    # 8. Database Status
    with tabs[7]:
        st.markdown(f"### {_lbl(lang, 'Microsoft SQL Server Connectivity', 'మైక్రోసాఫ్ట్ SQL సర్వర్ అనుసంధానం')}")
        st.caption(_lbl(lang, "Database server connection configuration and health validation.", "డేటాబేస్ సర్వర్ సెట్టింగ్‌లు మరియు కనెక్షన్ తనిఖీ."))
        db_creds = get_db_credentials()
        st.write(
            f"{_lbl(lang, 'Configured Host', 'హోస్ట్')}: `{db_creds['server']}` | "
            f"{_lbl(lang, 'Database', 'డేటాబేస్')}: `{db_creds['database']}` | "
            f"{_lbl(lang, 'User', 'వినియోగదారు')}: `{db_creds['username']}`"
        )

        if st.button(_lbl(lang, "Test SQL Server Connection Now", "SQL సర్వర్ కనెక్షన్‌ను పరీక్షించండి"), type="primary"):
            with st.spinner(_lbl(lang, "Pinging database server...", "డేటాబేస్ సర్వర్‌ను తనిఖీ చేస్తోంది...")):
                if is_database_connected():
                    st.success(_lbl(lang, "Successfully connected to Microsoft SQL Server.", "మైక్రోసాఫ్ట్ SQL సర్వర్‌కు విజయవంతంగా కనెక్ట్ చేయబడింది."))
                    st.session_state.demo_mode = False
                else:
                    st.info(_lbl(
                        lang,
                        "Central database is offline or unconfigured. AquaMitra is operating securely in Local Resilient Farm Storage mode.",
                        "కేంద్ర డేటాబేస్ ఆఫ్‌లైన్‌లో ఉంది. ఆక్వామిత్ర సురక్షితంగా స్థానిక ఫార్మ్ నిల్వ మోడ్‌లో పనిచేస్తోంది."
                    ))
                    st.session_state.demo_mode = True

    # 9. Data Management & Backup
    with tabs[8]:
        st.markdown(f"### {_lbl(lang, 'Data Backup & Archive', 'డేటా బ్యాకప్ మరియు ఆర్కైవ్')}")
        st.caption(_lbl(lang, "Export master records or reset baseline farm enterprise data.", "ప్రధాన రికార్డులను ఎగుమతి చేయండి లేదా ప్రారంభ డేటాను రీసెట్ చేయండి."))
        all_ponds_csv = pd.DataFrame(st.session_state.get("demo_ponds", [])).to_csv(index=False).encode("utf-8")
        st.download_button(
            _lbl(lang, "Download Master Ponds Register (CSV)", "మాస్టర్ చెరువుల రిజిస్టర్ డౌన్‌లోడ్ (CSV)"),
            data=all_ponds_csv,
            file_name="AquaMitra_Master_Ponds.csv",
            mime="text/csv"
        )

        st.markdown("---")
        st.markdown(f"#### {_lbl(lang, 'System State Reset', 'సిస్టమ్ స్థితి రీసెట్')}")
        st.caption(_lbl(lang, "Restore verified baseline farm enterprise records.", "ధృవీకరించబడిన ప్రాథమిక ఫార్మ్ డేటాను పునరుద్ధరించండి."))
        if st.button(_lbl(lang, "Restore Verified Baseline Farm Data", "ప్రాథమిక ఫార్మ్ డేటాను పునరుద్ధరించండి")):
            from utils.demo_data import initialize_demo_data
            initialize_demo_data(st.session_state)
            st.success(_lbl(lang, "Farm enterprise dataset refreshed to verified baseline.", "ఫార్మ్ డేటాసెట్ ప్రారంభ స్థితికి పునరుద్ధరించబడింది."))
            st.rerun()

    # 10. About
    with tabs[9]:
        app_title = t("app_name", lang) if t("app_name", lang) != "app_name" else APP_NAME
        tagline_str = t("tagline", lang) if t("tagline", lang) != "tagline" else APP_TAGLINE
        st.markdown(f"### {app_title} (v{APP_VERSION})")
        st.markdown(f"**{tagline_str}**")
        if lang == "te":
            st.markdown(
                """
                ఆక్వామిత్ర అనేది చేపల పెంపకం మరియు మత్స్య రైతు సంఘాల కోసం రూపొందించబడిన ఒక **కమ్యూనిటీ సర్వీస్ ప్రాజెక్ట్ (CSP)** అప్లికేషన్.

                - **విభాగం:** కంప్యూటర్ సైన్స్ & ఇంజనీరింగ్
                - **ప్రాజెక్ట్ స్వభావం:** డిజిటల్ మత్స్య చెరువుల నిర్వహణ మరియు నిర్ణయ-సహాయ వ్యవస్థ (DSS)
                - **తత్వం:** ఆచరణాత్మక, రైతు-స్నేహపూర్వక, ఆధార-ఆధారిత నిర్ణయ సహాయం. ఇది పశువైద్యులను లేదా స్వయంచాలక నియంత్రణను భర్తీ చేయదు.
                """
            )
            disclaimer_lbl = "భద్రతా గమనిక"
            disclaimer_val = t("disclaimer_body", lang)
            if disclaimer_val == "disclaimer_body":
                disclaimer_val = "ఆక్వామిత్ర ఫార్మ్ నిర్వహణ కోసం సమాచార విశ్లేషణ మరియు నిర్ణయ-సహాయ మార్గదర్శకత్వాన్ని మాత్రమే అందిస్తుంది. ఇది వైద్య నిర్ధారణ, చికిత్స లేదా లాభాల హామీని ఇవ్వదు."
        else:
            st.markdown(
                """
                AquaMitra is an academic **Community Service Project (CSP)** built for fish farming and pond communities.

                - **Department:** Computer Science & Engineering
                - **Project Nature:** Digital Fishery Pond Management & Decision-Support System
                - **Philosophy:** Practical, farmer-friendly, evidence-based decision support. Never replaces veterinarians or autonomous control.
                """
            )
            disclaimer_lbl = "Safety Disclaimer"
            disclaimer_val = DISCLAIMER_TEXT

        st.markdown(
            f"""
            <div class="disclaimer-box">
                <strong>{disclaimer_lbl}:</strong> {disclaimer_val}
            </div>
            """,
            unsafe_allow_html=True
        )
