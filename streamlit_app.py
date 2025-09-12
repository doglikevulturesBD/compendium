import streamlit as st

st.set_page_config(page_title="Compendium of a Curious Mind", layout="centered")

st.title("🧠 Compendium of a Curious Mind")
st.markdown(
    """
Welcome to my interactive portfolio of tools, experiments, and ideas.  
Choose a project below to explore.
"""
)

# --- 3 columns of buttons ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("## 📁")
    if st.button("Carbon Registry"):
        st.switch_page("pages/1_Project_Registration.py")

with col2:
    st.markdown("## 🧮")
    if st.button("GHG Calculators"):
        st.switch_page("pages/1_Project_Registration.py")  # same page for now, tabs inside

with col3:
    st.markdown("## 🎓")
    if st.button("Knowledge Hub"):
        st.switch_page("pages/3_Blog.py")  # (create later)

st.markdown("---")

# --- More coming soon ---
st.subheader("🚀 Coming Soon")
st.markdown(
    """
- 📺 **YouTube Projects** – Interactive explainers  
- 📑 **Innovation Blog** – Insights on carbon markets, energy, and emerging tech  
- 📊 **Case Studies** – Real-world demo projects
"""
)


