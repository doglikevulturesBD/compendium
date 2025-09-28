import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.header("📊 Monte Carlo Simulator: NPV & ROI")

st.markdown("""
This tool shows how **uncertainty in sales, prices, and costs** affects financial outcomes.  
Monte Carlo simulation runs thousands of scenarios to estimate distributions of **NPV** and **ROI**, 
as investors would calculate them.
""")

# ========================
# User Inputs
# ========================
st.subheader("Set Input Ranges")

years = st.slider("Project duration (years)", 1, 10, 5)

sales_min, sales_max = st.slider("Annual sales volume range (units)", 100, 10000, (1000, 2000))
price_min, price_max = st.slider("Price per unit range", 10, 500, (80, 120))
cost_min, cost_max = st.slider("Cost per unit range", 5, 400, (50, 90))

initial_investment = st.number_input("Initial investment (currency)", min_value=0, value=500000, step=10000)

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
annual_cashflows = revenues - expenses  # profit before investment

npvs = []
rois = []

for i in range(simulations):
    yearly_cf = annual_cashflows[i]
    discounted = [yearly_cf / ((1 + dr) ** t) for t in range(1, years + 1)]
    npv = sum(discounted) - initial_investment
    roi = (sum([yearly_cf for t in range(1, years + 1)]) - initial_investment) / initial_investment
    npvs.append(npv)
    rois.append(roi)

npvs = np.array(npvs)
rois = np.array(rois)

# ========================
# Results
# ========================
st.subheader("Simulation Results")

col1, col2, col3 = st.columns(3)
col1.metric("Average NPV", f"{np.mean(npvs):,.0f}")
col2.metric("Probability NPV > 0", f"{(np.mean(npvs > 0) * 100):.1f}%")
col3.metric("Average ROI", f"{np.mean(rois):.2f}")

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
    - **Initial Investment:** The upfront capital needed to start the project.  
    - **Cashflows:** Annual profits = (Sales × Price) – (Sales × Cost).  
    - **NPV (Net Present Value):** Present value of future profits **minus initial investment**.  
      - If NPV > 0, the project is financially attractive.  
    - **ROI (Return on Investment):**  
      \[
      ROI = \frac{\text{Total Net Cash Inflows} - \text{Investment}}{\text{Investment}}
      \]  
      Shows profitability relative to the initial investment.  
    - **Discount rate:** Adjusts for risk:  
        - 10% → Established, low-risk businesses  
        - 15% → Moderate risk ventures  
        - 20% → Early-stage, high-risk innovation projects  

    Monte Carlo shows **probabilities** instead of single values, giving innovators and investors 
    a clearer view of risk and opportunity.
    """)

