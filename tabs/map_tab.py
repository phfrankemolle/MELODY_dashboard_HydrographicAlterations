import streamlit as st
import zipfile
import io
import os
import numpy as np
import geopandas as gpd
from PIL import Image

def resolve_base_path(settings):
    main = settings["button"]          # Temperatuur, Saliniteit, Bathymetrie
    year = settings["year"]            # 2027, 2040
    var = settings["variable"]         # Diff, RelDiff, etc.

    # Bathymetrie is simple
    if main == "Bathymetrie":
        return "Data2/Base/Bathymetrie/Bathy.png"

    # Map UI variable → filename suffix
    var_map = {
        "Verschil t.o.v. referentie": "diff",
        "Relatieve verschil t.o.v. referentie": "reldiff",
        "Verschil stratificatie t.o.v. referentie": "diff",
        "Relatieve verschil stratificatie t.o.v. referentie": "reldiff",
        "Stratificatie": "strat",
        "Oppervlakte": "top",
        "Bodem": "bot",
    }
    prefix_map = {
        "Temperatuur": "T",
        "Saliniteit": "S",
        "Snelheid": "U",      # ← example, change if needed (U/V, Vel, etc.)
    }
    prefix = prefix_map.get(main)
    suffix = var_map.get(var)

    # Build filename based on your pattern:


    filename = f"{prefix}_{year}_{suffix}.png"

    return os.path.join(
        "Data2", "Base",
        main,
        str(year),
        filename
    )

def resolve_threshold_gpkg(settings):
    main = settings["button"]     # Saliniteit, Temperatuur, Snelheid
    year = settings["year"]
    var  = settings["variable"]

    if main not in ["Saliniteit", "Temperatuur", "Snelheid"]:
        return None

    if year in ["Referentie", None]:
        return None

    # Map variable → suffix
    var_map = {
        "Verschil t.o.v. referentie": "diff",
        "Relatieve verschil t.o.v. referentie": "reldiff",
        "Verschil stratificatie t.o.v. referentie": "diff",
        "Relatieve verschil stratificatie t.o.v. referentie": "reldiff",
    }

    suffix = var_map.get(var)
    if suffix is None:
        return None

    # Match your filenames like: polygons27diff.gpkg
    year_short = year[-2:]  # '2027' → '27'

    filename = f"polygons{year_short}{suffix}.gpkg"
    
    var_folder = var_map.get(var)
    if var_folder is None:
        return None
        
    return os.path.join(
        "Data2", "Overlay", "threshold",
        main,               # ✅ dynamic now
        str(year),
        var_folder,
        filename
    )
    
def resolve_wind_overlay(settings):
    year = settings["year"]

    # Toggle off → no overlay
    if not settings.get("wind"):
        return None

    # No wind layer for reference year
    if year in [None, "Referentie"]:
        return None
    
    if settings.get("wind_invert"):
        filename = f"yellow_{year}.png"
    else:
        filename = f"{year}.png"

    return os.path.join(
        "Data2", "Overlay", "windmill",
        filename
    )

def resolve_threshold_overlay(settings):
    main = settings["button"]       # Saliniteit / Temperatuur
    year = settings["year"]
    var = settings["variable"]
    overs = settings["slider"]

    # Basic guards
    if overs in [None, "none"]:
        return None

    if year in [None, "Referentie"]:
        return None

    # Only variables that actually support thresholds
    supported_mains = ["Saliniteit", "Temperatuur", "Snelheid"]
    if main not in supported_mains:
        return None

    # UI variable → folder mapping
    var_map = {
        # Differences
        "Verschil t.o.v. referentie": "diff",
        "Relatieve verschil t.o.v. referentie": "reldiff",
        "Verschil stratificatie t.o.v. referentie": "diff",
        "Relatieve verschil stratificatie t.o.v. referentie": "reldiff",

        # Absolute fields (if you have thresholds for these)
        "Oppervlakte": "top",
        "Bodem": "bot",
        "Stratificatie": "strat",
    }

    var_folder = var_map.get(var)
    if var_folder is None:
        return None

    return os.path.join(
        "Data2", "Overlay", "threshold",
        main,               # ✅ dynamic now
        str(year),
        var_folder,
        f"th_{overs}.png"
    )

def trim_white_border(img, threshold=245, buffer_px=20):
    """
    Trim white (or near-white) borders from an RGB/RGBA image.
    threshold: how close to white a pixel must be (0–255)
    """
    arr = np.array(img)

    # Drop alpha if present
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

    return img.crop((x_min, y_min, x_max + 1, y_max + 1))


