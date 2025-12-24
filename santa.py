import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone

# --- Setup ---
st.set_page_config(page_title="Santa Command Center", layout="wide")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("📡 Radar Spectrum")
    vision = st.selectbox(
        "Select Vision Mode", 
        ["Tactical Night Vision", "Infrared Heat", "Deep Space", "Standard Satellite"]
    )
    
    # Background Map Styles & Path Colors
    # Styles: dark, light, satellite, road
    if vision == "Tactical Night Vision":
        map_style = "mapbox://styles/mapbox/dark-v10"
        path_color = [0, 255, 65, 200] # Matrix Green
    elif vision == "Infrared Heat":
        map_style = "mapbox://styles/mapbox/navigation-guidance-night-v4"
        path_color = [255, 69, 0, 200] # Neon Orange
    elif vision == "Deep Space":
        map_style = "mapbox://styles/mapbox/satellite-v9"
        path_color = [157, 0, 255, 200] # Magic Purple
    else:
        map_style = "mapbox://styles/mapbox/light-v10"
        path_color = [255, 0, 0, 200] # Traditional Red

    st.divider()
    # Spirit Gauge (35% - 95%)
    now = datetime.now(timezone.utc)
    spirit = 35 + (60 * (now.hour / 24))
    st.write(f"✨ **Christmas Spirit Gauge**")
    st.progress(spirit/100)
    st.write(f"{spirit:.1f}% Strength")

# --- Tracking & Log Logic ---
def get_santa_data():
    # Start at 12:00 UTC (International Date Line Midnight)
    start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    minutes_passed = int((current_time - start_time).total_seconds() / 60)
    
    # 1. Historical Log of Regions
    regions = [
        "International Date Line", "Fiji Islands", "New Zealand", "Eastern Australia", 
        "Japan", "South Korea", "China", "Philippines", "Indonesia", "Thailand"
    ]
    # Calculate how many regions visited based on 1.5 hours per region approx
    visited_idx = min(len(regions), max(1, minutes_passed // 90))
    visited_log = regions[:visited_idx]

    # 2. Path Data for Map
    path = []
    if minutes_passed < 0:
        return [{"lat": 90, "lon": 0}], ["North Pole (Preparing)"], 90, 0
        
    for m in range(0, minutes_passed + 1, 5): # Ping every 5 mins
        p_lon = 180 - (m * 0.25)
        if p_lon < -180: p_lon += 360
        p_lat = 40 * np.sin(m * 0.01)
        path.append({"lat": p_lat, "lon": p_lon})
    
    return path, visited_log, path[-1]['lat'], path[-1]['lon']

history_path, log_entries, s_lat, s_lon = get_santa_data()

# --- Distance to Düsseldorf ---
user_lat, user_lon = 51.22, 6.77
dist = np.sqrt((user_lat - s_lat)**2 + (user_lon - s_lon)**2) * 111
if dist < 1.0: dist = 1.0

# --- Render Dashboard ---
st.title(f"🚀 Mission: Santa Tracker ({vision})")

col1, col2 = st.columns([3, 1])

with col1:
    # PyDeck Map allows changing the Map Style (Background)
    view_state = pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=2, pitch=45)
    
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame(history_path),
        get_position="[lon, lat]",
        get_color=path_color,
        get_radius=150000,
    )

    st.pydeck_chart(pdk.Deck(
        map_style=map_style,
        initial_view_state=view_state,
        layers=[layer]
    ))

with col2:
    st.metric("Distance to Düsseldorf", f"{dist:,.1f} km")
    
    st.subheader("📝 Past Locations Log")
    for city in reversed(log_entries):
        st.write(f"✅ **Visited:** {city}")
    
    if dist < 1000:
        st.error("🚨 ALERT: AIRSPACE DELAY! High Cookie Density Detected.")

# --- Action ---
if st.button("🔔 Send Chimney Signal"):
    st.snow()
    st.toast("Santa sees your house lights!")
