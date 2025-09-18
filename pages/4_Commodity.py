import streamlit as st
import pandas as pd
import json
import plotly.express as px
from streamlit_plotly_events import plotly_events

# -------------------------
# Load Africa country shapes
# -------------------------
with open("data/africa_countries.geojson", "r", encoding="utf-8") as f:
    africa_geojson = json.load(f)

# -------------------------
# Commodity dataset
# -------------------------
commodities_data = {
    "South Africa": ["Platinum", "Gold", "Chromium"],
    "Democratic Republic of the Congo": ["Cobalt", "Copper"],
    "Botswana": ["Diamonds", "Nickel"],
    "Zambia": ["Copper", "Cobalt"],
    "Ghana": ["Gold", "Bauxite"],
}
df = pd.DataFrame(list(commodities_data.items()), columns=["Country", "Commodities"])

# -------------------------
# Build map
# -------------------------
fig = px.choropleth(
    df,
    geojson=africa_geojson,
    featureidkey="properties.ADMIN",
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
