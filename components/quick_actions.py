"""
AquaMitra Quick Action Modals
Interactive dialog forms for immediate record entry across all core operations.
Updates session state and live database in real-time with zero dead-end buttons.
Strictly zero emojis.
"""

from datetime import date, datetime, timedelta
import streamlit as st
from utils.constants import POND_TYPES, AREA_UNITS, WATER_SOURCES, SPECIES_LIST, EXPENSE_CATEGORIES
from utils.calculations import calculate_initial_biomass
from database.queries import (
    save_fish_stock,
    get_fish_stocks,
    save_harvest_record,
    save_maintenance_record,
    update_pond_record
)


@st.dialog("Add New Fishery Pond")
def dialog_add_pond():
    st.caption("Register a new aquaculture pond into the farm system.")
    with st.form("quick_add_pond_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            p_id = st.text_input("Pond ID *", value=f"P-00{len(st.session_state.demo_ponds)+1}", placeholder="e.g. P-004")
            p_name = st.text_input("Pond Name *", placeholder="e.g. Surya Sunrise Pond")
            location = st.text_input("Location *", placeholder="e.g. West Godavari, Sector C")
            area = st.number_input("Pond Area *", min_value=0.1, value=2.0, step=0.1)
            area_unit = st.selectbox("Area Unit", options=AREA_UNITS, index=0)
        with col2:
            p_type = st.selectbox("Pond Type", options=POND_TYPES, index=0)
            water_source = st.selectbox("Water Source", options=WATER_SOURCES, index=0)
            depth = st.number_input("Average Depth (meters)", min_value=0.5, value=1.6, step=0.1)
            owner = st.text_input("Owner / Manager", value="Ramesh Varma")
            status = st.selectbox("Initial Status", options=["Active", "Preparing", "Maintenance"], index=0)

        notes = st.text_area("Pond Remarks / Soil Characteristics", placeholder="Compacted clay bottom with inlet screen...")
        
        submitted = st.form_submit_button("Save Pond Record", type="primary", use_container_width=True)
        if submitted:
            if not p_name or not p_id:
                st.error("Please enter a valid Pond ID and Pond Name.")
            elif any(p["PondID"] == p_id.strip() for p in st.session_state.demo_ponds):
                st.error(f"Pond ID '{p_id}' already exists. Please choose a unique ID.")
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
                st.success(f"Pond {p_id} ({p_name}) added successfully.")
                st.rerun()


@st.dialog("Edit Pond Profile")
def dialog_edit_pond(pond_id: str):
    pond = next((p for p in st.session_state.demo_ponds if p["PondID"] == pond_id), None)
    if not pond:
        st.error(f"Pond {pond_id} not found.")
        return

    st.caption(f"Update attributes and specifications for {pond_id} ({pond.get('PondName', '')}).")
    with st.form(f"edit_pond_form_{pond_id}"):
        c1, c2 = st.columns(2)
        with c1:
            p_name = st.text_input("Pond Name *", value=pond.get("PondName", ""))
            location = st.text_input("Location", value=pond.get("Location", ""))
            area = st.number_input("Area", min_value=0.1, value=float(pond.get("Area", 2.0)), step=0.1)
            area_unit = st.selectbox("Area Unit", options=AREA_UNITS, index=AREA_UNITS.index(pond.get("AreaUnit", "Acres")) if pond.get("AreaUnit") in AREA_UNITS else 0)
            avg_depth = st.number_input("Average Depth (m)", min_value=0.5, value=float(pond.get("AvgDepthMeters", 1.5)), step=0.1)
            max_depth = st.number_input("Max Depth (m)", min_value=0.5, value=float(pond.get("MaxDepthMeters", 2.0)), step=0.1)
        with c2:
            status = st.selectbox("Status", options=["Active", "Inactive", "Maintenance", "Preparing", "Harvested"], index=["Active", "Inactive", "Maintenance", "Preparing", "Harvested"].index(pond.get("Status", "Active")) if pond.get("Status") in ["Active", "Inactive", "Maintenance", "Preparing", "Harvested"] else 0)
            p_type = st.selectbox("Pond Type", options=POND_TYPES, index=POND_TYPES.index(pond.get("PondType", "Earthen")) if pond.get("PondType") in POND_TYPES else 0)
            water_src = st.selectbox("Water Source", options=WATER_SOURCES, index=WATER_SOURCES.index(pond.get("WaterSource", "Canal")) if pond.get("WaterSource") in WATER_SOURCES else 0)
            soil_type = st.text_input("Soil Type", value=pond.get("SoilType", "Clayey Loam"))
            owner = st.text_input("Owner / Manager", value=pond.get("Owner", "Ramesh Varma"))

        notes = st.text_area("Operational Notes", value=pond.get("Notes", ""))
        
        submitted = st.form_submit_button("Update Pond Record", type="primary", use_container_width=True)
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
            st.success(f"Pond {pond_id} updated successfully.")
            st.rerun()


@st.dialog("Log Water Quality Observation")
def dialog_add_water_reading():
    st.caption("Record routine water parameter observations. Missing parameters can be left empty.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_water_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            sel_pond = st.selectbox("Pond *", options=pond_ids)
            r_date = st.date_input("Date", value=date.today())
            r_time = st.time_input("Time", value=datetime.now().time())
        with col2:
            ph = st.number_input("pH (0 - 14)", min_value=0.0, max_value=14.0, value=7.5, step=0.1)
            temp = st.number_input("Temperature (°C)", min_value=10.0, max_value=45.0, value=28.5, step=0.5)
            do = st.number_input("Dissolved Oxygen (mg/L)", min_value=0.0, max_value=20.0, value=6.2, step=0.1)
        with col3:
            turb = st.number_input("Turbidity (NTU)", min_value=0.0, value=28.0, step=1.0)
            nh3 = st.number_input("Ammonia NH3 (mg/L)", min_value=0.0, value=0.01, step=0.005, format="%.3f")
            level = st.number_input("Water Level (m)", min_value=0.5, value=1.65, step=0.05)

        notes = st.text_input("Observation Notes", placeholder="Clear morning sunshine; aerator run for 2 hours prior.")
        submitted = st.form_submit_button("Save Water Observation", type="primary", use_container_width=True)
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
            st.success(f"Water observation for {sel_pond} recorded.")
            st.rerun()


@st.dialog("Record Fish Stocking Batch")
def dialog_add_fish_stock():
    st.caption("Log a new fish fingerling stocking batch into a pond.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_stock_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Stocking Pond *", options=pond_ids)
            species = st.selectbox("Species *", options=SPECIES_LIST)
            variety = st.text_input("Variety / Strain", placeholder="e.g. Jayanti Rohu, GIFT Tilapia")
            s_date = st.date_input("Stocking Date", value=date.today())
            num_fish = st.number_input("Number of Fingerlings *", min_value=100, value=3000, step=500)
        with col2:
            avg_weight = st.number_input("Average Initial Weight (grams) *", min_value=1.0, value=45.0, step=5.0)
            hatchery = st.text_input("Hatchery / Source", placeholder="e.g. Godavari Royal Hatchery")
            price_per_fish = st.number_input("Price per Fish (₹)", min_value=0.1, value=3.0, step=0.25)
            transport_cost = st.number_input("Transport Cost (₹)", min_value=0.0, value=1200.0, step=100.0)

        remarks = st.text_input("Stocking Remarks", placeholder="Saline dip bath given; released in surface water.")
        submitted = st.form_submit_button("Save Stocking Record", type="primary", use_container_width=True)
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
            saved = save_fish_stock(new_stock)
            st.success(f"Stocking batch for {sel_pond} recorded: {num_fish:,} {species} ({calculated_biomass:,.1f} kg biomass).")
            st.rerun()


@st.dialog("Record Fish Growth Sampling")
def dialog_add_growth_sample():
    st.caption("Record random cast-net sample observations to update estimated biomass.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_growth_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Sampled Pond *", options=pond_ids)
            sample_date = st.date_input("Sampling Date", value=date.today())
            sample_size = st.number_input("Sample Count (Fish Sampled)", min_value=5, value=25, step=5)
        with col2:
            avg_weight = st.number_input("Average Weight (grams) *", min_value=1.0, value=480.0, step=10.0)
            min_weight = st.number_input("Minimum Observed Weight (grams)", min_value=1.0, value=420.0, step=10.0)
            max_weight = st.number_input("Maximum Observed Weight (grams)", min_value=1.0, value=540.0, step=10.0)

        # Species lookup safely from pond stocks
        p_stocks = get_fish_stocks(pond_id=sel_pond)
        species_label = p_stocks[0].get("Species", "Sampled Fish") if p_stocks else "Sampled Fish"
        total_fish_count = sum(s.get("NumberOfFish", 0) for s in p_stocks) or 5000

        notes = st.text_input("Sampling Notes", placeholder="Healthy vigor, clear body shine, active feeding observed.")
        submitted = st.form_submit_button("Save Growth Observation", type="primary", use_container_width=True)
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
            st.success(f"Growth recorded for {sel_pond}: {avg_weight} g average weight. Estimated biomass: {est_biomass:,.0f} kg.")
            st.rerun()


@st.dialog("Record Daily Feed Application")
def dialog_add_feeding():
    st.caption("Record feed applied to a pond and assess fish feeding vigor.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_feed_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Feeding Pond *", options=pond_ids)
            f_date = st.date_input("Feeding Date", value=date.today())
            feed_type = st.selectbox("Feed Type", options=["Pellet (32% Protein)", "Floating Pellet (28%)", "Sinking Pellet (24%)", "Mash / Rice Bran Mix", "Other"])
            brand = st.selectbox("Feed Brand", options=["Godrej Aquafeed", "CP Aqua Classic", "Avanti Feeds", "Farm Mix"], index=0)
        with col2:
            actual_kg = st.number_input("Feed Given (kg) *", min_value=1.0, value=75.0, step=5.0)
            cost_per_kg = st.number_input("Feed Cost per kg (₹)", min_value=10.0, value=48.0, step=1.0)
            feedings_count = st.number_input("Number of Feedings Today", min_value=1, max_value=6, value=2)
            response = st.selectbox("Feed Response / Tray Check", options=["Good (Clean feeding tray)", "Moderate (Little left)", "Poor (Excess feed remaining)"], index=0)

        remarks = st.text_input("Feeding Notes", placeholder="Fed at 07:30 AM and 04:30 PM. Active response.")
        submitted = st.form_submit_button("Save Feed Record", type="primary", use_container_width=True)
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
            st.success(f"Recorded {actual_kg} kg feeding for {sel_pond} (Cost: ₹{total_cost:,.0f}).")
            st.rerun()


@st.dialog("Record Health / Incident Observation")
def dialog_add_incident():
    st.caption("Record unusual pond observations, health events, or dead fish counts. Non-diagnostic.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_incident_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Pond *", options=pond_ids)
            inc_date = st.date_input("Incident Date", value=date.today())
            inc_type = st.selectbox("Incident Category", options=["Mortality", "Unusual Behaviour", "Water Condition Issue", "Equipment Breakdown", "Predator Sighting", "Other"])
            dead_count = st.number_input("Number of Dead Fish", min_value=0, value=5, step=1)
            severity = st.selectbox("Severity Level", options=["INFO", "WARNING", "HIGH"], index=1)
        with col2:
            observed_beh = st.text_input("Observed Fish Behaviour", placeholder="e.g. Sluggish surface gathering at dawn")
            visible_sym = st.text_input("Visible Sample Symptoms", placeholder="e.g. Flared gills, no external lesions")
            action_taken = st.text_input("Action Taken", placeholder="e.g. Started emergency aerator for 3 hours")
            status = st.selectbox("Status", options=["Open", "Monitoring", "Resolved"], index=1)

        desc = st.text_area("Detailed Description", placeholder="Cloudy morning with low dissolved oxygen observed...")
        submitted = st.form_submit_button("Save Incident Record", type="primary", use_container_width=True)
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
            st.success(f"Incident recorded for {sel_pond}. Verify water parameters and aeration.")
            st.rerun()


@st.dialog("Add Operational Expense")
def dialog_add_expense():
    st.caption("Record operational expenditures categorized by pond and domain.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Pond", options=pond_ids)
            exp_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Expense Category", options=EXPENSE_CATEGORIES)
        with col2:
            amount = st.number_input("Amount (₹) *", min_value=1.0, value=5000.0, step=500.0)
            desc = st.text_input("Description *", placeholder="e.g. 10 bags feed pellets / Power bill")
            quantity = st.number_input("Quantity (Optional)", min_value=0.0, value=1.0, step=1.0)

        notes = st.text_input("Voucher / Payment Notes", placeholder="Paid via UPI / Cash voucher #42")
        submitted = st.form_submit_button("Save Expense", type="primary", use_container_width=True)
        if submitted:
            if not desc:
                st.error("Please provide a description.")
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
                st.success(f"Expense of ₹{amount:,.0f} ({category}) added for {sel_pond}.")
                st.rerun()


@st.dialog("Record Fish Sale")
def dialog_add_sale():
    st.caption("Record fish commercial sales and revenue.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_sale_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Harvest Pond *", options=pond_ids)
            species = st.selectbox("Species Sold", options=SPECIES_LIST)
            s_date = st.date_input("Sale Date", value=date.today())
            qty_kg = st.number_input("Total Quantity Sold (kg) *", min_value=1.0, value=500.0, step=50.0)
        with col2:
            price_kg = st.number_input("Selling Price per kg (₹) *", min_value=1.0, value=160.0, step=5.0)
            buyer = st.text_input("Buyer / Market Name *", placeholder="e.g. Bhimavaram Wholesale Market")
            transport = st.number_input("Transport Deduction (₹)", min_value=0.0, value=1500.0, step=100.0)
            payment_status = st.selectbox("Payment Status", options=["Paid", "Partial", "Pending"], index=0)

        notes = st.text_input("Sale Notes", placeholder="First selective harvest of Catla grade A.")
        submitted = st.form_submit_button("Save Sale Record", type="primary", use_container_width=True)
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
            st.success(f"Recorded sale of {qty_kg} kg {species} (Revenue: ₹{total_rev:,.0f}).")
            st.rerun()


@st.dialog("Record Fish Harvest")
def dialog_record_harvest():
    st.caption("Record commercial fish harvests (partial or final pond harvests).")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_record_harvest_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Pond *", options=pond_ids)
            h_date = st.date_input("Harvest Date", value=date.today())
            species = st.selectbox("Harvested Species *", options=SPECIES_LIST)
            qty_fish = st.number_input("Quantity Harvested (Fish Count)", min_value=1, value=500, step=50)
            avg_weight = st.number_input("Average Weight (grams)", min_value=10.0, value=1200.0, step=50.0)
        with col2:
            total_weight = st.number_input("Total Weight (kg) *", min_value=1.0, value=600.0, step=50.0)
            method = st.selectbox("Harvest Method", options=["Dragnet", "Cast Net", "Pond Drainage", "Partial Seining"], index=0)
            grade = st.selectbox("Grade / Quality", options=["Commercial Grade A", "Commercial Grade B", "Mixed"], index=0)
            buyer = st.text_input("Buyer / Merchant", placeholder="e.g. Godavari Aqua Traders")
            price_kg = st.number_input("Price per kg (₹)", min_value=1.0, value=165.0, step=5.0)

        c3, c4 = st.columns(2)
        with c3:
            transport_cost = st.number_input("Transport Cost (₹)", min_value=0.0, value=1200.0, step=100.0)
        with c4:
            labour_cost = st.number_input("Harvest Labour Cost (₹)", min_value=0.0, value=2500.0, step=200.0)

        notes = st.text_input("Harvest Remarks", placeholder="Partial thinning harvest to reduce density.")
        submitted = st.form_submit_button("Save Harvest Record", type="primary", use_container_width=True)
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
            st.success(f"Harvest of {total_weight:,.0f} kg {species} recorded for {sel_pond} (Revenue: ₹{revenue:,.0f}).")
            st.rerun()


@st.dialog("Add Maintenance Record")
def dialog_add_maintenance():
    st.caption("Record pond or equipment maintenance, servicing, and repairs.")
    pond_ids = [p["PondID"] for p in st.session_state.demo_ponds]
    with st.form("quick_add_maintenance_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sel_pond = st.selectbox("Pond (Optional)", options=["General Farm"] + pond_ids)
            m_date = st.date_input("Maintenance Date", value=date.today())
            m_type = st.selectbox("Maintenance Domain", options=[
                "Aerator Servicing",
                "Pump Repair",
                "Pipe & Sluice Maintenance",
                "Electrical System",
                "Embankment / Dyke Repair",
                "Drainage Canal Desilting",
                "Netting / Bird Fencing",
                "Cleaning & Disinfection",
                "Other"
            ])
            cost = st.number_input("Cost (₹)", min_value=0.0, value=1500.0, step=200.0)
        with col2:
            asset = st.text_input("Asset / Equipment Name *", placeholder="e.g. 2HP Paddlewheel Aerator #2")
            person = st.text_input("Technician / Contractor", placeholder="e.g. Srikanth Electricals")
            status = st.selectbox("Status", options=["Completed", "In Progress", "Scheduled"], index=0)
            next_date = st.date_input("Next Scheduled Service", value=date.today() + timedelta(days=90))

        desc = st.text_area("Work Description", placeholder="Oil seal replaced and motor greased. Tested run for 30 minutes.")
        submitted = st.form_submit_button("Save Maintenance Record", type="primary", use_container_width=True)
        if submitted:
            if not asset:
                st.error("Please enter asset or equipment name.")
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
                st.success(f"Maintenance record for {asset} saved.")
                st.rerun()
