import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

DB_PATH = "data/africa.db"

def get_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM country_data", conn)
    conn.close()
    return df

def upsert_country(iso_a3, country, commodities, export_value, co2, link, notes):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO country_data (iso_a3, country, commodities, export_value, co2, link, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(iso_a3) DO UPDATE SET
        country=excluded.country,
        commodities=excluded.commodities,
        export_value=excluded.export_value,
        co2=excluded.co2,
        link=excluded.link,
        notes=excluded.notes
    """, (iso_a3, country, commodities, export_value, co2, link, notes))
    conn.commit()
    conn.close()

df = get_data()

fig = px.choropleth(
    df,
    locations="iso_a3",
    scope="africa",
    projection="mercator",
    color_discrete_sequence=["#1f77b4"]
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    height=700,
    margin={"r":0,"t":0,"l":0,"b":0},
    showlegend=False,
    dragmode=False
)

st.title("🌍 Africa Commodities Atlas")
selected = plotly_events(fig, click_event=True, hover_event=False, override_height=700)

if selected:
    iso = selected[0].get("location")
    row = df.loc[df["iso_a3"] == iso]
    if not row.empty:
        r = row.iloc[0]
        st.markdown(f"### {r['country']}")
        for c in str(r['commodities']).split(";"):
            st.write(f"- {c.strip()}")
        st.write(f"**Export Values:** {r['export_value']}")
        st.write(f"**CO₂ per capita:** {r['co2']} tons")
        st.write(f"[🔗 Beneficiation Info]({r['link']})")
        st.write(f"**Notes:** {r['notes']}")

        # --- Admin section ---
        st.markdown("---")
        st.subheader("🔒 Admin Editor")
        pwd = st.text_input("Enter admin password to edit", type="password")
        if pwd == st.secrets.get("ADMIN_PASS", "my_secret_password"):  # use secrets.toml later
            st.success("Authenticated")
            with st.form("edit_form"):
                new_country = st.text_input("Country", r['country'])
                new_commodities = st.text_area("Commodities (semicolon-separated)", r['commodities'])
                new_export = st.text_input("Export Values", r['export_value'])
                new_co2 = st.text_input("CO₂ per capita", r['co2'])
                new_link = st.text_input("Link", r['link'])
                new_notes = st.text_area("Notes", r['notes'])
                if st.form_submit_button("Save"):
                    upsert_country(iso, new_country, new_commodities, new_export, new_co2, new_link, new_notes)
                    st.success("Updated successfully. Refresh to see changes.")
        elif pwd:
            st.error("Incorrect password.")
    else:
        st.warning("No data for this country.")
else:
    st.info("💡 Click a country to view its data")

