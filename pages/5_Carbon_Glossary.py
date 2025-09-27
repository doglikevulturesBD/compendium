import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "carbon_glossary.db"  # make sure db is in the root folder

# ---------------------------
# DB Functions
# ---------------------------
def search_terms(query, category=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    safe_query = f'"{query}"'  # wrap in quotes for FTS parsing

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
        # fallback: LIKE search if FTS fails
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

# ---------------------------
# Results Display (Card Style)
# ---------------------------
if results:
    for r in results:
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ccc; 
                border-radius: 10px; 
                padding: 15px; 
                margin-bottom: 12px; 
                background-color: #f9f9f9;
            ">
                <h4 style="margin-bottom:5px;">{r[0]} <span style="font-size:0.8em; color:gray;">({r[1]})</span></h4>
                <p><b>Definition:</b> {r[2]}</p>
                <p><b>Example:</b> {r[3]}</p>
                <p style="color:#b00020;"><b>⚠️ Greenwash Watch:</b> {r[4]}</p>
            </div>
            """, unsafe_allow_html=True
        )
else:
    if search_query:
        st.warning(f"🔎 '{search_query}' not currently in glossary.")
    else:
        st.info("Use the search bar or category filter to explore terms.")

   
