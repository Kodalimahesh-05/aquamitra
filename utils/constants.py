"""
AquaMitra Constants & Configurations
Defines standard lists, units, complete 15-menu hierarchy, and system enums.
"""

APP_NAME = "AquaMitra"
APP_TAGLINE = "Your Digital Partner for Smarter Fish Farming"
APP_VERSION = "1.0.0"

# 15 Major Menus matching exact production structure
MENUS = [
    "overview",
    "ponds",
    "fish",
    "water",
    "feeding",
    "health",
    "environment",
    "finance",
    "assets",
    "analytics",
    "alerts",
    "records",
    "ai",
    "reports",
    "settings"
]

# Complete Sub-Tabs for all 15 Menus
MENU_SUBTABS = {
    "overview": ["Dashboard", "Farm Summary", "Daily Brief"],
    "ponds": ["All Ponds", "Add Pond", "Pond Profiles", "Pond Activity", "Pond Maintenance"],
    "fish": ["Fish Stock", "Species", "Growth Tracking", "Biomass", "Stocking History", "Harvest"],
    "water": ["Water Dashboard", "Water Readings", "Water History", "Water Events", "Water Comparison", "Reference Ranges"],
    "feeding": ["Feeding Dashboard", "Record Feeding", "Feed History", "Feed Inventory", "Feed Costs"],
    "health": ["Incidents", "Mortality", "Observations", "Follow-ups", "Incident History"],
    "environment": ["Weather", "Weather History", "Environmental Context"],
    "finance": ["Finance Dashboard", "Expenses", "Purchases", "Labour", "Sales", "Payments", "Financial Analysis"],
    "assets": ["Equipment", "Maintenance", "Documents"],
    "analytics": ["Farm Analytics", "Pond Analytics", "Growth Analytics", "Water Analytics", "Feeding Analytics", "Incident Analytics", "Financial Analytics"],
    "alerts": ["Active Alerts", "All Alerts", "Resolved Alerts", "Alert History"],
    "records": ["Recent Activity", "All Records", "Data Health"],
    "ai": ["AquaMitra AI", "AI Insights", "AI Suggestions", "Daily Brief", "Ask AquaMitra"],
    "reports": ["Farm Report", "Pond Report", "Water Report", "Fish Report", "Feeding Report", "Incident Report", "Financial Report", "Custom Report"],
    "settings": ["Farm Profile", "General", "Appearance", "Language", "Data Mode", "Reference Ranges", "AI Settings", "Database", "Data Management", "About"]
}

# Pond Options
POND_STATUSES = ["Active", "Inactive", "Maintenance", "Preparing", "Harvested"]
POND_TYPES = ["Earthen", "Lined", "Biofloc", "Nursery", "Concrete", "Circular Tank"]
AREA_UNITS = ["Acres", "Hectares", "Sq Meters"]
WATER_SOURCES = ["Borewell", "Canal", "Rainfed", "River", "Reservoir", "Mixed"]

# Fish Species
SPECIES_LIST = ["Rohu", "Catla", "Mrigal", "Tilapia", "Pangasius", "Grass Carp", "Silver Carp", "Common Carp", "Other"]

# Alert Severity Levels
SEVERITY_LEVELS = ["INFO", "WARNING", "HIGH"]
ALERT_CATEGORIES = [
    "Water Quality",
    "Fish Growth",
    "Feeding",
    "Mortality",
    "Weather",
    "Finance",
    "Maintenance"
]

# Default Reference Ranges
DEFAULT_REFERENCE_RANGES = {
    "pH": {
        "lower": 6.5,
        "upper": 8.5,
        "unit": "pH",
        "description": "Acidity / alkalinity level of pond water"
    },
    "DissolvedOxygen": {
        "lower": 5.0,
        "upper": 10.0,
        "unit": "mg/L",
        "description": "Dissolved oxygen available for aquatic respiration"
    },
    "Temperature": {
        "lower": 24.0,
        "upper": 32.0,
        "unit": "°C",
        "description": "Surface pond water temperature"
    },
    "Turbidity": {
        "lower": 20.0,
        "upper": 40.0,
        "unit": "NTU",
        "description": "Water clarity and suspended solids"
    },
    "Ammonia": {
        "lower": 0.0,
        "upper": 0.05,
        "unit": "mg/L",
        "description": "Un-ionized toxic ammonia level"
    },
    "Nitrite": {
        "lower": 0.0,
        "upper": 0.1,
        "unit": "mg/L",
        "description": "Toxic intermediate nitrogen compound"
    },
    "Nitrate": {
        "lower": 0.0,
        "upper": 10.0,
        "unit": "mg/L",
        "description": "End product of nitrification"
    },
    "WaterLevel": {
        "lower": 1.2,
        "upper": 2.2,
        "unit": "meters",
        "description": "Effective pond water depth"
    }
}

# Expense Categories
EXPENSE_CATEGORIES = [
    "Fish Seed",
    "Feed",
    "Labour",
    "Electricity",
    "Pond Maintenance",
    "Equipment",
    "Transport",
    "Chemicals / Minerals",
    "Other"
]

# Smart Status Types (Strictly zero emojis)
STATUS_TYPES = {
    "GOOD": {"label": "Optimal", "badge_class": "status-optimal", "color": "#059669", "bg": "#ECFDF5", "border": "#A7F3D0"},
    "ATTENTION": {"label": "Monitor", "badge_class": "status-monitor", "color": "#D97706", "bg": "#FFFBEB", "border": "#FDE68A"},
    "RISK": {"label": "Alert", "badge_class": "status-alert", "color": "#DC2626", "bg": "#FEF2F2", "border": "#FECACA"},
    "NO_DATA": {"label": "No Data", "badge_class": "status-neutral", "color": "#64748B", "bg": "#F1F5F9", "border": "#CBD5E1"}
}

# Responsible Decision-Support Disclaimer
DISCLAIMER_TEXT = (
    "AquaMitra provides decision-support calculations and record management. "
    "Calculations are estimates based on user-entered records and reference thresholds. "
    "AquaMitra does not diagnose diseases or guarantee yields. "
    "Always consult a qualified fisheries extension officer or veterinarian for persistent pond anomalies."
)