def compose_layers(
    base_path,
    eez=False,
    wind_path=None,
    threshold_path=None,
):
    img = Image.open(base_path).convert("RGBA")

    # 1. EEZ
    if eez:
        overlay = Image.open("Data2/Overlay/eez/eez.png").convert("RGBA")
        img = Image.alpha_composite(img, overlay)

    # 2. Wind farms
    if wind_path and os.path.exists(wind_path):
        overlay = Image.open(wind_path).convert("RGBA")
        img = Image.alpha_composite(img, overlay)

    # 3. Threshold (top layer)
    if threshold_path and os.path.exists(threshold_path):
        overlay = Image.open(threshold_path).convert("RGBA")
        img = Image.alpha_composite(img, overlay)
    
    img = trim_white_border(img)
    return img
    
def compute_threshold_area(gpkg_path, threshold_value):
    if not gpkg_path or not os.path.exists(gpkg_path):
        return None

    gdf = gpd.read_file(gpkg_path)

    # Filter by threshold
    mask = gdf["threshold"] == threshold_value

    selected = gdf[mask]

    # Sum area
    total_area = selected["area_km2"].sum()

    return total_area

def build_zip_export(img, gpkg_path=None):
    """
    Create an in-memory ZIP containing:
    - map.png (always)
    - polygons.gpkg (optional)
    """

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:

        # --- Add PNG ---
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        zf.writestr("map.png", img_bytes.getvalue())

        # --- Add GPKG (if available) ---
        if gpkg_path and os.path.exists(gpkg_path):
            with open(gpkg_path, "rb") as f:
                zf.writestr("polygons.gpkg", f.read())

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def commit_settings(prefix):
    st.session_state[f"{prefix}_button"] = st.session_state.get(f"{prefix}_button_temp")
    st.session_state[f"{prefix}_year"] = st.session_state.get(f"{prefix}_year_temp")
    st.session_state[f"{prefix}_eez"] = st.session_state.get(f"{prefix}_eez_temp")
    st.session_state[f"{prefix}_wind"] = st.session_state.get(f"{prefix}_wind_temp")
    st.session_state[f"{prefix}_overs"] = st.session_state.get(f"{prefix}_overs_temp")
    st.session_state[f"{prefix}_slider"] = st.session_state.get(f"{prefix}_slider_temp")

    if f"{prefix}_var_temp" in st.session_state:
        st.session_state[f"{prefix}_var"] = st.session_state.get(f"{prefix}_var_temp")
    else:
        st.session_state[f"{prefix}_var"] = None

