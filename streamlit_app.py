import streamlit as st
from tabs.time_tab import show_time_series
from tabs.map_tab import show_sandwave_tool

st.set_page_config(layout="wide")
with st.sidebar:
    st.markdown(
    "<h2 style='font-size: 36px;'>MELODY Maps</h2>",
    unsafe_allow_html=True
    )
    
    tab = st.selectbox(
        "Kies functie",
        ["Kaarten", "Tijdreeksen"]
    )

if tab == "Kaarten":
    show_sandwave_tool()
    
elif tab == "Tijdreeksen":
    show_time_series()

