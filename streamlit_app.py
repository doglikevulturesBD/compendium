import streamlit as st

# --- Page config ---
st.set_page_config(
    page_title="Compendium of a Curious Mind",
    page_icon="🌱",
    layout="centered"
)

# --- Title and Intro ---
st.title("🌱 Compendium of a Curious Mind")
st.subheader("An Innovation Portfolio by Brandon Davoren")

st.markdown("""
Welcome to my interactive portfolio — a place where science, technology, and innovation 
come alive through hands-on tools, data-driven simulators, and explorative content.

This platform is designed to **demonstrate innovation**, **explain complex ideas simply**, 
and **inspire curiosity** about the world we can build.
""")

st.divider()

# --- What's Inside ---
st.markdown("## 📂 Current Sections")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💨 Carbon Registry Simulator")
    st.markdown("Track carbon projects, estimate credits, and simulate market logic.")

    st.markdown("### ⚡ Energy Systems Demos")
    st.markdown("Explore power systems, microgrids, and clean energy transitions.")

with col2:
    st.markdown("### 🧪 Physics & STEM Tools")
    st.markdown("Learn and experiment with interactive science visualizations.")

    st.markdown("### ✍️ Blogs & Articles")
    st.markdown("Read essays on climate, innovation, futures thinking, and more.")

st.info("Use the sidebar on the left to explore portfolio sections.", icon="🧭")

st.markdown("---")
st.caption("Built with ❤️ by Brandon Davoren · Powered by Streamlit")

