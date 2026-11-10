"""
AquaMitra Styling & UI Components
Enterprise SaaS stylesheet: Clean typography, subtle borders, deep navy/teal accents.
Strictly zero emojis.
"""

import streamlit as st
from components.theme import COLORS


def apply_custom_styles():
    """
    Injects custom CSS to style AquaMitra with a professional agricultural SaaS aesthetic.
    """
    st.markdown(
        f"""
        <style>
        /* Global Page Background, Font & Modern Typography */
        .stApp {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_primary']};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            overflow-wrap: anywhere;
        }}

        h1, h2, h3, h4 {{
            text-wrap: balance;
        }}
        p, li {{
            text-wrap: pretty;
        }}

        /* Clean Main Header Block */
        .page-header {{
            background: {COLORS['bg_surface']};
            border-bottom: 1px solid {COLORS['border']};
            padding: 16px 24px;
            margin: -1rem -1rem 1.5rem -1rem;
        }}
        .page-header h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {COLORS['primary']};
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .page-header p {{
            font-size: 0.85rem;
            color: {COLORS['text_muted']};
            margin: 4px 0 0 0;
        }}

        /* Standard SaaS Card Container */
        .saas-card {{
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }}

        /* KPI Metric Card */
        .metric-card {{
            background: {COLORS['bg_surface']};
            border-radius: 8px;
            padding: 14px 18px;
            border: 1px solid {COLORS['border']};
            border-top: 3px solid {COLORS['accent']};
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
            margin-bottom: 12px;
            height: 100%;
            min-height: 105px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .metric-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
            border-color: {COLORS['accent']};
        }}
        .metric-title {{
            font-size: 0.72rem;
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .metric-value {{
            font-size: 1.55rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            line-height: 1.2;
        }}
        .metric-subtitle {{
            font-size: 0.76rem;
            color: {COLORS['text_secondary']};
            margin-top: 4px;
            font-weight: 500;
        }}

        /* Pond Profile Summary Card */
        .pond-snapshot-card {{
            background: {COLORS['bg_surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            border-left: 4px solid {COLORS['primary']};
        }}
        .pond-snapshot-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            border-bottom: 1px solid {COLORS['border_subtle']};
            padding-bottom: 8px;
        }}
        .pond-snapshot-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: {COLORS['primary']};
            margin: 0;
        }}
        .pond-snapshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(105px, 1fr));
            gap: 10px;
            margin-top: 8px;
        }}
        .snapshot-item {{
            background: {COLORS['bg_main']};
            padding: 8px 10px;
            border-radius: 6px;
            border: 1px solid {COLORS['border_subtle']};
        }}
        .snapshot-item-label {{
            font-size: 0.68rem;
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 2px;
        }}
        .snapshot-item-val {{
            font-size: 0.90rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
        }}

        /* Subtle Status Badges (Text-only) */
        .status-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .status-optimal {{
            background-color: {COLORS['status_optimal_bg']};
            color: {COLORS['status_optimal']};
            border: 1px solid {COLORS['status_optimal_border']};
        }}
        .status-monitor {{
            background-color: {COLORS['status_monitor_bg']};
            color: {COLORS['status_monitor']};
            border: 1px solid {COLORS['status_monitor_border']};
        }}
        .status-alert {{
            background-color: {COLORS['status_alert_bg']};
            color: {COLORS['status_alert']};
            border: 1px solid {COLORS['status_alert_border']};
        }}
        .status-neutral {{
            background-color: {COLORS['status_neutral_bg']};
            color: {COLORS['status_neutral']};
            border: 1px solid {COLORS['border']};
        }}
        .status-info {{
            background-color: {COLORS['status_info_bg']};
            color: {COLORS['status_info']};
            border: 1px solid {COLORS['status_info_border']};
        }}

        /* Operating Mode Indicators */
        .demo-mode-badge {{
            background-color: #ECFDF5;
            color: #065F46;
            border: 1px solid #A7F3D0;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        .live-mode-badge {{
            background-color: #D1FAE5;
            color: #065F46;
            border: 1px solid #6EE7B7;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}

        /* Alert Notification Cards */
        .alert-item-card {{
            background: {COLORS['bg_surface']};
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 10px;
            border: 1px solid {COLORS['border']};
            border-left-width: 4px;
        }}
        .alert-item-card.sev-high {{
            border-left-color: {COLORS['status_alert']};
        }}
        .alert-item-card.sev-warning {{
            border-left-color: {COLORS['status_monitor']};
        }}
        .alert-item-card.sev-info {{
            border-left-color: {COLORS['status_info']};
        }}

        /* AI Insight Banner (Restrained Professional Styling) */
        .ai-banner {{
            background: #0F172A;
            border: 1px solid #1E293B;
            border-left: 4px solid {COLORS['accent']};
            border-radius: 8px;
            padding: 16px 20px;
            color: #F8FAFC;
            margin-bottom: 18px;
        }}
        .ai-banner-title {{
            font-size: 0.88rem;
            font-weight: 700;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }}
        .ai-banner-content {{
            font-size: 0.88rem;
            color: #E2E8F0;
            line-height: 1.5;
        }}

        /* Empty State */
        .empty-state-box {{
            background: {COLORS['bg_surface']};
            border: 1px dashed {COLORS['border']};
            border-radius: 8px;
            padding: 36px 20px;
            text-align: center;
            margin: 16px 0;
        }}
        .empty-state-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            margin-bottom: 6px;
        }}
        .empty-state-desc {{
            font-size: 0.84rem;
            color: {COLORS['text_muted']};
            max-width: 420px;
            margin: 0 auto 16px auto;
        }}

        /* Activity Timeline */
        .timeline-item {{
            display: flex;
            align-items: flex-start;
            padding: 10px 0;
            border-bottom: 1px solid {COLORS['border_subtle']};
        }}
        .timeline-date {{
            font-size: 0.74rem;
            font-weight: 600;
            color: {COLORS['text_muted']};
            min-width: 85px;
            padding-top: 2px;
        }}
        .timeline-body {{
            flex: 1;
        }}
        .timeline-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: {COLORS['text_primary']};
        }}
        .timeline-desc {{
            font-size: 0.78rem;
            color: {COLORS['text_secondary']};
            margin-top: 2px;
        }}

        /* Quick Action Bar Buttons & Layout */
        .quick-actions-container {{
            width: 100%;
            margin-bottom: 8px;
        }}
        .quick-actions-container div[data-testid="stHorizontalBlock"] .stButton button,
        div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) .stButton button {{
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.82rem;
            letter-spacing: 0.01em;
            padding: 8px 12px;
            white-space: nowrap;
        }}

        /* Tables & DataFrames */
        .stDataFrame, div[data-testid="stTable"] {{
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            max-width: 100% !important;
        }}

        /* Responsive Streamlit Tabs with Horizontal Swipe */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid {COLORS['border']};
            display: flex !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            padding-bottom: 2px;
        }}
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{
            display: none;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding: 8px 16px;
            font-size: 0.86rem;
            font-weight: 600;
            color: {COLORS['text_secondary']};
            border-radius: 6px 6px 0 0;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {COLORS['primary']} !important;
            border-bottom: 2px solid {COLORS['accent']} !important;
        }}

        /* Charts Container */
        .js-plotly-plot, .plot-container {{
            max-width: 100% !important;
        }}

        /* ===================================================== */
        /* MOBILE VIEW OPTIMIZATIONS (Smartphones & Touch Screens) */
        /* ===================================================== */

        /* Target size adaptation for touch screens (WCAG 2.5.5) */
        @media (pointer: coarse) {{
            button, select, input, [role="button"] {{
                min-height: 44px;
                touch-action: manipulation;
            }}
        }}

        @media (max-width: 768px) {{
            /* Page Header on Mobile with Safe Area */
            .page-header {{
                padding: 12px 14px !important;
                margin: -0.5rem -0.5rem 1rem -0.5rem !important;
                padding-top: max(12px, env(safe-area-inset-top, 0px)) !important;
            }}
            .page-header h1 {{
                font-size: 1.25rem !important;
            }}
            .page-header p {{
                font-size: 0.78rem !important;
            }}

            /* Quick Action Chips Carousel on Mobile */
            .quick-actions-container div[data-testid="stHorizontalBlock"],
            div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) {{
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch !important;
                gap: 8px !important;
                padding-bottom: 8px !important;
                padding-top: 2px !important;
                scrollbar-width: thin;
            }}
            .quick-actions-container div[data-testid="column"],
            div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div[data-testid="column"] {{
                flex: 0 0 auto !important;
                width: auto !important;
                min-width: 125px !important;
            }}
            .quick-actions-container button,
            div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) button {{
                min-height: 42px !important;
                padding: 8px 14px !important;
            }}

            /* Responsive 2-Column KPI Cards Grid on Mobile */
            div[data-testid="stHorizontalBlock"]:has(.metric-card) {{
                display: flex !important;
                flex-wrap: wrap !important;
                gap: 8px !important;
            }}
            div[data-testid="stHorizontalBlock"]:has(.metric-card) > div[data-testid="column"] {{
                flex: 1 1 calc(50% - 6px) !important;
                min-width: calc(50% - 6px) !important;
                max-width: calc(50% - 6px) !important;
            }}
            .metric-card {{
                padding: 10px 12px !important;
                margin-bottom: 4px !important;
            }}
            .metric-title {{
                font-size: 0.65rem !important;
            }}
            .metric-value {{
                font-size: 1.25rem !important;
            }}
            .metric-subtitle {{
                font-size: 0.68rem !important;
            }}

            /* Pond Snapshot Grid on Mobile */
            .pond-snapshot-grid {{
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 6px !important;
            }}
            .pond-snapshot-card {{
                padding: 12px 14px !important;
                margin-bottom: 10px !important;
            }}
            .snapshot-item {{
                padding: 6px 8px !important;
            }}
            .snapshot-item-label {{
                font-size: 0.62rem !important;
            }}
            .snapshot-item-val {{
                font-size: 0.82rem !important;
            }}

            /* Subtabs Sizing on Mobile */
            .stTabs [data-baseweb="tab"] {{
                padding: 10px 14px !important;
                font-size: 0.82rem !important;
                min-height: 42px !important;
            }}

            /* AI Banner & Alert Items on Mobile */
            .ai-banner {{
                padding: 12px 14px !important;
                margin-bottom: 12px !important;
            }}
            .ai-banner-title {{
                font-size: 0.80rem !important;
            }}
            .ai-banner-content {{
                font-size: 0.82rem !important;
            }}

            /* Floating Chat Input Safe Area Padding */
            [data-testid="stChatInput"] {{
                padding-bottom: max(10px, env(safe-area-inset-bottom, 0px)) !important;
            }}

            /* General Buttons on Touch Devices */
            .stButton > button {{
                min-height: 42px !important;
                touch-action: manipulation;
            }}
        }}

        /* Hide unwanted default Streamlit styling */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True
    )
