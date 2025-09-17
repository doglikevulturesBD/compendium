import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import altair as alt

st.set_page_config(page_title="Electricity Scenarios", layout="wide")

st.title("⚡ South African Electricity Price & CO₂ Scenario Explorer")

# -----------------------------
# 1. Raw historical data
# -----------------------------
hist_data = {
    'Residential': [88.53,95.61,107.74,117.86,127.33,127.87,145.6,158.36,182.21,199.72,236.97],
    'Business':    [79.85,86.23,97.17,106.31,108.64,115.32,131.32,142.82,164.32,180.11,213.07],
    'Industrial':  [61.815,66.765,75.235,82.31,84.115,89.295,101.675,110.58,127.24,139.46,165.475]
}
years_hist = list(range(2013,2024))

# -----------------------------
# 2. Forecast function (ARIMA + scenario divergence)
# -----------------------------
def make_forecast(prices, sector_name):
    series = pd.Series(prices, index=years_hist)
    model = ARIMA(series, order=(1,1,1))
    fit = model.fit()
    future_years = list(range(2024,2036))
    forecast = fit.forecast(steps=len(future_years))
    forecast.index = future_years
    
    # Scenario divergence
    n = len(forecast)
    irp_mult = np.linspace(1.0, 0.85, n)
    accel_mult = np.linspace(1.0, 0.70, n)
    
    # Combine into long format
    df_hist = pd.DataFrame({'Year': series.index, 'Sector': sector_name, 'Scenario': 'Historical', 'Price': series.values})
    df_bau = pd.DataFrame({'Year': forecast.index, 'Sector': sector_name, 'Scenario': 'BAU', 'Price': forecast.values})
    df_irp = pd.DataFrame({'Year': forecast.index, 'Sector': sector_name, 'Scenario': 'IRP', 'Price': forecast.values * irp_mult})
    df_accel = pd.DataFrame({'Year': forecast.index, 'Sector': sector_name, 'Scenario': 'Accelerated', 'Price': forecast.values * accel_mult})
    
    return pd.concat([df_hist, df_bau, df_irp, df_accel], ignore_index=True)

# -----------------------------
# 3. Build full combined dataset
# -----------------------------
res = make_forecast(hist_data['Residential'], 'Residential')
biz = make_forecast(hist_data['Business'], 'Business')
ind = make_forecast(hist_data['Industrial'], 'Industrial')

df = pd.concat([res, biz, ind], ignore_index=True)

# -----------------------------
# 4. Add fossil share and CO2
# -----------------------------
fossil_targets = {"BAU": 0.78, "IRP": 0.40, "Accelerated": 0.30}

df['FossilShare'] = np.nan
for scenario, target in fossil_targets.items():
    mask = df['Scenario'] == scenario
    if mask.any():
        years = df.loc[mask, 'Year'].values
        n = len(years)
        decline = np.linspace(0.85, target, n)  # from 85% in 2023 to target in 2035
        df.loc[mask, 'FossilShare'] = decline
df.loc[df['Scenario'] == 'Historical', 'FossilShare'] = 0.85
df['CO2_kg_per_kWh'] = df['FossilShare']

# -----------------------------
# 5. UI Controls
# -----------------------------
sector = st.selectbox("Select sector", df['Sector'].unique())
view_mode = st.radio("View mode", ["Single scenario", "Compare all scenarios"])

# -----------------------------
# 6. Plotting
# -----------------------------
if view_mode == "Single scenario":
    scenario = st.selectbox("Select scenario", df['Scenario'].unique())
    view = df[(df['Sector'] == sector) & (df['Scenario'] == scenario)]
else:
    view = df[(df['Sector'] == sector) & (df['Scenario'] != 'Historical')]

left, right = st.columns(2)

with left:
    st.subheader("💰 Electricity Price")
    price_chart = (
        alt.Chart(view)
        .mark_line(point=True)
        .encode(
            x='Year:O',
            y=alt.Y('Price', title='c/kWh'),
            color='Scenario',
            tooltip=['Year','Scenario','Price']
        )
        .properties(height=350)
    )
    st.altair_chart(price_chart, use_container_width=True)

with right:
    st.subheader("🌍 CO₂ Intensity")
    co2_chart = (
        alt.Chart(view)
        .mark_line(point=True)
        .encode(
            x='Year:O',
            y=alt.Y('CO2_kg_per_kWh', title='kg CO₂/kWh'),
            color='Scenario',
            tooltip=['Year','Scenario','CO2_kg_per_kWh']
        )
        .properties(height=350)
    )
    st.altair_chart(co2_chart, use_container_width=True)

# -----------------------------
# 7. Data Table
# -----------------------------
st.subheader("📋 Scenario Data")
st.dataframe(view[['Year','Sector','Scenario','Price','CO2_kg_per_kWh']])
