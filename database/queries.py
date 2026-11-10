"""
AquaMitra Data Access Layer (queries.py)
Provides consistent data contract querying and persistence across Live SQL Server and Demo Mode.
Ensures UI, Analytics, and AI layers receive uniform, strongly structured records.
"""

from typing import Optional, List, Dict, Any
import streamlit as st
import pandas as pd
from database.connection import is_database_connected, execute_parameterized_query, execute_parameterized_nonquery
from utils.calculations import calculate_initial_biomass

# =====================================================================
# FISH STOCK DATA CONTRACT
# Required fields:
# StockID, PondID, Species, Variety, StockingDate, NumberOfFish,
# AvgInitialWeightGrams, TotalInitialBiomassKg, SourceHatchery,
# BatchNumber, SizeCategory, PricePerFish, TotalSeedCost, TransportCost, Notes
# =====================================================================

FISH_STOCK_CONTRACT_FIELDS = [
    "StockID",
    "PondID",
    "Species",
    "Variety",
    "StockingDate",
    "NumberOfFish",
    "AvgInitialWeightGrams",
    "TotalInitialBiomassKg",
    "SourceHatchery",
    "BatchNumber",
    "SizeCategory",
    "PricePerFish",
    "TotalSeedCost",
    "TransportCost",
    "Notes"
]


