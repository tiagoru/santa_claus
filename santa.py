import streamlit as st
import pandas as pd
import numpy as np
import time

# --- Page Config ---
st.set_page_config(page_title="Official Santa Tracker 2025", page_icon="🎅")

st.title("🎅 North Pole Radar: Santa Tracker")
st.markdown("Help the Elves monitor Santa's flight path! Adjust the radar quality to get a better signal.")

# --- Sidebar Controls ---
st.sidebar.header("📡 Radar Settings")
quality = st.sidebar.select_slider(
    "Tracking Quality",
    options=["Low", "Medium", "High", "Ultra-HD"],
    value="Medium"
)

# Map quality to technical parameters
quality_map = {
    "Low": {"points": 5, "delay": 2.0, "color": "#FF0000"},
    "Medium": {"points": 20, "delay": 1.0, "color": "#00FF00"},
    "High": {"points": 50, "delay": 0.5, "color": "#0000FF"},
    "Ultra-HD": {"points": 100, "delay": 0.1, "color": "#FFD700"}
}

settings = quality_map[quality]

# --- Simulation Logic ---
if st.button("🚀 Start Tracking Santa"):
    status_text = st.empty()
    progress_bar = st.progress(0)
    map_placeholder = st.empty()
    
    # Create a simulated path
    for i in range(1, settings["points"] + 1):
        # Generate a random path starting from the North Pole area
        # Santa moves roughly around the globe
        lats = np.random.uniform(-60, 80, size=i)
        lons = np.random.uniform(-180, 180, size=i)
        
        df = pd.DataFrame({'lat': lats, 'lon': lons})
        
        # Update UI
        status_text.text(f"Signal Strength: {quality} | Detecting Reindeer at {lats[-1]:.2f}, {lons[-1]:.2f}")
        progress_bar.progress(i / settings["points"])
        
        # Update Map
        map_placeholder.map(df, color=settings["color"], size=20)
        
        # "Quality" affects how fast the radar sweeps
        time.sleep(settings["delay"])
    
    st.balloons()
    st.success("Santa has been successfully located! Merry Christmas!")
else:
    st.info("Click the button above to begin the satellite sweep.")

# --- Fun Facts ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Sleigh Speed", value="Mach 7", delta="Very Fast!")
with col2:
    st.metric(label="Presents Delivered", value="842M", delta="Increasing")
