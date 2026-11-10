"""
AquaMitra Comprehensive Demonstration Datasets & State Engine
Provides rich pre-populated records across all 18 modules for 100% functional offline use.
Supports complete manual CRUD (Add, View, Edit, Delete) in session state.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd


def get_demo_farm_profile() -> Dict[str, Any]:
    return {
        "FarmName": "Godavari Aqua Greens Farm",
        "OwnerName": "Ramesh Varma",
        "MobileNumber": "+91 98480 12345",
        "Village": "Undi",
        "Mandal": "Undi Mandal",
        "District": "West Godavari",
        "State": "Andhra Pradesh",
        "PINCode": "534199",
        "FarmAddress": "Survey No. 142/B, Kolleru Road, Undi",
        "FarmType": "Commercial Freshwater Semi-Intensive",
        "TotalFarmArea": 7.0,
        "AreaUnit": "Acres",
        "NumberOfPonds": 3,
        "PrimarySpecies": "Rohu, Catla, GIFT Tilapia",
        "WaterSource": "Godavari Canal & Deep Borewell",
        "DateStarted": "2024-03-15",
        "Notes": "Community-focused sustainable fishery adhering to standard BMP (Better Management Practices)."
    }


def get_demo_species() -> List[Dict[str, Any]]:
    return [
        {"SpeciesID": 1, "SpeciesName": "Rohu", "ScientificName": "Labeo rohita", "LocalName": "Rohu", "TeluguName": "రోహు (ఎర్రమీను)", "Category": "Major Carp", "DefaultFeedingRate": 3.0, "OptimalTempMin": 24.0, "OptimalTempMax": 32.0, "Active": True},
        {"SpeciesID": 2, "SpeciesName": "Catla", "ScientificName": "Gibelion catla", "LocalName": "Catla", "TeluguName": "బొచ్చె (కట్ల)", "Category": "Major Carp", "DefaultFeedingRate": 3.2, "OptimalTempMin": 25.0, "OptimalTempMax": 32.0, "Active": True},
        {"SpeciesID": 3, "SpeciesName": "Mrigal", "ScientificName": "Cirrhinus mrigala", "LocalName": "Mrigal", "TeluguName": "ఎర్రమోసు (మ్రిగాల్)", "Category": "Major Carp", "DefaultFeedingRate": 2.8, "OptimalTempMin": 24.0, "OptimalTempMax": 31.0, "Active": True},
        {"SpeciesID": 4, "SpeciesName": "Tilapia", "ScientificName": "Oreochromis niloticus", "LocalName": "GIFT Tilapia", "TeluguName": "తిలాపియా", "Category": "Cichlid", "DefaultFeedingRate": 3.5, "OptimalTempMin": 26.0, "OptimalTempMax": 33.0, "Active": True},
        {"SpeciesID": 5, "SpeciesName": "Pangasius", "ScientificName": "Pangasianodon hypophthalmus", "LocalName": "Basa / Panga", "TeluguName": "పంగాసియస్", "Category": "Catfish", "DefaultFeedingRate": 3.0, "OptimalTempMin": 26.0, "OptimalTempMax": 34.0, "Active": True},
        {"SpeciesID": 6, "SpeciesName": "Grass Carp", "ScientificName": "Ctenopharyngodon idella", "LocalName": "Grass Carp", "TeluguName": "గడ్డి చేప", "Category": "Exotic Carp", "DefaultFeedingRate": 4.0, "OptimalTempMin": 22.0, "OptimalTempMax": 30.0, "Active": True}
    ]


def get_demo_ponds() -> List[Dict[str, Any]]:
    return [
        {
            "PondID": "P-001",
            "PondName": "Green Valley Pond",
            "PondCode": "GVP-01",
            "Status": "Active",
            "Location": "East Godavari, Sector A",
            "Area": 2.50,
            "AreaUnit": "Acres",
            "LengthMeters": 140.0,
            "WidthMeters": 72.0,
            "AvgDepthMeters": 1.65,
            "MaxDepthMeters": 2.10,
            "WaterVolumeM3": 16600.0,
            "PondType": "Earthen",
            "WaterSource": "Canal",
            "WaterInlet": "6-inch PVC Sluice with Mesh Filter",
            "WaterOutlet": "Bottom Monk Drain with Screen",
            "WaterExchangeMethod": "Gravity & Diesel Pump",
            "SoilType": "Clayey Loam",
            "LiningType": "Natural Compacted Clay",
            "EmbankmentCondition": "Good (Vegetated with grass)",
            "BottomCondition": "De-silted prior to stocking",
            "Owner": "Ramesh Varma",
            "Manager": "K. Satyanarayana",
            "DateAdded": "2026-05-10",
            "LastRenovation": "2026-04-20",
            "Notes": "Primary freshwater composite culture pond (Rohu & Catla)."
        },
        {
            "PondID": "P-002",
            "PondName": "Krishna Aqua Pond",
            "PondCode": "KAP-02",
            "Status": "Active",
            "Location": "Krishna District, Sector 4",
            "Area": 3.00,
            "AreaUnit": "Acres",
            "LengthMeters": 160.0,
            "WidthMeters": 76.0,
            "AvgDepthMeters": 1.80,
            "MaxDepthMeters": 2.30,
            "WaterVolumeM3": 21800.0,
            "PondType": "Earthen",
            "WaterSource": "Borewell",
            "WaterInlet": "Submersible 10HP Pump line",
            "WaterOutlet": "Overflow spillway & side sluice",
            "WaterExchangeMethod": "Continuous supplementary aeration & pumping",
            "SoilType": "Sandy Clay Loam",
            "LiningType": "None (Earthen)",
            "EmbankmentCondition": "Recently compacted dyke",
            "BottomCondition": "Limed with 250kg Agricultural Lime",
            "Owner": "Suresh Babu",
            "Manager": "M. Venkat",
            "DateAdded": "2026-06-01",
            "LastRenovation": "2026-05-15",
            "Notes": "High-density GIFT Tilapia monoculture pond with paddlewheel aeration."
        },
        {
            "PondID": "P-003",
            "PondName": "Matsya Farm Pond",
            "PondCode": "MFP-03",
            "Status": "Maintenance",
            "Location": "West Godavari, Unit 2",
            "Area": 1.50,
            "AreaUnit": "Acres",
            "LengthMeters": 100.0,
            "WidthMeters": 60.0,
            "AvgDepthMeters": 1.50,
            "MaxDepthMeters": 1.90,
            "WaterVolumeM3": 9100.0,
            "PondType": "Lined",
            "WaterSource": "Rainfed & Canal",
            "WaterInlet": "Canal feeder channel",
            "WaterOutlet": "Central siphon drainage",
            "WaterExchangeMethod": "Batch draining",
            "SoilType": "Alluvial",
            "LiningType": "500 Micron HDPE Geomembrane",
            "EmbankmentCondition": "Lined perimeter slopes",
            "BottomCondition": "Currently dry for sun-drying and liner weld repairs",
            "Owner": "Lakshmi Narayana",
            "Manager": "P. Srinivas",
            "DateAdded": "2026-07-15",
            "LastRenovation": "2026-07-20",
            "Notes": "Lined nursery and transition pond undergoing liner inspection and valve maintenance."
        }
    ]


def get_demo_fish_stock() -> List[Dict[str, Any]]:
    return [
        {
            "StockID": 101,
            "PondID": "P-001",
            "Species": "Rohu",
            "Variety": "Jayanti Rohu (CIFA Strain)",
            "StockingDate": "2026-05-15",
            "NumberOfFish": 5000,
            "AvgInitialWeightGrams": 45.0,
            "TotalInitialBiomassKg": 225.0,
            "SourceHatchery": "Godavari Royal Hatcheries, Kovvur",
            "SourceLocation": "Kovvur, AP",
            "BatchNumber": "ROH-2026-05A",
            "SizeCategory": "Fingerling (3-4 inches)",
            "PricePerFish": 3.0,
            "TotalSeedCost": 15000.0,
            "TransportCost": 1500.0,
            "AcclimatizationNotes": "Tempered in oxygen bags for 45 mins; saline dip bath given prior to release.",
            "Notes": "Healthy uniform fingerlings.",
            "Remarks": "Healthy uniform fingerlings."
        },
        {
            "StockID": 102,
            "PondID": "P-001",
            "Species": "Catla",
            "Variety": "Riverine Broodstock F1",
            "StockingDate": "2026-05-15",
            "NumberOfFish": 3000,
            "AvgInitialWeightGrams": 55.0,
            "TotalInitialBiomassKg": 165.0,
            "SourceHatchery": "Godavari Royal Hatcheries, Kovvur",
            "SourceLocation": "Kovvur, AP",
            "BatchNumber": "CAT-2026-05A",
            "SizeCategory": "Fingerling (4-5 inches)",
            "PricePerFish": 3.5,
            "TotalSeedCost": 10500.0,
            "TransportCost": 1200.0,
            "AcclimatizationNotes": "Released in surface column early morning (06:30 AM).",
            "Notes": "Surface feeder batch stocked with Rohu for composite polyculture.",
            "Remarks": "Surface feeder batch stocked with Rohu for composite polyculture."
        },
        {
            "StockID": 103,
            "PondID": "P-002",
            "Species": "Tilapia",
            "Variety": "Genetically Improved Farmed Tilapia (GIFT)",
            "StockingDate": "2026-06-05",
            "NumberOfFish": 10000,
            "AvgInitialWeightGrams": 30.0,
            "TotalInitialBiomassKg": 300.0,
            "SourceHatchery": "Delta Aqua Hatchery, Vijayawada",
            "SourceLocation": "Gannavaram, AP",
            "BatchNumber": "TIL-2026-06B",
            "SizeCategory": "Fingerling (2.5-3 inches)",
            "PricePerFish": 2.8,
            "TotalSeedCost": 28000.0,
            "TransportCost": 2000.0,
            "AcclimatizationNotes": "100% mono-sex male fry certified. 1 hour temperature equalization.",
            "Notes": "Intensive culture with supplementary pelleted feed.",
            "Remarks": "Intensive culture with supplementary pelleted feed."
        }
    ]


def get_demo_fish_growth() -> List[Dict[str, Any]]:
    records = []
    base_date = date.today() - timedelta(days=90)
    
    # Growth trajectory for P-001 (Rohu / Catla composite)
    weights_p1 = [50, 95, 160, 245, 340, 440, 550, 680]
    dates_p1 = [base_date + timedelta(days=i * 12) for i in range(len(weights_p1))]
    for i, (d, w) in enumerate(zip(dates_p1, weights_p1)):
        records.append({
            "GrowthID": 200 + i,
            "PondID": "P-001",
            "Species": "Rohu & Catla",
            "ObservationDate": d.strftime("%Y-%m-%d"),
            "SampleSize": 35,
            "AvgFishWeightGrams": float(w),
            "MinWeightGrams": round(float(w) * 0.85, 1),
            "MaxWeightGrams": round(float(w) * 1.15, 1),
            "EstimatedBiomassKg": round((8000 * float(w)) / 1000.0, 1),
            "SamplingMethod": "Cast Netting (3 random sampling points)",
            "Observer": "K. Satyanarayana",
            "Notes": f"Sampling check #{i+1}. Clear body sheen, robust belly development."
        })

    # Growth trajectory for P-002 (Tilapia)
    weights_p2 = [30, 75, 140, 220, 310, 410, 490]
    dates_p2 = [base_date + timedelta(days=15 + i * 12) for i in range(len(weights_p2))]
    for i, (d, w) in enumerate(zip(dates_p2, weights_p2)):
        records.append({
            "GrowthID": 300 + i,
            "PondID": "P-002",
            "Species": "Tilapia",
            "ObservationDate": d.strftime("%Y-%m-%d"),
            "SampleSize": 40,
            "AvgFishWeightGrams": float(w),
            "MinWeightGrams": round(float(w) * 0.90, 1),
            "MaxWeightGrams": round(float(w) * 1.12, 1),
            "EstimatedBiomassKg": round((10000 * float(w)) / 1000.0, 1),
            "SamplingMethod": "Seine Net scoop",
            "Observer": "M. Venkat",
            "Notes": f"Tilapia sampling check #{i+1}. Uniform grading, active surface feeding."
        })

    return records


def get_demo_water_quality() -> List[Dict[str, Any]]:
    records = []
    today = date.today()
    
    # 20 days for P-001
    for day_offset in range(20, -1, -1):
        d = today - timedelta(days=day_offset)
        do_val = 4.2 if day_offset == 3 else round(5.8 + (day_offset % 3) * 0.4, 2)
        ph_val = round(7.4 + ((day_offset % 4) - 2) * 0.15, 2)
        temp_val = round(28.0 + (day_offset % 5) * 0.5, 1)
        turb_val = round(28.0 + (day_offset % 4) * 2.5, 1)
        nh3_val = round(0.015 + (0.04 if day_offset == 3 else 0.01), 3)

        records.append({
            "ReadingID": 1000 + (20 - day_offset),
            "PondID": "P-001",
            "ReadingDate": d.strftime("%Y-%m-%d"),
            "ReadingTime": "07:30:00",
            "pH": ph_val,
            "Temperature": temp_val,
            "DissolvedOxygen": do_val,
            "Turbidity": turb_val,
            "Ammonia": nh3_val,
            "Nitrite": 0.01,
            "Nitrate": 2.5,
            "WaterLevel": 1.65,
            "Transparency": 30.0,
            "Salinity": 0.0,
            "Alkalinity": 120.0,
            "Hardness": 110.0,
            "Conductivity": 450.0,
            "Notes": "Morning routine measurement." if day_offset != 3 else "Cloudy morning, low aeration recorded."
        })

    # 15 days for P-002
    for day_offset in range(15, -1, -1):
        d = today - timedelta(days=day_offset)
        ph_val = round(7.8 + ((day_offset % 3) - 1) * 0.2, 2)
        temp_val = round(29.2 + (day_offset % 3) * 0.4, 1)
        do_val = round(6.1 + (day_offset % 4) * 0.3, 2)
        turb_val = round(32.0 + (day_offset % 5) * 1.5, 1)
        nh3_val = round(0.02 + (day_offset % 2) * 0.01, 3)

        records.append({
            "ReadingID": 2000 + (15 - day_offset),
            "PondID": "P-002",
            "ReadingDate": d.strftime("%Y-%m-%d"),
            "ReadingTime": "08:00:00",
            "pH": ph_val,
            "Temperature": temp_val,
            "DissolvedOxygen": do_val,
            "Turbidity": turb_val,
            "Ammonia": nh3_val,
            "Nitrite": 0.02,
            "Nitrate": 3.0,
            "WaterLevel": 1.80,
            "Transparency": 28.0,
            "Salinity": 0.5,
            "Alkalinity": 135.0,
            "Hardness": 125.0,
            "Conductivity": 510.0,
            "Notes": "Borewell water added 2 days ago."
        })

    return records


def get_demo_water_events() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "EventID": 1,
            "PondID": "P-001",
            "Date": (today - timedelta(days=12)).strftime("%Y-%m-%d"),
            "EventType": "Water Added",
            "EstimatedQuantity": 1500.0,
            "Unit": "m³",
            "Reason": "Replenish evaporation loss via canal feeder channel",
            "Notes": "Screen placed at inlet to stop wild fish entry."
        },
        {
            "EventID": 2,
            "PondID": "P-001",
            "Date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "EventType": "Water Exchange",
            "EstimatedQuantity": 800.0,
            "Unit": "m³",
            "Reason": "Bottom discharge of organic accumulation followed by top-up",
            "Notes": "Water clarity restored from 24cm to 32cm."
        },
        {
            "EventID": 3,
            "PondID": "P-002",
            "Date": (today - timedelta(days=7)).strftime("%Y-%m-%d"),
            "EventType": "Borewell Refill",
            "EstimatedQuantity": 1200.0,
            "Unit": "m³",
            "Reason": "Routine weekly water freshening for Tilapia culture",
            "Notes": "Aerated in sump before entering pond."
        }
    ]


def get_demo_feeding() -> List[Dict[str, Any]]:
    records = []
    today = date.today()
    for day_offset in range(14, -1, -1):
        d = today - timedelta(days=day_offset)
        records.append({
            "FeedingID": 400 + (14 - day_offset),
            "PondID": "P-001",
            "FeedingDate": d.strftime("%Y-%m-%d"),
            "FeedingTime": "08:00:00",
            "Species": "Rohu & Catla",
            "FeedType": "Floating Pellet (28% Protein)",
            "FeedBrand": "CP Aqua Feeds",
            "FeedBatch": "CP-28P-884",
            "BiomassKg": 5440.0,
            "FeedingRatePercent": 2.6,
            "NumberOfFeedings": 2,
            "RecommendedFeedKg": 141.4,
            "ActualFeedKg": 140.0,
            "FeedUnit": "kg",
            "FeedingMethod": "Manual Broadcasting along dykes",
            "FeedCostPerKg": 48.0,
            "TotalFeedCost": 6720.0,
            "WeatherCondition": "Sunny / Normal",
            "FishBehaviour": "Vigorous feeding surface activity",
            "FeedResponse": "Good (Tray empty in 90 mins)",
            "Remarks": "Morning 70kg, Evening 70kg."
        })
        records.append({
            "FeedingID": 500 + (14 - day_offset),
            "PondID": "P-002",
            "FeedingDate": d.strftime("%Y-%m-%d"),
            "FeedingTime": "08:30:00",
            "Species": "Tilapia",
            "FeedType": "Commercial Tilapia Grower (32% Protein)",
            "FeedBrand": "Godrej Agrovet Aqua",
            "FeedBatch": "GA-TIL-320",
            "BiomassKg": 4900.0,
            "FeedingRatePercent": 2.9,
            "NumberOfFeedings": 3,
            "RecommendedFeedKg": 142.1,
            "ActualFeedKg": 140.0,
            "FeedUnit": "kg",
            "FeedingMethod": "Automatic Solar Feeder + Hand Broadcast",
            "FeedCostPerKg": 52.0,
            "TotalFeedCost": 7280.0,
            "WeatherCondition": "Warm / Humid",
            "FishBehaviour": "Extremely aggressive feeding response",
            "FeedResponse": "Excellent (No feed residual)",
            "Remarks": "Split into 3 morning/noon/evening rations."
        })
    return records


def get_demo_feed_inventory() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "InventoryID": 1,
            "FeedType": "Floating Pellet (28% Protein, 3mm)",
            "Brand": "CP Aqua Feeds",
            "BatchNumber": "CP-28P-884",
            "PurchaseDate": (today - timedelta(days=25)).strftime("%Y-%m-%d"),
            "QuantityPurchasedKg": 4000.0,
            "QuantityUsedKg": 2100.0,
            "RemainingQuantityKg": 1900.0,
            "UnitCost": 48.0,
            "Supplier": "Sri Balaji Aqua Feeds, Bhimavaram",
            "ExpiryDate": (today + timedelta(days=120)).strftime("%Y-%m-%d"),
            "StorageLocation": "Farm Feed Shed, Bay 1",
            "Notes": "Pallets raised 6 inches above floor on wooden racks."
        },
        {
            "InventoryID": 2,
            "FeedType": "Commercial Tilapia Grower (32% Protein, 2mm)",
            "Brand": "Godrej Agrovet Aqua",
            "BatchNumber": "GA-TIL-320",
            "PurchaseDate": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "QuantityPurchasedKg": 3500.0,
            "QuantityUsedKg": 2100.0,
            "RemainingQuantityKg": 1400.0,
            "UnitCost": 52.0,
            "Supplier": "Coastal Aqua Enterprises, Vijayawada",
            "ExpiryDate": (today + timedelta(days=90)).strftime("%Y-%m-%d"),
            "StorageLocation": "Farm Feed Shed, Bay 2",
            "Notes": "Moisture-free sealed bags."
        }
    ]


def get_demo_mortality() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "IncidentID": 1,
            "PondID": "P-001",
            "IncidentDate": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "NumberOfDead": 12,
            "EstimatedMortalityPercent": 0.15,
            "ObservedBehaviour": "Fish gathering near water inlet surface early morning",
            "VisibleSymptoms": "Gills flared, no external body lesions",
            "WaterCondition": "Cloudy overcast morning with low DO (4.2 mg/L)",
            "Remarks": "Aerator turned on immediately for 4 hours. Condition stabilized.",
            "PhotoPath": None
        },
        {
            "IncidentID": 2,
            "PondID": "P-002",
            "IncidentDate": (today - timedelta(days=18)).strftime("%Y-%m-%d"),
            "NumberOfDead": 8,
            "EstimatedMortalityPercent": 0.08,
            "ObservedBehaviour": "Sluggish swimming along western dyke",
            "VisibleSymptoms": "Minor fin rot signs on 2 samples",
            "WaterCondition": "Normal",
            "Remarks": "Treated pond with approved water disinfectant. Monitored for 3 days.",
            "PhotoPath": None
        }
    ]


def get_demo_incidents() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "IncidentID": 1,
            "PondID": "P-001",
            "Date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "Time": "06:45:00",
            "IncidentType": "Mortality & Low DO",
            "NumberAffected": 12,
            "ObservedBehaviour": "Fish piping at water surface in inlet quadrant",
            "VisibleObservation": "Gills pale red, flared opercula, no visible lesions",
            "WaterCondition": "Overcast sky, Dissolved Oxygen 4.2 mg/L",
            "WeatherCondition": "Heavy cloud cover, zero wind",
            "Severity": "HIGH",
            "Description": "Early dawn low dissolved oxygen incident resulting in 12 dead fingerlings.",
            "ActionTaken": "Started 2 paddlewheel aerators immediately for 4.5 hours. Added 150m³ fresh canal water.",
            "FollowUpDate": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "Status": "Resolved",
            "Notes": "Recheck confirmed DO returned to 5.8 mg/L by 10:00 AM."
        },
        {
            "IncidentID": 2,
            "PondID": "P-002",
            "Date": (today - timedelta(days=18)).strftime("%Y-%m-%d"),
            "Time": "09:15:00",
            "IncidentType": "Fin Observation",
            "NumberAffected": 8,
            "ObservedBehaviour": "Isolated sluggish swimming along western embankment",
            "VisibleObservation": "Mild fin fraying on sample fish",
            "WaterCondition": "Normal (pH 7.8, DO 6.2 mg/L)",
            "WeatherCondition": "Sunny, 32°C",
            "Severity": "WARNING",
            "Description": "Mild fin rot symptoms noticed on 8 juvenile Tilapia.",
            "ActionTaken": "Applied permitted mineral salt bath to affected area. Disinfected scoop nets.",
            "FollowUpDate": (today - timedelta(days=14)).strftime("%Y-%m-%d"),
            "Status": "Resolved",
            "Notes": "Subsequent netting after 4 days confirmed fins regenerated and zero new incidents."
        },
        {
            "IncidentID": 3,
            "PondID": "P-003",
            "Date": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "Time": "16:00:00",
            "IncidentType": "Pond Liner Damage",
            "NumberAffected": 0,
            "ObservedBehaviour": "None (Pond was unstocked)",
            "VisibleObservation": "Tear of ~15cm on southern berm lining",
            "WaterCondition": "Water drained for maintenance",
            "WeatherCondition": "Hot dry winds",
            "Severity": "INFO",
            "Description": "Pre-stocking inspection detected minor geomembrane rupture.",
            "ActionTaken": "Scheduled hot-air extrusion welding with specialized contractor.",
            "FollowUpDate": today.strftime("%Y-%m-%d"),
            "Status": "Monitoring",
            "Notes": "Repair ongoing during current pond maintenance phase."
        }
    ]


def get_demo_equipment() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "EquipmentID": 1,
            "EquipmentName": "4-Paddlewheel Aerator 2HP",
            "Category": "Aeration",
            "PondID": "P-001",
            "PurchaseDate": "2025-06-10",
            "PurchaseCost": 32000.0,
            "Supplier": "Godavari Aqua Machinery, Bhimavaram",
            "Condition": "Good",
            "LastMaintenance": (today - timedelta(days=40)).strftime("%Y-%m-%d"),
            "NextMaintenance": (today + timedelta(days=50)).strftime("%Y-%m-%d"),
            "Warranty": "2 Years (Expires Jun 2027)",
            "Notes": "Gearbox oil replaced last month. Electric cable insulated."
        },
        {
            "EquipmentID": 2,
            "EquipmentName": "Diesel Water Pump 10HP",
            "Category": "Pumps",
            "PondID": "P-001",
            "PurchaseDate": "2024-11-20",
            "PurchaseCost": 45000.0,
            "Supplier": "Kirloskar Dealers, Eluru",
            "Condition": "Good",
            "LastMaintenance": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "NextMaintenance": (today + timedelta(days=40)).strftime("%Y-%m-%d"),
            "Warranty": "1 Year (Expired)",
            "Notes": "Mobile pump for emergency pond water exchange."
        },
        {
            "EquipmentID": 3,
            "EquipmentName": "Digital Optical DO & pH Meter",
            "Category": "Testing Kit",
            "PondID": "All Ponds",
            "PurchaseDate": "2025-02-15",
            "PurchaseCost": 22500.0,
            "Supplier": "Hanna Instruments Direct",
            "Condition": "Excellent",
            "LastMaintenance": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
            "NextMaintenance": (today + timedelta(days=75)).strftime("%Y-%m-%d"),
            "Warranty": "3 Years",
            "Notes": "Calibrated with pH 7.0 and 4.0 buffer solutions every 14 days."
        },
        {
            "EquipmentID": 4,
            "EquipmentName": "Solar Automatic Fish Feeder",
            "Category": "Feeding",
            "PondID": "P-002",
            "PurchaseDate": "2025-08-01",
            "PurchaseCost": 28000.0,
            "Supplier": "Surya Solar Tech, Guntur",
            "Condition": "Good",
            "LastMaintenance": (today - timedelta(days=35)).strftime("%Y-%m-%d"),
            "NextMaintenance": (today + timedelta(days=55)).strftime("%Y-%m-%d"),
            "Warranty": "2 Years",
            "Notes": "Capacity 60kg pellets. Timer set for 3 daily cycles."
        }
    ]


def get_demo_maintenance() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "MaintenanceID": 1,
            "PondID": "P-001",
            "Date": (today - timedelta(days=40)).strftime("%Y-%m-%d"),
            "MaintenanceType": "Aeration Equipment",
            "Description": "Gearbox oil flushing, impeller nylon bushing replacement",
            "Cost": 2400.0,
            "Contractor": "Anand Electrical Works",
            "Status": "Completed",
            "NextMaintenanceDate": (today + timedelta(days=50)).strftime("%Y-%m-%d"),
            "Notes": "Both paddlewheels operational."
        },
        {
            "MaintenanceID": 2,
            "PondID": "P-003",
            "Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "MaintenanceType": "Lining & Embankment",
            "Description": "HDPE geomembrane inspection, drainage valve overhaul",
            "Cost": 8500.0,
            "Contractor": "GeoLiner Specialists, Hyderabad",
            "Status": "In Progress",
            "NextMaintenanceDate": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "Notes": "Pond de-silted; liner patch welding in final stage."
        }
    ]


def get_demo_labour() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "LabourID": 1,
            "WorkerName": "P. Nageswara Rao",
            "Role": "Farm Feeder & Technician",
            "Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "PondID": "P-001",
            "WorkType": "Daily Feeding & Water Testing",
            "Hours": 8.0,
            "Rate": 75.0,
            "TotalCost": 600.0,
            "Notes": "Routine daily duties."
        },
        {
            "LabourID": 2,
            "WorkerName": "V. Prasad & Team",
            "Role": "Harvest Netters",
            "Date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "PondID": "P-002",
            "WorkType": "Selective Dragnet Catching",
            "Hours": 6.0,
            "Rate": 500.0,
            "TotalCost": 3000.0,
            "Notes": "Catch of 850 kg Tilapia sorted by grade."
        }
    ]


def get_demo_purchases() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "PurchaseID": 1,
            "Date": (today - timedelta(days=25)).strftime("%Y-%m-%d"),
            "Item": "Floating Fish Feed (28%)",
            "Category": "Feed",
            "Supplier": "Sri Balaji Aqua Feeds",
            "Quantity": 4000.0,
            "Unit": "kg",
            "UnitPrice": 48.0,
            "TotalPrice": 192000.0,
            "PondID": "P-001",
            "InvoiceNumber": "INV-2026-884",
            "Notes": "Paid via NEFT. Batch verified."
        },
        {
            "PurchaseID": 2,
            "Date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "Item": "GIFT Tilapia Feed (32%)",
            "Category": "Feed",
            "Supplier": "Coastal Aqua Enterprises",
            "Quantity": 3500.0,
            "Unit": "kg",
            "UnitPrice": 52.0,
            "TotalPrice": 182000.0,
            "PondID": "P-002",
            "InvoiceNumber": "INV-2026-921",
            "Notes": "50% paid on delivery, 50% 30-day credit."
        },
        {
            "PurchaseID": 3,
            "Date": (today - timedelta(days=40)).strftime("%Y-%m-%d"),
            "Item": "Agricultural Lime (Calcium Carbonate)",
            "Category": "Chemicals / Minerals",
            "Supplier": "Delta Minerals Depot",
            "Quantity": 500.0,
            "Unit": "kg",
            "UnitPrice": 8.5,
            "TotalPrice": 4250.0,
            "PondID": "All Ponds",
            "InvoiceNumber": "INV-MIN-102",
            "Notes": "Water buffering."
        }
    ]


def get_demo_harvests() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "HarvestID": 1,
            "PondID": "P-001",
            "Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "Species": "Catla",
            "QuantityHarvestedFish": 700,
            "AverageWeightGrams": 1714.0,
            "TotalWeightKg": 1200.0,
            "HarvestMethod": "Partial Selective Dragnet",
            "Grade": "A Grade (>1.5 kg)",
            "Buyer": "Bhimavaram Wholesale Fish Market",
            "PricePerKg": 165.0,
            "TotalRevenue": 198000.0,
            "TransportCost": 4500.0,
            "LabourCost": 2500.0,
            "Notes": "Loaded onto iced transport truck within 45 mins."
        },
        {
            "HarvestID": 2,
            "PondID": "P-002",
            "Date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "Species": "Tilapia",
            "QuantityHarvestedFish": 1700,
            "AverageWeightGrams": 500.0,
            "TotalWeightKg": 850.0,
            "HarvestMethod": "Seine Netting",
            "Grade": "Standard Grade (450-550g)",
            "Buyer": "Vijayawada Local Fish Traders Association",
            "PricePerKg": 140.0,
            "TotalRevenue": 119000.0,
            "TransportCost": 3000.0,
            "LabourCost": 2000.0,
            "Notes": "First batch selective harvest of mature GIFT Tilapia."
        }
    ]


def get_demo_sales() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "SaleID": 1,
            "PondID": "P-001",
            "SaleDate": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "Species": "Catla",
            "QuantitySoldKg": 1200.0,
            "PricePerKg": 165.0,
            "TotalRevenue": 198000.0,
            "BuyerMarket": "Bhimavaram Wholesale Fish Market",
            "TransportCost": 4500.0,
            "PaymentStatus": "Paid",
            "PaymentDate": (today - timedelta(days=4)).strftime("%Y-%m-%d"),
            "Notes": "Bank transfer received in full."
        },
        {
            "SaleID": 2,
            "PondID": "P-002",
            "SaleDate": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "Species": "Tilapia",
            "QuantitySoldKg": 850.0,
            "PricePerKg": 140.0,
            "TotalRevenue": 119000.0,
            "BuyerMarket": "Vijayawada Local Fish Traders Association",
            "TransportCost": 3000.0,
            "PaymentStatus": "Partial",
            "PaymentDate": (today - timedelta(days=6)).strftime("%Y-%m-%d"),
            "Notes": "₹75,000 paid as advance; balance ₹44,000 due next week."
        }
    ]


def get_demo_expenses() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "ExpenseID": 1,
            "PondID": "P-001",
            "ExpenseDate": (today - timedelta(days=85)).strftime("%Y-%m-%d"),
            "Category": "Fish Seed",
            "Description": "8,000 Fingerlings (Rohu + Catla composite)",
            "Quantity": 8000.0,
            "Amount": 24000.0,
            "Notes": "Procured from Godavari Hatcheries."
        },
        {
            "ExpenseID": 2,
            "PondID": "P-001",
            "ExpenseDate": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "Category": "Feed",
            "Description": "50 bags commercial floating pellet feed (28%)",
            "Quantity": 2000.0,
            "Amount": 96000.0,
            "Notes": "Monthly feed supply."
        },
        {
            "ExpenseID": 3,
            "PondID": "P-001",
            "ExpenseDate": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
            "Category": "Electricity",
            "Description": "Aerator & pumping power tariff bill",
            "Quantity": 1.0,
            "Amount": 7800.0,
            "Notes": "Agricultural power slab."
        },
        {
            "ExpenseID": 4,
            "PondID": "P-002",
            "ExpenseDate": (today - timedelta(days=70)).strftime("%Y-%m-%d"),
            "Category": "Fish Seed",
            "Description": "10,000 GIFT Tilapia fingerlings",
            "Quantity": 10000.0,
            "Amount": 28000.0,
            "Notes": "High quality mono-sex seed."
        },
        {
            "ExpenseID": 5,
            "PondID": "P-002",
            "ExpenseDate": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "Category": "Feed",
            "Description": "Tilapia grower feed pellets (32%)",
            "Quantity": 2200.0,
            "Amount": 114400.0,
            "Notes": "32% protein formulation."
        },
        {
            "ExpenseID": 6,
            "PondID": "P-002",
            "ExpenseDate": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "Category": "Labour",
            "Description": "Netting, feeding labor and dyke cleaning",
            "Quantity": 1.0,
            "Amount": 12000.0,
            "Notes": "Monthly farm labor wages."
        }
    ]


def get_demo_documents() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "DocID": 1,
            "PondID": "P-001",
            "Category": "Hatchery Certificate",
            "Title": "Seed Certification & Quarantine Clearance",
            "Date": (today - timedelta(days=85)).strftime("%Y-%m-%d"),
            "FileName": "Godavari_Seed_Certificate_May2026.pdf",
            "Notes": "Validates pathogen-free Jayanti Rohu & Catla batch."
        },
        {
            "DocID": 2,
            "PondID": "P-002",
            "Category": "Invoice",
            "Title": "Godrej Aqua Feed Purchase Bill #884",
            "Date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "FileName": "Feed_Invoice_INV921.pdf",
            "Notes": "GST compliant tax invoice."
        },
        {
            "DocID": 3,
            "PondID": "P-003",
            "Category": "Pond Photo",
            "Title": "HDPE Liner Inspection Pre-Repair Photo",
            "Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "FileName": "Pond3_Liner_SouthernSlope.jpg",
            "Notes": "Shows localized tear repaired by GeoLiner team."
        }
    ]


def get_demo_reminders() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "ReminderID": 1,
            "ReminderDate": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "ReminderType": "Water Test",
            "PondID": "P-001",
            "Description": "Follow-up dissolved oxygen & ammonia reading in Green Valley Pond.",
            "Status": "Pending"
        },
        {
            "ReminderID": 2,
            "ReminderDate": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            "ReminderType": "Growth Sampling",
            "PondID": "P-002",
            "Description": "Bi-weekly 40-fish sample netting to update Tilapia biomass model.",
            "Status": "Pending"
        },
        {
            "ReminderID": 3,
            "ReminderDate": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "ReminderType": "Payment Follow-up",
            "PondID": "P-002",
            "Description": "Collect pending balance ₹44,000 from Vijayawada Fish Traders.",
            "Status": "Pending"
        }
    ]


def get_demo_alerts() -> List[Dict[str, Any]]:
    today = date.today()
    return [
        {
            "AlertID": 1,
            "Category": "Water Quality",
            "PondID": "P-001",
            "Title": "Dissolved Oxygen — Needs Attention",
            "Reason": "Observation (4.2 mg/L) below configured baseline (5.0 mg/L).",
            "Severity": "WARNING",
            "SuggestedAction": "Recheck reading. Run aerator during dawn hours. Monitor pond closely.",
            "Date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "IsRead": False,
            "IsResolved": False
        },
        {
            "AlertID": 2,
            "Category": "Mortality",
            "PondID": "P-001",
            "Title": "Mortality Incident Recorded (12 Fish)",
            "Reason": "12 dead fish reported on cloudy morning.",
            "Severity": "WARNING",
            "SuggestedAction": "Check water-quality readings and aeration. If mortality persists, consult a qualified fisheries professional.",
            "Date": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
            "IsRead": True,
            "IsResolved": True
        },
        {
            "AlertID": 3,
            "Category": "Weather",
            "PondID": "P-002",
            "Title": "High Surface Temperature Notice",
            "Reason": "Forecast predicts temperatures approaching 35°C.",
            "Severity": "INFO",
            "SuggestedAction": "Check water depth and consider maintaining adequate water exchange.",
            "Date": today.strftime("%Y-%m-%d"),
            "IsRead": False,
            "IsResolved": False
        }
    ]


def get_demo_weather() -> Dict[str, Any]:
    today = date.today()
    forecast = []
    conditions = ["Partly Cloudy", "Sunny & Warm", "Light Rain Showers", "Overcast", "Clear Sky"]
    temps_max = [33.5, 34.0, 31.0, 30.5, 34.2]
    temps_min = [25.0, 25.5, 24.0, 24.2, 25.8]
    rainfalls = [0.0, 0.0, 14.5, 6.0, 0.0]
    humidities = [74, 68, 88, 82, 70]
    winds = [12, 10, 18, 15, 9]

    for i in range(5):
        d = today + timedelta(days=i)
        forecast.append({
            "date": d.strftime("%Y-%m-%d"),
            "day": d.strftime("%A"),
            "condition": conditions[i % len(conditions)],
            "temp_max": temps_max[i % len(temps_max)],
            "temp_min": temps_min[i % len(temps_min)],
            "rainfall_mm": rainfalls[i % len(rainfalls)],
            "humidity_pct": humidities[i % len(humidities)],
            "wind_kmh": winds[i % len(winds)],
            "cautionary_note": (
                "Moderate rain forecasted. Ensure overflow pipes are clear and check pond dykes."
                if rainfalls[i % len(rainfalls)] > 5
                else "Warm sunny weather. Monitor dissolved oxygen and surface temperatures in afternoon."
            )
        })

    return {
        "location": "Krishna-Godavari Fishery Belt, Andhra Pradesh",
        "current_temp": 32.0,
        "current_condition": "Partly Cloudy",
        "current_humidity": 75,
        "current_wind_kmh": 12,
        "today_rainfall_mm": 0.0,
        "forecast": forecast,
        "is_demo": True
    }


def get_unified_recent_activity(pond_id: Optional[str] = None, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Combines events across all modules into a unified chronological feed.
    """
    activities = []
    
    # 1. Water Quality
    for w in get_demo_water_quality()[-5:]:
        if pond_id is None or w["PondID"] == pond_id:
            status = "Needs Attention" if w["DissolvedOxygen"] < 5.0 else "Optimal"
            activities.append({
                "type": "water",
                "icon": "WATER",
                "title": f"Water reading logged ({w['PondID']})",
                "pond_id": w["PondID"],
                "date": w["ReadingDate"],
                "time": w["ReadingTime"],
                "details": f"pH {w['pH']} | Temp {w['Temperature']}°C | DO {w['DissolvedOxygen']} mg/L",
                "status": status
            })

    # 2. Feeding
    for f in get_demo_feeding()[-4:]:
        if pond_id is None or f["PondID"] == pond_id:
            activities.append({
                "type": "feeding",
                "icon": "FEED",
                "title": f"Feeding recorded ({f['PondID']})",
                "pond_id": f["PondID"],
                "date": f["FeedingDate"],
                "time": "17:00:00",
                "details": f"Fed {f['ActualFeedKg']} kg ({f['FeedType']})",
                "status": "Completed"
            })

    # 3. Mortality
    for m in get_demo_mortality():
        if pond_id is None or m["PondID"] == pond_id:
            activities.append({
                "type": "mortality",
                "icon": "INCIDENT",
                "title": f"Mortality incident logged ({m['PondID']})",
                "pond_id": m["PondID"],
                "date": m["IncidentDate"],
                "time": "08:15:00",
                "details": f"{m['NumberOfDead']} dead fish | {m['ObservedBehaviour']}",
                "status": "Alert Recorded"
            })

    # 4. Sales / Harvest
    for s in get_demo_sales():
        if pond_id is None or s["PondID"] == pond_id:
            activities.append({
                "type": "sale",
                "icon": "SALE",
                "title": f"Fish sale recorded ({s['PondID']})",
                "pond_id": s["PondID"],
                "date": s["SaleDate"],
                "time": "11:30:00",
                "details": f"Harvested {s['QuantitySoldKg']} kg @ ₹{s['PricePerKg']}/kg (₹{s['TotalRevenue']:,.0f})",
                "status": "Revenue"
            })

    # 5. Growth
    for g in get_demo_fish_growth()[-2:]:
        if pond_id is None or g["PondID"] == pond_id:
            activities.append({
                "type": "growth",
                "icon": "GROWTH",
                "title": f"Growth sampling check ({g['PondID']})",
                "pond_id": g["PondID"],
                "date": g["ObservationDate"],
                "time": "09:00:00",
                "details": f"Sample size {g['SampleSize']} fish | Avg weight {g['AvgFishWeightGrams']} g",
                "status": "Growth Recorded"
            })

    # Sort descending
    activities.sort(key=lambda x: (x["date"], x.get("time", "")), reverse=True)
    return activities[:limit]


