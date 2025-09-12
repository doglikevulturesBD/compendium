import streamlit as st

# ======================
# EV CHARGING CALCULATOR
# ======================

def run_ev_charging_calculator():
    st.subheader("⚡ EV Charging Calculator (VM0038)")

    st.markdown("""
    This tool estimates emissions from electricity used for EV charging,
    and calculates avoided emissions compared to a baseline ICE vehicle fleet.
    """)

    # --- Inputs ---
    with st.form("ev_form"):
        energy_consumed = st.number_input("Electricity Consumed for Charging (kWh)", min_value=0.0, step=0.1)
        grid_emission_factor = st.number_input("Grid Emission Factor (kg CO₂/kWh)", min_value=0.0, step=0.01)
        num_vehicles = st.number_input("Number of EVs Charged", min_value=0, step=1)
        baseline_emissions_per_vehicle = st.number_input("Baseline ICE Emissions (kg CO₂/vehicle)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Calculate")

    # --- Logic ---
    if submitted:
        charging_emissions = energy_consumed * grid_emission_factor
        baseline_emissions = num_vehicles * baseline_emissions_per_vehicle
        avoided_emissions = baseline_emissions - charging_emissions

        st.markdown("### 📊 Results")
        st.metric("Charging Emissions", f"{charging_emissions:.2f} kg CO₂")
        st.metric("Baseline Emissions", f"{baseline_emissions:.2f} kg CO₂")
        st.metric("Avoided Emissions", f"{avoided_emissions:.2f} kg CO₂")

        if avoided_emissions > 0:
            st.success("✅ This EV charging project reduces emissions.")
        else:
            st.warning("⚠️ No emission reduction achieved.")


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
        tool = st.selectbox("Choose a methodology:", ["EV Charging (VM0038)", "Fleet Efficiency (VMR0004)", "Solid Waste Recycling (VMR0007)"])

        if tool == "EV Charging (VM0038)":
            run_ev_charging_calculator()
        else:
            st.info("⚠️ This calculator will be added soon.")

if __name__ == "__main__":
    main()
