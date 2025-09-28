import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import numpy_financial as npf  # for IRR calculation

st.header("📊 Monte Carlo Simulator: NPV, ROI & IRR")

st.markdown("""
This tool shows how **uncertainty in sales, prices, and costs** affects financial outcomes.  
Monte Carlo simulation runs thousands of scenarios to estimate distributions of **NPV**, **ROI**, and **IRR**.
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

npvs, rois, irrs, breakeven_sales = [], [], [], []

for i in range(simulations):
    yearly_cf = annual_cashflows[i]
    # Discounted cashflows for NPV
    discounted = [yearly_cf / ((1 + dr) ** t) for t in range(1, years + 1)]
    npv = sum(discounted) - initial_investment
    npvs.append(npv)

    # ROI (total inflows vs investment)
    total_inflows = yearly_cf * years
    roi = (total_inflows - initial_investment) / initial_investment
    rois.append(roi)

    # IRR (cashflow stream: -investment, then yearly CFs)
    cashflows = [-initial_investment] + [yearly_cf] * years
    try:
        irr = npf.irr(cashflows)
        if irr is not None:
            irrs.append(irr)
    except:
        continue

    # Break-even sales volume (NPV=0 approx)
    # Required sales ~ investment / ((price - cost) * PV_factor)
    margin = prices[i] - costs[i]
    if margin > 0:
        pv_factor = sum([1 / ((1 + dr) ** t) for t in range(1, years + 1)])
        required_sales = initial_investment / (margin * pv_factor)
        breakeven_sales.append(required_sales)

npvs = np.array(npvs)
rois = np.array(rois)
irrs = np.array(irrs)
breakeven_sales = np.array(breakeven_sales)

# ========================
# Results
# ========================
st.subheader("Simulation Results")

col1, col2, col3 = st.columns(3)
col1.metric("Average NPV", f"{np.mean(npvs):,.0f}")
col2.metric("Probability NPV > 0", f"{(np.mean(npvs > 0) * 100):.1f}%")
col3.metric("Average ROI", f"{np.mean(rois):.2f}")

col4, col5 = st.columns(2)
if len(irrs) > 0:
    col4.metric("Average IRR", f"{np.mean(irrs) * 100:.1f}%")
if len(breakeven_sales) > 0:
    col5.metric("Avg Break-even Sales", f"{np.mean(breakeven_sales):,.0f} units/yr")

# Histogram for NPV
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
    - **Initial Investment:** Upfront capital needed to start the project.  
    - **Cashflows:** Annual profits = (Sales × Price) – (Sales × Cost).  
    - **NPV (Net Present Value):** Discounted value of future profits minus investment.  
      - Positive NPV = project creates value.  
    - **ROI (Return on Investment):**  
      \[
      ROI = \frac{\text{Total Inflows} - \text{Investment}}{\text{Investment}}
      \]  
    - **IRR (Internal Rate of Return):** The effective annual return % that sets NPV = 0.  
      - Higher IRR = more attractive project.  
    - **Break-even Sales:** Minimum annual sales needed for NPV = 0 (on average).  
    - **Discount Rate Guidelines:**  
        - 10% → Established, low-risk businesses  
        - 15% → Medium risk ventures  
        - 20% → High-risk innovation projects  
    """)

