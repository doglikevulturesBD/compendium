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

# Extract all country names from GeoJSON
all_countries = [f["properties"]["name"] for f in africa_geojson["features"]]

# -------------------------
# Load commodities CSV
# -------------------------
csv_path = os.path.join("data", "commodities.csv")
if not os.path.exists(csv_path):
    st.error("commodities.csv not found. Please place it in the data/ folder.")
    st.stop()

commodities_df = pd.read_csv(csv_path)
commodities_df["Commodities"] = commodities_df["Commodities"].apply(lambda x: [c.strip() for c in x.split(";")])

# -------------------------
# Build combined dataframe
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
        "Has Data": "#1f77b4",   # blue
        "No Data": "#dddddd"     # grey
    },
    projection="mercator"
)

fig.update_geos(
    fitbounds="locations",
    visible=False,
    showcountries=True,
    showframe=False
)

# Lock map size and disable zoom/pan
fig.update_layout(
    height=700,
    margin={"r":0, "t":0, "l":0, "b":0},
    dragmode=False,
    hovermode='closest',
    modebar_remove=["zoom", "pan", "select", "lasso", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"]
)

# -------------------------
# Streamlit UI
# -------------------------
st.title("🌍 Africa Commodities Atlas")
st.write("Click on a highlighted country to view its major commodities")

selected = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

if selected:
    clicked_country = selected[0].get("location")
    row = df.loc[df["Country"] == clicked_country]

    st.subheader(clicked_country)

    if not row.empty and isinstance(row["Commodities"].values[0], list):
        commodities = row["Commodities"].values[0]
        st.write("**Key commodities:**")
        for c in commodities:
            st.write(f"- {c}")
    else:
        st.write("No commodity data available for this country.")
else:
    st.info("💡 Tip: Click on a blue country to see its data")

