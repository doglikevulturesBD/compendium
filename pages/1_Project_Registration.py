import streamlit as st
import pandas as pd
from registry_db import init_db, insert_project, fetch_projects

# =========================
# Utility: Clear Form State
# =========================
def clear_form(keys):
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

# =========================
# REGISTRY
# =========================
def run_registry():
    st.subheader("📁 Project Registry")
    st.markdown("Register carbon projects and estimate potential credits.")
    init_db()

    with st.form("project_form"):
        name = st.text_input("Project Name", key="reg_name")
        description = st.text_area("Description", key="reg_desc")
        industry = st.selectbox("Industry", ["Cement","Steel","Aluminium","Electricity","Fertilizer","Glass","Pulp & Paper"], key="reg_ind")
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

    # Display table of projects
    st.markdown("---")
    st.subheader("📊 Registered Projects")
    rows = fetch_projects()
    if rows:
        df = pd.DataFrame(rows, columns=["ID","Name","Description","Industry","Baseline","Output","Actual","Leakage","Estimated Credits"])
        st.dataframe(df)
    else:
        st.info("No projects registered yet.")

# =========================
# EV CHARGING CALCULATOR
# =========================
def run_ev_charging_calculator():
    st.subheader("⚡ EV Charging Calculator (VM0038)")

    with st.form("ev_form"):
        fuel_avoided = st.number_input("Fuel Avoided (L or MJ)", key="ev_fuel", min_value=0.0, step=0.1)
        ef_fuel = st.number_input("Emission Factor of Fuel (kg CO₂e/L or MJ)", key="ev_ef_fuel", min_value=0.0, step=0.01)
        elec_used = st.number_input("Electricity Used for Charging (kWh)", key="ev_elec", min_value=0.0, step=0.1)
        ef_grid = st.number_input("Grid Emission Factor (kg CO₂e/kWh)", key="ev_ef_grid", min_value=0.0, step=0.01)
        years = st.number_input("Project Duration (years)", key="ev_years", min_value=1, step=1)
        submitted = st.form_submit_button("Calculate", key="ev_submit")

    if submitted:
        BEy = fuel_avoided * ef_fuel
        PEy = elec_used * ef_grid
        annual_reduction = BEy - PEy
        total_reduction = annual_reduction * years

        st.metric("Baseline Emissions (BEy)", f"{BEy:.2f} kg CO₂e/year")
        st.metric("Project Emissions (PEy)", f"{PEy:.2f} kg CO₂e/year")
        st.metric("Annual Reduction", f"{annual_reduction:.2f} kg CO₂e/year")
        st.metric("Total Reduction", f"{total_reduction:.2f} kg CO₂e")

    if st.button("Clear EV Calculator", key="ev_clear"):
        clear_form(["ev_fuel","ev_ef_fuel","ev_elec","ev_ef_grid","ev_years"])
        st.rerun()

# =========================
# FLEET EFFICIENCY CALCULATOR
# =========================
def run_fleet_efficiency_calculator():
    st.subheader("🚚 Fleet Efficiency Calculator (VMR0004)")

    with st.form("fleet_form"):
        old_rate = st.number_input("Old Fuel Consumption (L/100 km)", key="fl_old", min_value=0.0, step=0.1)
        new_rate = st.number_input("New Fuel Consumption (L/100 km)", key="fl_new", min_value=0.0, step=0.1)
        ef_fuel = st.number_input("Fuel Emission Factor (kg CO₂e/L)", key="fl_ef", min_value=0.0, step=0.01)
        distance = st.number_input("Distance Travelled (km/year)", key="fl_dist", min_value=0.0, step=10.0)
        submitted = st.form_submit_button("Calculate", key="fl_submit")

    if submitted:
        old_em = (old_rate/100.0) * distance * ef_fuel
        new_em = (new_rate/100.0) * distance * ef_fuel
        reduction = old_em - new_em

        st.metric("Old Fleet Emissions", f"{old_em:.2f} kg CO₂e/year")
        st.metric("New Fleet Emissions", f"{new_em:.2f} kg CO₂e/year")
        st.metric("Emission Reduction", f"{reduction:.2f} kg CO₂e/year")

    if st.button("Clear Fleet Calculator", key="fl_clear"):
        clear_form(["fl_old","fl_new","fl_ef","fl_dist"])
        st.rerun()

