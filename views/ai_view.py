"""
AquaMitra AI Intelligence View Module
Provides AquaMitra AI Conversational Companion, AI Insights Center,
Actionable AI Suggestions ([Accept Action], [Ignore]), and Daily Farm Brief.
100% Zero-Emoji Professional SaaS Interface.
"""

import streamlit as st
from services.ai.ai_service import ask_aquamitra_ai, generate_daily_briefing, generate_ai_suggestions
from services.ai.insights import generate_farm_insights
from components.cards import render_empty_state
from components.quick_actions import dialog_add_water_reading, dialog_add_growth_sample


def render_ai_view():
    subtabs = ["AquaMitra AI", "AI Insights", "AI Suggestions", "Daily Brief", "Ask AquaMitra"]
    tabs = st.tabs(subtabs)

    # 1. AquaMitra AI Conversational Assistant
    with tabs[0]:
        st.markdown("### AquaMitra AI — Intelligent Farming Companion")
        st.caption("Ask questions about your ponds, water parameters, feed records, or finances. Answers are grounded in your farm's records.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)

        user_input = st.chat_input("Ask AquaMitra AI about your farm...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing farm records..."):
                    res = ask_aquamitra_ai(user_input, st.session_state)
                    badge_clean = res['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()
                    badge_html = f"<span style='font-size: 0.70rem; color: #0E7490; background: #E0F2FE; padding: 2px 8px; border-radius: 4px; font-weight: 700;'>[{badge_clean}]</span>"
                    ans_text = f"{badge_html}\n\n{res['answer']}"
                    st.markdown(ans_text, unsafe_allow_html=True)
                    st.session_state.chat_history.append({"role": "assistant", "content": ans_text})

    # 2. AI Insights Center
    with tabs[1]:
        st.markdown("### Categorized AI Insights & Anomaly Analysis")
        cat_filter = st.selectbox("Category Filter", options=["All", "Water Quality", "Feeding", "Mortality", "Growth", "Finance", "Data Quality"], key="ai_view_cat_filter")
        insights = generate_farm_insights(st.session_state, category=cat_filter)
        if insights:
            for ins in insights:
                sev_color = "#DC2626" if ins["severity"] == "HIGH ATTENTION" else "#D97706" if ins["severity"] == "MONITOR" else "#0D9488"
                sev_bg = "#FEF2F2" if ins["severity"] == "HIGH ATTENTION" else "#FFFBEB" if ins["severity"] == "MONITOR" else "#F0FDFA"
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; border-left: 4px solid {sev_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #0F172A; font-size: 0.98rem;">{ins['title']}</strong>
                            <span style="background: {sev_bg}; color: {sev_color}; padding: 2px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700;">
                                {ins['severity']}
                            </span>
                        </div>
                        <div style="font-size: 0.88rem; color: #334155; margin-bottom: 8px;">{ins['observation']}</div>
                        <div style="font-size: 0.80rem; color: #0E7490; font-weight: 600; margin-bottom: 6px;">Suggested Next Step: {ins['suggested_next_step']}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8;">{ins['supporting_data']} | Generated: {ins['generated_at']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            render_empty_state("info", "No Insights", "No anomalies or observations found for this category.")

    # 3. AI Suggestions Center
    with tabs[2]:
        st.markdown("### Actionable AI Suggestions Center")
        st.caption("Context-aware recommendations that connect directly to farm operations. Farmers maintain full manual control.")
        suggestions = generate_ai_suggestions(st.session_state)

        for s in suggestions:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border-left: 5px solid #0D9488;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #0D9488; text-transform: uppercase;">{s['category']}</div>
                    <h4 style="margin: 4px 0 8px 0; color: #0F172A;">{s['title']}</h4>
                    <p style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;"><strong>Why:</strong> {s['why']}</p>
                    <p style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;"><em>Based on: {s['based_on']}</em></p>
                    <div style="font-size: 0.85rem; color: #0F2942; font-weight: 600; margin-bottom: 12px;">What to check: {s['what_to_check']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("Accept Action", key=f"acc_{s['id']}", type="primary", use_container_width=True):
                    if s["action_menu"] == "water":
                        dialog_add_water_reading()
                    elif s["action_menu"] == "fish":
                        dialog_add_growth_sample()
                    else:
                        st.session_state.active_menu = s["action_menu"]
                        st.rerun()
            with c2:
                if st.button("Ignore", key=f"ign_{s['id']}", use_container_width=True):
                    st.info("Suggestion dismissed for this session.")

    # 4. Daily Brief
    with tabs[3]:
        st.markdown("### Morning Farm Brief")
        st.caption("Operational daily brief summarizing normal parameters, watch items, and practical checks.")
        daily = generate_daily_briefing(st.session_state)
        brief_clean = daily["text"].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("📊", "").replace("💰", "").replace("💡", "").replace("🤖", "").strip()
        st.markdown(brief_clean)

    # 5. Ask AquaMitra Quick Portal
    with tabs[4]:
        st.markdown("### Quick Farm Inquiries")
        st.caption("Click any frequently asked inquiry to receive instant data analysis:")
        queries = [
            "Which pond needs attention?",
            "How much feed did I use?",
            "How is fish growth in P-001?",
            "Where am I spending the most money?",
            "Check record completeness"
        ]
        for q in queries:
            if st.button(q, key=f"portal_{q}", use_container_width=True):
                res = ask_aquamitra_ai(q, st.session_state)
                badge_clean = res['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()
                st.info(f"[{badge_clean}]\n\n{res['answer']}")