def show_sandwave_tool():
    # ---------------------------------------------------------
    # DEFAULT SETTINGS
    # ---------------------------------------------------------
    defa_but= "Temperatuur"
    defa_var= "Verschil stratificatie t.o.v. referentie"
    defa_yr = "2027"
    if "fig1_button" not in st.session_state:
        st.session_state["fig1_button"] = defa_but
    if "fig2_button" not in st.session_state:
        st.session_state["fig2_button"] = defa_but
    
    if "fig1_button_temp" not in st.session_state:
        st.session_state["fig1_button_temp"] = defa_but
    if "fig2_button_temp" not in st.session_state:
        st.session_state["fig2_button_temp"] = defa_but

    if "fig1_var" not in st.session_state:
        st.session_state["fig1_var"] = defa_var
    if "fig2_var" not in st.session_state:
        st.session_state["fig2_var"] = defa_var
    
    if "fig1_var_temp" not in st.session_state:
        st.session_state["fig1_var_temp"] = defa_var
    if "fig2_var_temp" not in st.session_state:
        st.session_state["fig2_var_temp"] = defa_var
        
    if "fig1_year" not in st.session_state:
        st.session_state["fig1_year"] = defa_yr
    if "fig2_year" not in st.session_state:
        st.session_state["fig2_year"] = defa_yr
    
    if "fig1_year_temp" not in st.session_state:
        st.session_state["fig1_year_temp"] = defa_yr
    if "fig2_year_temp" not in st.session_state:
        st.session_state["fig2_year_temp"] = defa_yr
    # ---------------------------------------------------------
    # CSS (kept, but no longer used for buttons — harmless)
    # ---------------------------------------------------------
    st.markdown("""
    <style>
    .button-active {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 1px solid #4CAF50 !important;
        border-radius: 6px !important;
    }
    .button-inactive {
        background-color: #e0e0e0 !important;
        color: black !important;
        border: 1px solid #bdbdbd !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # INTERNAL: Render controls for one figure (Mode A)
    # ---------------------------------------------------------
    def render_controls(prefix):
        """
        Renders UI controls for one figure.
        UI updates immediately (Mode A),
        figures update only when Toepassen is pressed.
        """

        # --- OPTIONS ---
        button_options = ["Temperatuur", "Saliniteit", "Snelheid", "Bathymetrie"]

        
        selected_temp = st.selectbox(
            "Parameter",
            button_options,
            key=f"{prefix}_button_temp"
        )


        # ---------------------------------------------------------
        # CONDITIONAL SELECTBOX BASED ON BUTTON SELECTION
        # ---------------------------------------------------------

        temp_saliniteit_vars = [
            "Oppervlakte",
            "Bodem",
            "Stratificatie",
            "Verschil stratificatie t.o.v. referentie",
            "Relatieve verschil stratificatie t.o.v. referentie",
        ]
        
        temp_saliniteit_desc = {
            "Oppervlakte": "Gemiddelde waarde in de waterkolom vlak onder het wateroppervlak",
            "Bodem": "Gemiddelde waarde in de waterkolom vlak boven de bodem",
            "Stratificatie": "Verschil tussen de gemiddelde waardes van de boven en onder laag",
            "Verschil stratificatie t.o.v. referentie": "Het verschil tussen de stratificatie in het gekozen jaar en het referentiejaar (2012)-> (jaar-ref)",
            "Relatieve verschil stratificatie t.o.v. referentie": "Het relatieve verschil tussen de stratificatie in het gekozen jaar en het referentiejaar (2012)-> (jaar-ref)/ref",
        }

        snelheid_vars = [
            "Bodem",
            "Verschil t.o.v. referentie",
            "Relatieve verschil stratificatie t.o.v. referentie"
        ]
        snelheid_desc = {
            "Bodem": "Magnitude van de residuele bodemsnelheid",
            "Verschil stratificatie t.o.v. referentie": "Het verschil tussen de residuele bodemsnelheid in het gekozen jaar en het referentiejaar (2012)-> (jaar-ref)",
            "Relatieve verschil stratificatie t.o.v. referentie": "Het relatieve verschil tussen de stratificatie in het gekozen jaar en het referentiejaar (2012)-> (jaar-ref)/ref",
        }

        # Only show selectbox for these buttons
        if selected_temp in ["Temperatuur", "Saliniteit"]:
            st.selectbox(
                "Variabele",
                temp_saliniteit_vars,
                key=f"{prefix}_var_temp"
            )
            st.info(temp_saliniteit_desc[temp_saliniteit_vars])

        elif selected_temp == "Snelheid":
            st.selectbox(
                "Variabele",
                snelheid_vars,
                key=f"{prefix}_var_temp"
            )
            st.info(snelheid_desc[snelheid_vars])

        # Bathymetrie → no selectbox

        # ---------------------------------------------------------
        # DROPDOWN (always shown)
        # ---------------------------------------------------------
        st.selectbox(
            "Jaar simulatie",
            #["Referentie", "2012", "2027", "2040"],
            ["ref", "2027", "2040"],
            key=f"{prefix}_year_temp"
        )

        # ---------------------------------------------------------
        # TOGGLES (always shown)
        # ---------------------------------------------------------
        st.toggle("EEZ", key=f"{prefix}_eez_temp")
               
        col1, col2 = st.columns([3, 1]) #windfarm toggle 
        
        with col1:
            show_wind = st.toggle("Windparken", key=f"{prefix}_wind_temp")
        with col2:
            if show_wind:
                st.toggle(
                    "🎨",
                    key=f"{prefix}_wind_invert",
                    label_visibility="collapsed"
                )   
                
        st.toggle("Overschrijdingswaarde polygons", key=f"{prefix}_overs_temp")


        # Conditional slider (only if overschrijding is ON)
        if st.session_state.get(f"{prefix}_overs_temp"):
        
            main = st.session_state.get(f"{prefix}_button_temp")
            var  = st.session_state.get(f"{prefix}_var_temp")
        
            # Default threshold values
            slider_options = ["none", 0.05, 0.1, 0.2, 0.3]
        
            # Special case: Snelheid + diff
            if main == "Snelheid" and var == "Verschil t.o.v. referentie":
                slider_options = ["none",.001,.002,.005,.01]
        
            st.select_slider(
                "Selecteer waarde",
                options=slider_options,
                key=f"{prefix}_slider_temp"
            )

        # ---------------------------------------------------------
        # Return committed values (used for figures)
        # ---------------------------------------------------------
        return {
            "button": st.session_state.get(f"{prefix}_button"),
            "year": st.session_state.get(f"{prefix}_year"),
            "eez": st.session_state.get(f"{prefix}_eez"),
            "wind": st.session_state.get(f"{prefix}_wind"),
            "wind_invert": st.session_state.get(f"{prefix}_wind_invert"),
            "overs": st.session_state.get(f"{prefix}_overs"),
            "slider": st.session_state.get(f"{prefix}_slider"),
            "variable": st.session_state.get(f"{prefix}_var"),
        }

    st.subheader("Kaarten Nederlandse Noordzee")
    st.divider()
    # ---------------------------------------------------------
    # TWO COLUMNS
    # ---------------------------------------------------------
    with st.sidebar:
    
        col1, col2 = st.columns(2)
        
        # --- FIRST: Render both sets of controls (temporary values) ---
        with col1:
            st.subheader("Linker figuur")
            render_controls("fig1")
        
        with col2:
            st.subheader("Rechter figuur")
            render_controls("fig2")
        
        # --- SECOND: Full-width row for the global Toepassen button ---
        apply_container = st.container()
        with apply_container:
            if st.button("Toepassen", key="apply_both"):
                commit_settings("fig1")
                commit_settings("fig2")
        
        # --- THIRD: Now read committed values and render figures ---
    col1_fig, col2_fig = st.columns(2)
    
    with col1_fig:
        settings_left = {
            "button": st.session_state.get("fig1_button"),
            "year": st.session_state.get("fig1_year"),
            "eez": st.session_state.get("fig1_eez"),
            "wind": st.session_state.get("fig1_wind"),
            "wind_invert": st.session_state.get(f"fig1_wind_invert", False),
            "overs": st.session_state.get("fig1_overs"),
            "slider": st.session_state.get("fig1_slider"),
            "variable": st.session_state.get("fig1_var"),
        }
    
        if settings_left["button"] and settings_left["year"]:
            base_path = resolve_base_path(settings_left)
            wind_path = resolve_wind_overlay(settings_left)
            threshold_path = resolve_threshold_overlay(settings_left)
            img = compose_layers(base_path, eez=settings_left["eez"], wind_path=wind_path,threshold_path=threshold_path)
            st.image(img, use_column_width=True)
        
        # Always determine gpkg_path (may be None)
        gpkg_path = None
        
        if settings_left["overs"] and settings_left["slider"] not in [None, "none"]:
    
            gpkg_path = resolve_threshold_gpkg(settings_left)
    
            area = compute_threshold_area(
                gpkg_path,
                settings_left["slider"]
            )
    
            if area is not None:
                st.markdown(f"**Totale oppervlakte:** {area:.2f} km²")
            else:
                st.caption("Geen oppervlakte beschikbaar")
        # --- ZIP export ---
        zip_bytes = build_zip_export(img, gpkg_path)
        
        st.download_button(
            label="Export map + polygons",
            data=zip_bytes,
            file_name = f"{settings_left['button']}_{settings_left['year']}_{settings_left['variable']}.zip",
            mime="application/zip",
            key = "download_left"
        )

    
    with col2_fig:
        settings_right = {
            "button": st.session_state.get("fig2_button"),
            "year": st.session_state.get("fig2_year"),
            "eez": st.session_state.get("fig2_eez"),
            "wind": st.session_state.get("fig2_wind"),
            "wind_invert": st.session_state.get(f"fig2_wind_invert", False),
            "overs": st.session_state.get("fig2_overs"),
            "slider": st.session_state.get("fig2_slider"),
            "variable": st.session_state.get("fig2_var"),
        }
    
        if settings_right["button"] and settings_right["year"]:
            base_path = resolve_base_path(settings_right)
            wind_path = resolve_wind_overlay(settings_right)
            threshold_path = resolve_threshold_overlay(settings_right)
            img = compose_layers(base_path, eez=settings_right["eez"], wind_path=wind_path, threshold_path=threshold_path)
            st.image(img, use_column_width=True)

         # Always determine gpkg_path (may be None)
        gpkg_path = None
        if settings_right["overs"] and settings_right["slider"] not in [None, "none"]:
            gpkg_path = resolve_threshold_gpkg(settings_right)
            area = compute_threshold_area(
                gpkg_path,
                settings_right["slider"]
            )
    
            if area is not None:
                st.markdown(f"**Totale oppervlakte:** {area:.2f} km²")
            else:
                st.caption("Geen oppervlakte beschikbaar")

        zip_bytes2 = build_zip_export(img, gpkg_path)
        
        st.download_button(
            label="Export map + polygons",
            data=zip_bytes2,
            file_name = f"{settings_right['button']}_{settings_right['year']}_{settings_right['variable']}.zip",
            mime="application/zip",
            key = "download_right"
        )

