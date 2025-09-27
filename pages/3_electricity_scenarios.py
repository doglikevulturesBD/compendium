# ========================
# 5. Visualisation
# ========================
if view_mode == "View one sector":
    sector = st.selectbox("Select Sector", df['Sector'].unique())
    scenario = st.selectbox("Select Scenario", ['BAU','IRP','Accelerated'])
    st.markdown(f"**Scenario explanation:**")
    if scenario == "BAU":
        st.info("**Business as Usual:** Fossil-heavy future, price growth continues following historical trend. Carbon intensity remains high.")
    elif scenario == "IRP":
        st.info("**IRP-aligned:** Moderate renewables build-out as planned by government; price growth slows. Carbon intensity falls steadily.")
    else:
        st.info("**Accelerated:** Aggressive renewables rollout; price growth flattens and carbon intensity drops sharply.")
        
    filtered = df[(df['Sector']==sector) & (df['Scenario'].isin(['Historical',scenario]))]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Electricity Price")
        chart_price = (
            alt.Chart(filtered)
            .mark_line(point=True)
            .encode(
                x='Year:O', y=alt.Y('Price', title='c/kWh'),
                color='Scenario', tooltip=['Year','Scenario','Price']
            )
        )
        st.altair_chart(chart_price, use_container_width=True)

    with col2:
        st.subheader("CO₂ Intensity")
        chart_co2 = (
            alt.Chart(filtered)
            .mark_line(point=True)
            .encode(
                x='Year:O', y=alt.Y('CO2_kg_per_kWh', title='kg CO₂/kWh'),
                color='Scenario', tooltip=['Year','Scenario','CO2_kg_per_kWh']
            )
        )
        st.altair_chart(chart_co2, use_container_width=True)

    # ========================
    # 6. 2035 Summary Cards
    # ========================
    st.markdown("### 2035 Summary")
    summary = df[(df['Sector']==sector) & (df['Year']==2035) & (df['Scenario'].isin(['BAU','IRP','Accelerated']))]
    colA, colB, colC = st.columns(3)
    for (scenario_name, color, col) in zip(['BAU','IRP','Accelerated'], ['red','green','blue'], [colA,colB,colC]):
        row = summary[summary['Scenario']==scenario_name].iloc[0]
        with col:
            st.markdown(f"#### {scenario_name}")
            st.metric(label="Price (c/kWh)", value=f"{row['Price']:.1f}")
            st.metric(label="CO₂ (kg/kWh)", value=f"{row['CO2_kg_per_kWh']:.2f}")

elif view_mode == "Compare all sectors":
    st.markdown("**Compare electricity price and CO₂ trends across all three sectors** (Residential, Business, Industrial).")
    scenario = st.selectbox("Select Scenario", ['BAU','IRP','Accelerated'])
    metric = st.radio("Select metric to compare:", ["Price (c/kWh)", "CO₂ Intensity (kg CO₂/kWh)"])
    compare_df = df[(df['Scenario']==scenario)]
    
    if "Price" in metric:
        chart = (
            alt.Chart(compare_df)
            .mark_line(point=True)
            .encode(
                x='Year:O', y=alt.Y('Price', title='c/kWh'),
                color='Sector', tooltip=['Year','Sector','Price']
            )
        )
    else:
        chart = (
            alt.Chart(compare_df)
            .mark_line(point=True)
            .encode(
                x='Year:O', y=alt.Y('CO2_kg_per_kWh', title='kg CO₂/kWh'),
                color='Sector', tooltip=['Year','Sector','CO2_kg_per_kWh']
            )
        )
    st.altair_chart(chart, use_container_width=True)

else:  # New overlay mode
    st.markdown("**Overlay all sectors and scenarios for a complete comparison.**")
    metric = st.radio("Select metric:", ["Price (c/kWh)", "CO₂ Intensity (kg CO₂/kWh)"])
    
    if "Price" in metric:
        chart = (
            alt.Chart(df[df['Scenario'] != "Historical"])  # skip historical if you prefer
            .mark_line()
            .encode(
                x='Year:O',
                y=alt.Y('Price', title='c/kWh'),
                color='Sector',
                strokeDash='Scenario',
                tooltip=['Year','Sector','Scenario','Price']
            )
        )
    else:
        chart = (
            alt.Chart(df[df['Scenario'] != "Historical"])
            .mark_line()
            .encode(
                x='Year:O',
                y=alt.Y('CO2_kg_per_kWh', title='kg CO₂/kWh'),
                color='Sector',
                strokeDash='Scenario',
                tooltip=['Year','Sector','Scenario','CO2_kg_per_kWh']
            )
        )
    st.altair_chart(chart, use_container_width=True)

