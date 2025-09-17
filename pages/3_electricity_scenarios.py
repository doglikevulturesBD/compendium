import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import altair as alt

st.set_page_config(page_title="Electricity Scenarios", layout="wide")

# ========================
# Intro & CO2 context
# ========================
st.title("⚡ South African Electricity Price & CO₂ Scenario Explorer")

st.markdown("""
Explore how **South Africa’s electricity prices and carbon intensity** could evolve from **2023 to 2035**
under different policy pathways:

- **BAU (Business as Usual):** Fossil-heavy, follows historic trends
- **IRP-aligned:** Government's planned Integrated Resource Plan — moderate renewables growth
- **Accelerated:** Rapid renewables build-out, lower cost and CO₂

**Why CO₂ matters:**  
This app estimates the **carbon intensity (kg CO₂ per kWh)** of grid electricity.  
This is directly linked to companies’ **Scope 2 emissions** — the greenhouse gases from purchased electricity.

- Higher Scope 2 = higher **carbon tax liability** under South Africa’s carbon tax  
- Higher Scope 2 = greater risk under the EU’s **Carbon Border Adjustment Mechanism (CBAM)**  
- Lower Scope 2 = better climate disclosure scores, lower export risk
""")

# ========================
# 1. Raw historical data
# ========================
hist_data = {
    'Residential': [88.53,95.61,107.74,117.86,127.33,127.87,145.6,158.36,182.21,199.72,236.97],
    'Business':    [79.85,86.23,97.17,106.31,108.64,115.32,131.32,142.82,164.32,180.11,213.07],
    'Industrial':  [61.815,66.765,75.235,82.31,84.115,89.295,101.675,110.58,127.24,139.46,165.475]
}
years_hist = list(range(2013,2024))

# ========================
# 2. Forecast + scenarios
# ========================
def make_forecast(prices, sector_name):
    series = pd.Series(prices, index=years_hist)
    model = ARIMA(series, order=(1,1,1))
    fit = model.fit()
    future_years = list(range(2024,2036))
    forecast = fit.forecast(steps=len(future_years))
    forecast.index = future_years
    
    n = len(forecast)
    irp_mult = np.linspace(1.0, 0.85, n)
    accel_mult = np.linspace(1.0, 0.70, n)
    
    df_hist = pd.DataFrame({'Year': series.index, 'Sector': sector_name, 'Scenario': 'Historical', 'Price': series.values})
    df_bau = pd.DataFrame({'Year': forecast.index, 'Sector': sector_name, 'Scenario': 'BAU', 'Price': forecast.values})
    df_irp = pd.DataFrame({'Year': forecast.index, 'Sector': sector_name, 'Scenario': 'IRP', 'Price': forecast.values * irp_mult})
    df_accel = pd.DataFrame({'Year': forecast.index, 'Sector': sector_name, 'Scenario': 'Accelerated', 'Price': forecast.values * accel_mult})
    
    return pd.concat([df_hist, df_bau, df_irp, df_accel], ignore_index=True)

res = make_forecast(hist_data['Residential'], 'Residential')
biz = make_forecast(hist_data['Business'], 'Business')
ind = make_forecast(hist_data['Industrial'], 'Industrial')
df = pd.concat([res, biz, ind], ignore_index=True)

# ========================
# 3. Add CO₂ intensities (fixed: BAU flat at 0.85)
# ========================
fossil_targets = {"BAU": 0.85, "IRP": 0.40, "Accelerated": 0.30}
df['FossilShare'] = np.nan

for scenario, target in fossil_targets.items():
    mask = df['Scenario'] == scenario
    if mask.any():
        unique_years = sorted(df.loc[mask, 'Year'].unique())
        n = len(unique_years)
        if scenario == "BAU":
            # BAU stays flat at 0.85
            df.loc[mask, 'FossilShare'] = 0.85
        else:
            decline = np.linspace(0.85, target, n)
            for year, val in zip(unique_years, decline):
                df.loc[(df['Scenario']==scenario) & (df['Year']==year), 'FossilShare'] = val

df.loc[df['Scenario']=='Historical','FossilShare'] = 0.85
df['CO2_kg_per_kWh'] = df['FossilShare']

# ========================
# 4. UI Controls
# ========================
view_mode = st.radio("View Mode", ["🔍 View one sector", "📊 Compare all sectors"])

# ========================
# 5. Visualisation
# ========================
if view_mode == "🔍 View one sector":
    sector = st.selectbox("Select Sector", df['Sector'].unique())
    scenario = st.selectbox("Select Scenario", ['BAU','IRP','Accelerated'])
    st.markdown(f"**Scenario explanation:**")
    if scenario == "BAU":
        st.info("**Business as Usual:** Fossil-heavy future, price growth continues following historical trend. Carbon intensity remains high.")
    elif scenario == "IRP":
        st.info("**IRP-aligned:** Moderate renewables build-out as planned by government; price growth slows. Carbon intensity falls steadily.")
    else:
        st.info("**Accelerated:** Aggressive renewables rollout; price growth flattens and carbon intensity drops sharply.")
        
    filtered = df[(df['Sector']==sector) & (df['Scenario'].isin(['Historical',scenario]))]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Electricity Price")
        chart_price = (
            alt.Chart(filtered)
            .mark_line(point=True)
            .encode(
                x='Year:O', y=alt.Y('Price', title='c/kWh'),
                color='Scenario', tooltip=['Year','Scenario','Price']
            )
        )
        st.altair_chart(chart_price, use_container_width=True)

    with col2:
        st.subheader("🌍 CO₂ Intensity")
        chart_co2 = (
            alt.Chart(filtered)
            .mark_line(point=True)
            .encode(
                x='Year:O', y=alt.Y('CO2_kg_per_kWh', title='kg CO₂/kWh'),
                color='Scenario', tooltip=['Year','Scenario','CO2_kg_per_kWh']
            )
        )
        st.altair_chart(chart_co2, use_container_width=True)

    # ========================
    # 6. 2035 Summary Cards
    # ========================
    st.markdown("### 📌 2035 Summary")
    summary = df[(df['Sector']==sector) & (df['Year']==2035) & (df['Scenario'].isin(['BAU','IRP','Accelerated']))]
    colA, colB, colC = st.columns(3)
    for (scenario_name, color, col) in zip(['BAU','IRP','Accelerated'], ['red','green','blue'], [colA,colB,colC]):
        row = summary[summary['Scenario']==scenario_name].iloc[0]
        with col:
            st.markdown(f"#### {scenario_name}")
            st.metric(label="Price (c/kWh)", value=f"{row['Price']:.1f}")
            st.metric(label="CO₂ (kg/kWh)", value=f"{row['CO2_kg_per_kWh']:.2f}")

else:
    st.markdown("**Compare electricity price trends across all three sectors** (Residential, Business, Industrial).")
    scenario = st.selectbox("Select Scenario", ['BAU','IRP','Accelerated'])
    compare_df = df[(df['Scenario']==scenario)]
    
    chart_compare = (
        alt.Chart(compare_df)
        .mark_line(point=True)
        .encode(
            x='Year:O', y=alt.Y('Price', title='c/kWh'),
            color='Sector', tooltip=['Year','Sector','Price']
        )
    )
    st.altair_chart(chart_compare, use_container_width=True)
