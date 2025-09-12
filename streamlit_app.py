import streamlit as st

st.set_page_config(page_title="Compendium of a Curious Mind")

st.title("🧠 Compendium of a Curious Mind")
st.markdown("Explore my interactive portfolio of experiments, tools, and ideas.")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("📁") 
    if st.button("Carbon Registry"):
        st.switch_page("pages/1_Project_Registration.py")

with col2:
    st.image("🧮")
    if st.button("GHG Calculators"):
        st.switch_page("pages/2_GHG_Calculators.py")

with col3:
    st.image("🎓")
    if st.button("Knowledge Hub"):
        st.switch_page("pages/3_Blog.py")

