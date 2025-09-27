import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "carbon_glossary.db"

# ---------------------------
# DB Functions
# ---------------------------
def search_terms(query, category=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    safe_query = f'"{query}"'

    sql = """
    SELECT g.term, g.category, g.definition, g.example, g.greenwash_watch
    FROM glossary g
    JOIN glossary_fts f ON g.id = f.rowid
    WHERE f MATCH ?
    """
    params = [safe_query]

    if category and category != "All":
        sql += " AND g.category = ?"
        params.append(category)

    try:
        cur.execute(sql, params)
        results = cur.fetchall()
    except sqlite3.OperationalError:
        # fallback search
        sql = """
        SELECT term, category, definition, example, greenwash_watch
        FROM glossary
        WHERE term LIKE ? OR definition LIKE ? OR example LIKE ? OR greenwash_watch LIKE ?
        """
        like_query = f"%{query}%"
        cur.execute(sql, (like_query, like_query, like_query, like_query))
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
st.write("Quick reference for key terms in carbon markets, credits, and sustainability.")

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

# ---------------------------
# Results Display (Alphabetical by A–Z)
# ---------------------------
if results:
    # sort results by term (safe conversion to string)
    results = sorted(results, key=lambda x: str(x[0]).lower() if x[0] else "")

    # group by first letter
    grouped = {}
    for r in results:
        term = str(r[0]) if r[0] else "?"
        letter = term[0].upper()
        grouped.setdefault(letter, []).append(r)

    for letter, terms in grouped.items():
        st.subheader(letter)
        for r in terms:
            with st.expander(f"{r[0]} ({r[1]})"):
                st.markdown(f"**Definition:** {r[2]}")
                st.markdown(f"**Example:** {r[3]}")
                st.markdown(f"⚠️ **Greenwash Watch:** {r[4]}")
else:
    if search_query:
        st.warning(f"🔎 '{search_query}' not currently in glossary.")
    else:
        st.info("Use the search bar or category filter to explore terms.")


   