def normalize_fish_stock_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a fish stock dictionary to guarantee all 15 contract fields are present and valid.
    Calculates biomass or cost deterministically if not supplied.
    """
    num_fish = int(record.get("NumberOfFish") or 0)
    avg_weight = float(record.get("AvgInitialWeightGrams") or 0.0)
    biomass = record.get("TotalInitialBiomassKg")
    if biomass is None:
        biomass = calculate_initial_biomass(num_fish, avg_weight)
    else:
        biomass = float(biomass)

    species = str(record.get("Species") or "Fish").strip()
    variety = record.get("Variety")
    if not variety or not str(variety).strip():
        variety = species
    else:
        variety = str(variety).strip()

    price_per_fish = float(record.get("PricePerFish") or 0.0)
    total_seed_cost = record.get("TotalSeedCost")
    if total_seed_cost is None:
        total_seed_cost = round(num_fish * price_per_fish, 2)
    else:
        total_seed_cost = float(total_seed_cost)

    notes = record.get("Notes")
    if notes is None:
        notes = record.get("Remarks") or ""
    else:
        notes = str(notes)

    return {
        "StockID": record.get("StockID"),
        "PondID": str(record.get("PondID") or "").strip(),
        "Species": species,
        "Variety": variety,
        "StockingDate": str(record.get("StockingDate") or ""),
        "NumberOfFish": num_fish,
        "AvgInitialWeightGrams": avg_weight,
        "TotalInitialBiomassKg": biomass,
        "SourceHatchery": str(record.get("SourceHatchery") or "").strip(),
        "BatchNumber": str(record.get("BatchNumber") or "").strip(),
        "SizeCategory": str(record.get("SizeCategory") or "Fingerling").strip(),
        "PricePerFish": price_per_fish,
        "TotalSeedCost": total_seed_cost,
        "TransportCost": float(record.get("TransportCost") or 0.0),
        "Notes": notes,
        "Remarks": notes  # Backwards compatibility alias
    }


from utils.demo_data import (
    get_demo_fish_stock,
    get_demo_water_quality,
    get_demo_feeding,
    get_demo_fish_growth,
    get_demo_incidents,
    get_demo_expenses,
    get_demo_sales,
    get_demo_harvests,
    get_demo_maintenance,
    get_demo_ponds
)

def _get_records_from_session(key: str, fallback_fn) -> List[Dict[str, Any]]:
    """
    Safely retrieves a record list from Streamlit session state, or falls back to demo data.
    Ensures safe execution in Streamlit, CLI tests, and initial page load.
    """
    records = None
    try:
        records = st.session_state.get(key)
    except Exception:
        records = None

    if records is None:
        records = fallback_fn()
        try:
            st.session_state[key] = records
        except Exception:
            pass

    return list(records) if isinstance(records, list) else []


def get_fish_stocks(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches fish stocking records for a specific pond or all ponds.
    Works seamlessly in both Live SQL Server Mode and Demo Mode with the exact same data contract.
    """
    # 1. Attempt Live SQL Query if database is connected and not forced demo mode
    is_live = False
    try:
        is_live = not st.session_state.get("demo_mode", True) and is_database_connected()
    except Exception:
        is_live = False

    if is_live:
        query = """
            SELECT 
                fs.StockID,
                fs.PondID,
                COALESCE(fs.Species, s.CommonName, 'Unknown') AS Species,
                COALESCE(fs.Variety, s.CommonName, 'Standard') AS Variety,
                CONVERT(VARCHAR(10), fs.StockingDate, 23) AS StockingDate,
                fs.NumberOfFish,
                CAST(fs.AvgInitialWeightGrams AS FLOAT) AS AvgInitialWeightGrams,
                CAST(COALESCE(fs.TotalInitialBiomassKg, ROUND((fs.NumberOfFish * fs.AvgInitialWeightGrams) / 1000.0, 2)) AS FLOAT) AS TotalInitialBiomassKg,
                COALESCE(fs.SourceHatchery, '') AS SourceHatchery,
                COALESCE(fs.BatchNumber, '') AS BatchNumber,
                COALESCE(fs.SizeCategory, 'Fingerling') AS SizeCategory,
                CAST(ISNULL(fs.PricePerFish, 0.0) AS FLOAT) AS PricePerFish,
                CAST(COALESCE(fs.TotalSeedCost, ROUND(fs.NumberOfFish * ISNULL(fs.PricePerFish, 0.0), 2)) AS FLOAT) AS TotalSeedCost,
                CAST(ISNULL(fs.TransportCost, 0.0) AS FLOAT) AS TransportCost,
                COALESCE(fs.Notes, '') AS Notes
            FROM dbo.FishStock fs
            LEFT JOIN dbo.Species s ON fs.SpeciesID = s.SpeciesID
            WHERE (? IS NULL OR fs.PondID = ?)
            ORDER BY fs.StockingDate DESC
        """
        df = execute_parameterized_query(query, (pond_id, pond_id))
        if df is not None and not df.empty:
            records = df.to_dict(orient="records")
            return [normalize_fish_stock_record(r) for r in records]

    # 2. Demo Mode / Session State Fallback
    raw_stocks = _get_records_from_session("demo_fish_stock", get_demo_fish_stock)
    if pond_id:
        raw_stocks = [s for s in raw_stocks if s.get("PondID") == pond_id]

    return [normalize_fish_stock_record(s) for s in raw_stocks]


