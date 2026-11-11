"""
AquaMitra Finance View Module
Provides Finance Dashboard, Expenses, Purchases, Labour, Sales,
and Payments with strictly zero emojis. Fully bilingual (EN/TE).
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.translations import tv, rename_df_for_display
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_expense, dialog_add_sale
from services.ai.ai_service import analyze_finances
from database.queries import get_expenses, get_sales


def _lbl(lang: str, en: str, te: str) -> str:
    return te if lang == "te" else en


def render_finance_view():
    lang = st.session_state.get("lang", "en")
    subtabs = [
        _lbl(lang, "Finance Dashboard", "ఆర్థిక డాష్‌బోర్డ్"),
        _lbl(lang, "Expenses", "ఖర్చులు"),
        _lbl(lang, "Purchases", "కొనుగోళ్లు"),
        _lbl(lang, "Labour", "కూలీ వివరాలు"),
        _lbl(lang, "Sales", "అమ్మకాలు"),
        _lbl(lang, "Payments", "చెల్లింపులు")
    ]
    tabs = st.tabs(subtabs)

    expenses = get_expenses()
    sales = get_sales()
    purchases = st.session_state.get("demo_purchases", [])
    labour = st.session_state.get("demo_labour", [])

    tot_exp = sum(e.get("Amount", 0) for e in expenses)
    tot_rev = sum(s.get("TotalRevenue", 0) for s in sales)
    net_diff = tot_rev - tot_exp

    purch_cats_te = {
        "Chemicals & Minerals": "రసాయనాలు మరియు ఖనిజాలు",
        "Feed": "మేత",
        "Seed": "చేప పిల్లలు",
        "Equipment Parts": "పరికరాల భాగాలు",
        "Fuel & Energy": "ఇంధనం మరియు విద్యుత్",
        "Other": "ఇతరములు",
    }
    role_te = {
        "Netting & Harvesting Crew": "వలలు వేసే మరియు కోత బృందం",
        "Daily Feeding & Guarding": "రోజువారీ మేత మరియు కాపలా",
        "Dyke & Pond Repair": "గట్టు మరియు చెరువు మరమ్మతు",
        "Aerator Maintenance": "ఏరేటర్ నిర్వహణ",
        "Other": "ఇతరములు",
    }

    # 1. Finance Dashboard
    with tabs[0]:
        st.markdown(f"#### {_lbl(lang, 'Farm Financial Dashboard', 'ఫార్మ్ ఆర్థిక డాష్‌బోర్డ్')}")
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button(_lbl(lang, "Analyze Finances with AI", "AI తో ఆర్థిక విశ్లేషణ"), type="secondary", use_container_width=True):
                st.session_state.show_fin_ai = True

        if st.session_state.get("show_fin_ai", False):
            f_ai = analyze_finances(st.session_state)
            clean_obs = f_ai['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = f_ai['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_att = f_ai['attention'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = f_ai['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(
                f"**{_lbl(lang, 'Observation', 'పరిశీలన')}:** {clean_obs}\n\n"
                f"**{_lbl(lang, 'Trend', 'ధోరణి')}:** {clean_tr}\n\n"
                f"**{_lbl(lang, 'Attention Area', 'శ్రద్ధ వహించాల్సిన అంశం')}:** {clean_att}\n\n"
                f"**{_lbl(lang, 'Suggested Action', 'సూచించిన చర్య')}:** {clean_ck}"
            )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card(
                _lbl(lang, "Total Recorded Revenue", "మొత్తం నమోదైన ఆదాయం"),
                f"₹{tot_rev:,.0f}",
                f"{len(sales)} {_lbl(lang, 'Sales Transactions', 'అమ్మకం లావాదేవీలు')}"
            )
        with c2:
            render_metric_card(
                _lbl(lang, "Total Operational Expenses", "మొత్తం నిర్వహణ ఖర్చులు"),
                f"₹{tot_exp:,.0f}",
                f"{len(expenses)} {_lbl(lang, 'Recorded Costs', 'నమోదైన ఖర్చులు')}"
            )
        with c3:
            render_metric_card(
                _lbl(lang, "Estimated Net Difference", "అంచనా నికర తేడా"),
                f"{'+' if net_diff >= 0 else ''}₹{net_diff:,.0f}",
                _lbl(lang, "Operating Variance", "నిర్వహణ వ్యత్యాసం"),
                value_color="#059669" if net_diff >= 0 else "#DC2626"
            )
        with c4:
            feed_exp = sum(e.get("Amount", 0) for e in expenses if e.get("Category") == "Feed")
            pct = int(feed_exp / tot_exp * 100) if tot_exp else 0
            render_metric_card(
                _lbl(lang, "Feed Expenditure", "మేత ఖర్చు"),
                f"₹{feed_exp:,.0f}",
                f"{pct}% {_lbl(lang, 'of Total Expenses', 'మొత్తం ఖర్చులలో')}"
            )

        st.caption(_lbl(
            lang,
            "Notice: Financial metrics represent user-recorded operational figures. Figures are labeled Estimated Net Difference and do not represent audited statutory accounting.",
            "గమనిక: ఆర్థిక గణాంకాలు వినియోగదారు నమోదు చేసిన నిర్వహణ వివరాలను మాత్రమే చూపుతాయి. ఇవి ఆడిట్ చేసిన చట్టబద్ధమైన ఖాతాలు కావు."
        ))

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if expenses:
                df_exp = pd.DataFrame(expenses)
                df_exp["CategoryDisplay"] = df_exp["Category"].apply(lambda c: tv(c, lang))
                fig_exp_cat = px.pie(
                    df_exp,
                    names="CategoryDisplay",
                    values="Amount",
                    hole=0.4,
                    title=_lbl(lang, "Expenses by Operational Category", "విభాగం వారీగా నిర్వహణ ఖర్చులు")
                )
                fig_exp_cat.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_exp_cat, use_container_width=True)
        with col_g2:
            if sales:
                df_sl = pd.DataFrame(sales)
                fig_sales = px.bar(
                    df_sl,
                    x="BuyerMarket",
                    y="TotalRevenue",
                    color="Species",
                    title=_lbl(lang, "Harvest Revenue by Buyer / Market (₹)", "కొనుగోలుదారు / మార్కెట్ వారీగా ఆదాయం (₹)"),
                    labels={
                        "BuyerMarket": _lbl(lang, "Buyer / Market", "కొనుగోలుదారు / మార్కెట్"),
                        "TotalRevenue": _lbl(lang, "Total Revenue (₹)", "మొత్తం ఆదాయం (₹)"),
                        "Species": _lbl(lang, "Species", "చేప జాతి")
                    }
                )
                fig_sales.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_sales, use_container_width=True)

    # 2. Expenses
    with tabs[1]:
        st.markdown(f"#### {_lbl(lang, 'Operational Expenses Ledger', 'నిర్వహణ ఖర్చుల ఖాతా')}")
        e_top1, e_top2 = st.columns([3, 1])
        with e_top2:
            if st.button(_lbl(lang, "Add Expense Record", "ఖర్చు రికార్డు జోడించు"), type="primary", use_container_width=True):
                dialog_add_expense()

        if expenses:
            df_e = pd.DataFrame(expenses)
            if "ExpenseDate" in df_e.columns:
                df_e = df_e.sort_values("ExpenseDate", ascending=False)
            e_cols = ["ExpenseID", "PondID", "ExpenseDate", "Category", "Description", "Quantity", "Amount", "Notes"]
            for col in e_cols:
                if col not in df_e.columns:
                    df_e[col] = ""
            st.dataframe(rename_df_for_display(df_e[e_cols], lang), use_container_width=True, hide_index=True)

            with st.expander(_lbl(lang, "Manage Expense Records", "ఖర్చు రికార్డులను నిర్వహించండి")):
                del_eid = st.selectbox(_lbl(lang, "Select Expense ID to Delete", "తొలగించాల్సిన ఖర్చు ID ఎంచుకోండి"), options=[e.get("ExpenseID") for e in expenses])
                if st.button(_lbl(lang, "Delete Expense Record", "ఖర్చు రికార్డును తొలగించండి"), type="secondary"):
                    st.session_state.demo_expenses = [e for e in st.session_state.demo_expenses if e.get("ExpenseID") != del_eid]
                    st.success(_lbl(lang, "Expense removed successfully.", "ఖర్చు రికార్డు తొలగించబడింది."))
                    st.rerun()
        else:
            render_empty_state(
                _lbl(lang, "Expenses", "ఖర్చులు"),
                _lbl(lang, "No Expenses Recorded", "ఖర్చులు నమోదు కాలేదు"),
                _lbl(lang, "Add operational cost entries.", "నిర్వహణ ఖర్చు ఎంట్రీలను జోడించండి."),
                _lbl(lang, "Add Expense", "ఖర్చు జోడించు"),
                "exp_empty_btn"
            )

    # 3. Purchases
    with tabs[2]:
        st.markdown(f"#### {_lbl(lang, 'Commercial Procurement & Purchases', 'వాణిజ్య కొనుగోళ్ల వివరాలు')}")
        with st.expander(_lbl(lang, "Log Material / Supply Purchase", "కొనుగోలు / సామగ్రి బిల్లు నమోదు చేయండి")):
            with st.form("add_purch_form", clear_on_submit=True):
                p1, p2 = st.columns(2)
                with p1:
                    p_date = st.date_input(_lbl(lang, "Purchase Date", "కొనుగోలు తేదీ"), value=date.today())
                    p_item = st.text_input(_lbl(lang, "Item Name *", "వస్తువు పేరు *"), placeholder=_lbl(lang, "e.g. Agricultural Dolomite Lime", "ఉదా. వ్యవసాయ డోలమైట్ సున్నం"))
                    p_cat = st.selectbox(
                        _lbl(lang, "Category", "విభాగం"),
                        options=["Chemicals & Minerals", "Feed", "Seed", "Equipment Parts", "Fuel & Energy", "Other"],
                        format_func=lambda x: purch_cats_te.get(x, x) if lang == "te" else x
                    )
                    p_sup = st.text_input(_lbl(lang, "Supplier / Merchant", "సరఫరాదారు / వ్యాపారి"), placeholder="e.g. Godavari Aqua Inputs")
                with p2:
                    p_qty = st.number_input(_lbl(lang, "Quantity *", "పరిమాణం *"), min_value=1.0, value=20.0, step=5.0)
                    p_unit = st.text_input(_lbl(lang, "Unit (e.g. Bags, Liters, kg)", "యూనిట్ (బస్తాలు, లీటర్లు, కేజీ)"), value="Bags (50kg)")
                    p_price = st.number_input(_lbl(lang, "Unit Price (₹) *", "యూనిట్ ధర (₹) *"), min_value=1.0, value=350.0, step=25.0)
                    p_inv = st.text_input(_lbl(lang, "Invoice / Receipt Number", "ఇన్‌వాయిస్ / రసీదు నంబర్"), placeholder="e.g. INV-2026-089")

                p_submit = st.form_submit_button(_lbl(lang, "Save Purchase Record", "కొనుగోలు రికార్డును సేవ్ చేయండి"), type="primary")
                if p_submit:
                    if not p_item:
                        st.error(_lbl(lang, "Item name is required.", "వస్తువు పేరు తప్పనిసరి."))
                    else:
                        tot_cost = round(float(p_qty) * float(p_price), 2)
                        new_purch = {
                            "PurchaseID": len(purchases) + 1,
                            "Date": p_date.strftime("%Y-%m-%d"),
                            "Item": p_item.strip(),
                            "Category": p_cat,
                            "Supplier": p_sup.strip(),
                            "Quantity": float(p_qty),
                            "Unit": p_unit.strip(),
                            "UnitPrice": float(p_price),
                            "TotalPrice": tot_cost,
                            "PondID": "General Farm",
                            "InvoiceNumber": p_inv.strip(),
                            "Notes": "Purchased for pond water conditioning."
                        }
                        st.session_state.demo_purchases.append(new_purch)
                        st.success(_lbl(lang, f"Recorded purchase of {p_item} (Total: ₹{tot_cost:,.0f}).", f"{p_item} కొనుగోలు నమోదైంది (మొత్తం: ₹{tot_cost:,.0f})."))
                        st.rerun()

        if purchases:
            df_purch = pd.DataFrame(purchases)
            p_cols = ["PurchaseID", "Date", "Item", "Category", "Supplier", "Quantity", "Unit", "UnitPrice", "TotalPrice", "InvoiceNumber"]
            for col in p_cols:
                if col not in df_purch.columns:
                    df_purch[col] = ""
            disp_purch = rename_df_for_display(df_purch[p_cols], lang)
            if lang == "te":
                disp_purch = disp_purch.rename(columns={
                    "PurchaseID": "కొనుగోలు ID",
                    "Item": "వస్తువు",
                    "Supplier": "సరఫరాదారు",
                    "Unit": "యూనిట్",
                    "TotalPrice": "మొత్తం ధర (₹)",
                    "InvoiceNumber": "ఇన్‌వాయిస్ నంబర్"
                })
            st.dataframe(disp_purch, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Purchases", "కొనుగోళ్లు"),
                _lbl(lang, "No Purchases Logged", "కొనుగోళ్లు నమోదు కాలేదు"),
                _lbl(lang, "Log material and supply purchase receipts.", "సామగ్రి కొనుగోలు రసీదులను నమోదు చేయండి.")
            )

    # 4. Labour
    with tabs[3]:
        st.markdown(f"#### {_lbl(lang, 'Farm Labour & Workforce Register', 'ఫార్మ్ కూలీ మరియు కార్మికుల రిజిస్టర్')}")
        with st.expander(_lbl(lang, "Record Labour Payment", "కూలీ చెల్లింపును నమోదు చేయండి")):
            with st.form("add_labour_form", clear_on_submit=True):
                l1, l2 = st.columns(2)
                with l1:
                    l_date = st.date_input(_lbl(lang, "Date", "తేదీ"), value=date.today())
                    worker = st.text_input(_lbl(lang, "Worker / Team Name *", "కార్మికుడు / బృందం పేరు *"), placeholder="e.g. K. Prasad & Team")
                    role = st.selectbox(
                        _lbl(lang, "Role / Task", "పని విభాగం"),
                        options=["Netting & Harvesting Crew", "Daily Feeding & Guarding", "Dyke & Pond Repair", "Aerator Maintenance", "Other"],
                        format_func=lambda x: role_te.get(x, x) if lang == "te" else x
                    )
                with l2:
                    hours = st.number_input(_lbl(lang, "Hours Worked", "పనిచేసిన గంటలు"), min_value=1.0, value=8.0, step=1.0)
                    rate = st.number_input(_lbl(lang, "Rate per Hour or Daily Rate (₹)", "రోజువారీ లేదా గంటకు వేతనం (₹)"), min_value=50.0, value=600.0, step=50.0)
                    l_notes = st.text_input(_lbl(lang, "Work Notes", "పని గమనికలు"), placeholder=_lbl(lang, "e.g. 3-point sample dragnetting in Pond 1", "ఉదా. చెరువు 1 లో నమూనా వల వేత"))

                l_submit = st.form_submit_button(_lbl(lang, "Save Labour Record", "కూలీ రికార్డును సేవ్ చేయండి"), type="primary")
                if l_submit:
                    if not worker:
                        st.error(_lbl(lang, "Worker name is required.", "కార్మికుడి పేరు తప్పనిసరి."))
                    else:
                        new_lab = {
                            "LabourID": len(labour) + 1,
                            "Worker": worker.strip(),
                            "Role": role,
                            "Date": l_date.strftime("%Y-%m-%d"),
                            "PondID": "General Farm",
                            "WorkType": role,
                            "Hours": float(hours),
                            "Rate": float(rate),
                            "TotalCost": float(rate),
                            "Notes": l_notes.strip()
                        }
                        st.session_state.demo_labour.append(new_lab)
                        st.success(_lbl(lang, f"Recorded labour payout for {worker}.", f"{worker} కోసం కూలీ చెల్లింపు నమోదైంది."))
                        st.rerun()

        if labour:
            df_lab = pd.DataFrame(labour)
            l_cols = ["LabourID", "Worker", "Role", "Date", "WorkType", "TotalCost", "Notes"]
            for col in l_cols:
                if col not in df_lab.columns:
                    df_lab[col] = ""
            disp_lab = rename_df_for_display(df_lab[l_cols], lang)
            if lang == "te":
                disp_lab = disp_lab.rename(columns={
                    "LabourID": "కూలీ ID",
                    "Worker": "కార్మికుడు / బృందం",
                    "Role": "బాధ్యత",
                    "WorkType": "పని రకం",
                    "TotalCost": "మొత్తం ఖర్చు (₹)"
                })
            st.dataframe(disp_lab, use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Labour", "కూలీ వివరాలు"),
                _lbl(lang, "No Labour Records", "కూలీ రికార్డులు లేవు"),
                _lbl(lang, "Record worker shifts and labour wages.", "కార్మికుల పని సమయాలు మరియు వేతనాలను నమోదు చేయండి.")
            )

    # 5. Sales
    with tabs[4]:
        st.markdown(f"#### {_lbl(lang, 'Fish Sales & Harvest Offtake', 'చేపల అమ్మకాలు మరియు పంట విక్రయాలు')}")
        s_top1, s_top2 = st.columns([3, 1])
        with s_top2:
            if st.button(_lbl(lang, "Record Commercial Sale", "వాణిజ్య అమ్మకం నమోదు"), type="primary", use_container_width=True):
                dialog_add_sale()

        if sales:
            df_s = pd.DataFrame(sales)
            if "SaleDate" in df_s.columns:
                df_s = df_s.sort_values("SaleDate", ascending=False)
            s_cols = ["SaleID", "PondID", "SaleDate", "Species", "QuantitySoldKg", "PricePerKg", "TotalRevenue", "BuyerMarket", "PaymentStatus", "Notes"]
            for col in s_cols:
                if col not in df_s.columns:
                    df_s[col] = ""
            st.dataframe(rename_df_for_display(df_s[s_cols], lang), use_container_width=True, hide_index=True)
        else:
            render_empty_state(
                _lbl(lang, "Sales", "అమ్మకాలు"),
                _lbl(lang, "No Sales Recorded", "అమ్మకాలు నమోదు కాలేదు"),
                _lbl(lang, "Record fish sales as harvests reach the market.", "పంట కోత మార్కెట్‌కు చేరినప్పుడు అమ్మకాలను నమోదు చేయండి."),
                _lbl(lang, "Record Sale", "అమ్మకం నమోదు"),
                "sal_empty_btn"
            )

    # 6. Payments
    with tabs[5]:
        st.markdown(f"#### {_lbl(lang, 'Receivable Payments & Invoicing', 'రావలసిన చెల్లింపులు మరియు బిల్లులు')}")
        if sales:
            df_pay = pd.DataFrame(sales)
            p_cols = ["SaleID", "SaleDate", "BuyerMarket", "TotalRevenue", "PaymentStatus", "PaymentDate"]
            for col in p_cols:
                if col not in df_pay.columns:
                    df_pay[col] = ""
            disp_pay = rename_df_for_display(df_pay[p_cols], lang)
            if lang == "te":
                disp_pay = disp_pay.rename(columns={"PaymentDate": "చెల్లింపు తేదీ"})
            st.dataframe(disp_pay, use_container_width=True, hide_index=True)

            pending = [s for s in sales if s.get("PaymentStatus") in ["Pending", "Partial"]]
            if pending:
                st.warning(_lbl(lang, f"{len(pending)} pending or partial receivable payment entries detected.", f"{len(pending)} పెండింగ్ లేదా పాక్షిక చెల్లింపు ఎంట్రీలు గుర్తించబడ్డాయి."))
            else:
                st.success(_lbl(lang, "All recorded sales receipts are fully settled.", "నమోదైన అన్ని అమ్మకాల చెల్లింపులు పూర్తిగా పరిష్కరించబడ్డాయి."))
        else:
            render_empty_state(
                _lbl(lang, "Payments", "చెల్లింపులు"),
                _lbl(lang, "No Payment Records", "చెల్లింపు రికార్డులు లేవు"),
                _lbl(lang, "Sales invoices and payment statuses will appear here.", "అమ్మకాల ఇన్‌వాయిస్‌లు మరియు చెల్లింపు స్థితి ఇక్కడ కనిపిస్తాయి.")
            )
