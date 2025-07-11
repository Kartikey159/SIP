import streamlit as st
import pandas as pd
from datetime import datetime
import math

# -----------------------------
# Utility Functions
# -----------------------------
def calculate_future_value(present_value, rate, years):
    """
    Calculate the future value considering inflation or return.
    Formula: FV = PV * (1 + rate)^years
    """
    return present_value * ((1 + rate) ** years)

def calculate_sip(fv, rate, n_months):
    """
    Calculate SIP required to reach a Future Value (FV) in 'n_months' time,
    assuming monthly contributions and compounding.
    Formula: SIP = FV * r / (((1 + r)^n - 1))
    """
    monthly_rate = rate / 12
    sip = fv * monthly_rate / (((1 + monthly_rate) ** n_months - 1))
    return sip

def calculate_lump_sum(fv, rate, years):
    """
    Calculate the lump sum required today to meet a future value.
    Formula: PV = FV / (1 + r)^n
    """
    return fv / ((1 + rate) ** years)

# -----------------------------
# Streamlit App Layout
# -----------------------------
st.set_page_config(page_title="Goal-based SIP Calculator", layout="wide")
st.title("🌟 Smart SIP & Lump Sum Planner")

st.header("1. Investor Profile")
age = st.number_input("Current Age", min_value=0, max_value=100, value=30)
current_savings = st.number_input("Current Savings (in ₹)", min_value=0.0, step=1000.0)

st.header("2. Goal Planning")
num_goals = st.number_input("How many financial goals do you want to plan for?", min_value=1, max_value=10, value=2)

goals = []
current_year = datetime.now().year

default_inflation = 0.06

for i in range(int(num_goals)):
    st.subheader(f"Goal #{i+1}")
    goal_name = st.text_input(f"Name of Goal #{i+1}", key=f"goal_name_{i}")
    target_year = st.number_input(f"Target Year for {goal_name}", min_value=current_year, max_value=current_year+50, value=current_year+5, key=f"year_{i}")
    present_cost = st.number_input(f"Estimated Present Cost of {goal_name} (in ₹)", min_value=0.0, step=1000.0, key=f"cost_{i}")
    inflation_rate = st.number_input(f"Expected Inflation Rate for {goal_name} (default = {default_inflation*100:.1f}%)", min_value=0.0, max_value=1.0, value=default_inflation, step=0.005, key=f"inf_{i}")

    years_to_goal = target_year - current_year
    future_value = calculate_future_value(present_cost, inflation_rate, years_to_goal)

    goals.append({
        "Name": goal_name,
        "Year": target_year,
        "Present Cost": present_cost,
        "Inflation Rate": inflation_rate,
        "Years to Goal": years_to_goal,
        "Future Value": future_value
    })

st.header("3. SIP Preferences")
sip_start_year = st.number_input("Year you want to start SIP", min_value=current_year, max_value=current_year+50, value=current_year)
sip_grows = st.radio("Do you want to increase SIP every year?", ["No (Constant)", "Yes (Grow Annually)"])
annual_growth_rate = 0.0
if sip_grows == "Yes (Grow Annually)":
    annual_growth_rate = st.number_input("SIP Annual Growth Rate (e.g., 10% = 0.10)", min_value=0.0, max_value=1.0, value=0.10, step=0.01)

expected_return = st.number_input("Expected Annual Return on SIP/Lump Sum", min_value=0.01, max_value=0.20, value=0.12, step=0.005)

# -----------------------------
# Backend Calculation
# -----------------------------
if st.button("Calculate Plan"):
    st.header("📊 Calculation Results")
    results = []
    total_fv = 0
    total_lumpsum = 0
    total_sip = 0

    for goal in goals:
        n_years = goal["Year"] - sip_start_year
        n_months = n_years * 12
        fv = goal["Future Value"]
        total_fv += fv

        lumpsum_required = calculate_lump_sum(fv, expected_return, n_years)
        total_lumpsum += lumpsum_required

        sip_required = calculate_sip(fv, expected_return, n_months)
        total_sip += sip_required

        results.append({
            "Goal": goal["Name"],
            "Target Year": goal["Year"],
            "Future Cost (₹)": round(fv, 2),
            "Years to Goal": n_years,
            "Monthly SIP Required (₹)": round(sip_required, 2),
            "Lump Sum Today (₹)": round(lumpsum_required, 2)
        })

    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)

    st.subheader("💸 Summary")
    col1, col2 = st.columns(2)
    col1.metric("Total Future Value Needed", f"₹ {total_fv:,.0f}")
    col2.metric("Total Monthly SIP (Today)", f"₹ {total_sip:,.0f}")
    col1.metric("Total Lump Sum Needed Today", f"₹ {total_lumpsum:,.0f}")

    st.success("Plan generated successfully! Adjust values to simulate different scenarios.")
