"""
AquaMitra Finance View Module
Provides Finance Dashboard, Expenses, Purchases, Labour, Sales,
and Payments with strictly zero emojis.
"""

from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
from components.cards import render_metric_card, render_empty_state
from components.quick_actions import dialog_add_expense, dialog_add_sale
from services.ai.ai_service import analyze_finances
from database.queries import get_expenses, get_sales


def render_finance_view():
    subtabs = ["Finance Dashboard", "Expenses", "Purchases", "Labour", "Sales", "Payments"]
    tabs = st.tabs(subtabs)

    expenses = get_expenses()
    sales = get_sales()
    purchases = st.session_state.get("demo_purchases", [])
    labour = st.session_state.get("demo_labour", [])

    tot_exp = sum(e.get("Amount", 0) for e in expenses)
    tot_rev = sum(s.get("TotalRevenue", 0) for s in sales)
    net_diff = tot_rev - tot_exp

    # 1. Finance Dashboard
    with tabs[0]:
        st.markdown("#### Farm Financial Dashboard")
        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c2:
            if st.button("Analyze Finances with AI", type="secondary", use_container_width=True):
                st.session_state.show_fin_ai = True

        if st.session_state.get("show_fin_ai", False):
            f_ai = analyze_finances(st.session_state)
            clean_obs = f_ai['observation'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_tr = f_ai['trend'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_att = f_ai['attention'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            clean_ck = f_ai['suggested_check'].replace("🟢", "").replace("🟡", "").replace("🔴", "").replace("🤖", "").strip()
            st.info(f"**Observation:** {clean_obs}\n\n**Trend:** {clean_tr}\n\n**Attention Area:** {clean_att}\n\n**Suggested Action:** {clean_ck}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Total Recorded Revenue", f"₹{tot_rev:,.0f}", f"{len(sales)} Sales Transactions")
        with c2:
            render_metric_card("Total Operational Expenses", f"₹{tot_exp:,.0f}", f"{len(expenses)} Recorded Costs")
        with c3:
            render_metric_card("Estimated Net Difference", f"{'+' if net_diff>=0 else ''}₹{net_diff:,.0f}", "Operating Variance", value_color="#059669" if net_diff>=0 else "#DC2626")
        with c4:
            feed_exp = sum(e.get("Amount", 0) for e in expenses if e.get("Category") == "Feed")
            pct = int(feed_exp / tot_exp * 100) if tot_exp else 0
            render_metric_card("Feed Expenditure", f"₹{feed_exp:,.0f}", f"{pct}% of Total Expenses")

        st.caption("Notice: Financial metrics represent user-recorded operational figures. Figures are labeled Estimated Net Difference and do not represent audited statutory accounting.")

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if expenses:
                df_exp = pd.DataFrame(expenses)
                fig_exp_cat = px.pie(df_exp, names="Category", values="Amount", hole=0.4, title="Expenses by Operational Category")
                fig_exp_cat.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_exp_cat, use_container_width=True)
        with col_g2:
            if sales:
                df_sl = pd.DataFrame(sales)
                fig_sales = px.bar(df_sl, x="BuyerMarket", y="TotalRevenue", color="Species", title="Harvest Revenue by Buyer / Market (₹)")
                fig_sales.update_layout(height=300, margin=dict(l=15, r=15, t=35, b=15))
                st.plotly_chart(fig_sales, use_container_width=True)

    # 2. Expenses
    with tabs[1]:
        st.markdown("#### Operational Expenses Ledger")
        e_top1, e_top2 = st.columns([3, 1])
        with e_top2:
            if st.button("Add Expense Record", type="primary", use_container_width=True):
                dialog_add_expense()

        if expenses:
            df_e = pd.DataFrame(expenses)
            if "ExpenseDate" in df_e.columns:
                df_e = df_e.sort_values("ExpenseDate", ascending=False)
            e_cols = ["ExpenseID", "PondID", "ExpenseDate", "Category", "Description", "Quantity", "Amount", "Notes"]
            for col in e_cols:
                if col not in df_e.columns:
                    df_e[col] = ""
            st.dataframe(df_e[e_cols], use_container_width=True, hide_index=True)
            
            with st.expander("Manage Expense Records"):
                del_eid = st.selectbox("Select Expense ID to Delete", options=[e.get("ExpenseID") for e in expenses])
                if st.button("Delete Expense Record", type="secondary"):
                    st.session_state.demo_expenses = [e for e in st.session_state.demo_expenses if e.get("ExpenseID") != del_eid]
                    st.success("Expense removed successfully.")
                    st.rerun()
        else:
            render_empty_state("Expenses", "No Expenses Recorded", "Add operational cost entries.", "Add Expense", "exp_empty_btn")

    # 3. Purchases
    with tabs[2]:
        st.markdown("#### Commercial Procurement & Purchases")
        with st.expander("Log Material / Supply Purchase"):
            with st.form("add_purch_form", clear_on_submit=True):
                p1, p2 = st.columns(2)
                with p1:
                    p_date = st.date_input("Purchase Date", value=date.today())
                    p_item = st.text_input("Item Name *", placeholder="e.g. Agricultural Dolomite Lime")
                    p_cat = st.selectbox("Category", options=["Chemicals & Minerals", "Feed", "Seed", "Equipment Parts", "Fuel & Energy", "Other"])
                    p_sup = st.text_input("Supplier / Merchant", placeholder="e.g. Godavari Aqua Inputs")
                with p2:
                    p_qty = st.number_input("Quantity *", min_value=1.0, value=20.0, step=5.0)
                    p_unit = st.text_input("Unit (e.g. Bags, Liters, kg)", value="Bags (50kg)")
                    p_price = st.number_input("Unit Price (₹) *", min_value=1.0, value=350.0, step=25.0)
                    p_inv = st.text_input("Invoice / Receipt Number", placeholder="e.g. INV-2026-089")

                p_submit = st.form_submit_button("Save Purchase Record", type="primary")
                if p_submit:
                    if not p_item:
                        st.error("Item name is required.")
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
                        st.success(f"Recorded purchase of {p_item} (Total: ₹{tot_cost:,.0f}).")
                        st.rerun()

        if purchases:
            df_purch = pd.DataFrame(purchases)
            p_cols = ["PurchaseID", "Date", "Item", "Category", "Supplier", "Quantity", "Unit", "UnitPrice", "TotalPrice", "InvoiceNumber"]
            for col in p_cols:
                if col not in df_purch.columns:
                    df_purch[col] = ""
            st.dataframe(df_purch[p_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Purchases", "No Purchases Logged", "Log material and supply purchase receipts.")

    # 4. Labour
    with tabs[3]:
        st.markdown("#### Farm Labour & Workforce Register")
        with st.expander("Record Labour Payment"):
            with st.form("add_labour_form", clear_on_submit=True):
                l1, l2 = st.columns(2)
                with l1:
                    l_date = st.date_input("Date", value=date.today())
                    worker = st.text_input("Worker / Team Name *", placeholder="e.g. K. Prasad & Team")
                    role = st.selectbox("Role / Task", options=["Netting & Harvesting Crew", "Daily Feeding & Guarding", "Dyke & Pond Repair", "Aerator Maintenance", "Other"])
                with l2:
                    hours = st.number_input("Hours Worked", min_value=1.0, value=8.0, step=1.0)
                    rate = st.number_input("Rate per Hour or Daily Rate (₹)", min_value=50.0, value=600.0, step=50.0)
                    l_notes = st.text_input("Work Notes", placeholder="e.g. 3-point sample dragnetting in Pond 1")

                l_submit = st.form_submit_button("Save Labour Record", type="primary")
                if l_submit:
                    if not worker:
                        st.error("Worker name is required.")
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
                        st.success(f"Recorded labour payout for {worker}.")
                        st.rerun()

        if labour:
            df_lab = pd.DataFrame(labour)
            l_cols = ["LabourID", "Worker", "Role", "Date", "WorkType", "TotalCost", "Notes"]
            for col in l_cols:
                if col not in df_lab.columns:
                    df_lab[col] = ""
            st.dataframe(df_lab[l_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Labour", "No Labour Records", "Record worker shifts and labour wages.")

    # 5. Sales
    with tabs[4]:
        st.markdown("#### Fish Sales & Harvest Offtake")
        s_top1, s_top2 = st.columns([3, 1])
        with s_top2:
            if st.button("Record Commercial Sale", type="primary", use_container_width=True):
                dialog_add_sale()

        if sales:
            df_s = pd.DataFrame(sales)
            if "SaleDate" in df_s.columns:
                df_s = df_s.sort_values("SaleDate", ascending=False)
            s_cols = ["SaleID", "PondID", "SaleDate", "Species", "QuantitySoldKg", "PricePerKg", "TotalRevenue", "BuyerMarket", "PaymentStatus", "Notes"]
            for col in s_cols:
                if col not in df_s.columns:
                    df_s[col] = ""
            st.dataframe(df_s[s_cols], use_container_width=True, hide_index=True)
        else:
            render_empty_state("Sales", "No Sales Recorded", "Record fish sales as harvests reach the market.", "Record Sale", "sal_empty_btn")

    # 6. Payments
    with tabs[5]:
        st.markdown("#### Receivable Payments & Invoicing")
        if sales:
            df_pay = pd.DataFrame(sales)
            p_cols = ["SaleID", "SaleDate", "BuyerMarket", "TotalRevenue", "PaymentStatus", "PaymentDate"]
            for col in p_cols:
                if col not in df_pay.columns:
                    df_pay[col] = ""
            st.dataframe(df_pay[p_cols], use_container_width=True, hide_index=True)
            
            pending = [s for s in sales if s.get("PaymentStatus") in ["Pending", "Partial"]]
            if pending:
                st.warning(f"{len(pending)} pending or partial receivable payment entries detected.")
            else:
                st.success("All recorded sales receipts are fully settled.")
        else:
            render_empty_state("Payments", "No Payment Records", "Sales invoices and payment statuses will appear here.")
