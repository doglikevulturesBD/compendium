import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from streamlit_plotly_events import plotly_events

# -------------------------
# Load Africa GeoJSON
# -------------------------
geojson_path = os.path.join("data", "africa_countries.geojson")
if not os.path.exists(geojson_path):
    st.error("GeoJSON file not found. Please place africa_countries.geojson in the data/ folder.")
    st.stop()

with open(geojson_path, "r", encoding="utf-8") as f:
    africa_geojson = json.load(f)

# Extract all country names from the geojson
all_countries = [f["properties"]["name"] for f in africa_geojson["features"]]

# -------------------------
# Load commodities CSV
# -------------------------
csv_path = os.path.join("data", "commodities_extended.csv")
if not os.path.exists(csv_path):
    st.error("commodities_extended.csv not found. Please place it in the data/ folder.")
    st.stop()

commodities_df = pd.read_csv(csv_path)

# Clean data
commodities_df["Commodities"] = commodities_df["Commodities"].apply(
    lambda x: [c.strip() for c in str(x).split(";")]
)

# -------------------------
# Merge with all Africa countries
# -------------------------
df = pd.DataFrame({"Country": all_countries})
df = df.merge(commodities_df, on="Country", how="left")
df["HasData"] = df["Commodities"].notna().map({True: "Has Data", False: "No Data"})

# -------------------------
# Build static, non-zoomable map
# -------------------------
fig = px.choropleth(
    df,
    geojson=africa_geojson,
    featureidkey="properties.name",
    locations="Country",
    color="HasData",
    color_discrete_map={
        "Has Data": "#1f77b4",  # blue
        "No Data": "#dddddd"    # grey
    },
    projection="mercator"
)

fig.update_geos(
    fitbounds="locations",
    visible=False
)

fig.update_layout(
    height=700,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    dragmode=False,
    hovermode='closest',
    modebar_remove=[
        "zoom", "pan", "select", "lasso",
        "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"
    ]
)

# -------------------------
# Streamlit UI
# -------------------------
st.title("🌍 Africa Commodities Atlas")
st.write("Click on a blue country to view its commodities and related data")

selected = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

if selected:
    clicked_country = selected[0].get("location")
    row = df.loc[df["Country"] == clicked_country]

    st.subheader(clicked_country)

    if not row.empty and isinstance(row["Commodities"].values[0], list):
        st.write("**Key Commodities:**")
        for c in row["Commodities"].values[0]:
            st.write(f"- {c}")

        st.write(f"**Export Values:** {row['Commodity_Export_Value_USD'].values[0]}")
        st.write(f"**CO₂ per capita:** {row['CO2_emissions_per_capita_tons'].values[0]} tons")
        st.write(f"[🔗 Beneficiation Info]({row['Beneficiation_links'].values[0]})")
        st.write(f"**Notes:** {row['Notes'].values[0]}")
    else:
        st.write("No commodity data available for this country.")
else:
    st.info("💡 Tip: Click on a blue country to see its data")