# =========================
# SOLID WASTE CALCULATOR
# =========================
def run_solid_waste_calculator():
    st.subheader("🗑️ Solid Waste Recycling Calculator (VMR0007)")

    baseline_factors = {"Plastic":1.3,"Paper":1.0,"Metal":1.8,"Glass":0.5,"Other":0.8}
    avoided_factors = {"Plastic":1.1,"Paper":0.6,"Metal":2.5,"Glass":0.3,"Other":0.5}

    with st.form("waste_form"):
        material = st.selectbox("Material Type", list(baseline_factors.keys()), key="sw_material")
        tons = st.number_input("Tons Recovered per Year", key="sw_tons", min_value=0.0, step=0.1)
        pe = st.number_input("Project Emissions (tCO₂e/year)", key="sw_pe", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Calculate", key="sw_submit")

    if submitted:
        BE = tons * baseline_factors[material]
        AE = tons * avoided_factors[material]
        ER = BE + AE - pe

        st.metric("Baseline Emissions Avoided (BE)", f"{BE:.2f} tCO₂e/year")
        st.metric("Avoided Virgin Material Emissions (AE)", f"{AE:.2f} tCO₂e/year")
        st.metric("Project Emissions (PE)", f"{pe:.2f} tCO₂e/year")
        st.metric("Total Emission Reductions (ER)", f"{ER:.2f} tCO₂e/year")

    if st.button("Clear Solid Waste Calculator", key="sw_clear"):
        clear_form(["sw_material","sw_tons","sw_pe"])
        st.rerun()

# =========================
# GENERAL CALCULATOR
# =========================
def run_general_calculator():
    st.subheader("🧮 General GHG Calculator")

    tab1, tab2, tab3 = st.tabs(["📊 Calculator", "📘 Definitions", "📋 Common Factors"])

    with tab1:
        with st.form("general_form"):
            s1_activity = st.number_input("Scope 1 Activity (e.g. liters fuel)", key="gen_s1_act", min_value=0.0, step=0.1)
            s1_ef = st.number_input("Scope 1 EF (kg CO₂e/unit)", key="gen_s1_ef", min_value=0.0, step=0.01)
            s2_activity = st.number_input("Scope 2 Activity (e.g. kWh electricity)", key="gen_s2_act", min_value=0.0, step=0.1)
            s2_ef = st.number_input("Scope 2 EF (kg CO₂e/unit)", key="gen_s2_ef", min_value=0.0, step=0.01)
            s3_activity = st.number_input("Scope 3 Activity (e.g. ton-km transport)", key="gen_s3_act", min_value=0.0, step=0.1)
            s3_ef = st.number_input("Scope 3 EF (kg CO₂e/unit)", key="gen_s3_ef", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Calculate", key="gen_submit")

        if submitted:
            s1_em = s1_activity * s1_ef
            s2_em = s2_activity * s2_ef
            s3_em = s3_activity * s3_ef
            total = s1_em + s2_em + s3_em

            st.metric("Scope 1 Emissions", f"{s1_em:.2f} kg CO₂e")
            st.metric("Scope 2 Emissions", f"{s2_em:.2f} kg CO₂e")
            st.metric("Scope 3 Emissions", f"{s3_em:.2f} kg CO₂e")
            st.metric("Total GHG Emissions", f"{total:.2f} kg CO₂e")

        if st.button("Clear General Calculator", key="gen_clear"):
            clear_form(["gen_s1_act","gen_s1_ef","gen_s2_act","gen_s2_ef","gen_s3_act","gen_s3_ef"])
            st.rerun()

    with tab2:
        st.markdown("""
        ### 📘 Scope Definitions
        **Scope 1:** Direct emissions from owned or controlled sources  
        **Scope 2:** Indirect emissions from purchased electricity  
        **Scope 3:** All other indirect emissions in the value chain
        """)

    with tab3:
        st.markdown("""
        ### 📋 Typical Emission Factors

        | Activity | EF | Unit |
        |---|---|---|
        | Diesel | 2.68 | kg CO₂e/L |
        | Petrol | 2.31 | kg CO₂e/L |
        | Grid Electricity (SA avg) | 0.95 | kg CO₂e/kWh |
        """)

# =========================
# MAIN PAGE
# =========================
def main():
    st.title("🌱 Carbon Registry Hub")

    section = st.radio("Choose a section:",
                       ["Registry", "General Calculator", "Methodology Calculators"],
                       key="main_section_selector")

    if section == "Registry":
        run_registry()
    elif section == "General Calculator":
        run_general_calculator()
    elif section == "Methodology Calculators":
        tool = st.selectbox("Choose a methodology:",
                            ["EV Charging (VM0038)", "Fleet Efficiency (VMR0004)", "Solid Waste Recycling (VMR0007)"],
                            key="methodology_selector")
        if tool == "EV Charging (VM0038)":
            run_ev_charging_calculator()
        elif tool == "Fleet Efficiency (VMR0004)":
            run_fleet_efficiency_calculator()
        elif tool == "Solid Waste Recycling (VMR0007)":
            run_solid_waste_calculator()

if __name__ == "__main__":
    main()