def get_pond_health_snapshot(pond_id: str) -> Dict[str, Any]:
    """
    Computes a clean, compact health snapshot dictionary for a specific pond.
    """
    ponds = {p["PondID"]: p for p in get_demo_ponds()}
    pond = ponds.get(pond_id, {"PondID": pond_id, "PondName": f"Pond {pond_id}", "Status": "Active"})

    stocks = [s for s in get_demo_fish_stock() if s["PondID"] == pond_id]
    total_fish = sum(s["NumberOfFish"] for s in stocks)
    species_str = ", ".join(set(s["Species"] for s in stocks)) if stocks else "No Stock"

    growths = [g for g in get_demo_fish_growth() if g["PondID"] == pond_id]
    latest_weight = growths[-1]["AvgFishWeightGrams"] if growths else 50.0
    biomass = round((total_fish * latest_weight) / 1000.0, 1) if total_fish else 0.0

    waters = [w for w in get_demo_water_quality() if w["PondID"] == pond_id]
    latest_water = waters[-1] if waters else None
    if latest_water:
        if latest_water["DissolvedOxygen"] < 5.0 or latest_water["pH"] < 6.5 or latest_water["pH"] > 8.5:
            water_status = "Needs Attention"
        else:
            water_status = "Optimal"
    else:
        water_status = "No Data"

    feeds = [f for f in get_demo_feeding() if f["PondID"] == pond_id]
    daily_feed = f"{feeds[-1]['ActualFeedKg']} kg/day" if feeds else "No Feed Log"

    mortalities = [m for m in get_demo_mortality() if m["PondID"] == pond_id]
    incident_count = len(mortalities)
    last_activity = waters[-1]["ReadingDate"] if waters else "No Recent Logs"

    return {
        "pond_id": pond["PondID"],
        "pond_name": pond["PondName"],
        "status": pond["Status"],
        "species": species_str,
        "fish_count": f"{total_fish:,}" if total_fish else "0",
        "biomass": f"{biomass:,.0f} kg" if biomass else "0 kg",
        "water_status": water_status,
        "daily_feed": daily_feed,
        "incidents": str(incident_count),
        "last_activity": last_activity
    }


