import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# --- Auto-Refresh (Updates every 60 seconds) ---
st_autorefresh(interval=60000, key="santatracker")

# --- Setup ---
st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("📡 Sensor Calibration")
    vision = st.selectbox(
        "Select Vision Mode", 
        ["Night Vision", "Infrared Heat", "Satellite View", "Standard Radar"]
    )
    
    # Map Tiles & Color Logic
    if vision == "Night Vision":
        map_style = "mapbox://styles/mapbox/dark-v10"
        path_color = [0, 255, 65, 200] # Matrix Green
    elif vision == "Infrared Heat":
        map_style = "mapbox://styles/mapbox/navigation-night-v1"
        path_color = [255, 69, 0, 220] # Heat Orange
    elif vision == "Satellite View":
        map_style = "mapbox://styles/mapbox/satellite-v9"
        path_color = [255, 255, 255, 250] # Bright White
    else:
        map_style = "mapbox://styles/mapbox/light-v10"
        path_color = [255, 0, 0, 200] # Standard Red

    st.divider()
    # Christmas Spirit Calculation
    now_utc = datetime.now(timezone.utc)
    spirit = 35 + (60 * (now_utc.hour / 24))
    st.write(f"✨ **Christmas Spirit Level**")
    st.progress(min(spirit/100, 1.0))
    st.write(f"Current Signal: **{spirit:.1f}%**")

# --- Data Logic ---
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_since_start = (now_utc - start_time).total_seconds()

# Counters
presents = int(max(0, seconds_since_start * 150000))
speed = 24500 + np.random.randint(-500, 500) if seconds_since_start > 0 else 0

# Path Building
def get_flight_data():
    minutes = int(max(0, seconds_since_start / 60))
    path = []
    for m in range(0, minutes + 1, 5):
        p_lon = 180 - (m * 0.25)
        if p_lon < -180: p_lon += 360
        p_lat = 40 * np.sin(m * 0.01)
        path.append({"lat": p_lat, "lon": p_lon})
    
    # Final location or North Pole
    curr_lat = path[-1]['lat'] if path else 90
    curr_lon = path[-1]['lon'] if path else 0
    return path, curr_lat, curr_lon

history, s_lat, s_lon = get_flight_data()

# --- Distance to Düsseldorf ---
dist = np.sqrt((51.22 - s_lat)**2 + (6.77 - s_lon)**2) * 111
if dist < 1.0: dist = 1.0

# --- Dashboard Layout ---
st.title(f"🌍 Santa Flight Command - {vision}")

# Top Metric Gauges
m1, m2, m3 = st.columns(3)
m1.metric("🎁 Presents Delivered", f"{presents:,}", delta="Auto-updating")
m2.metric("🚀 Sleigh Speed", f"{speed:,} km/h", delta="Mach 20")
m3.metric("📏 Distance to You", f"{dist:,.1f} km")

col1, col2 = st.columns([3, 1])

with col1:
    # High-tech Map
    st.pydeck_chart(pdk.Deck(
        map_style=map_style,
        initial_view_state=pdk.ViewState(
            latitude=s_lat, longitude=s_lon, zoom=1.8, pitch=35
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(history),
                get_position="[lon, lat]",
                get_color=path_color,
                get_radius=250000,
            ),
        ],
    ))

with col2:
    st.subheader("📝 Mission Log")
    regions = ["North Pole", "Pacific Is.", "New Zealand", "Australia", "Japan", "Asia"]
    visited = regions[:int(min(len(regions), max(1, seconds_since_start // 3600)))]
    for place in reversed(visited):
        st.write(f"✅ **{place}** - Cleared")
    
    st.divider()
    if st.button("🔔 Test Chimney Sensor"):
        st.snow()
