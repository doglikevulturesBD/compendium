import streamlit as st
import sqlite3, json, os, pandas as pd, string

# ---------- Config ----------
JSON_PATH = "carbon_glossary.json"   # keep this in your repo (source of truth)
DB_PATH = "carbon_glossary_runtime.db"  # runtime-only; safe to ignore in Git

st.set_page_config(page_title="Carbon Glossary", page_icon="🌍", layout="wide")

# ---------- DB init from JSON ----------
def init_db_from_json(json_path=JSON_PATH, db_path=DB_PATH):
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Fresh tables
    cur.execute("DROP TABLE IF EXISTS glossary")
    cur.execute("""
        CREATE TABLE glossary(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            category TEXT,
            definition TEXT,
            example TEXT,
            greenwash_watch TEXT
        )
    """)

    # Insert rows
    for row in data:
        cur.execute("""
            INSERT INTO glossary (term, category, definition, example, greenwash_watch)
            VALUES (?, ?, ?, ?, ?)
        """, (row.get("term",""), row.get("category",""), row.get("definition",""),
              row.get("example",""), row.get("greenwash_watch","")))

    # FTS index
    cur.execute("DROP TABLE IF EXISTS glossary_fts")
    cur.execute("""
        CREATE VIRTUAL TABLE glossary_fts USING fts5(
            term, definition, example, greenwash_watch,
            content='glossary', content_rowid='id'
        )
    """)
    cur.execute("""
        INSERT INTO glossary_fts(rowid, term, definition, example, greenwash_watch)
        SELECT id, term, definition, example, greenwash_watch FROM glossary
    """)

    conn.commit()
    conn.close()

def ensure_db():
    # Build DB at runtime if missing or JSON newer than DB
    build_needed = (not os.path.exists(DB_PATH))
    if not build_needed:
        json_mtime = os.path.getmtime(JSON_PATH) if os.path.exists(JSON_PATH) else 0
        db_mtime = os.path.getmtime(DB_PATH)
        if json_mtime > db_mtime:
            build_needed = True
    if build_needed:
        init_db_from_json()

# ---------- Query helpers ----------
def load_categories():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT category FROM glossary ORDER BY category", conn)
    conn.close()
    return ["All"] + df["category"].dropna().tolist()

def search_terms(query, category=None, start_letter=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Build base SQL using FTS with relevance ranking (bm25: lower = better)
    base_sql = """
    SELECT g.term, g.category, g.definition, g.example, g.greenwash_watch,
           bm25(glossary_fts) as rank
    FROM glossary g
    JOIN glossary_fts f ON g.id = f.rowid
    WHERE f MATCH ?
    """
    params = [f'"{query}"'] if query else ['*']  # '*' matches everything in FTS

    # Filters
    if category and category != "All":
        base_sql += " AND g.category = ?"
        params.append(category)
    if start_letter and start_letter in string.ascii_uppercase:
        base_sql += " AND UPPER(SUBSTR(g.term,1,1)) = ?"
        params.append(start_letter.upper())

    base_sql += " ORDER BY rank ASC, g.term COLLATE NOCASE ASC"

    try:
        cur.execute(base_sql, params)
        results = cur.fetchall()
        conn.close()
        return results
    except sqlite3.OperationalError:
        # Fallback to LIKE search if FTS parsing fails
        like_sql = """
        SELECT term, category, definition, example, greenwash_watch, 0 as rank
        FROM glossary
        WHERE 1=1
        """
        like_params = []
        if query:
            like_sql += " AND (term LIKE ? OR definition LIKE ? OR example LIKE ? OR greenwash_watch LIKE ?)"
            like_q = f"%{query}%"
            like_params += [like_q, like_q, like_q, like_q]
        if category and category != "All":
            like_sql += " AND category = ?"
            like_params.append(category)
        if start_letter and start_letter in string.ascii_uppercase:
            like_sql += " AND UPPER(SUBSTR(term,1,1)) = ?"
            like_params.append(start_letter.upper())

        like_sql += " ORDER BY term COLLATE NOCASE ASC"
        cur.execute(like_sql, like_params)
        results = cur.fetchall()
        conn.close()
        return results

def group_by_letter(rows):
    # rows: tuples (term, category, definition, example, greenwash, rank)
    grouped = {}
    for r in rows:
        term = str(r[0]) if r[0] else ""
        letter = term[:1].upper() if term else "?"
        if not letter.isalpha():
            letter = "#"
        grouped.setdefault(letter, []).append(r)
    # sort letters A-Z, with '#' last
    keys = sorted([k for k in grouped.keys() if k != "#"]) + (["#"] if "#" in grouped else [])
    return [(k, grouped[k]) for k in keys]

# ---------- App ----------
# Ensure DB exists from JSON
if not os.path.exists(JSON_PATH):
    st.error("JSON glossary not found. Place 'carbon_glossary.json' in the app root.")
    st.stop()
ensure_db()

st.title("Carbon Glossary")
st.write("Quick reference for the most important terms in **carbon markets**, **ESG**, and **climate policy**. "
         "Use search, category and A–Z filters below. The glossary is curated from a Carbon 101 foundation and progresses to advanced topics.")

# Controls
cols = st.columns([2, 1, 1])
with cols[0]:
    q = st.text_input("Search", placeholder="Try: additionality, CBAM, double counting, REC, etc.")
with cols[1]:
    category = st.selectbox("Category", load_categories(), index=0)
with cols[2]:
    letters = ["All"] + list(string.ascii_uppercase)
    jump_letter = st.selectbox("A–Z", letters, index=0)

# Fetch
start_letter = None if jump_letter == "All" else jump_letter
rows = search_terms(q.strip() if q else None, category=None if category == "All" else category, start_letter=start_letter)

# Display
if not rows:
    if q:
        st.warning(f"🔎 '{q}' not currently in glossary.")
    else:
        st.info("Use the search bar, category, or A–Z filter to explore terms.")
    st.stop()

# Group A–Z and render with expanders per term (neat, not cluttered)
for letter, terms in group_by_letter(rows):
    st.subheader(letter)
    for r in terms:
        term, cat, definition, example, greenwash, _rank = r
        with st.expander(f"{term}  ·  {cat}"):
            st.markdown(f"**Definition**  \n{definition}")
            if example:
                st.markdown(f"**Example**  \n{example}")
            if greenwash:
                st.markdown(f"**⚠️ Greenwash Watch**  \n{greenwash}")

