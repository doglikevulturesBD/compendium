import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

# --- Get data from DB ---
def get_data():
    conn = sqlite3.connect("data/africa.db")
    df = pd.read_sql_query("SELECT * FROM country_data", conn)
    conn.close()
    return df

df = get_data()

# --- Map ---
fig = px.choropleth(
    df,
    locations="iso_a3",
    scope="africa",
    projection="mercator",
    color_discrete_sequence=["#1f77b4"]
)
fig.update_traces(marker_line_width=0.2)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    height=700,
    margin={"r":0,"t":0,"l":0,"b":0},
    showlegend=False,
    dragmode=False,
    modebar_remove=[
        "zoom","pan","select","lasso",
        "zoomIn2d","zoomOut2d","autoScale2d","resetScale2d"
    ]
)

# --- UI ---
st.title("🌍 Africa Commodities Atlas")

selected = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

if selected:
    iso = selected[0].get("location")
    row = df.loc[df["iso_a3"] == iso]

    if not row.empty:
        row = row.iloc[0]
        with st.container():
            st.markdown(f"### {row['country']}")
            st.markdown(f"**Commodities:**")
            for c in str(row['commodities']).split(";"):
                st.write(f"- {c.strip()}")
            st.write(f"**Export Values:** {row['export_value']}")
            st.write(f"**CO₂ per capita:** {row['co2']} tons")
            st.write(f"[🔗 Beneficiation Info]({row['link']})")
            st.write(f"**Notes:** {row['notes']}")
    else:
        st.warning("No data available for this country.")
else:
    st.info("💡 Click a country to view its data")

