import streamlit as st
from tabs.time_tab import show_time_series
from tabs.map_tab import show_sandwave_tool
from tabs.about_tab import about
st.set_page_config(layout="wide")

col1, col2 = st.columns([10, 1])
with col1:
    with st.sidebar:
        st.markdown(
        "<h2 style='font-size: 36px;'>MELODY Maps</h2>",
        unsafe_allow_html=True
        )

with col2:
    if st.button("ℹ️", help="About MELODY"):
        about()

    tab = st.selectbox(
        "Kies functie",
        ["Kaarten", "Tijdreeksen"]
    )

if tab == "Kaarten":
    show_sandwave_tool()
    
elif tab == "Tijdreeksen":
    show_time_series()

