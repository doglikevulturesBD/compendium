import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events

DB_PATH = "data/africa.db"

# -----------------------------
# DB functions
# -----------------------------
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS country_data (
            iso_a3 TEXT PRIMARY KEY,
            country TEXT,
            commodities TEXT,
            export_value TEXT,
            co2 TEXT,
            link TEXT,
            notes TEXT
        )
    """)
    # seed if empty
    cur.execute("SELECT COUNT(*) FROM country_data")
    if cur.fetchone()[0] == 0:
        seed = [
            ("ZAF", "South Africa", "Gold; Platinum; Coal", "Gold: 25.9B; Platinum: 13.8B", "6.5", "https://www.mineralscouncil.org.za/", "Highly industrialised mining sector"),
            ("GHA", "Ghana", "Gold; Cocoa; Timber", "Gold: 15.6B; Cocoa: 1.5B", "1.5", "https://www.mincom.gov.gh/", "Strong gold and cocoa exports"),
            ("NGA", "Nigeria", "Crude Oil; Cocoa", "Crude oil: 43.5B", "0.8", "https://www.nnpcgroup.com/", "Oil dominates exports")
        ]
        cur.executemany("INSERT INTO country_data VALUES (?,?,?,?,?,?,?)", seed)
    conn.commit()
    conn.close()

def get_data():
    if not os.path.exists(DB_PATH):
        init_db()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM country_data", conn)

