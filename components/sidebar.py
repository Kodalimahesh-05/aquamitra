"""
AquaMitra Shared Sidebar Component
Provides brand header, bilingual switcher, operating mode status, global search,
pond filter, and the 15-menu main application navigation.
Strictly zero emojis.
"""

from typing import Tuple, Optional
import streamlit as st
from utils.constants import APP_NAME, APP_TAGLINE, MENUS
from utils.translations import t
from database.connection import is_database_connected


def render_sidebar() -> Tuple[str, str, str]:
    """
    Renders the standardized AquaMitra sidebar without emojis.
    Returns:
        (active_menu_key, selected_pond_filter, search_query)
    """
    with st.sidebar:
        # 2. Operating Mode Status Badge
        if "demo_mode" not in st.session_state:
            st.session_state.demo_mode = not is_database_connected()

        lang = st.session_state.get("lang", "en")

        # 1. App Branding
        st.markdown(
            f"""
            <div style="text-align: left; padding: 4px 0 14px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 14px;">
                <div style="font-size: 1.35rem; font-weight: 800; color: #0F2942; letter-spacing: -0.02em;">{t('app_name', lang)}</div>
                <div style="color: #64748B; font-size: 0.74rem; font-weight: 500; margin-top: 2px;">{t('tagline', lang)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.demo_mode:
            st.markdown(
                f"""
                <div class="demo-mode-badge" style="width: 100%; text-align: center;">
                    {t('demo_mode_badge', lang)}<br>
                    <span style="font-size: 0.68rem; font-weight: 500; color: #065F46;">{t('storage_local_sub', lang)}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="live-mode-badge" style="width: 100%; text-align: center;">
                    {t('live_mode_badge', lang)}<br>
                    <span style="font-size: 0.68rem; font-weight: 500; color: #064E3B;">{t('storage_sql_sub', lang)}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 3. Bilingual Switcher (English | తెలుగు)
        current_lang = st.session_state.get("lang", "en")
        col_en, col_te = st.columns(2)
        with col_en:
            if st.button("English", use_container_width=True, type="primary" if current_lang == "en" else "secondary"):
                st.session_state.lang = "en"
                try:
                    st.query_params["lang"] = "en"
                except Exception:
                    pass
                st.rerun()
        with col_te:
            if st.button("తెలుగు", use_container_width=True, type="primary" if current_lang == "te" else "secondary"):
                st.session_state.lang = "te"
                try:
                    st.query_params["lang"] = "te"
                except Exception:
                    pass
                st.rerun()

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        # 4. Global Search
        search_query = st.text_input(
            "Global Search",
            value=st.session_state.get("global_search_query", ""),
            placeholder=t("search_placeholder", lang),
            label_visibility="collapsed"
        )
        st.session_state.global_search_query = search_query

        # 5. Global Pond Selector
        ponds = st.session_state.get("demo_ponds", [])
        pond_options = ["All Ponds"] + [f"{p['PondID']} - {p['PondName']}" for p in ponds]
        if st.session_state.get("global_selected_pond") not in pond_options:
            st.session_state["global_selected_pond"] = "All Ponds"
        selected_pond = st.selectbox(
            t("select_pond", lang),
            options=pond_options,
            index=0,
            key="global_selected_pond",
            format_func=lambda x: t("all_ponds", lang) if x == "All Ponds" else x
        )

        st.markdown("<div style='border-top: 1px solid #E2E8F0; margin: 12px 0;'></div>", unsafe_allow_html=True)

        # 6. Main 15-Menu Navigation (Canonical key-backed radio avoids widget ID churn)
        menu_labels = {m: t(f"menu_{m}", lang) for m in MENUS}
        desired_menu = st.session_state.get("active_menu", "overview")
        if desired_menu not in MENUS:
            desired_menu = "overview"
        if "nav_active_menu" not in st.session_state:
            st.session_state.nav_active_menu = desired_menu
        elif desired_menu != st.session_state.get("_last_rendered_menu"):
            st.session_state.nav_active_menu = desired_menu

        st.caption(t("main_navigation", lang))
        selected_menu_key = st.radio(
            "Navigation",
            options=MENUS,
            key="nav_active_menu",
            format_func=lambda m: menu_labels.get(m, m),
            label_visibility="collapsed"
        )

        st.session_state.active_menu = selected_menu_key
        st.session_state["_last_rendered_menu"] = selected_menu_key

        # 7. Sidebar Footer
        st.markdown(
            f"""
            <div style="margin-top: 24px; padding: 10px 12px; background-color: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0; font-size: 0.70rem; color: #64748B;">
                <strong>{t('footer_title', lang)}</strong><br>
                {t('footer_subtitle', lang)}
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected_menu_key, selected_pond, search_query
