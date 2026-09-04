import streamlit as st
from PIL import Image
import os

SCEN_MAP = {
    "Referentie": "ref",
    "2027": "2027",
    "2040": "2040",
}

TIME_BACKGROUND = "Data2/Time/Background.jpg"

def stack_timeseries_images(paths, background_path=TIME_BACKGROUND):
    """
    Stack timeseries PNGs on top of a fixed background image.
    """

    # Start with background
    if not os.path.exists(background_path):
        return None

    base = Image.open(background_path).convert("RGBA")

    for path in paths:
        if not path or not os.path.exists(path):
            continue

        overlay = Image.open(path).convert("RGBA")
        base = Image.alpha_composite(base, overlay)

    return base



def resolve_timeseries_path(var, scen, station):
    var_letter = {
        "Snelheid": "U",
        "Temperatuur": "T",
        "Saliniteit": "S",
    }.get(var)

    if var_letter is None:
        return None

    scen_folder = SCEN_MAP.get(scen)
    if scen_folder is None:
        return None

    filename = f"{var_letter}_{station}.png"

    return os.path.join(
        "Data2", "Time",
        var,
        scen_folder,
        filename
    )

STATIONS = [
    "Doordewind I",
    "Borssele I en II",
    "Borssele V",
    "Luchterduinen",
    "Hollandse Kust (noord) V",
    "OWEZ",
    "Borssele III en IV",
    "Prinses Amaliawindpark",
    "Nederwiek II en III",
    "IJmuiden Ver Gamma",
    "Doordewind II",
    "Nederwiek I",
    "Hollandse Kust (west) VI",
    "Hollandse Kust (west) VII",
    "Gemini",
    "Hollandse Kust (zuid) III en IV",
    "Hollandse Kust (zuid) I en II",
    "IJmuiden Ver Alpha",
    "IJmuiden Ver Beta",
    "Ten noorden van de Waddeneilanden",
]
def show_time_series():

    st.subheader("Tijdseries per locatie")
    with st.sidebar:
        col1, col2 = st.columns([2, 1])
    
        with col1:
            var = st.selectbox(
                "Variabele",
                ["Snelheid", "Temperatuur", "Saliniteit"],
                key="ts_var"
            )
    
            station = st.selectbox(
                "Meetlocatie",
                STATIONS,
                key="ts_station"
            )
    
        with col2:
            st.markdown("**Scenario's**")
    
            scen_ref = st.checkbox("🔵 Referentie", value=True, key="ts_ref")
            scen_2027 = st.checkbox("🟡 2027", value=False, key="ts_2027")
            scen_2040 = st.checkbox("🔴 2040", value=False, key="ts_2040")

    selected_scenarios = []
    if scen_ref:
        selected_scenarios.append("Referentie")
    if scen_2027:
        selected_scenarios.append("2027")
    if scen_2040:
        selected_scenarios.append("2040")

    st.divider()

    if not selected_scenarios:
        st.info("Selecteer minstens één scenario.")
        return

    paths = [
        resolve_timeseries_path(var, scen, station)
        for scen in selected_scenarios
    ]

    img = stack_timeseries_images(paths)

    if img:
        st.image(img, width = 'stretch')
    else:
        st.warning("Geen tijdseries beschikbaar voor deze combinatie.")
        st.caption(paths)

