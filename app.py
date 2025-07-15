import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# Utility Functions
# -----------------------------
def calculate_future_value(present_value, rate, years):
    """
    Calculate the future value considering inflation or return.
    Formula: FV = PV * (1 + rate)^years
    """
    return present_value * ((1 + rate) ** years)

def calculate_sip_step_up(fv, annual_return, years, annual_step_up):
    """
    Calculate the starting SIP amount for a step-up SIP.
    SIP increases by a fixed percentage every year.
    """
    monthly_rate = annual_return / 12
    total_months = years * 12

    def future_value_of_step_up_sip(start_sip):
        fv_accum = 0
        for year in range(years):
            yearly_sip = start_sip * ((1 + annual_step_up) ** year)
            for month in range(12):
                month_index = year * 12 + month
                months_left = total_months - month_index
                fv_accum += yearly_sip * ((1 + monthly_rate) ** months_left)
        return fv_accum

    # Binary search for SIP
    low = 0
    high = fv
    for _ in range(100):
        mid = (low + high) / 2
        if future_value_of_step_up_sip(mid) < fv:
            low = mid
        else:
            high = mid

    return round(mid, 2)

def calculate_sip(fv, rate, n_months):
    monthly_rate = rate / 12
    return fv * monthly_rate / (((1 + monthly_rate) ** n_months - 1))

def calculate_lump_sum(fv, rate, years):
    return fv / ((1 + rate) ** years)

# -----------------------------
# Streamlit App Layout
# -----------------------------
st.set_page_config(page_title="SIP Calculator KG Capital", layout="wide")
st.title("SIP Calculator KG Capital")

st.header("1. Investor Profile")
age = st.number_input("Current Age", min_value=0, max_value=100, value=30)
current_savings = st.number_input("Current Savings (in ₹)", min_value=0.0, step=1000.0, format="%0.2f")

st.header("2. Goal Planning")
num_goals = st.number_input("How many financial goals do you want to plan for?", min_value=1, max_value=10, value=2)

goals = []
current_year = datetime.now().year

default_inflation = 6.0

for i in range(int(num_goals)):
    st.subheader(f"Goal #{i+1}")
    goal_name = st.text_input(f"Name of Goal #{i+1}", key=f"goal_name_{i}")
    target_year = st.number_input(f"Target Year for {goal_name}", min_value=current_year, max_value=current_year+50, value=current_year+5, key=f"year_{i}")
    present_cost = st.number_input(f"Estimated Present Cost of {goal_name} (in ₹)", min_value=0.0, step=1000.0, format="%0.2f", key=f"cost_{i}")
    inflation_rate = st.number_input(f"Expected Inflation Rate for {goal_name} (%)", min_value=0.0, max_value=100.0, value=default_inflation, step=0.1, key=f"inf_{i}") / 100

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
sip_start_month = st.selectbox("Select SIP Start Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
sip_grows = st.radio("Do you want to increase SIP every year?", ["No (Constant)", "Yes (Grow Annually)"])
annual_growth_rate = 0.0
if sip_grows == "Yes (Grow Annually)":
    annual_growth_rate = st.number_input("SIP Annual Growth Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5) / 100

expected_return = st.number_input("Expected Annual Return on SIP/Lump Sum (%)", min_value=1.0, max_value=20.0, value=12.0, step=0.5) / 100

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
        month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        sip_start_month_num = month_map[sip_start_month]

        start_date_month_index = sip_start_year * 12 + sip_start_month_num
        target_date_month_index = goal["Year"] * 12  # assuming December as default target month
        n_months = target_date_month_index - start_date_month_index
        n_years = n_months / 12

        fv = goal["Future Value"]
        total_fv += fv

        lumpsum_required = calculate_lump_sum(fv, expected_return, n_years)
        total_lumpsum += lumpsum_required

        if sip_grows == "Yes (Grow Annually)":
            sip_required = calculate_sip_step_up(fv, expected_return, n_years, annual_growth_rate)
        else:
            sip_required = calculate_sip(fv, expected_return, n_months)

        total_sip += sip_required

        results.append({
            "Goal": goal["Name"],
            "Target Year": goal["Year"],
            "Future Cost (₹)": round(fv, 2),
            "Years to Goal": round(n_years, 2),
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
