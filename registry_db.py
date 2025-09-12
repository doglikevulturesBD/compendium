import sqlite3

def init_db():
    conn = sqlite3.connect("registry.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        industry TEXT,
        baseline_intensity REAL,
        output_tonnes REAL,
        actual_emissions REAL,
        leakage REAL,
        estimated_credits REAL
    )
    """)
    conn.commit()
    conn.close()

def insert_project(data):
    conn = sqlite3.connect("registry.db")
    c = conn.cursor()
    c.execute("""
    INSERT INTO projects
    (name, description, industry, baseline_intensity, output_tonnes, actual_emissions, leakage, estimated_credits)
    VALUES (?,?,?,?,?,?,?,?)
    """, data)
    conn.commit()
    conn.close()

def fetch_projects():
    conn = sqlite3.connect("registry.db")
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    rows = c.fetchall()
    conn.close()
    return rows

def update_project(project_id, name, description, industry, baseline, output, actual, leakage, credits):
    conn = sqlite3.connect("registry.db")
    c = conn.cursor()
    c.execute("""
        UPDATE projects
        SET name=?, description=?, industry=?, baseline_intensity=?, output_tonnes=?,
            actual_emissions=?, leakage=?, estimated_credits=?
        WHERE id=?
    """, (name, description, industry, baseline, output, actual, leakage, credits, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect("registry.db")
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()

