import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Expense Tracker Dashboard", page_icon="chart_with_upwards_trend", layout="wide")

EXPENSES_FILE = "expenses.json"
BUDGET_FILE = "budget.json"

# Helper: Initialize with sample data if file is missing or corrupted
def initialize_file_if_empty():
    if not os.path.exists(EXPENSES_FILE) or os.path.getsize(EXPENSES_FILE) == 0:
        sample_data = [
            {"id": 1, "date": "2026-01-15", "description": "New Year Shopping", "amount": 150.0, "category": "Shopping"},
            {"id": 2, "date": "2026-03-10", "description": "Grocery shopping", "amount": 45.0, "category": "Food"},
            {"id": 3, "date": "2026-06-14", "description": "Gas tank fill", "amount": 35.0, "category": "Transport"},
            {"id": 4, "date": "2026-06-20", "description": "Internet Bill", "amount": 60.0, "category": "Other"},
            {"id": 5, "date": "2025-12-25", "description": "Holiday Gifts", "amount": 120.0, "category": "Shopping"}
        ]
        with open(EXPENSES_FILE, "w") as f:
            json.dump(sample_data, f, indent=4)

# Load Data Functions
def load_data():
    initialize_file_if_empty()
    try:
        with open(EXPENSES_FILE, "r") as f:
            data = json.load(f)
            if not data:
                return pd.DataFrame(columns=["id", "date", "description", "amount", "category"])
            
            df = pd.DataFrame(data)
            if "category" not in df.columns:
                df["category"] = "Other"
            else:
                df["category"] = df["category"].fillna("Other")
                
            df["date"] = pd.to_datetime(df["date"])
            df["Month_Num"] = df["date"].dt.month
            df["Year_Num"] = df["date"].dt.year
            return df
    except Exception:
        return pd.DataFrame(columns=["id", "date", "description", "amount", "category"])

def save_new_expense(description, amount, category, date_obj):
    try:
        if os.path.exists(EXPENSES_FILE) and os.path.getsize(EXPENSES_FILE) > 0:
            with open(EXPENSES_FILE, "r") as f:
                expenses = json.load(f)
        else:
            expenses = []
    except Exception:
        expenses = []
        
    next_id = max([e["id"] for e in expenses], default=0) + 1
    new_expense = {
        "id": next_id,
        "date": date_obj.strftime("%Y-%m-%d"),
        "description": description,
        "amount": float(amount),
        "category": category
    }
    expenses.append(new_expense)
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

def load_yearly_budget(year):
    if not os.path.exists(BUDGET_FILE):
        return 0.0
    try:
        with open(BUDGET_FILE, "r") as f:
            budget_data = json.load(f)
            return sum(float(v) for k, v in budget_data.items() if k.startswith(str(year)))
    except Exception:
        return 0.0

def load_budget_limit(month, year):
    if not os.path.exists(BUDGET_FILE):
        return 0.0
    try:
        with open(BUDGET_FILE, "r") as f:
            budget_data = json.load(f)
            key = f"{year}-{month:02d}"
            return float(budget_data.get(key, 0.0))
    except Exception:
        return 0.0

def save_budget_limit(month, year, amount):
    try:
        if os.path.exists(BUDGET_FILE) and os.path.getsize(BUDGET_FILE) > 0:
            with open(BUDGET_FILE, "r") as f:
                budget_data = json.load(f)
        else:
            budget_data = {}
    except Exception:
        budget_data = {}
        
    key = f"{year}-{month:02d}"
    budget_data[key] = float(amount)
    with open(BUDGET_FILE, "w") as f:
        json.dump(budget_data, f, indent=4)

# Load fresh data
df = load_data()

# Month names helper dictionary
month_names = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 
               7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}

# Sidebar Form 1: Interactive Input Expense Form
st.sidebar.header("Add New Expense")
with st.sidebar.form(key="expense_form", clear_on_submit=True):
    input_desc = st.text_input("Description", placeholder="e.g., Dinner")
    input_amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
    input_cat = st.selectbox("Category", ["Food", "Transport", "Housing", "Shopping", "Entertainment", "Other"])
    input_date = st.date_input("Date", datetime.now())
    submit_button = st.form_submit_button(label="Save Expense")
    
    if submit_button:
        if input_desc:
            save_new_expense(input_desc, input_amount, input_cat, input_date)
            st.sidebar.success("Expense Added!")
            st.rerun()
        else:
            st.sidebar.error("Please enter a description.")

