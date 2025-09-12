import streamlit as st
from registry_db import init_db, insert_project, fetch_projects

# =========================
# REGISTRY PAGE
# =========================
def run_registry():
    st.subheader("📁 Project Registry")
    st.markdown("Register carbon projects and estimate potential credits.")

    # Ensure DB is created
    init_db()

    with st.form("project_form"):
        name = st.text_input("Project Name", key="reg_name")
        description = st.text_area("Description", key="reg_desc")
        industry = st.selectbox("Industry", ["Cement", "Steel", "Aluminium", "Electricity", "Fertilizer", "Glass", "Pulp & Paper"], key="reg_ind")
        baseline_intensity = st.number_input("Baseline Emission Intensity (tCO₂e/tonne)", key="reg_base", min_value=0.0, step=0.01)
        output_tonnes = st.number_input("Output Produced (tonnes)", key="reg_out", min_value=0.0, step=0.1)
        actual_emissions = st.number_input("Actual Emissions (tCO₂e)", key="reg_act", min_value=0.0, step=0.1)
        leakage = st.number_input("Leakage (tCO₂e)", key="reg_leak", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Save Project")

    if submitted:
        estimated_credits = (baseline_intensity * output_tonnes) - actual_emissions - leakage
        data = (name, description, industry, baseline_intensity, output_tonnes, actual_emissions, leakage, estimated_credits)
        insert_project(data)
        st.success(f"✅ {name} saved with {estimated_credits:.2f} tCO₂e credits estimated.")
        st.rerun()

    # Table of projects
    st.markdown("---")
    st.subheader("📊 Registered Projects")
    rows = fetch_projects()
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["ID","Name","Description","Industry","Baseline","Output","Actual","Leakage","Estimated Credits"])
        st.dataframe(df)
    else:
        st.info("No projects registered yet.")
