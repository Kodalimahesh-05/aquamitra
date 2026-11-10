"""
AquaMitra Design System & Theme Tokens
Centralized color palette, typography, spacing, and visual constants.
Adheres to enterprise agricultural technology / SaaS design standards.
Strictly zero emojis.
"""

from typing import Dict, Any

# Primary enterprise agricultural SaaS color palette
COLORS = {
    # Brand Primary: Deep Navy
    "primary": "#0F2942",
    "primary_light": "#1E3A8A",
    "primary_dark": "#0A192F",
    
    # Secondary Accent: Teal / Aqua
    "accent": "#0D9488",
    "accent_light": "#14B8A6",
    "accent_subtle": "#F0FDFA",
    
    # Backgrounds & Surfaces
    "bg_main": "#F8FAFC",
    "bg_surface": "#FFFFFF",
    "bg_subtle": "#F1F5F9",
    "bg_card": "#FFFFFF",
    
    # Borders & Dividers
    "border": "#E2E8F0",
    "border_subtle": "#F1F5F9",
    "border_focus": "#0D9488",
    
    # Text Hierarchy (Slate)
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#64748B",
    "text_disabled": "#94A3B8",
    
    # Status Indicators
    "status_optimal": "#059669",
    "status_optimal_bg": "#ECFDF5",
    "status_optimal_border": "#A7F3D0",
    
    "status_monitor": "#D97706",
    "status_monitor_bg": "#FFFBEB",
    "status_monitor_border": "#FDE68A",
    
    "status_alert": "#DC2626",
    "status_alert_bg": "#FEF2F2",
    "status_alert_border": "#FECACA",
    
    "status_neutral": "#64748B",
    "status_neutral_bg": "#F8FAFC",
    "status_neutral_border": "#E2E8F0",
    
    "status_info": "#2563EB",
    "status_info_bg": "#EFF6FF",
    "status_info_border": "#BFDBFE"
}

# Standard Status Badge Generator
def get_status_badge_html(label: str, level: str = "optimal") -> str:
    """
    Renders a clean, text-based CSS status badge without emojis.
    Levels: optimal, monitor, alert, neutral, info
    """
    level_map = {
        "optimal": (COLORS["status_optimal"], COLORS["status_optimal_bg"], COLORS["status_optimal_border"]),
        "monitor": (COLORS["status_monitor"], COLORS["status_monitor_bg"], COLORS["status_monitor_border"]),
        "alert": (COLORS["status_alert"], COLORS["status_alert_bg"], COLORS["status_alert_border"]),
        "neutral": (COLORS["status_neutral"], COLORS["status_neutral_bg"], COLORS["status_neutral_border"]),
        "info": (COLORS["status_info"], COLORS["status_info_bg"], COLORS["status_info_border"])
    }
    color, bg, border = level_map.get(level.lower(), level_map["neutral"])
    return f"""<span style="display: inline-block; padding: 2px 8px; font-size: 0.72rem; font-weight: 600; color: {color}; background-color: {bg}; border: 1px solid {border}; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.03em;">{label}</span>"""

# Standard Metric Card HTML Generator
def get_metric_card_html(title: str, value: str, subtitle: str = "", delta: str = "", level: str = "neutral") -> str:
    """
    Renders an enterprise KPI metric card.
    """
    accent_bar = COLORS["accent"]
    if level == "alert":
        accent_bar = COLORS["status_alert"]
    elif level == "monitor":
        accent_bar = COLORS["status_monitor"]
    elif level == "optimal":
        accent_bar = COLORS["status_optimal"]
        
    return f"""
    <div style="background: {COLORS['bg_surface']}; border: 1px solid {COLORS['border']}; border-top: 3px solid {accent_bar}; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
        <div style="font-size: 0.72rem; font-weight: 600; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">{title}</div>
        <div style="font-size: 1.55rem; font-weight: 700; color: {COLORS['text_primary']}; line-height: 1.2;">{value}</div>
        {f'<div style="font-size: 0.76rem; color: {COLORS["text_secondary"]}; margin-top: 4px; font-weight: 500;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