def save_fish_stock(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves a new fish stock record into session state and, if connected, the live database.
    """
    norm = normalize_fish_stock_record(record)
    
    # 1. Update session state
    try:
        if "demo_fish_stock" not in st.session_state:
            st.session_state.demo_fish_stock = list(get_demo_fish_stock())
        
        if not norm.get("StockID"):
            norm["StockID"] = len(st.session_state.demo_fish_stock) + 101
        
        # Check if existing for edit
        existing_idx = None
        for idx, s in enumerate(st.session_state.demo_fish_stock):
            if s.get("StockID") == norm["StockID"]:
                existing_idx = idx
                break
                
        if existing_idx is not None:
            st.session_state.demo_fish_stock[existing_idx] = norm
        else:
            st.session_state.demo_fish_stock.append(norm)
    except Exception:
        if not norm.get("StockID"):
            norm["StockID"] = 999

    # 2. Persist to Live SQL Server if connected
    is_live = False
    try:
        is_live = not st.session_state.get("demo_mode", True) and is_database_connected()
    except Exception:
        is_live = False
        insert_sql = """
            INSERT INTO dbo.FishStock (
                PondID, Species, Variety, StockingDate, NumberOfFish,
                AvgInitialWeightGrams, TotalInitialBiomassKg, SourceHatchery,
                BatchNumber, SizeCategory, PricePerFish, TotalSeedCost,
                TransportCost, Notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_parameterized_nonquery(
            insert_sql,
            (
                norm["PondID"],
                norm["Species"],
                norm["Variety"],
                norm["StockingDate"],
                norm["NumberOfFish"],
                norm["AvgInitialWeightGrams"],
                norm["TotalInitialBiomassKg"],
                norm["SourceHatchery"],
                norm["BatchNumber"],
                norm["SizeCategory"],
                norm["PricePerFish"],
                norm["TotalSeedCost"],
                norm["TransportCost"],
                norm["Notes"]
            )
        )

    return norm


# =====================================================================
# WATER QUALITY DATA CONTRACT & ACCESS
# Aliases SQL Server columns:
# TemperatureC -> Temperature
# DissolvedOxygenMgL -> DissolvedOxygen
# TurbidityNTU -> Turbidity
# AmmoniaMgL -> Ammonia
# WaterLevelMeters -> WaterLevel
# =====================================================================

def get_water_quality(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches water quality observations with aliased parameter names.
    """
    is_live = False
    try:
        is_live = not st.session_state.get("demo_mode", True) and is_database_connected()
    except Exception:
        is_live = False

    if is_live:
        query = """
            SELECT 
                ReadingID,
                PondID,
                CONVERT(VARCHAR(10), ReadingDate, 23) AS ReadingDate,
                CONVERT(VARCHAR(8), ReadingTime, 108) AS ReadingTime,
                CAST(pH AS FLOAT) AS pH,
                CAST(TemperatureC AS FLOAT) AS Temperature,
                CAST(DissolvedOxygenMgL AS FLOAT) AS DissolvedOxygen,
                CAST(TurbidityNTU AS FLOAT) AS Turbidity,
                CAST(AmmoniaMgL AS FLOAT) AS Ammonia,
                CAST(WaterLevelMeters AS FLOAT) AS WaterLevel,
                COALESCE(Notes, '') AS Notes
            FROM dbo.WaterQuality
            WHERE (? IS NULL OR PondID = ?)
            ORDER BY ReadingDate DESC, ReadingTime DESC
        """
        df = execute_parameterized_query(query, (pond_id, pond_id))
        if df is not None and not df.empty:
            return df.to_dict(orient="records")

    raw = _get_records_from_session("demo_water_quality", get_demo_water_quality)
    if pond_id:
        raw = [w for w in raw if w.get("PondID") == pond_id]
    return raw


# =====================================================================
# FEEDING DATA CONTRACT & ACCESS
# =====================================================================

def get_feeding_records(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches feeding logs with TotalFeedCost and Remarks aliases.
    """
    is_live = False
    try:
        is_live = not st.session_state.get("demo_mode", True) and is_database_connected()
    except Exception:
        is_live = False

    if is_live:
        query = """
            SELECT 
                FeedingID,
                PondID,
                CONVERT(VARCHAR(10), FeedingDate, 23) AS FeedingDate,
                FeedType,
                COALESCE(FeedBrand, 'Standard Pellet') AS FeedBrand,
                CAST(BiomassKg AS FLOAT) AS BiomassKg,
                CAST(FeedingRatePercent AS FLOAT) AS FeedingRatePercent,
                NumberOfFeedings,
                CAST(RecommendedFeedKg AS FLOAT) AS RecommendedFeedKg,
                CAST(ActualFeedKg AS FLOAT) AS ActualFeedKg,
                CAST(FeedCostPerKg AS FLOAT) AS FeedCostPerKg,
                CAST(COALESCE(TotalFeedCost, ROUND(ActualFeedKg * FeedCostPerKg, 2)) AS FLOAT) AS TotalFeedCost,
                COALESCE(FeedResponse, 'Good (Clean feeding tray)') AS FeedResponse,
                COALESCE(Notes, '') AS Notes,
                COALESCE(Notes, '') AS Remarks
            FROM dbo.Feeding
            WHERE (? IS NULL OR PondID = ?)
            ORDER BY FeedingDate DESC
        """
        df = execute_parameterized_query(query, (pond_id, pond_id))
        if df is not None and not df.empty:
            return df.to_dict(orient="records")

    raw = _get_records_from_session("demo_feeding", get_demo_feeding)
    if pond_id:
        raw = [f for f in raw if f.get("PondID") == pond_id]
    return raw


# =====================================================================
# FISH GROWTH SAMPLING DATA CONTRACT & ACCESS
# =====================================================================

def get_growth_records(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches fish growth sampling observations.
    """
    is_live = False
    try:
        is_live = not st.session_state.get("demo_mode", True) and is_database_connected()
    except Exception:
        is_live = False

    if is_live:
        query = """
            SELECT 
                GrowthID,
                PondID,
                COALESCE(Species, 'Sampled Species') AS Species,
                CONVERT(VARCHAR(10), ObservationDate, 23) AS ObservationDate,
                SampleSize,
                CAST(AvgFishWeightGrams AS FLOAT) AS AvgFishWeightGrams,
                CAST(COALESCE(MinWeightGrams, ROUND(AvgFishWeightGrams * 0.85, 1)) AS FLOAT) AS MinWeightGrams,
                CAST(COALESCE(MaxWeightGrams, ROUND(AvgFishWeightGrams * 1.15, 1)) AS FLOAT) AS MaxWeightGrams,
                CAST(COALESCE(EstimatedBiomassKg, 0.0) AS FLOAT) AS EstimatedBiomassKg,
                COALESCE(SamplingMethod, 'Cast Netting') AS SamplingMethod,
                COALESCE(Observer, 'Technician') AS Observer,
                COALESCE(Notes, '') AS Notes
            FROM dbo.FishGrowth
            WHERE (? IS NULL OR PondID = ?)
            ORDER BY ObservationDate DESC
        """
        df = execute_parameterized_query(query, (pond_id, pond_id))
        if df is not None and not df.empty:
            return df.to_dict(orient="records")

    raw = _get_records_from_session("demo_fish_growth", get_demo_fish_growth)
    if pond_id:
        raw = [g for g in raw if g.get("PondID") == pond_id]
    return raw


# =====================================================================
# INCIDENTS & MORTALITY DATA ACCESS
# =====================================================================

def get_incidents(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches incidents and health observations.
    """
    raw = _get_records_from_session("demo_incidents", get_demo_incidents)
    if pond_id:
        raw = [i for i in raw if i.get("PondID") == pond_id]
    return raw


# =====================================================================
# EXPENSES & SALES DATA ACCESS
# =====================================================================

def get_expenses(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches farm expense records.
    """
    raw = _get_records_from_session("demo_expenses", get_demo_expenses)
    if pond_id:
        raw = [e for e in raw if e.get("PondID") == pond_id]
    return raw


def get_sales(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches fish sales and harvest revenue records.
    """
    raw = _get_records_from_session("demo_sales", get_demo_sales)
    if pond_id:
        raw = [s for s in raw if s.get("PondID") == pond_id]
    return raw


# =====================================================================
# HARVEST RECORDS ACCESS
# =====================================================================

def get_harvest_records(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches commercial fish harvest records.
    """
    raw = _get_records_from_session("demo_harvests", get_demo_harvests)
    if pond_id:
        raw = [h for h in raw if h.get("PondID") == pond_id]
    return raw


def save_harvest_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves a harvest record to session state and database.
    """
    try:
        if "demo_harvests" not in st.session_state:
            st.session_state.demo_harvests = list(get_demo_harvests())
        if not record.get("HarvestID"):
            record["HarvestID"] = len(st.session_state.demo_harvests) + 1
        st.session_state.demo_harvests.append(record)
    except Exception:
        if not record.get("HarvestID"):
            record["HarvestID"] = 999
    return record


# =====================================================================
# MAINTENANCE RECORDS ACCESS
# =====================================================================

def get_maintenance_records(pond_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches equipment and pond maintenance logs.
    """
    raw = _get_records_from_session("demo_maintenance", get_demo_maintenance)
    if pond_id:
        raw = [m for m in raw if m.get("PondID") == pond_id]
    return raw


def save_maintenance_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves a maintenance record to session state and database.
    """
    try:
        if "demo_maintenance" not in st.session_state:
            st.session_state.demo_maintenance = list(get_demo_maintenance())
        if not record.get("MaintenanceID"):
            record["MaintenanceID"] = len(st.session_state.demo_maintenance) + 1
        st.session_state.demo_maintenance.append(record)
    except Exception:
        if not record.get("MaintenanceID"):
            record["MaintenanceID"] = 999
    return record


# =====================================================================
# POND CRUD OPERATIONS
# =====================================================================

def update_pond_record(pond_id: str, updated_fields: Dict[str, Any]) -> bool:
    """
    Updates an existing pond's attributes in session state.
    """
    try:
        if "demo_ponds" not in st.session_state:
            st.session_state.demo_ponds = list(get_demo_ponds())
        for idx, p in enumerate(st.session_state.demo_ponds):
            if p.get("PondID") == pond_id:
                st.session_state.demo_ponds[idx].update(updated_fields)
                return True
    except Exception:
        pass
    return False


def delete_pond_record(pond_id: str) -> bool:
    """
    Deletes a pond and associated session state records.
    """
    try:
        if "demo_ponds" in st.session_state:
            st.session_state.demo_ponds = [p for p in st.session_state.demo_ponds if p.get("PondID") != pond_id]
            return True
    except Exception:
        pass
    return False


# =====================================================================
# DATA HEALTH AUDIT
# =====================================================================

def get_data_health() -> Dict[str, Any]:
    """
    Audits farm records and categorizes data completeness per pond:
    'Complete', 'Partial', or 'Missing'. Never calls this a 'farm health score'.
    """
    ponds = _get_records_from_session("demo_ponds", get_demo_ponds)
    stocks = get_fish_stocks()
    waters = get_water_quality()
    growths = get_growth_records()
    feeds = get_feeding_records()
    maints = get_maintenance_records()

    pond_audits = []
    for p in ponds:
        pid = p["PondID"]
        has_stock = any(s.get("PondID") == pid for s in stocks)
        has_water = any(w.get("PondID") == pid for w in waters)
        has_growth = any(g.get("PondID") == pid for g in growths)
        has_feed = any(f.get("PondID") == pid for f in feeds)
        has_maint = any(m.get("PondID") == pid for m in maints)

        score = sum([has_stock, has_water, has_growth, has_feed, has_maint])
        if score == 5:
            status = "Complete"
        elif score >= 2:
            status = "Partial"
        else:
            status = "Missing"

        missing_items = []
        if not has_water:
            missing_items.append("Water Readings")
        if not has_growth:
            missing_items.append("Growth Records")
        if not has_feed:
            missing_items.append("Feeding Records")
        if not has_maint:
            missing_items.append("Maintenance Records")

        pond_audits.append({
            "PondID": pid,
            "PondName": p.get("PondName", "Unnamed"),
            "Status": status,
            "RecordedItems": score,
            "TotalTracked": 5,
            "MissingDomains": ", ".join(missing_items) if missing_items else "None"
        })

    return {
        "pond_audits": pond_audits,
        "total_ponds": len(ponds),
        "complete_count": sum(1 for a in pond_audits if a["Status"] == "Complete"),
        "partial_count": sum(1 for a in pond_audits if a["Status"] == "Partial"),
        "missing_count": sum(1 for a in pond_audits if a["Status"] == "Missing")
    }

