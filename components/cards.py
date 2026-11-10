"""
AquaMitra Reusable Component Cards & UI Elements
Provides clean, consistent UI components: Metric Cards, Pond Health Snapshots,
Smart Empty States, Unified Activity Timelines, and Alert Cards.
Strictly zero emojis.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
from components.theme import COLORS, get_status_badge_html


def render_metric_card(title: str, value: Any, subtitle: str = "", value_color: str = "#0F172A"):
    """
    Renders a clean, responsive metric KPI card without emojis.
    """
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value" style="color: {value_color};">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_pond_snapshot(snapshot: Dict[str, Any]):
    """
    Renders a compact, visually rich Pond Health Snapshot card without emojis.
    """
    status = snapshot.get("status", "Active")
    status_level = "optimal" if status == "Active" else ("monitor" if status == "Preparing" else "neutral")
    badge_html = get_status_badge_html(status, status_level)
    
    # Strip any emojis from water_status string
    water_status = str(snapshot.get("water_status", "No Data")).replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("⚪", "").strip()
    if not water_status:
        water_status = "No Data"

    st.markdown(
        f"""
        <div class="pond-snapshot-card">
            <div class="pond-snapshot-header">
                <div>
                    <h4 class="pond-snapshot-title">{snapshot['pond_id']}: {snapshot['pond_name']}</h4>
                    <span style="font-size: 0.78rem; color: #64748B;">Species: <strong>{snapshot.get('species', 'N/A')}</strong></span>
                </div>
                <div>
                    {badge_html}
                </div>
            </div>
            <div class="pond-snapshot-grid">
                <div class="snapshot-item">
                    <div class="snapshot-item-label">Fish Stock</div>
                    <div class="snapshot-item-val">{snapshot.get('fish_count', '0')}</div>
                </div>
                <div class="snapshot-item">
                    <div class="snapshot-item-label">Biomass</div>
                    <div class="snapshot-item-val">{snapshot.get('biomass', '0 kg')}</div>
                </div>
                <div class="snapshot-item">
                    <div class="snapshot-item-label">Water Status</div>
                    <div class="snapshot-item-val">{water_status}</div>
                </div>
                <div class="snapshot-item">
                    <div class="snapshot-item-label">Feed Rate</div>
                    <div class="snapshot-item-val">{snapshot.get('daily_feed', 'N/A')}</div>
                </div>
                <div class="snapshot-item">
                    <div class="snapshot-item-label">Incidents</div>
                    <div class="snapshot-item-val">{snapshot.get('incidents', '0')}</div>
                </div>
                <div class="snapshot-item">
                    <div class="snapshot-item-label">Last Activity</div>
                    <div class="snapshot-item-val" style="font-size: 0.80rem; font-weight: 600;">{snapshot.get('last_activity', 'N/A')}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_empty_state(
    icon_or_category: str,
    title: str,
    message: str,
    action_label: Optional[str] = None,
    action_key: Optional[str] = None
) -> bool:
    """
    Renders an actionable smart empty state box without emojis.
    Returns True if the action button was clicked.
    """
    st.markdown(
        f"""
        <div class="empty-state-box">
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-desc">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if action_label and action_key:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            return st.button(action_label, key=action_key, type="primary", use_container_width=True)
    return False


def render_activity_feed(activities: List[Dict[str, Any]]):
    """
    Renders a clean, unified chronological farm activity timeline without emojis.
    """
    if not activities:
        render_empty_state("Activity", "No Recent Activity", "Pond management events will appear here as you log them.")
        return

    st.markdown('<div class="saas-card" style="padding: 12px 18px;">', unsafe_allow_html=True)
    for act in activities:
        title = act.get('title', 'Event')
        # Clean any emoji from title
        clean_title = "".join(ch for ch in title if ord(ch) < 0x2600 or ord(ch) > 0x27BF and ord(ch) < 0x1F000).strip()
        if not clean_title:
            clean_title = title
            
        st.markdown(
            f"""
            <div class="timeline-item">
                <div class="timeline-date">{act.get('date', '')} {act.get('time', '')}</div>
                <div class="timeline-body">
                    <div class="timeline-title">{clean_title}</div>
                    <div class="timeline-desc">{act.get('details', '')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_alert_card(alert: Dict[str, Any], show_action: bool = True) -> bool:
    """
    Renders a compact, responsible decision-support alert card without emojis.
    Returns True if 'Mark as Resolved' was clicked.
    """
    sev = alert.get("Severity", "WARNING").upper()
    sev_class = "sev-high" if sev == "HIGH" else ("sev-warning" if sev == "WARNING" else "sev-info")
    badge_level = "alert" if sev == "HIGH" else ("monitor" if sev == "WARNING" else "info")
    badge_html = get_status_badge_html(sev, badge_level)

    title = alert.get('Title', 'Alert Notice')
    clean_title = "".join(ch for ch in title if ord(ch) < 0x2600 or ord(ch) > 0x27BF and ord(ch) < 0x1F000).strip()
    if not clean_title:
        clean_title = title

    st.markdown(
        f"""
        <div class="alert-item-card {sev_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #64748B;">
                        {alert.get('Category', 'Alert')} &bull; {alert.get('PondID', 'General')}
                    </span>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #0F172A; margin: 2px 0 4px 0;">{clean_title}</div>
                </div>
                <div>{badge_html}</div>
            </div>
            <div style="font-size: 0.84rem; color: #475569; margin-top: 4px; line-height: 1.4;">
                {alert.get('Reason', '')}
            </div>
            <div style="font-size: 0.76rem; color: #0D9488; margin-top: 6px; font-weight: 600;">
                Next Step: {alert.get('SuggestedAction', 'Monitor conditions closely.')}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if show_action and not alert.get("IsResolved"):
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button("Mark Resolved", key=f"res_{alert.get('AlertID')}", use_container_width=True):
                alert["IsResolved"] = True
                return True
    return False
