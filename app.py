"""
AquaMitra: Digital Fishery Pond Management & Decision-Support System
AI-First Multi-Menu Application Coordinator
Strictly zero emojis. Enterprise SaaS design.
"""

import streamlit as st
from utils.constants import APP_NAME, APP_TAGLINE, MENUS
from utils.translations import t
from utils.demo_data import (
    initialize_demo_session_state,
    get_pond_health_snapshot
)
from components.styles import apply_custom_styles
from components.sidebar import render_sidebar
from components.cards import (
    render_pond_snapshot,
    render_empty_state,
    render_alert_card
)
from components.quick_actions import (
    dialog_add_pond,
    dialog_add_water_reading,
    dialog_add_growth_sample,
    dialog_add_feeding,
    dialog_add_incident,
    dialog_add_expense,
    dialog_add_sale,
    dialog_record_harvest,
    dialog_add_maintenance
)

# Import all 15 modular views
from views.overview_view import render_overview_view
from views.ponds_view import render_ponds_view
from views.fish_view import render_fish_view
from views.water_view import render_water_view
from views.feeding_view import render_feeding_view
from views.health_view import render_health_view
from views.environment_view import render_environment_view
from views.finance_view import render_finance_view
from views.assets_view import render_assets_view
from views.analytics_view import render_analytics_view
from views.alerts_view import render_alerts_view
from views.records_view import render_records_view
from views.ai_view import render_ai_view
from views.reports_view import render_reports_view
from views.settings_view import render_settings_view

# 1. Page Configuration (Strictly zero emojis)
st.set_page_config(
    page_title=f"{APP_NAME} - {APP_TAGLINE}",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. State Initialization
initialize_demo_session_state(st.session_state)
if "lang" not in st.session_state:
    req_lang = str(st.query_params.get("lang", "")).lower() if hasattr(st, "query_params") else ""
    st.session_state.lang = req_lang if req_lang in ("en", "te") else "en"
if hasattr(st, "query_params") and "menu" in st.query_params:
    req_menu = str(st.query_params["menu"]).lower()
    if req_menu in MENUS and req_menu != st.session_state.get("_last_qp_menu"):
        st.session_state.active_menu = req_menu
        st.session_state._last_qp_menu = req_menu
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "overview"
_curr_lang_init = st.session_state.get("lang", "en")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": t("ai_welcome_chat", _curr_lang_init)}
    ]
elif len(st.session_state.chat_history) == 1 and st.session_state.chat_history[0].get("role") == "assistant":
    st.session_state.chat_history[0]["content"] = t("ai_welcome_chat", _curr_lang_init)

# 3. Apply Styles & Render Shared Sidebar
apply_custom_styles()
active_menu, selected_pond, search_query = render_sidebar()
lang = st.session_state.get("lang", "en")

# 4. Standard Top Page Header
menu_titles = {m: (t(f"title_{m}", lang), t(f"desc_{m}", lang)) for m in MENUS}

curr_title, curr_desc = menu_titles.get(active_menu, (t("app_name", lang), t("tagline", lang)))

st.markdown(
    f"""
    <div class="page-header">
        <h1>{curr_title}</h1>
        <p>{curr_desc}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 5. Global Search Handler
if search_query and search_query.strip():
    q = search_query.strip().lower()
    st.markdown(f"##### {t('search_results_for', lang)} *\"{search_query}\"*")

    matched_ponds = [p for p in st.session_state.demo_ponds if q in p.get("PondName", "").lower() or q in p.get("PondID", "").lower() or q in p.get("Location", "").lower()]
    matched_alerts = [a for a in st.session_state.demo_alerts if q in a.get("Title", "").lower() or q in a.get("Reason", "").lower() or q in a.get("Category", "").lower()]

    col_p, col_a = st.columns(2)
    with col_p:
        st.caption(f"{t('ponds_matched', lang)} ({len(matched_ponds)})")
        if matched_ponds:
            for p in matched_ponds:
                snap = get_pond_health_snapshot(p["PondID"])
                render_pond_snapshot(snap)
        else:
            render_empty_state(t("ponds_label", lang), t("no_matching_ponds_title", lang), f"{t('no_matching_ponds_msg', lang)} '{search_query}'.")

    with col_a:
        st.caption(f"{t('alerts_matched', lang)} ({len(matched_alerts)})")
        if matched_alerts:
            for a in matched_alerts:
                render_alert_card(a)
        else:
            render_empty_state(t("alerts_label", lang), t("no_matching_alerts_title", lang), f"{t('no_matching_alerts_msg', lang)} '{search_query}'.")

    st.markdown("<div style='border-top: 1px solid #E2E8F0; margin: 16px 0;'></div>", unsafe_allow_html=True)

# 6. Global Quick Actions Bar (All 9 Workflows, Zero Emojis)
st.caption(t("quick_actions", lang))
st.markdown('<div class="quick-actions-container">', unsafe_allow_html=True)
qa1, qa2, qa3, qa4, qa5, qa6, qa7, qa8, qa9 = st.columns(9)
with qa1:
    if st.button(t("qa_add_pond", lang), use_container_width=True, key="top_qa_add_pond"):
        dialog_add_pond()
with qa2:
    if st.button(t("qa_log_water", lang), use_container_width=True, key="top_qa_rec_water"):
        dialog_add_water_reading()
with qa3:
    if st.button(t("qa_add_growth", lang), use_container_width=True, key="top_qa_add_growth"):
        dialog_add_growth_sample()
with qa4:
    if st.button(t("qa_log_feed", lang), use_container_width=True, key="top_qa_rec_feed"):
        dialog_add_feeding()
with qa5:
    if st.button(t("qa_log_incident", lang), use_container_width=True, key="top_qa_rec_incident"):
        dialog_add_incident()
with qa6:
    if st.button(t("qa_add_expense", lang), use_container_width=True, key="top_qa_add_expense"):
        dialog_add_expense()
with qa7:
    if st.button(t("qa_record_sale", lang), use_container_width=True, key="top_qa_rec_sale"):
        dialog_add_sale()
with qa8:
    if st.button(t("qa_record_harvest", lang), use_container_width=True, key="top_qa_rec_harvest"):
        dialog_record_harvest()
with qa9:
    if st.button(t("qa_add_maintenance", lang), use_container_width=True, key="top_qa_add_maint"):
        dialog_add_maintenance()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='border-top: 1px solid #E2E8F0; margin: 12px 0 18px 0;'></div>", unsafe_allow_html=True)

# 7. Active 15-Menu Dispatcher
if active_menu == "overview":
    render_overview_view()
elif active_menu == "ponds":
    render_ponds_view()
elif active_menu == "fish":
    render_fish_view()
elif active_menu == "water":
    render_water_view()
elif active_menu == "feeding":
    render_feeding_view()
elif active_menu == "health":
    render_health_view()
elif active_menu == "environment":
    render_environment_view()
elif active_menu == "finance":
    render_finance_view()
elif active_menu == "assets":
    render_assets_view()
elif active_menu == "analytics":
    render_analytics_view()
elif active_menu == "alerts":
    render_alerts_view()
elif active_menu == "records":
    render_records_view()
elif active_menu == "ai":
    render_ai_view()
elif active_menu == "reports":
    render_reports_view()
elif active_menu == "settings":
    render_settings_view()
