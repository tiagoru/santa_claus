import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone
from streamlit_geolocation import streamlit_geolocation

# --- Page Config ---
st.set_page_config(page_title="Global Santa Command Center", page_icon="🦌")

st.title("🛰️ Santa Command Center 2025")
st.markdown("Monitor the Big Guy's progress across the globe in real-time.")

# --- Sidebar Controls ---
st.sidebar.header("🕹️ Signal Calibration")

# 1. Radar Quality
radar_val = st.sidebar.select_slider(
    "Radar Resolution",
    options=["Low (VGA)", "High (4K)", "Quantum Scan"],
    value="High (4K)"
)

# 2. GPS Signal Strength
gps_strength = st.sidebar.slider("GPS Signal Stability (%)", 0, 100, 85)

# --- 3. User Current Position Logic ---
st.sidebar.divider()
st.sidebar.subheader("📍 Your Location")
location = streamlit_geolocation()

user_lat, user_lon = None, None
if location and location['latitude']:
    user_lat = location['latitude']
    user_lon = location['longitude']
    st.sidebar.success(f"Locked on: {user_lat:.2f}, {user_lon:.2f}")
else:
    st.sidebar.info("Click the icon in the sidebar to sync your GPS.")

# --- 4. Historical Path Calculation ---
# Santa starts at International Date Line (IDL) and moves West.
def get_santa_path():
    now = datetime.now(timezone.utc)
    # Total hours into Christmas Eve (starting from 00:00 UTC)
    hours_passed = now.hour + (now.minute / 60)
    
    # Simulate historical points (where he has been)
    # He starts at Lon 180 (IDL) and moves towards -180
    historical_points = []
    current_lon = 180 - (hours_passed * 15) # 15 degrees per hour roughly
    
    for h in range(int(hours_passed) + 1):
        path_lon = 180 - (h * 15)
        # Sinuous path for the "magic flight"
        path_lat = 20 * np.sin(path_lon / 30) + 10 
        historical_points.append({"lat": path_lat, "lon": path_lon, "type": "Past"})
    
    # Current Santa Position
    santa_current = {"lat": 20 * np.sin(current_lon / 30) + 10, "lon": current_lon, "type": "Santa"}
    return historical_points, santa_current

# --- Layout ---
col1, col2, col3 = st.columns(3)
col1.metric("Status", "In Flight" if gps_strength > 20 else "Signal Lost")
col2.metric("Radar Quality", radar_val)
col3.metric("Local Time (UTC)", datetime.now(timezone.utc).strftime("%H:%M"))

# --- Tracking Map ---
st.subheader("🌍 Live Tracking Map")

if gps_strength < 10:
    st.error("⚠️ GPS Signal too weak to pinpoint Santa! Boost signal in sidebar.")
else:
    history, current = get_santa_path()
    
    # Combine data for map
    map_data = pd.DataFrame(history)
    
    # Add User to map if GPS shared
    if user_lat:
        map_data = pd.concat([map_data, pd.DataFrame([{"lat": user_lat, "lon": user_lon, "type": "You"}])])
    
    # Add current Santa
    map_data = pd.concat([map_data, pd.DataFrame([current])])

    # Display Map
    st.map(map_data, color="#ff4b4b" if radar_val == "Quantum Scan" else "#00ff00", size=30)

    # Show distance if user location is known
    if user_lat:
        dist = np.sqrt((user_lat - current['lat'])**2 + (user_lon - current['lon'])**2) * 111 # rough km
        st.write(f"📏 Santa is approximately **{dist:,.0f} km** away from your chimney!")

# --- Footer Fun ---
if st.button("🔔 Ring Reindeer Bells"):
    st.snow()
    st.audio("https://www.soundjay.com/holiday/sounds/sleigh-bells-1.mp3")