def initialize_demo_session_state(st_session_state):
    """
    Initializes or refreshes all 18 interactive collections in Streamlit session state or dict.
    """
    is_dict = isinstance(st_session_state, dict)
    has_init = ("demo_initialized" in st_session_state) if (is_dict or hasattr(st_session_state, "__contains__")) else hasattr(st_session_state, "demo_initialized")

    if not has_init:
        data = {
            "demo_farm_profile": get_demo_farm_profile(),
            "demo_species": get_demo_species(),
            "demo_ponds": get_demo_ponds(),
            "demo_fish_stock": get_demo_fish_stock(),
            "demo_fish_growth": get_demo_fish_growth(),
            "demo_water_quality": get_demo_water_quality(),
            "demo_water_events": get_demo_water_events(),
            "demo_feeding": get_demo_feeding(),
            "demo_feed_inventory": get_demo_feed_inventory(),
            "demo_mortality": get_demo_mortality(),
            "demo_incidents": get_demo_incidents(),
            "demo_equipment": get_demo_equipment(),
            "demo_maintenance": get_demo_maintenance(),
            "demo_labour": get_demo_labour(),
            "demo_purchases": get_demo_purchases(),
            "demo_harvests": get_demo_harvests(),
            "demo_sales": get_demo_sales(),
            "demo_expenses": get_demo_expenses(),
            "demo_documents": get_demo_documents(),
            "demo_reminders": get_demo_reminders(),
            "demo_alerts": get_demo_alerts(),
            "demo_weather": get_demo_weather(),
            "demo_initialized": True
        }

        if is_dict:
            st_session_state.update(data)
        else:
            for k, v in data.items():
                setattr(st_session_state, k, v)
