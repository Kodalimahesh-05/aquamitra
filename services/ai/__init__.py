"""
AquaMitra AI Intelligence Package
Provides contextual insights, daily farm briefings, anomaly detection,
safety filters, and the AquaMitra AI Assistant.
"""

from .safety import enforce_ai_safety, check_prohibited_terms
from .context_builder import build_farm_context, build_pond_context
from .prompts import SYSTEM_PROMPT, FARM_SUMMARY_PROMPT
from .anomaly_detection import detect_farm_anomalies, audit_data_health
from .insights import generate_farm_insights
from .query_assistant import answer_farmer_query
from .ai_service import ask_aquamitra_ai, generate_farm_summary, generate_daily_briefing
