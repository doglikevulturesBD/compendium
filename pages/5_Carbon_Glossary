import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "carbon_glossary.db"  # keep this in root folder

# ---------------------------
# DB Functions
# ---------------------------
def search_terms(query, category=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    sql = """
    SELECT g.term, g.category, g.definition, g.example, g.greenwash_watch
    FROM glossary g
    JOIN glossary_fts f ON g.id = f.rowid
    WHERE f MATCH ?
    """
    params = [query]

    if category and category != "All":
        sql += " AND g.category = ?"
        params.append(category)

    cur.execute(sql, params)
    results = cur.fetchall()
    conn.close()
    return results


def load_categories():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT category FROM glossary ORDER BY category", conn)
    conn.close()
    return df["category"].tolist()


def load_all():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM glossary", conn)
    conn.close()
    return df


# ---------------------------
# Page Layout
# ---------------------------
st.title("🌍 Carbon Glossary")
st.write("Quick reference for the most important terms in carbon markets, credits, and sustainability.")

# Sidebar filters
categories = load_categories()
selected_category = st.sidebar.selectbox("Filter by Category", ["All"] + categories)
search_query = st.sidebar.text_input("Search term")

# Data retrieval
if search_query:
    results = search_terms(search_query, selected_category)
else:
    df = load_all()
    if selected_category != "All":
        df = df[df['category'] == selected_category]
    results = df.values.tolist()

# Display results
if results:
    for r in results:
        with st.expander(f"**{r[0]}**  ({r[1]})"):
            st.markdown(f"**Definition:** {r[2]}")
            st.markdown(f"**Example:** {r[3]}")
            st.markdown(f"⚠️ **Greenwash Watch:** {r[4]}")
else:
    st.info("No results found. Try a different search term or category.")
