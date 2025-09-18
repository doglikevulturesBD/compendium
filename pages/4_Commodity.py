import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from streamlit_plotly_events import plotly_events
import unicodedata

# -------------------------
# Helper to normalize names
# -------------------------
def normalize_name(name):
    if pd.isna(name):
        return ""
    # Remove accents and unify case
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
    return name.strip().lower()

# -------------------------
# Load Africa GeoJSON
# -------------------------
geojson_path = os.path.join("data", "africa_countries.geojson")
with open(geojson_path, "r", encoding="utf-8") as f:
    africa_geojson = json.load(f)

geo_countries = [f["properties"]["name"] for f in africa_geojson["features"]]

# -------------------------
# Load CSV
# -------------------------
csv_path = os.path.join("data", "commodities_extended.csv")
commodities_df = pd.read_csv(csv_path)

# Normalize for joining
commodities_df["Country_norm"] = commodities_df["Country"].apply(normalize_name)
geo_df = pd.DataFrame({"Country": geo_countries})
geo_df["Country_norm"] = geo_df["Country"].apply(normalize_name)

# Merge
df = geo_df.merge(commodities_df, on="Country_norm", how="left")
df["HasData"] = df["Commodities"].notna().map({True: "Has Data", False: "No Data"})

# -------------------------
# Build map
# -------------------------
fig = px.choropleth(
    df,
    geojson=africa_geojson,
    featureidkey="properties.name",
    locations="Country_x",  # from geo_df side
    color="HasData",
    color_discrete_map={"Has Data": "#1f77b4", "No Data": "#dddddd"},
    projection="mercator"
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    height=700,
    margin={"r":0, "t":0, "l":0, "b":0},
    dragmode=False,
    hovermode='closest',
    modebar_remove=["zoom","pan","select","lasso","zoomIn2d","zoomOut2d"]
)

# -------------------------
# Streamlit UI
# -------------------------
st.title("🌍 Africa Commodities Atlas")
st.write("Click on a blue country to view its data")

selected = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

if selected:
    clicked_country = selected[0].get("location")
    row = df.loc[df["Country_x"] == clicked_country]

    st.subheader(clicked_country)

    if not row.empty and pd.notna(row["Commodities"].values[0]):
        commodities = [c.strip() for c in row["Commodities"].values[0].split(";")]
        st.write("**Key Commodities:**")
        for c in commodities:
            st.write(f"- {c}")

        st.write(f"**Export Values:** {row['Commodity_Export_Value_USD'].values[0]}")
        st.write(f"**CO₂ per capita:** {row['CO2_emissions_per_capita_tons'].values[0]} tons")
        if pd.notna(row['Beneficiation_links'].values[0]):
            st.write(f"[🔗 Beneficiation Info]({row['Beneficiation_links'].values[0]})")
        st.write(f"**Notes:** {row['Notes'].values[0]}")
    else:
        st.warning("No commodity data available for this country.")
else:
    st.info("💡 Tip: Click on a blue country to see its data")

# -------------------------
# Debugging helper
# -------------------------
missing = df[df["HasData"] == "No Data"]["Country_x"].tolist()
st.caption(f"⚠️ No matches for: {', '.join(missing[:10])} ...")

