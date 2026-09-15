import streamlit as st
import numpy as np
from PIL import Image
import os

SCEN_MAP = {
    "Referentie": "ref",
    "2027": "2027",
    "2040": "2040",
}
SCENARIO_MAP = {
    "Wind Farms": "WindFarm",
    "Sand Pits": "SandPit",
}

TIME_BACKGROUND = "Data2/WindFarm/Time/Background.jpg"

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

def trim_white_border(img, threshold=245, buffer_px=0):
    """
    Trim white (or near-white) borders from an RGB/RGBA image.
    threshold: how close to white a pixel must be (0–255)
    """
    arr = np.array(img)

    #Drop alpha if present
    if arr.shape[2] == 4:
        rgb = arr[:, :, :3]
    else:
        rgb = arr

    # Mask: True where pixel is NOT white
    non_white = np.any(rgb < threshold, axis=2)

    if not non_white.any():
        return img  # nothing to crop

    coords = np.column_stack(np.where(non_white))
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    
    # Apply buffer and clamp to image bounds
    x_min = max(0, x_min - buffer_px)
    y_min = max(0, y_min - buffer_px)
    x_max = min(img.width,  x_max + buffer_px + 1)
    y_max = min(img.height, y_max + buffer_px + 1)
    st.write(x_min, y_min, x_max + 1, y_max + 1)
    return img.crop((x_min, y_min, x_max, y_max))

def resolve_timeseries_path(var, scen, station,scenario_folder):
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
        "Data2",
        scenario_folder,
        "Time",
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

    #st.subheader("Tijdseries per locatie")
    with st.sidebar:
        col1, col2 = st.columns([2, 1])
    
        with col1:
            scenario_label = st.selectbox(
                "Scenario type",
                list(SCENARIO_MAP.keys()),
                key="ts_scenario"
            )
            scenario_folder = SCENARIO_MAP[scenario_label]
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
        #PLOTTING THE STATION IMAGES
        station_img = os.path.join(
            "Data2",
            "WindFarm",
            "Time",
            "Stations",
            f"{station}.jpg"
        )
        
        if os.path.exists(station_img):
            img_station = Image.open(station_img).convert("RGBA")
            img_station = trim_white_border(img_station)
            st.image(img_station, use_container_width=True)

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
        resolve_timeseries_path(
            var,
            scen,
            station,
            scenario_folder
    )
        for scen in selected_scenarios
]

    img = stack_timeseries_images(paths)

    if img:
        MAX_HEIGHT = 900
        
        if img.height > MAX_HEIGHT:
            scale = MAX_HEIGHT / img.height
            img = img.resize(
                (int(img.width * scale), MAX_HEIGHT)
            )
        
        st.image(img)
    else:
        st.warning("Geen tijdseries beschikbaar voor deze combinatie.")
        st.caption(paths)

