import streamlit as st
import pandas as pd
import json
import plotly.express as px
from streamlit_plotly_events import plotly_events
import os

# -------------------------
# Load Africa country shapes
# -------------------------
geojson_path = os.path.join("data", "africa_countries.geojson")
if not os.path.exists(geojson_path):
    st.error("GeoJSON file not found. Please place africa_countries.geojson in the data/ folder.")
    st.stop()

with open(geojson_path, "r", encoding="utf-8") as f:
    africa_geojson = json.load(f)

# -------------------------
# Load commodities CSV
# -------------------------
csv_path = os.path.join("data", "commodities.csv")
if not os.path.exists(csv_path):
    st.error("commodities.csv not found. Please place it in the data/ folder.")
    st.stop()

df = pd.read_csv(csv_path)
# Convert commodities column from string to list
df["Commodities"] = df["Commodities"].apply(lambda x: [c.strip() for c in x.split(";")])

# -------------------------
# Build interactive map
# -------------------------
fig = px.choropleth(
    df,
    geojson=africa_geojson,
    featureidkey="properties.name",
    locations="Country",
    color_discrete_sequence=["#87ceeb"],
    projection="mercator"
)
fig.update_geos(fitbounds="locations", visible=False)

# -------------------------
# Streamlit UI
# -------------------------
st.title("🌍 Africa Commodities Atlas")
st.write("Click on a country to view its major commodities")

selected = plotly_events(fig, click_event=True, hover_event=False)

if selected:
    clicked_country = selected[0].get("location")
    commodities = df.loc[df["Country"] == clicked_country, "Commodities"].values
    if len(commodities) > 0:
        st.subheader(clicked_country)
        st.write("**Key commodities:**")
        for c in commodities[0]:
            st.write(f"- {c}")
    else:
        st.write("No data yet for this country.")
else:
    st.info("💡 Tip: Click on a country to see its data")

