import streamlit as st

# ==============
# Reset helper
# ==============
def clear_form(keys):
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

# ======================
# EV CHARGING CALCULATOR
# ======================
def run_ev_charging_calculator():
    st.subheader("⚡ EV Charging Calculator (VM0038)")

    with st.form("ev_form"):
        fuel_avoided = st.number_input("Fuel Avoided (liters or MJ)", key="ev_fuel", min_value=0.0, step=0.1)
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
        st.experimental_rerun()

# ============================
# FLEET EFFICIENCY CALCULATOR
# ============================
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
        st.experimental_rerun()

# ============================
# SOLID WASTE CALCULATOR
# ============================
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
        st.experimental_rerun()

# ==========================
# MAIN PAGE
# ==========================
def main():
    st.title("🌱 Carbon Registry Hub")

    section = st.radio("Choose a section:",
                       ["Registry", "General Calculator", "Methodology Calculators"],
                       key="main_section_selector")

    if section == "Registry":
        st.info("📂 Registry App will go here (coming soon)")

    elif section == "General Calculator":
        st.info("🧮 General carbon calculator will go here (coming soon)")

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

