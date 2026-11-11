"""
AquaMitra Quick Action Modals
Interactive dialog forms for immediate record entry across all core operations.
Updates session state and live database in real-time with zero dead-end buttons.
Strictly zero emojis. Fully bilingual (English / Telugu).
"""

from datetime import date, datetime, timedelta
import streamlit as st
from utils.constants import POND_TYPES, AREA_UNITS, WATER_SOURCES, SPECIES_LIST, EXPENSE_CATEGORIES
from utils.calculations import calculate_initial_biomass
from utils.translations import tv
from database.queries import (
    save_fish_stock,
    get_fish_stocks,
    save_harvest_record,
    save_maintenance_record,
    update_pond_record
)


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def dialog_add_pond():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Add New Fishery Pond", "కొత్త చేపల చెరువును జోడించు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Register a new aquaculture pond into the farm system.",
            "మీ ఫార్మ్ సిస్టమ్‌లో కొత్త చేపల చెరువును నమోదు చేయండి."
        ))
        with st.form("quick_add_pond_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                p_id = st.text_input(
                    _lbl(lang, "Pond ID *", "చెరువు ID *"),
                    value=f"P-00{len(st.session_state.demo_ponds)+1}",
                    placeholder="e.g. P-004"
                )
                p_name = st.text_input(
                    _lbl(lang, "Pond Name *", "చెరువు పేరు *"),
                    placeholder=_lbl(lang, "e.g. Surya Sunrise Pond", "ఉదా. సూర్య సన్‌రైజ్ చెరువు")
                )
                location = st.text_input(
                    _lbl(lang, "Location *", "ప్రాంతం *"),
                    placeholder=_lbl(lang, "e.g. West Godavari, Sector C", "ఉదా. పశ్చిమ గోదావరి, సెక్టార్ C")
                )
                area = st.number_input(_lbl(lang, "Pond Area *", "చెరువు విస్తీర్ణం *"), min_value=0.1, value=2.0, step=0.1)
                area_unit = st.selectbox(
                    _lbl(lang, "Area Unit", "విస్తీర్ణ ప్రమాణం"),
                    options=AREA_UNITS,
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )
            with col2:
                p_type = st.selectbox(
                    _lbl(lang, "Pond Type", "చెరువు రకం"),
                    options=POND_TYPES,
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )
                water_source = st.selectbox(
                    _lbl(lang, "Water Source", "నీటి వనరు"),
                    options=WATER_SOURCES,
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )
                depth = st.number_input(_lbl(lang, "Average Depth (meters)", "సగటు లోతు (మీటర్లు)"), min_value=0.5, value=1.6, step=0.1)
                owner = st.text_input(_lbl(lang, "Owner / Manager", "యజమాని / మేనేజర్"), value="Ramesh Varma")
                status = st.selectbox(
                    _lbl(lang, "Initial Status", "ప్రారంభ స్థితి"),
                    options=["Active", "Preparing", "Maintenance"],
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )

            notes = st.text_area(
                _lbl(lang, "Pond Remarks / Soil Characteristics", "చెరువు గమనికలు / నేల వివరాలు"),
                placeholder=_lbl(lang, "Compacted clay bottom with inlet screen...", "గట్టిపడిన బంకమట్టి అడుగు భాగం మరియు ఇన్‌లెట్ జాలీ...")
            )

            submitted = st.form_submit_button(_lbl(lang, "Save Pond Record", "చెరువు రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                if not p_name or not p_id:
                    st.error(_lbl(lang, "Please enter a valid Pond ID and Pond Name.", "దయచేసి సరైన చెరువు ID మరియు పేరు నమోదు చేయండి."))
                elif any(p["PondID"] == p_id.strip() for p in st.session_state.demo_ponds):
                    st.error(_lbl(lang, f"Pond ID '{p_id}' already exists. Please choose a unique ID.", f"చెరువు ID '{p_id}' ఇప్పటికే ఉంది. దయచేసి వేరే ID ఎంచుకోండి."))
                else:
                    new_pond = {
                        "PondID": p_id.strip().upper(),
                        "PondName": p_name.strip(),
                        "PondCode": f"{p_id.strip().upper()}-01",
                        "Status": status,
                        "Location": location.strip(),
                        "Area": float(area),
                        "AreaUnit": area_unit,
                        "LengthMeters": round(float(area) * 55.0, 1),
                        "WidthMeters": 40.0,
                        "AvgDepthMeters": float(depth),
                        "MaxDepthMeters": float(depth) + 0.5,
                        "WaterVolumeM3": round(float(area) * 4046.86 * float(depth), 0),
                        "PondType": p_type,
                        "WaterSource": water_source,
                        "WaterInlet": "PVC Sluice with Mesh Filter",
                        "WaterOutlet": "Bottom Monk Drain",
                        "WaterExchangeMethod": "Gravity / Pump",
                        "SoilType": "Clayey Loam",
                        "LiningType": "Natural Compacted Clay" if p_type == "Earthen" else "HDPE",
                        "EmbankmentCondition": "Good",
                        "BottomCondition": "De-silted and limed",
                        "Owner": owner.strip(),
                        "Manager": owner.strip(),
                        "DateAdded": date.today().strftime("%Y-%m-%d"),
                        "LastRenovation": date.today().strftime("%Y-%m-%d"),
                        "Notes": notes.strip()
                    }
                    st.session_state.demo_ponds.append(new_pond)
                    st.success(_lbl(lang, f"Pond {p_id} ({p_name}) added successfully.", f"చెరువు {p_id} ({p_name}) విజయవంతంగా జోడించబడింది."))
                    st.rerun()

    _render()


def dialog_edit_pond(pond_id: str):
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Edit Pond Profile", "చెరువు ప్రొఫైల్‌ను సవరించండి"))
    def _render():
        pond = next((p for p in st.session_state.demo_ponds if p["PondID"] == pond_id), None)
        if not pond:
            st.error(_lbl(lang, f"Pond {pond_id} not found.", f"చెరువు {pond_id} కనుగొనబడలేదు."))
            return

        st.caption(_lbl(
            lang,
            f"Update attributes and specifications for {pond_id} ({pond.get('PondName', '')}).",
            f"{pond_id} ({pond.get('PondName', '')}) వివరాలు మరియు కొలతలను అప్‌డేట్ చేయండి."
        ))
        with st.form(f"edit_pond_form_{pond_id}"):
            c1, c2 = st.columns(2)
            with c1:
                p_name = st.text_input(_lbl(lang, "Pond Name *", "చెరువు పేరు *"), value=pond.get("PondName", ""))
                location = st.text_input(_lbl(lang, "Location", "ప్రాంతం"), value=pond.get("Location", ""))
                area = st.number_input(_lbl(lang, "Area", "విస్తీర్ణం"), min_value=0.1, value=float(pond.get("Area", 2.0)), step=0.1)
                area_unit = st.selectbox(
                    _lbl(lang, "Area Unit", "విస్తీర్ణ ప్రమాణం"),
                    options=AREA_UNITS,
                    index=AREA_UNITS.index(pond.get("AreaUnit", "Acres")) if pond.get("AreaUnit") in AREA_UNITS else 0,
                    format_func=lambda x: tv(x, lang)
                )
                avg_depth = st.number_input(_lbl(lang, "Average Depth (m)", "సగటు లోతు (మీ.)"), min_value=0.5, value=float(pond.get("AvgDepthMeters", 1.5)), step=0.1)
                max_depth = st.number_input(_lbl(lang, "Max Depth (m)", "గరిష్ట లోతు (మీ.)"), min_value=0.5, value=float(pond.get("MaxDepthMeters", 2.0)), step=0.1)
            with c2:
                status_opts = ["Active", "Inactive", "Maintenance", "Preparing", "Harvested"]
                status = st.selectbox(
                    _lbl(lang, "Status", "స్థితి"),
                    options=status_opts,
                    index=status_opts.index(pond.get("Status", "Active")) if pond.get("Status") in status_opts else 0,
                    format_func=lambda x: tv(x, lang)
                )
                p_type = st.selectbox(
                    _lbl(lang, "Pond Type", "చెరువు రకం"),
                    options=POND_TYPES,
                    index=POND_TYPES.index(pond.get("PondType", "Earthen")) if pond.get("PondType") in POND_TYPES else 0,
                    format_func=lambda x: tv(x, lang)
                )
                water_src = st.selectbox(
                    _lbl(lang, "Water Source", "నీటి వనరు"),
                    options=WATER_SOURCES,
                    index=WATER_SOURCES.index(pond.get("WaterSource", "Canal")) if pond.get("WaterSource") in WATER_SOURCES else 0,
                    format_func=lambda x: tv(x, lang)
                )
                soil_type = st.text_input(_lbl(lang, "Soil Type", "నేల రకం"), value=pond.get("SoilType", "Clayey Loam"))
                owner = st.text_input(_lbl(lang, "Owner / Manager", "యజమాని / మేనేజర్"), value=pond.get("Owner", "Ramesh Varma"))

            notes = st.text_area(_lbl(lang, "Operational Notes", "నిర్వహణ గమనికలు"), value=pond.get("Notes", ""))

            submitted = st.form_submit_button(_lbl(lang, "Update Pond Record", "చెరువు రికార్డును అప్‌డేట్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                updated = {
                    "PondName": p_name.strip(),
                    "Location": location.strip(),
                    "Area": float(area),
                    "AreaUnit": area_unit,
                    "AvgDepthMeters": float(avg_depth),
                    "MaxDepthMeters": float(max_depth),
                    "Status": status,
                    "PondType": p_type,
                    "WaterSource": water_src,
                    "SoilType": soil_type.strip(),
                    "Owner": owner.strip(),
                    "Notes": notes.strip()
                }
                update_pond_record(pond_id, updated)
                st.success(_lbl(lang, f"Pond {pond_id} updated successfully.", f"చెరువు {pond_id} విజయవంతంగా అప్‌డేట్ చేయబడింది."))
                st.rerun()

    _render()


def dialog_add_water_reading():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Log Water Quality Observation", "నీటి నాణ్యత పరిశీలన నమోదు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Record routine water parameter observations. Missing parameters can be left empty.",
            "రోజువారీ నీటి పారామితుల వివరాలను నమోదు చేయండి."
        ))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_water_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Pond *", "చెరువు *"), options=pond_ids)
                r_date = st.date_input(_lbl(lang, "Date", "తేదీ"), value=date.today())
                r_time = st.time_input(_lbl(lang, "Time", "సమయం"), value=datetime.now().time())
            with col2:
                ph = st.number_input(_lbl(lang, "pH (0 - 14)", "pH విలువ (0 - 14)"), min_value=0.0, max_value=14.0, value=7.5, step=0.1)
                temp = st.number_input(_lbl(lang, "Temperature (°C)", "ఉష్ణోగ్రత (°C)"), min_value=10.0, max_value=45.0, value=28.5, step=0.5)
                do = st.number_input(_lbl(lang, "Dissolved Oxygen (mg/L)", "కరిగిన ఆక్సిజన్ (mg/L)"), min_value=0.0, max_value=20.0, value=6.2, step=0.1)
            with col3:
                turb = st.number_input(_lbl(lang, "Turbidity (NTU)", "టర్బిడిటీ (NTU)"), min_value=0.0, value=28.0, step=1.0)
                nh3 = st.number_input(_lbl(lang, "Ammonia NH3 (mg/L)", "అమోనియా NH3 (mg/L)"), min_value=0.0, value=0.01, step=0.005, format="%.3f")
                level = st.number_input(_lbl(lang, "Water Level (m)", "నీటి మట్టం (మీ.)"), min_value=0.5, value=1.65, step=0.05)

            notes = st.text_input(
                _lbl(lang, "Observation Notes", "పరిశీలన గమనికలు"),
                placeholder=_lbl(lang, "Clear morning sunshine; aerator run for 2 hours prior.", "ఉదయం స్పష్టమైన ఎండ; ముందుగా 2 గంటలు ఏరేటర్ నడిచింది.")
            )
            submitted = st.form_submit_button(_lbl(lang, "Save Water Observation", "నీటి పరిశీలనను సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                new_reading = {
                    "ReadingID": len(st.session_state.demo_water_quality) + 1001,
                    "PondID": sel_pond,
                    "ReadingDate": r_date.strftime("%Y-%m-%d"),
                    "ReadingTime": r_time.strftime("%H:%M:%S"),
                    "pH": float(ph),
                    "Temperature": float(temp),
                    "DissolvedOxygen": float(do),
                    "Turbidity": float(turb),
                    "Ammonia": float(nh3),
                    "Nitrite": 0.01,
                    "Nitrate": 2.5,
                    "WaterLevel": float(level),
                    "Transparency": 30.0,
                    "Salinity": 0.0,
                    "Alkalinity": 120.0,
                    "Hardness": 110.0,
                    "Conductivity": 450.0,
                    "Notes": notes.strip()
                }
                st.session_state.demo_water_quality.append(new_reading)
                st.success(_lbl(lang, f"Water observation for {sel_pond} recorded.", f"{sel_pond} కోసం నీటి పరిశీలన నమోదైంది."))
                st.rerun()

    _render()


def dialog_add_fish_stock():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Record Fish Stocking Batch", "చేప పిల్లల నిల్వ బ్యాచ్ నమోదు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Log a new fish fingerling stocking batch into a pond.",
            "చెరువులో కొత్త చేప పిల్లల నిల్వ బ్యాచ్‌ను నమోదు చేయండి."
        ))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_stock_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Stocking Pond *", "నిల్వ చెరువు *"), options=pond_ids)
                species = st.selectbox(_lbl(lang, "Species *", "చేప జాతి *"), options=SPECIES_LIST)
                variety = st.text_input(_lbl(lang, "Variety / Strain", "రకం / స్ట్రెయిన్"), placeholder="e.g. Jayanti Rohu, GIFT Tilapia")
                s_date = st.date_input(_lbl(lang, "Stocking Date", "నిల్వ తేదీ"), value=date.today())
                num_fish = st.number_input(_lbl(lang, "Number of Fingerlings *", "చేప పిల్లల సంఖ్య *"), min_value=100, value=3000, step=500)
            with col2:
                avg_weight = st.number_input(_lbl(lang, "Average Initial Weight (grams) *", "ప్రారంభ సగటు బరువు (గ్రా.) *"), min_value=1.0, value=45.0, step=5.0)
                hatchery = st.text_input(_lbl(lang, "Hatchery / Source", "హేచరీ / మూలం"), placeholder="e.g. Godavari Royal Hatchery")
                price_per_fish = st.number_input(_lbl(lang, "Price per Fish (₹)", "ఒక్క చేప పిల్ల ధర (₹)"), min_value=0.1, value=3.0, step=0.25)
                transport_cost = st.number_input(_lbl(lang, "Transport Cost (₹)", "రవాణా ఖర్చు (₹)"), min_value=0.0, value=1200.0, step=100.0)

            remarks = st.text_input(
                _lbl(lang, "Stocking Remarks", "నిల్వ గమనికలు"),
                placeholder=_lbl(lang, "Saline dip bath given; released in surface water.", "ఉప్పునీటి శుద్ధి తర్వాత ఉపరితల నీటిలో వదిలాము.")
            )
            submitted = st.form_submit_button(_lbl(lang, "Save Stocking Record", "నిల్వ రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                total_seed_cost = round(float(num_fish) * float(price_per_fish), 2)
                calculated_biomass = calculate_initial_biomass(int(num_fish), float(avg_weight))
                new_stock = {
                    "PondID": sel_pond,
                    "Species": species,
                    "Variety": variety.strip() if variety else species,
                    "StockingDate": s_date.strftime("%Y-%m-%d"),
                    "NumberOfFish": int(num_fish),
                    "AvgInitialWeightGrams": float(avg_weight),
                    "TotalInitialBiomassKg": calculated_biomass,
                    "SourceHatchery": hatchery.strip(),
                    "BatchNumber": f"{species[:3].upper()}-{s_date.strftime('%Y%m')}-B",
                    "SizeCategory": "Fingerling (3-4 inches)",
                    "PricePerFish": float(price_per_fish),
                    "TotalSeedCost": total_seed_cost,
                    "TransportCost": float(transport_cost),
                    "Notes": remarks.strip(),
                    "Remarks": remarks.strip()
                }
                save_fish_stock(new_stock)
                st.success(_lbl(
                    lang,
                    f"Stocking batch for {sel_pond} recorded: {num_fish:,} {species} ({calculated_biomass:,.1f} kg biomass).",
                    f"{sel_pond} కోసం బ్యాచ్ నమోదైంది: {num_fish:,} {species} ({calculated_biomass:,.1f} కేజీ బయోమాస్)."
                ))
                st.rerun()

    _render()


def dialog_add_growth_sample():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Record Fish Growth Sampling", "చేపల పెరుగుదల నమూనా నమోదు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Record random cast-net sample observations to update estimated biomass.",
            "అంచనా బయోమాస్‌ను అప్‌డేట్ చేయడానికి వల నమూనా వివరాలను నమోదు చేయండి."
        ))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_growth_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Sampled Pond *", "నమూనా చెరువు *"), options=pond_ids)
                sample_date = st.date_input(_lbl(lang, "Sampling Date", "నమూనా తేదీ"), value=date.today())
                sample_size = st.number_input(_lbl(lang, "Sample Count (Fish Sampled)", "పరీక్షించిన చేపల సంఖ్య"), min_value=5, value=25, step=5)
            with col2:
                avg_weight = st.number_input(_lbl(lang, "Average Weight (grams) *", "సగటు బరువు (గ్రా.) *"), min_value=1.0, value=480.0, step=10.0)
                min_weight = st.number_input(_lbl(lang, "Minimum Observed Weight (grams)", "కనిష్ట బరువు (గ్రా.)"), min_value=1.0, value=420.0, step=10.0)
                max_weight = st.number_input(_lbl(lang, "Maximum Observed Weight (grams)", "గరిష్ట బరువు (గ్రా.)"), min_value=1.0, value=540.0, step=10.0)

            p_stocks = get_fish_stocks(pond_id=sel_pond)
            species_label = p_stocks[0].get("Species", "Sampled Fish") if p_stocks else "Sampled Fish"
            total_fish_count = sum(s.get("NumberOfFish", 0) for s in p_stocks) or 5000

            notes = st.text_input(
                _lbl(lang, "Sampling Notes", "నమూనా గమనికలు"),
                placeholder=_lbl(lang, "Healthy vigor, clear body shine, active feeding observed.", "ఆరోగ్యంగా చురుకుగా ఉన్నాయి, మేత బాగా తీసుకుంటున్నాయి.")
            )
            submitted = st.form_submit_button(_lbl(lang, "Save Growth Observation", "పెరుగుదల పరిశీలనను సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                est_biomass = round((total_fish_count * float(avg_weight)) / 1000.0, 1)
                new_growth = {
                    "GrowthID": len(st.session_state.demo_fish_growth) + 1,
                    "PondID": sel_pond,
                    "Species": species_label,
                    "ObservationDate": sample_date.strftime("%Y-%m-%d"),
                    "SampleSize": int(sample_size),
                    "AvgFishWeightGrams": float(avg_weight),
                    "MinWeightGrams": float(min_weight),
                    "MaxWeightGrams": float(max_weight),
                    "EstimatedBiomassKg": est_biomass,
                    "SamplingMethod": "Cast Netting (3-point haul)",
                    "Observer": "Technician K. Rao",
                    "Notes": notes.strip()
                }
                st.session_state.demo_fish_growth.append(new_growth)
                st.success(_lbl(
                    lang,
                    f"Growth recorded for {sel_pond}: {avg_weight} g average weight. Estimated biomass: {est_biomass:,.0f} kg.",
                    f"{sel_pond} పెరుగుదల నమోదైంది: {avg_weight} గ్రా. సగటు బరువు. అంచనా బయోమాస్: {est_biomass:,.0f} కేజీ."
                ))
                st.rerun()

    _render()


def dialog_add_feeding():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Record Daily Feed Application", "రోజువారీ మేత నమోదు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Record feed applied to a pond and assess fish feeding vigor.",
            "చెరువుకు వేసిన మేత మరియు చేపల మేత స్పందనను నమోదు చేయండి."
        ))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_feed_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Feeding Pond *", "మేత చెరువు *"), options=pond_ids)
                f_date = st.date_input(_lbl(lang, "Feeding Date", "మేత తేదీ"), value=date.today())
                feed_type = st.selectbox(
                    _lbl(lang, "Feed Type", "మేత రకం"),
                    options=["Pellet (32% Protein)", "Floating Pellet (28%)", "Sinking Pellet (24%)", "Mash / Rice Bran Mix", "Other"],
                    format_func=lambda x: tv(x, lang)
                )
                brand = st.selectbox(
                    _lbl(lang, "Feed Brand", "మేత బ్రాండ్"),
                    options=["Godrej Aquafeed", "CP Aqua Classic", "Avanti Feeds", "Farm Mix"],
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )
            with col2:
                actual_kg = st.number_input(_lbl(lang, "Feed Given (kg) *", "వేసిన మేత (కేజీ) *"), min_value=1.0, value=75.0, step=5.0)
                cost_per_kg = st.number_input(_lbl(lang, "Feed Cost per kg (₹)", "కేజీ మేత ధర (₹)"), min_value=10.0, value=48.0, step=1.0)
                feedings_count = st.number_input(_lbl(lang, "Number of Feedings Today", "ఈ రోజు మేత విడతల సంఖ్య"), min_value=1, max_value=6, value=2)
                response = st.selectbox(
                    _lbl(lang, "Feed Response / Tray Check", "మేత స్పందన / చెక్ ట్రే"),
                    options=["Good (Clean feeding tray)", "Moderate (Little left)", "Poor (Excess feed remaining)"],
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )

            remarks = st.text_input(
                _lbl(lang, "Feeding Notes", "మేత గమనికలు"),
                placeholder=_lbl(lang, "Fed at 07:30 AM and 04:30 PM. Active response.", "ఉదయం 07:30 మరియు సాయంత్రం 04:30 గంటలకు మేత వేసాము.")
            )
            submitted = st.form_submit_button(_lbl(lang, "Save Feed Record", "మేత రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                total_cost = round(float(actual_kg) * float(cost_per_kg), 2)
                new_feed = {
                    "FeedingID": len(st.session_state.demo_feeding) + 1,
                    "PondID": sel_pond,
                    "FeedingDate": f_date.strftime("%Y-%m-%d"),
                    "FeedType": feed_type,
                    "FeedBrand": brand,
                    "BiomassKg": 2500.0,
                    "FeedingRatePercent": 3.0,
                    "NumberOfFeedings": int(feedings_count),
                    "RecommendedFeedKg": float(actual_kg),
                    "ActualFeedKg": float(actual_kg),
                    "FeedCostPerKg": float(cost_per_kg),
                    "TotalFeedCost": total_cost,
                    "WeatherCondition": "Normal",
                    "FishBehaviour": "Surface feeding",
                    "FeedResponse": response,
                    "Remarks": remarks.strip(),
                    "Notes": remarks.strip()
                }
                st.session_state.demo_feeding.append(new_feed)
                st.success(_lbl(
                    lang,
                    f"Recorded {actual_kg} kg feeding for {sel_pond} (Cost: ₹{total_cost:,.0f}).",
                    f"{sel_pond} కోసం {actual_kg} కేజీ మేత నమోదైంది (ఖర్చు: ₹{total_cost:,.0f})."
                ))
                st.rerun()

    _render()


def dialog_add_incident():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Record Health / Incident Observation", "ఆరోగ్యం / సంఘటన పరిశీలన నమోదు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Record unusual pond observations, health events, or dead fish counts. Non-diagnostic.",
            "అసాధారణ చెరువు పరిశీలనలు, ఆరోగ్య సంఘటనలు లేదా మరణాల సంఖ్యను నమోదు చేయండి (వైద్య నిర్ధారణ కాదు)."
        ))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_incident_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Pond *", "చెరువు *"), options=pond_ids)
                inc_date = st.date_input(_lbl(lang, "Incident Date", "సంఘటన తేదీ"), value=date.today())
                inc_type = st.selectbox(
                    _lbl(lang, "Incident Category", "సంఘటన విభాగం"),
                    options=["Mortality", "Unusual Behaviour", "Water Condition Issue", "Equipment Breakdown", "Predator Sighting", "Other"],
                    format_func=lambda x: tv(x, lang)
                )
                dead_count = st.number_input(_lbl(lang, "Number of Dead Fish", "చనిపోయిన చేపల సంఖ్య"), min_value=0, value=5, step=1)
                severity = st.selectbox(
                    _lbl(lang, "Severity Level", "తీవ్రత స్థాయి"),
                    options=["INFO", "WARNING", "HIGH"],
                    index=1,
                    format_func=lambda x: tv(x, lang)
                )
            with col2:
                observed_beh = st.text_input(_lbl(lang, "Observed Fish Behaviour", "గమనించిన చేపల ప్రవర్తన"), placeholder=_lbl(lang, "e.g. Sluggish surface gathering at dawn", "ఉదా. తెల్లవారుజామున ఉపరితలం వద్ద మందకొడిగా ఉండటం"))
                visible_sym = st.text_input(_lbl(lang, "Visible Sample Symptoms", "కనిపించే లక్షణాలు"), placeholder=_lbl(lang, "e.g. Flared gills, no external lesions", "ఉదా. మొప్పలు తెరిచి ఉండటం"))
                action_taken = st.text_input(_lbl(lang, "Action Taken", "తీసుకున్న చర్య"), placeholder=_lbl(lang, "e.g. Started emergency aerator for 3 hours", "ఉదా. 3 గంటల పాటు అత్యవసర ఏరేటర్ నడిపాము"))
                status = st.selectbox(
                    _lbl(lang, "Status", "స్థితి"),
                    options=["Open", "Monitoring", "Resolved"],
                    index=1,
                    format_func=lambda x: tv(x, lang)
                )

            desc = st.text_area(_lbl(lang, "Detailed Description", "వివరణాత్మక నివేదిక"), placeholder=_lbl(lang, "Cloudy morning with low dissolved oxygen observed...", "మేఘావృతమైన ఉదయం తక్కువ ఆక్సిజన్ గమనించబడింది..."))
            submitted = st.form_submit_button(_lbl(lang, "Save Incident Record", "సంఘటన రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                new_inc = {
                    "IncidentID": len(st.session_state.demo_incidents) + 1,
                    "PondID": sel_pond,
                    "Date": inc_date.strftime("%Y-%m-%d"),
                    "Time": "07:00:00",
                    "IncidentType": inc_type,
                    "NumberAffected": int(dead_count),
                    "ObservedBehaviour": observed_beh.strip(),
                    "VisibleObservation": visible_sym.strip(),
                    "WaterCondition": "Monitored",
                    "WeatherCondition": "Cloudy",
                    "Severity": severity,
                    "Description": desc.strip(),
                    "ActionTaken": action_taken.strip(),
                    "FollowUpDate": (inc_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "Status": status,
                    "Notes": "Incident logged via Quick Action."
                }
                st.session_state.demo_incidents.append(new_inc)
                if dead_count > 0:
                    st.session_state.demo_mortality.append({
                        "IncidentID": new_inc["IncidentID"],
                        "PondID": sel_pond,
                        "IncidentDate": inc_date.strftime("%Y-%m-%d"),
                        "NumberOfDead": int(dead_count),
                        "EstimatedMortalityPercent": 0.05,
                        "ObservedBehaviour": observed_beh.strip(),
                        "VisibleSymptoms": visible_sym.strip(),
                        "WaterCondition": "Monitored",
                        "Remarks": action_taken.strip(),
                        "PhotoPath": None
                    })
                st.success(_lbl(lang, f"Incident recorded for {sel_pond}. Verify water parameters and aeration.", f"{sel_pond} కోసం సంఘటన నమోదైంది. నీటి నాణ్యత మరియు ఏరేషన్ తనిఖీ చేయండి."))
                st.rerun()

    _render()


def dialog_add_expense():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Add Operational Expense", "నిర్వహణ ఖర్చును జోడించు"))
    def _render():
        st.caption(_lbl(
            lang,
            "Record operational expenditures categorized by pond and domain.",
            "చెరువు మరియు విభాగం వారీగా నిర్వహణ ఖర్చులను నమోదు చేయండి."
        ))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Pond", "చెరువు"), options=pond_ids)
                exp_date = st.date_input(_lbl(lang, "Date", "తేదీ"), value=date.today())
                category = st.selectbox(_lbl(lang, "Expense Category", "ఖర్చు విభాగం"), options=EXPENSE_CATEGORIES, format_func=lambda x: tv(x, lang))
            with col2:
                amount = st.number_input(_lbl(lang, "Amount (₹) *", "మొత్తం (₹) *"), min_value=1.0, value=5000.0, step=500.0)
                desc = st.text_input(_lbl(lang, "Description *", "వివరణ *"), placeholder=_lbl(lang, "e.g. 10 bags feed pellets / Power bill", "ఉదా. 10 బస్తాల మేత / విద్యుత్ బిల్లు"))
                quantity = st.number_input(_lbl(lang, "Quantity (Optional)", "పరిమాణం (ఐచ్ఛికం)"), min_value=0.0, value=1.0, step=1.0)

            notes = st.text_input(_lbl(lang, "Voucher / Payment Notes", "చెల్లింపు గమనికలు"), placeholder=_lbl(lang, "Paid via UPI / Cash voucher #42", "UPI / నగదు వోచర్ #42 ద్వారా చెల్లింపు"))
            submitted = st.form_submit_button(_lbl(lang, "Save Expense", "ఖర్చును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                if not desc:
                    st.error(_lbl(lang, "Please provide a description.", "దయచేసి వివరణ నమోదు చేయండి."))
                else:
                    new_exp = {
                        "ExpenseID": len(st.session_state.demo_expenses) + 1,
                        "PondID": sel_pond,
                        "ExpenseDate": exp_date.strftime("%Y-%m-%d"),
                        "Category": category,
                        "Description": desc.strip(),
                        "Quantity": float(quantity),
                        "Amount": float(amount),
                        "Notes": notes.strip()
                    }
                    st.session_state.demo_expenses.append(new_exp)
                    st.success(_lbl(lang, f"Expense of ₹{amount:,.0f} ({category}) added for {sel_pond}.", f"{sel_pond} కోసం ₹{amount:,.0f} ఖర్చు జోడించబడింది."))
                    st.rerun()

    _render()


def dialog_add_sale():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Record Fish Sale", "చేపల అమ్మకం నమోదు"))
    def _render():
        st.caption(_lbl(lang, "Record fish commercial sales and revenue.", "చేపల వాణిజ్య అమ్మకాలు మరియు ఆదాయాన్ని నమోదు చేయండి."))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_sale_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Harvest Pond *", "చెరువు *"), options=pond_ids)
                species = st.selectbox(_lbl(lang, "Species Sold", "అమ్మిన చేప జాతి"), options=SPECIES_LIST)
                s_date = st.date_input(_lbl(lang, "Sale Date", "అమ్మకం తేదీ"), value=date.today())
                qty_kg = st.number_input(_lbl(lang, "Total Quantity Sold (kg) *", "అమ్మిన పరిమాణం (కేజీ) *"), min_value=1.0, value=500.0, step=50.0)
            with col2:
                price_kg = st.number_input(_lbl(lang, "Selling Price per kg (₹) *", "కేజీ అమ్మకం ధర (₹) *"), min_value=1.0, value=160.0, step=5.0)
                buyer = st.text_input(_lbl(lang, "Buyer / Market Name *", "కొనుగోలుదారు / మార్కెట్ పేరు *"), placeholder=_lbl(lang, "e.g. Bhimavaram Wholesale Market", "ఉదా. భీమవరం హోల్‌సేల్ మార్కెట్"))
                transport = st.number_input(_lbl(lang, "Transport Deduction (₹)", "రవాణా తగ్గింపు (₹)"), min_value=0.0, value=1500.0, step=100.0)
                payment_status = st.selectbox(
                    _lbl(lang, "Payment Status", "చెల్లింపు స్థితి"),
                    options=["Paid", "Partial", "Pending"],
                    index=0,
                    format_func=lambda x: tv(x, lang)
                )

            notes = st.text_input(_lbl(lang, "Sale Notes", "అమ్మకం గమనికలు"), placeholder=_lbl(lang, "First selective harvest of Catla grade A.", "మొదటి కట్లా గ్రేడ్ A పంట అమ్మకం."))
            submitted = st.form_submit_button(_lbl(lang, "Save Sale Record", "అమ్మకం రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                total_rev = round(float(qty_kg) * float(price_kg), 2)
                new_sale = {
                    "SaleID": len(st.session_state.demo_sales) + 1,
                    "PondID": sel_pond,
                    "SaleDate": s_date.strftime("%Y-%m-%d"),
                    "Species": species,
                    "QuantitySoldKg": float(qty_kg),
                    "PricePerKg": float(price_kg),
                    "TotalRevenue": total_rev,
                    "BuyerMarket": buyer.strip() if buyer else "Local Market",
                    "TransportCost": float(transport),
                    "PaymentStatus": payment_status,
                    "PaymentDate": s_date.strftime("%Y-%m-%d"),
                    "Notes": notes.strip()
                }
                st.session_state.demo_sales.append(new_sale)
                st.success(_lbl(lang, f"Recorded sale of {qty_kg} kg {species} (Revenue: ₹{total_rev:,.0f}).", f"{qty_kg} కేజీ {species} అమ్మకం నమోదైంది (ఆదాయం: ₹{total_rev:,.0f})."))
                st.rerun()

    _render()


def dialog_record_harvest():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Record Fish Harvest", "చేపల పంట కోత నమోదు"))
    def _render():
        st.caption(_lbl(lang, "Record commercial fish harvests (partial or final pond harvests).", "చెరువు పాక్షిక లేదా పూర్తి పంట కోత వివరాలను నమోదు చేయండి."))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_record_harvest_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Pond *", "చెరువు *"), options=pond_ids)
                h_date = st.date_input(_lbl(lang, "Harvest Date", "కోత తేదీ"), value=date.today())
                species = st.selectbox(_lbl(lang, "Harvested Species *", "కోత జాతి *"), options=SPECIES_LIST)
                qty_fish = st.number_input(_lbl(lang, "Quantity Harvested (Fish Count)", "కోత చేపల సంఖ్య"), min_value=1, value=500, step=50)
                avg_weight = st.number_input(_lbl(lang, "Average Weight (grams)", "సగటు బరువు (గ్రా.)"), min_value=10.0, value=1200.0, step=50.0)
            with col2:
                total_weight = st.number_input(_lbl(lang, "Total Weight (kg) *", "మొత్తం బరువు (కేజీ) *"), min_value=1.0, value=600.0, step=50.0)
                method = st.selectbox(_lbl(lang, "Harvest Method", "కోత పద్ధతి"), options=["Dragnet", "Cast Net", "Pond Drainage", "Partial Seining"], index=0, format_func=lambda x: tv(x, lang))
                grade = st.selectbox(_lbl(lang, "Grade / Quality", "గ్రేడ్ / నాణ్యత"), options=["Commercial Grade A", "Commercial Grade B", "Mixed"], index=0, format_func=lambda x: tv(x, lang))
                buyer = st.text_input(_lbl(lang, "Buyer / Merchant", "కొనుగోలుదారు / వ్యాపారి"), placeholder="e.g. Godavari Aqua Traders")
                price_kg = st.number_input(_lbl(lang, "Price per kg (₹)", "కేజీ ధర (₹)"), min_value=1.0, value=165.0, step=5.0)

            c3, c4 = st.columns(2)
            with c3:
                transport_cost = st.number_input(_lbl(lang, "Transport Cost (₹)", "రవాణా ఖర్చు (₹)"), min_value=0.0, value=1200.0, step=100.0)
            with c4:
                labour_cost = st.number_input(_lbl(lang, "Harvest Labour Cost (₹)", "కోత కూలీ ఖర్చు (₹)"), min_value=0.0, value=2500.0, step=200.0)

            notes = st.text_input(_lbl(lang, "Harvest Remarks", "కోత గమనికలు"), placeholder=_lbl(lang, "Partial thinning harvest to reduce density.", "సాంద్రత తగ్గించడానికి పాక్షిక పంట కోత."))
            submitted = st.form_submit_button(_lbl(lang, "Save Harvest Record", "కోత రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                revenue = round(float(total_weight) * float(price_kg), 2)
                record = {
                    "PondID": sel_pond,
                    "Date": h_date.strftime("%Y-%m-%d"),
                    "Species": species,
                    "QuantityHarvestedFish": int(qty_fish),
                    "AverageWeightGrams": float(avg_weight),
                    "TotalWeightKg": float(total_weight),
                    "HarvestMethod": method,
                    "Grade": grade,
                    "Buyer": buyer.strip(),
                    "PricePerKg": float(price_kg),
                    "TotalRevenue": revenue,
                    "TransportCost": float(transport_cost),
                    "LabourCost": float(labour_cost),
                    "OtherCosts": 0.0,
                    "Notes": notes.strip()
                }
                save_harvest_record(record)
                st.success(_lbl(lang, f"Harvest of {total_weight:,.0f} kg {species} recorded for {sel_pond} (Revenue: ₹{revenue:,.0f}).", f"{sel_pond} కోసం {total_weight:,.0f} కేజీ {species} కోత నమోదైంది (ఆదాయం: ₹{revenue:,.0f})."))
                st.rerun()

    _render()


def dialog_add_maintenance():
    lang = st.session_state.get("lang", "en")

    @st.dialog(_lbl(lang, "Add Maintenance Record", "నిర్వహణ రికార్డును జోడించు"))
    def _render():
        st.caption(_lbl(lang, "Record pond or equipment maintenance, servicing, and repairs.", "చెరువు లేదా పరికరాల నిర్వహణ, సర్వీసింగ్ మరియు మరమ్మతులను నమోదు చేయండి."))
        pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
        with st.form("quick_add_maintenance_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sel_pond = st.selectbox(_lbl(lang, "Pond (Optional)", "చెరువు (ఐచ్ఛికం)"), options=["General Farm"] + pond_ids, format_func=lambda x: tv(x, lang))
                m_date = st.date_input(_lbl(lang, "Maintenance Date", "నిర్వహణ తేదీ"), value=date.today())
                m_type = st.selectbox(
                    _lbl(lang, "Maintenance Domain", "నిర్వహణ విభాగం"),
                    options=[
                        "Aerator Servicing",
                        "Pump Repair",
                        "Pipe & Sluice Maintenance",
                        "Electrical System",
                        "Embankment / Dyke Repair",
                        "Drainage Canal Desilting",
                        "Netting / Bird Fencing",
                        "Cleaning & Disinfection",
                        "Other"
                    ],
                    format_func=lambda x: tv(x, lang)
                )
                cost = st.number_input(_lbl(lang, "Cost (₹)", "ఖర్చు (₹)"), min_value=0.0, value=1500.0, step=200.0)
            with col2:
                asset = st.text_input(_lbl(lang, "Asset / Equipment Name *", "పరికరం / ఆస్తి పేరు *"), placeholder=_lbl(lang, "e.g. 2HP Paddlewheel Aerator #2", "ఉదా. 2HP పాడిల్‌వీల్ ఏరేటర్ #2"))
                person = st.text_input(_lbl(lang, "Technician / Contractor", "టెక్నీషియన్ / కాంట్రాక్టర్"), placeholder="e.g. Srikanth Electricals")
                status = st.selectbox(_lbl(lang, "Status", "స్థితి"), options=["Completed", "In Progress", "Scheduled"], index=0, format_func=lambda x: tv(x, lang))
                next_date = st.date_input(_lbl(lang, "Next Scheduled Service", "తదుపరి సర్వీస్ తేదీ"), value=date.today() + timedelta(days=90))

            desc = st.text_area(_lbl(lang, "Work Description", "పని వివరణ"), placeholder=_lbl(lang, "Oil seal replaced and motor greased. Tested run for 30 minutes.", "ఆయిల్ సీల్ మార్చబడింది మరియు మోటార్ గ్రీజింగ్ చేయబడింది."))
            submitted = st.form_submit_button(_lbl(lang, "Save Maintenance Record", "నిర్వహణ రికార్డును సేవ్ చేయండి"), type="primary", use_container_width=True)
            if submitted:
                if not asset:
                    st.error(_lbl(lang, "Please enter asset or equipment name.", "దయచేసి పరికరం లేదా ఆస్తి పేరును నమోదు చేయండి."))
                else:
                    record = {
                        "Date": m_date.strftime("%Y-%m-%d"),
                        "PondID": sel_pond if sel_pond != "General Farm" else None,
                        "Asset": asset.strip(),
                        "MaintenanceType": m_type,
                        "Description": desc.strip(),
                        "Cost": float(cost),
                        "Person": person.strip(),
                        "Status": status,
                        "NextMaintenance": next_date.strftime("%Y-%m-%d"),
                        "Notes": "Logged via Quick Action"
                    }
                    save_maintenance_record(record)
                    st.success(_lbl(lang, f"Maintenance record for {asset} saved.", f"{asset} కోసం నిర్వహణ రికార్డు సేవ్ చేయబడింది."))
                    st.rerun()

    _render()
