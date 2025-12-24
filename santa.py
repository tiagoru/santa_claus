import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone

# --- Setup ---
st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# --- Interactive Sidebar ---
with st.sidebar:
    st.header("📡 Sensor Calibration")
    vision = st.selectbox(
        "Select Vision Mode", 
        ["Tactical Night Vision", "Infrared Heat", "Deep Space Satellite", "Standard Radar"]
    )
    
    # Logic to change Map Background AND Point Colors
    if vision == "Tactical Night Vision":
        map_style = "dark" # Dark grey/black background
        path_color = [0, 255, 65, 200] # Matrix Green
    elif vision == "Infrared Heat":
        map_style = "road" # High contrast
        path_color = [255, 69, 0, 220] # Glowing Orange
    elif vision == "Deep Space Satellite":
        map_style = "satellite" # Real earth photos
        path_color = [255, 255, 255, 250] # Bright White
    else:
        map_style = "light" # Standard blue/white
        path_color = [255, 0, 0, 200] # Red

    st.divider()
    # Spirit Gauge
    now_utc = datetime.now(timezone.utc)
    spirit = 35 + (60 * (now_utc.hour / 24))
    st.write(f"✨ **Christmas Spirit Gauge**")
    st.progress(spirit/100)
    st.write(f"Strength: {spirit:.1f}%")

# --- Telemetry Logic (Speed & Presents) ---
# Journey started at 12:00 UTC today
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_since_start = (now_utc - start_time).total_seconds()

if seconds_since_start < 0:
    presents_delivered = 0
    current_speed = 0
else:
    # Santa delivers approx 150,000 gifts per second!
    presents_delivered = int(seconds_since_start * 150000)
    # Speed is Mach 20 with some variation
    current_speed = 24500 + np.random.randint(-500, 500)

# --- Path & Log Logic ---
def get_flight_data():
    minutes_passed = int(seconds_since_start / 60)
    
    regions = ["North Pole Hub", "International Date Line", "Fiji", "New Zealand", "Australia", "Japan", "Asia Coastal"]
    visited_idx = min(len(regions), max(1, minutes_passed // 60))
    
    path = []
    if minutes_passed < 0:
        return [{"lat": 90, "lon": 0}], ["Preparing for Takeoff"], 90, 0
        
    for m in range(0, minutes_passed + 1, 5):
        p_lon = 180 - (m * 0.25)
        if p_lon < -180: p_lon += 360
        p_lat = 40 * np.sin(m * 0.01)
        path.append({"lat": p_lat, "lon": p_lon})
    
    return path, regions[:visited_idx], path[-1]['lat'], path[-1]['lon']

history_path, log_entries, s_lat, s_lon = get_flight_data()

# --- Distance to Düsseldorf ---
user_lat, user_lon = 51.22, 6.77
dist = np.sqrt((user_lat - s_lat)**2 + (user_lon - s_lon)**2) * 111

# --- Main Dashboard UI ---
st.title(f"🎯 Global Flight Command: {vision}")

# Top Row: Gauges
m1, m2, m3 = st.columns(3)
m1.metric("🎁 Presents Delivered", f"{presents_delivered:,}")
m2.metric("🚀 Sleigh Speed", f"{current_speed:,} km/h", delta="Mach 20")
m3.metric("📏 Distance to You", f"{dist:,.1f} km")

col1, col2 = st.columns([3, 1])

with col1:
    # Professional PyDeck Map
    st.pydeck_chart(pdk.Deck(
        map_style=map_style,
        initial_view_state=pdk.ViewState(
            latitude=s_lat,
            longitude=s_lon,
            zoom=1.5,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(history_path),
                get_position="[lon, lat]",
                get_color=path_color,
                get_radius=200000,
            ),
        ],
    ))

with col2:
    st.subheader("📝 Mission Log")
    for place in reversed(log_entries):
        st.write(f"✅ {place} - **Cleared**")
    
    st.divider()
    if st.button("🔔 Activate Landing Lights"):
        st.snow()
        st.balloons()
