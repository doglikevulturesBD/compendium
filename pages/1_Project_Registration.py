import streamlit as st

# ======================
# RESET FORM FUNCTION
# ======================
def clear_form(keys):
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

# ======================
# EV CHARGING CALCULATOR
# ======================
def run_ev_charging_calculator():
    st.subheader("⚡ EV Charging Calculator (VM0038)")
    st.markdown("Estimate avoided emissions by switching from ICE vehicles to EVs.")

    with st.form("ev_form"):
        energy = st.number_input("Electricity Consumed (kWh)", key="ev_energy", min_value=0.0, step=0.1)
        grid_factor = st.number_input("Grid Emission Factor (kg CO₂/kWh)", key="ev_grid", min_value=0.0, step=0.01)
        vehicles = st.number_input("Number of EVs Charged", key="ev_vehicles", min_value=0, step=1)
        baseline = st.number_input("Baseline ICE Emissions (kg CO₂/vehicle)", key="ev_base", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Calculate")

    if submitted:
        charging_em = energy * grid_factor
        base_em = vehicles * baseline
        avoided = base_em - charging_em

        st.metric("Charging Emissions", f"{charging_em:.2f} kg CO₂")
        st.metric("Baseline Emissions", f"{base_em:.2f} kg CO₂")
        st.metric("Avoided Emissions", f"{avoided:.2f} kg CO₂")

        if avoided > 0:
            st.success("✅ This EV charging project reduces emissions.")
        else:
            st.warning("⚠️ No emission reduction achieved.")

    if st.button("Clear EV Calculator"):
        clear_form(["ev_energy","ev_grid","ev_vehicles","ev_base"])
        st.experimental_rerun()


# ============================
# FLEET EFFICIENCY CALCULATOR
# ============================
def run_fleet_efficiency_calculator():
    st.subheader("🚚 Fleet Efficiency Calculator (VMR0004)")
    st.markdown("Estimate emissions saved from improved fleet fuel efficiency.")

    with st.form("fleet_form"):
        old_eff = st.number_input("Old Fuel Consumption (L/100km)", key="fl_old", min_value=0.0, step=0.1)
        new_eff = st.number_input("New Fuel Consumption (L/100km)", key="fl_new", min_value=0.0, step=0.1)
        distance = st.number_input("Distance Travelled (km)", key="fl_dist", min_value=0.0, step=10.0)
        emission_factor = st.number_input("Emission Factor (kg CO₂/L)", key="fl_ef", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Calculate")

    if submitted:
        old_em = (old_eff/100) * distance * emission_factor
        new_em = (new_eff/100) * distance * emission_factor
        saved = old_em - new_em

        st.metric("Old Fleet Emissions", f"{old_em:.2f} kg CO₂")
        st.metric("New Fleet Emissions", f"{new_em:.2f} kg CO₂")
        st.metric("Emissions Saved", f"{saved:.2f} kg CO₂")

        if saved > 0:
            st.success("✅ This fleet project reduces emissions.")
        else:
            st.warning("⚠️ No emission reduction achieved.")

    if st.button("Clear Fleet Calculator"):
        clear_form(["fl_old","fl_new","fl_dist","fl_ef"])
        st.experimental_rerun()


# ============================
# SOLID WASTE CALCULATOR
# ============================
def run_solid_waste_calculator():
    st.subheader("🗑️ Solid Waste Recycling Calculator (VMR0007)")
    st.markdown("Estimate avoided emissions from diverting solid waste from landfill.")

    with st.form("waste_form"):
        waste_diverted = st.number_input("Waste Diverted (tonnes)", key="sw_waste", min_value=0.0, step=0.1)
        landfill_factor = st.number_input("Landfill Emission Factor (kg CO₂/tonne)", key="sw_land", min_value=0.0, step=1.0)
        recycling_factor = st.number_input("Recycling Emission Factor (kg CO₂/tonne)", key="sw_rec", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Calculate")

    if submitted:
        landfill_em = waste_diverted * landfill_factor
        recycling_em = waste_diverted * recycling_factor
        avoided = landfill_em - recycling_em

        st.metric("Landfill Emissions", f"{landfill_em:.2f} kg CO₂")
        st.metric("Recycling Emissions", f"{recycling_em:.2f} kg CO₂")
        st.metric("Avoided Emissions", f"{avoided:.2f} kg CO₂")

        if avoided > 0:
            st.success("✅ This solid waste project reduces emissions.")
        else:
            st.warning("⚠️ No emission reduction achieved.")

    if st.button("Clear Solid Waste Calculator"):
        clear_form(["sw_waste","sw_land","sw_rec"])
        st.experimental_rerun()


# ==========================
# MAIN CARBON REGISTRY PAGE
# ==========================
def main():
    st.title("🌱 Carbon Registry Hub")

    section = st.radio("Choose a section:", ["Registry", "General Calculator", "Methodology Calculators"])

    if section == "Registry":
        st.info("📂 Registry App will go here (coming soon)")

    elif section == "General Calculator":
        st.info("🧮 General carbon calculator will go here (coming soon)")

    elif section == "Methodology Calculators":
        st.subheader("📚 Methodology Calculators")
        tool = st.selectbox("Choose a methodology:", [
            "EV Charging (VM0038)",
            "Fleet Efficiency (VMR0004)",
            "Solid Waste Recycling (VMR0007)"
        ])

        if tool == "EV Charging (VM0038)":
            run_ev_charging_calculator()
        elif tool == "Fleet Efficiency (VMR0004)":
            run_fleet_efficiency_calculator()
        elif tool == "Solid Waste Recycling (VMR0007)":
            run_solid_waste_calculator()

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
