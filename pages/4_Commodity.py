import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import pycountry

# Load CSV
df = pd.read_csv("data/commodities_extended.csv")

# Clean and split commodities
df["Commodities"] = df["Commodities"].apply(lambda x: [c.strip() for c in str(x).split(";")])

# Get ISO codes from country names (needed for Plotly)
def get_iso3(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

df["iso_a3"] = df["Country"].apply(get_iso3)

# Build map
fig = px.choropleth(
    df,
    locations="iso_a3",
    color="Country",
    hover_name="Country",
    scope="africa",
    projection="mercator",
    color_discrete_sequence=["#1f77b4"]
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    height=700,
    margin={"r":0,"t":0,"l":0,"b":0},
    dragmode=False,
    modebar_remove=[
        "zoom","pan","select","lasso",
        "zoomIn2d","zoomOut2d","autoScale2d","resetScale2d"
    ]
)

# UI
st.title("🌍 Africa Commodities Atlas (No GeoJSON)")
st.write("Click on a blue country to see its data")

selected = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

if selected:
    iso_clicked = selected[0].get("location")
    row = df.loc[df["iso_a3"] == iso_clicked]

    if not row.empty:
        st.subheader(row["Country"].values[0])
        for c in row["Commodities"].values[0]:
            st.write(f"- {c}")
        st.write(f"**Export Values:** {row['Commodity_Export_Value_USD'].values[0]}")
        st.write(f"**CO₂ per capita:** {row['CO2_emissions_per_capita_tons'].values[0]} tons")
        st.write(f"[🔗 Beneficiation Info]({row['Beneficiation_links'].values[0]})")
        st.write(f"**Notes:** {row['Notes'].values[0]}")
    else:
        st.warning("No data available for this country.")
else:
    st.info("💡 Tip: Click on a blue country to see its data")

