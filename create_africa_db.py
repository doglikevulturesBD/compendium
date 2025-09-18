import sqlite3
import os

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/africa.db")
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

sample = [
    ("ZAF", "South Africa", "Gold; Platinum; Coal", "Gold: 25.9B; Platinum: 13.8B", "6.5", "https://www.mineralscouncil.org.za/", "Highly industrialised mining sector"),
    ("GHA", "Ghana", "Gold; Cocoa; Timber", "Gold: 15.6B; Cocoa: 1.5B", "1.5", "https://www.mincom.gov.gh/", "Strong gold and cocoa exports"),
    ("NGA", "Nigeria", "Crude Oil; Cocoa", "Crude oil: 43.5B", "0.8", "https://www.nnpcgroup.com/", "Oil dominates exports")
]
cur.executemany("INSERT OR REPLACE INTO country_data VALUES (?, ?, ?, ?, ?, ?, ?)", sample)

conn.commit()
conn.close()

print("✅ africa.db created in /data")
