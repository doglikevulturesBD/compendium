import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.header("📊 Monte Carlo Simulator: NPV & ROI")

st.markdown("""
This tool shows how **uncertainty in sales, prices, and costs** affects financial outcomes.  
Monte Carlo simulation runs thousands of scenarios to estimate distributions of **NPV** and **ROI**.
""")

# ========================
# User Inputs
# ========================
st.subheader("Set Input Ranges")

years = st.slider("Project duration (years)", 1, 10, 5)

sales_min, sales_max = st.slider("Annual sales volume range (units)", 100, 10000, (1000, 2000))
price_min, price_max = st.slider("Price per unit range (currency)", 10, 500, (80, 120))
cost_min, cost_max = st.slider("Cost per unit range (currency)", 5, 400, (50, 90))

discount_rate = st.selectbox(
    "Discount rate (reflects risk level)",
    ["10% (established business)", "15% (medium risk)", "20% (high risk)", "Custom"]
)

if discount_rate == "Custom":
    dr = st.slider("Custom discount rate (%)", 5, 40, 12) / 100
else:
    dr = float(discount_rate.split("%")[0]) / 100

simulations = st.number_input("Number of Monte Carlo trials", min_value=1000, max_value=20000, value=5000, step=1000)

# ========================
# Monte Carlo Simulation
# ========================
np.random.seed(42)  # reproducibility

sales = np.random.uniform(sales_min, sales_max, simulations)
prices = np.random.uniform(price_min, price_max, simulations)
costs = np.random.uniform(cost_min, cost_max, simulations)

revenues = sales * prices
expenses = sales * costs
cashflows = revenues - expenses

# ROI (simple, annualized over project horizon)
roi = (cashflows - expenses) / expenses

# NPV: assume constant cashflows each year for "years"
npvs = []
for i in range(simulations):
    yearly_cf = cashflows[i]
    discounted = [yearly_cf / ((1 + dr) ** t) for t in range(1, years + 1)]
    npvs.append(sum(discounted))

npvs = np.array(npvs)

# ========================
# Results
# ========================
st.subheader("Simulation Results")

col1, col2, col3 = st.columns(3)
col1.metric("Average NPV", f"{np.mean(npvs):,.0f}")
col2.metric("Probability NPV > 0", f"{(np.mean(npvs > 0) * 100):.1f}%")
col3.metric("Average ROI", f"{np.mean(roi):.2f}")

# Histogram
fig, ax = plt.subplots()
ax.hist(npvs, bins=40, color="skyblue", edgecolor="black")
ax.axvline(np.mean(npvs), color="red", linestyle="dashed", linewidth=2, label=f"Mean NPV = {np.mean(npvs):,.0f}")
ax.set_title("NPV Distribution")
ax.set_xlabel("NPV")
ax.set_ylabel("Frequency")
ax.legend()
st.pyplot(fig)

# ========================
# Educational Overlay
# ========================
with st.expander("💡 What does this mean?"):
    st.markdown("""
    - **NPV (Net Present Value):** Shows the value of future profits today, after discounting for risk and time.  
    - **ROI (Return on Investment):** Ratio of profit relative to cost.  
    - **Discount rate:**  
        - 10% → Established, low-risk businesses  
        - 15% → Moderate risk ventures  
        - 20% → Early-stage, high-risk innovation projects  

    A **positive NPV** means the project is expected to create value.  
    Monte Carlo shows the *probability* of success, not a single answer.
    """)
