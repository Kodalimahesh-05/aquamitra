"""
AquaMitra AI Intelligence View Module
Provides AquaMitra AI Conversational Companion, AI Insights Center,
Actionable AI Suggestions ([Accept Action], [Ignore]), and Daily Farm Brief.
100% Zero-Emoji Professional SaaS Interface. Fully bilingual (EN/TE).
"""

import streamlit as st
from utils.translations import tv
from services.ai.ai_service import ask_aquamitra_ai, generate_daily_briefing, generate_ai_suggestions
from services.ai.insights import generate_farm_insights
from components.cards import render_empty_state
from components.quick_actions import dialog_add_water_reading, dialog_add_growth_sample


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_ai_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "AquaMitra AI", "ఆక్వామిత్ర AI"),
        _lbl(lang, "AI Insights", "AI విశ్లేషణలు"),
        _lbl(lang, "AI Suggestions", "AI సూచనలు"),
        _lbl(lang, "Daily Brief", "రోజువారీ నివేదిక"),
        _lbl(lang, "Ask AquaMitra", "ఆక్వామిత్రను అడగండి")
    ]
    tabs = st.tabs(subtabs)

    def _fmt_cat(val: str) -> str:
        if val == "Data Quality" and lang == "te":
            return "డేటా నాణ్యత"
        return tv(val, lang)

    # 1. AquaMitra AI Conversational Assistant
    with tabs[0]:
        st.markdown(f"### {_lbl(lang, 'AquaMitra AI — Intelligent Farming Companion', 'ఆక్వామిత్ర AI — స్మార్ట్ మత్స్య సాగు సహాయకుడు')}")
        st.caption(_lbl(
            lang,
            "Ask questions about your ponds, water parameters, feed records, or finances. Answers are grounded in your farm's records.",
            "మీ చెరువులు, నీటి నాణ్యత, మేత రికార్డులు లేదా ఆర్థిక వివరాల గురించి ప్రశ్నలు అడగండి. సమాధానాలు మీ ఫార్మ్ డేటాపై ఆధారపడి ఉంటాయి."
        ))

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)

        user_input = st.chat_input(_lbl(lang, "Ask AquaMitra AI about your farm...", "మీ ఫార్మ్ గురించి ఆక్వామిత్ర AI ని అడగండి..."))
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner(_lbl(lang, "Analyzing farm records...", "ఫార్మ్ రికార్డులను విశ్లేషిస్తోంది...")):
                    res = ask_aquamitra_ai(user_input, st.session_state, lang=lang)
                    badge_clean = res['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()
                    badge_html = f"<span style='font-size: 0.70rem; color: #0E7490; background: #E0F2FE; padding: 2px 8px; border-radius: 4px; font-weight: 700;'>[{badge_clean}]</span>"
                    ans_text = f"{badge_html}\n\n{res['answer']}"
                    st.markdown(ans_text, unsafe_allow_html=True)
                    st.session_state.chat_history.append({"role": "assistant", "content": ans_text})

    # 2. AI Insights Center
    with tabs[1]:
        st.markdown(f"### {_lbl(lang, 'Categorized AI Insights & Anomaly Analysis', 'విభాగాల వారీ AI విశ్లేషణలు & అసమానతల గుర్తింపు')}")
        cat_filter = st.selectbox(
            _lbl(lang, "Category Filter", "విభాగం వడపోత"),
            options=["All", "Water Quality", "Feeding", "Mortality", "Growth", "Finance", "Data Quality"],
            key="ai_view_cat_filter",
            format_func=_fmt_cat
        )
        insights = generate_farm_insights(st.session_state, category=cat_filter)
        if insights:
            next_step_lbl = _lbl(lang, "Suggested Next Step", "తదుపరి సూచన")
            gen_lbl = _lbl(lang, "Generated", "రూపొందించబడినది")
            for ins in insights:
                sev_color = "#DC2626" if ins["severity"] == "HIGH ATTENTION" else "#D97706" if ins["severity"] == "MONITOR" else "#0D9488"
                sev_bg = "#FEF2F2" if ins["severity"] == "HIGH ATTENTION" else "#FFFBEB" if ins["severity"] == "MONITOR" else "#F0FDFA"
                sev_disp = ins.get("severity_display", ins["severity"])
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; border-left: 4px solid {sev_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <strong style="color: #0F172A; font-size: 0.98rem;">{ins['title']}</strong>
                            <span style="background: {sev_bg}; color: {sev_color}; padding: 2px 8px; border-radius: 12px; font-size: 0.72rem; font-weight: 700;">
                                {sev_disp}
                            </span>
                        </div>
                        <div style="font-size: 0.88rem; color: #334155; margin-bottom: 8px;">{ins['observation']}</div>
                        <div style="font-size: 0.80rem; color: #0E7490; font-weight: 600; margin-bottom: 6px;">{next_step_lbl}: {ins['suggested_next_step']}</div>
                        <div style="font-size: 0.72rem; color: #94A3B8;">{ins['supporting_data']} | {gen_lbl}: {ins['generated_at']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            render_empty_state(
                _lbl(lang, "info", "సమాచారం"),
                _lbl(lang, "No Insights", "విశ్లేషణలు లేవు"),
                _lbl(lang, "No anomalies or observations found for this category.", "ఈ విభాగంలో అసమానతలు లేదా పరిశీలనలు కనుగొనబడలేదు.")
            )

    # 3. AI Suggestions Center
    with tabs[2]:
        st.markdown(f"### {_lbl(lang, 'Actionable AI Suggestions Center', 'కార్యాచరణకు తగిన AI సూచనల కేంద్రం')}")
        st.caption(_lbl(
            lang,
            "Context-aware recommendations that connect directly to farm operations. Farmers maintain full manual control.",
            "ఫార్మ్ నిర్వహణకు నేరుగా సహాయపడే AI సూచనలు. తుది నిర్ణయం మరియు నియంత్రణ రైతు చేతిలోనే ఉంటుంది."
        ))
        suggestions = generate_ai_suggestions(st.session_state)

        why_lbl = _lbl(lang, "Why", "కారణం")
        based_lbl = _lbl(lang, "Based on", "ఆధారం")
        chk_lbl = _lbl(lang, "What to check", "పరిశీలించవలసిన అంశం")

        for s in suggestions:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); border-left: 5px solid #0D9488;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #0D9488; text-transform: uppercase;">{s['category']}</div>
                    <h4 style="margin: 4px 0 8px 0; color: #0F172A;">{s['title']}</h4>
                    <p style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;"><strong>{why_lbl}:</strong> {s['why']}</p>
                    <p style="font-size: 0.82rem; color: #64748B; margin-bottom: 8px;"><em>{based_lbl}: {s['based_on']}</em></p>
                    <div style="font-size: 0.85rem; color: #0F2942; font-weight: 600; margin-bottom: 12px;">{chk_lbl}: {s['what_to_check']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button(_lbl(lang, "Accept Action", "చర్యను స్వీకరించండి"), key=f"acc_{s['id']}", type="primary", use_container_width=True):
                    if s["action_menu"] == "water":
                        dialog_add_water_reading()
                    elif s["action_menu"] == "fish":
                        dialog_add_growth_sample()
                    else:
                        st.session_state.active_menu = s["action_menu"]
                        st.rerun()
            with c2:
                if st.button(_lbl(lang, "Ignore", "వదిలివేయండి"), key=f"ign_{s['id']}", use_container_width=True):
                    st.info(_lbl(lang, "Suggestion dismissed for this session.", "ఈ సెషన్ కోసం సూచన విస్మరించబడింది."))

    # 4. Daily Brief
    with tabs[3]:
        st.markdown(f"### {_lbl(lang, 'Morning Farm Brief', 'ఉదయపు ఫార్మ్ నివేదిక')}")
        st.caption(_lbl(
            lang,
            "Operational daily brief summarizing normal parameters, watch items, and practical checks.",
            "సాధారణ పారామితులు, గమనించవలసిన అంశాలు మరియు ఆచరణాత్మక తనిఖీల రోజువారీ సారాంశం."
        ))
        daily = generate_daily_briefing(st.session_state, lang=lang)
        brief_clean = daily["text"].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("📊", "").replace("💰", "").replace("💡", "").replace("🤖", "").strip()
        st.markdown(brief_clean)

    # 5. Ask AquaMitra Quick Portal
    with tabs[4]:
        st.markdown(f"### {_lbl(lang, 'Quick Farm Inquiries', 'త్వరిత ఫార్మ్ ప్రశ్నలు')}")
        st.caption(_lbl(lang, "Click any frequently asked inquiry to receive instant data analysis:", "తక్షణ డేటా విశ్లేషణ కోసం కింది ప్రశ్నలలో ఒకదాన్ని క్లిక్ చేయండి:"))
        if lang == "te":
            queries = [
                "ఏ చెరువుపై శ్రద్ధ అవసరం?",
                "నేను ఎంత మేత వాడాను?",
                "P-001 లో చేపల పెరుగుదల ఎలా ఉంది?",
                "నేను ఎక్కడ ఎక్కువ ఖర్చు చేస్తున్నాను?",
                "రికార్డుల డేటా ఆరోగ్యం తనిఖీ చేయండి"
            ]
        else:
            queries = [
                "Which pond needs attention?",
                "How much feed did I use?",
                "How is fish growth in P-001?",
                "Where am I spending the most money?",
                "Check record completeness"
            ]
        for idx, q in enumerate(queries):
            if st.button(q, key=f"portal_{lang}_{idx}", use_container_width=True):
                res = ask_aquamitra_ai(q, st.session_state, lang=lang)
                badge_clean = res['badge'].replace("🟡", "").replace("🟢", "").replace("🤖", "").strip()
                st.info(f"[{badge_clean}]\n\n{res['answer']}")
