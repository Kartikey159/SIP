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
    Calculates initial SIP with step-up logic using accurate month-level compounding.
    """
    monthly_rate = annual_return / 12
    total_months = int(years * 12)

    def compute_future_value(start_sip):
        fv_accum = 0
        sip_amount = start_sip
        for month in range(total_months):
            fv_accum += sip_amount * ((1 + monthly_rate) ** (total_months - month))
            if (month + 1) % 12 == 0:
                sip_amount *= (1 + annual_step_up)
        return fv_accum

    low, high = 0, fv
    for _ in range(100):
        mid = (low + high) / 2
        if compute_future_value(mid) < fv:
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
# current_year is now defined above with investor profile section

# Future lump sum entries
st.subheader("Future Lump Sum Inflows (Optional)")
future_lumps = []
num_lumps = st.number_input("How many future lump sum infusions do you expect?", min_value=0, max_value=5, value=0, key="num_lumps")
for i in range(num_lumps):
    lump_year = st.number_input(f"Year of Lump Sum #{i+1}", min_value=current_year, max_value=current_year+50, value=current_year+1, key=f"lump_year_{i}")
    lump_amount = st.number_input(f"Expected Amount of Lump Sum #{i+1} (₹)", min_value=0.0, step=1000.0, format="%0.2f", key=f"lump_amt_{i}")
    future_lumps.append({"year": lump_year, "amount": lump_amount})
future_lumps = []
num_lumps = st.number_input("How many future lump sum infusions do you expect?", min_value=0, max_value=5, value=0)
for i in range(num_lumps):
    lump_year = st.number_input(f"Year of Lump Sum #{i+1}", min_value=current_year, max_value=current_year+50, value=current_year+1, key=f"lump_year_{i}")
    lump_amount = st.number_input(f"Expected Amount of Lump Sum #{i+1} (₹)", min_value=0.0, step=1000.0, format="%0.2f", key=f"lump_amt_{i}")
    future_lumps.append({"year": lump_year, "amount": lump_amount})
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
        month_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                     "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        sip_start_month_num = month_map[sip_start_month]

        start_date_month_index = sip_start_year * 12 + sip_start_month_num
        target_date_month_index = goal["Year"] * 12 + 12  # Assuming goal month is December
        n_months = target_date_month_index - start_date_month_index
        n_years = n_months / 12

        if n_months <= 0:
            st.warning(f"⚠️ Goal '{goal['Name']}' must be after SIP start date. Skipping this goal.")
            continue

                                fv = goal["Future Value"]

        # Adjust FV based on all future lump sums before this goal
        for lump in future_lumps:
            if lump["year"] <= goal["Year"]:
                years_before_goal = goal["Year"] - lump["year"]
                value_at_goal = lump["amount"] * ((1 + expected_return) ** years_before_goal)
                fv = max(0, fv - value_at_goal)

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