st.sidebar.markdown("---")

# Sidebar Form 2: Budget Target Configurator Form
st.sidebar.header("Set Monthly Budget")
with st.sidebar.form(key="budget_form", clear_on_submit=True):
    budget_year = st.number_input("Year", min_value=2020, max_value=2035, value=2026, step=1)
    budget_month = st.selectbox("Month", list(range(1, 13)), format_func=lambda x: month_names.get(x))
    budget_amount = st.number_input("Budget Target ($)", min_value=0.0, step=50.0)
    budget_submit = st.form_submit_button(label="Update Budget")
    
    if budget_submit:
        save_budget_limit(budget_month, budget_year, budget_amount)
        st.sidebar.success(f"Budget updated for {month_names[budget_month]} {budget_year}!")
        st.rerun()

st.sidebar.markdown("---")

# Sidebar 3: Filter Controls
st.sidebar.header("Filter Controls")
if not df.empty:
    available_years = sorted(df["Year_Num"].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Select Year", available_years)
    
    view_full_year = st.sidebar.checkbox("Show Whole Year Overview", value=True)
    
    if not view_full_year:
        months_pool = df[df["Year_Num"] == selected_year]
        available_months = sorted(months_pool["Month_Num"].unique())
        selected_month = st.sidebar.selectbox(
            "Select Month", 
            available_months, 
            format_func=lambda x: month_names.get(x, str(x))
        )
        filtered_df = df[(df["Year_Num"] == selected_year) & (df["Month_Num"] == selected_month)]
        title_context = f"for {month_names.get(selected_month, '')} {selected_year}"
        monthly_budget = load_budget_limit(selected_month, selected_year)
    else:
        filtered_df = df[df["Year_Num"] == selected_year]
        title_context = f"for Full Year {selected_year}"
        monthly_budget = load_yearly_budget(selected_year)
else:
    filtered_df = pd.DataFrame()
    title_context = ""
    monthly_budget = 0.0

# Application Main View Layout
st.title("Personal Expense and Budget Dashboard")
st.markdown(f"Visualize your spending habits and manage financial targets instantly {title_context}.")

if filtered_df.empty:
    st.warning("No data found matching the selected filters. Use the form on the left to add expenses!")
else:
    # Calculate Budget & Spent Metrics
    total_spent = filtered_df["amount"].sum()
    remaining_budget = monthly_budget - total_spent
    
    # Row 1: KPI Summary Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Spent", value=f"${total_spent:,.2f}")
    with col2:
        budget_display = f"${monthly_budget:,.2f}" if monthly_budget > 0 else "Not Set"
        st.metric(label="Combined Budget Target", value=budget_display)
    with col3:
        if monthly_budget > 0:
            if remaining_budget >= 0:
                st.metric(label="Remaining Budget Balance", value=f"${remaining_budget:,.2f}", delta=f"${remaining_budget:,.2f} Safe")
            else:
                st.metric(label="Over Budget Deficit", value=f"${abs(remaining_budget):,.2f}", delta=f"-${abs(remaining_budget):,.2f}", delta_color="inverse")
        else:
            st.metric(label="Budget Status", value="N/A", delta="Set budget target via sidebar")

    st.markdown("---")
    
    # Row 2: Analytical Visual Graphs
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Spending Breakdown by Category")
        category_df = filtered_df.groupby("category", as_index=False)["amount"].sum()
        fig_pie = px.pie(category_df, values="amount", names="category", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)
            
    with col_chart2:
        st.subheader("Spending Trajectory Trend")
        timeline_df = filtered_df.groupby(filtered_df['date'].dt.date)["amount"].sum().reset_index()
        fig_line = px.line(timeline_df, x="date", y="amount", labels={"date":"Date", "amount":"Daily Spent ($)"}, markers=True)
        fig_line.update_traces(line=dict(color="#22a6b3", width=3))
        fig_line.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # Row 3: Filtered Data Ledger Table Display
    st.subheader("Expense Ledger Records")
    display_cols = ["date", "description", "category", "amount"]
    formatted_table_df = filtered_df[display_cols].copy()
    formatted_table_df = formatted_table_df.sort_values(by="date", ascending=False)
    formatted_table_df["date"] = formatted_table_df["date"].dt.strftime("%Y-%m-%d")
    
    st.dataframe(
        formatted_table_df.rename(columns={"date": "Date", "description": "Description", "category": "Category", "amount": "Amount ($)"}),
        use_container_width=True,
        hide_index=True
    )
