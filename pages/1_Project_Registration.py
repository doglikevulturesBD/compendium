import streamlit as st

# --- Sample Industry Emissions Intensity (tCO2e per tonne of product) ---
industry_baselines = {
    "Cement": 0.9,
    "Steel": 1.9,
    "Aluminium": 12.0,
    "Electricity (Coal Grid)": 0.95,
    "Fertilizer (Urea)": 1.5,
    "Glass": 0.8,
    "Pulp & Paper": 1.1
}

st.title("📄 Register a Carbon Project")

st.markdown("Fill out the details below to simulate a new carbon project and estimate the credits it could generate.")

# --- Form Input ---
with st.form("project_form"):
    project_name = st.text_input("Project Name")
    industry = st.selectbox("Industry / Sector", list(industry_baselines.keys()))
    tonnes_produced = st.number_input("Total Output (Tonnes)", min_value=0.0, step=0.1)
    actual_emissions = st.number_input("Actual Emissions (tCO₂e)", min_value=0.0, step=0.1)
    leakage = st.number_input("Leakage (tCO₂e)", min_value=0.0, step=0.1, value=0.0)
    description = st.text_area("Project Description", height=100)

    submitted = st.form_submit_button("Calculate & Preview Credits")

# --- Logic ---
if submitted:
    baseline_intensity = industry_baselines[industry]
    baseline_emissions = baseline_intensity * tonnes_produced
    estimated_credits = baseline_emissions - actual_emissions - leakage

    st.subheader("📊 Project Summary")
    st.markdown(f"**Project:** {project_name}")
    st.markdown(f"**Industry:** {industry}")
    st.markdown(f"**Baseline Emissions:** {baseline_emissions:.2f} tCO₂e")
    st.markdown(f"**Actual Emissions:** {actual_emissions:.2f} tCO₂e")
    st.markdown(f"**Leakage:** {leakage:.2f} tCO₂e")
    st.markdown(f"**Estimated Credits:** `{estimated_credits:.2f}` tCO₂e")

    if estimated_credits > 0:
        st.success("✅ This project would generate carbon credits.")
    elif estimated_credits == 0:
        st.info("⚠️ This project would be neutral — no credits.")
    else:
        st.warning("❌ This project would not qualify for credits (net emissions increase).")
