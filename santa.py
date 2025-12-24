import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# Try to get GPS, but don't crash if it's not installed
try:
    from streamlit_geolocation import streamlit_geolocation
    HAS_GPS = True
except ImportError:
    HAS_GPS = False

st.set_page_config(page_title="Santa Radar", page_icon="🎅")

# --- Header ---
st.title("🎅 Santa's Live Flight Radar")
st.write("Current Status: **In Flight - Delivering Presents!**")

# --- Sidebar Controls ---
st.sidebar.header("📡 Calibration")
radar_quality = st.sidebar.select_slider("Radar Quality", ["Standard", "Deep Scan", "Quantum"])
gps_strength = st.sidebar.slider("GPS Signal Strength", 0, 100, 90)

# --- Location Logic ---
user_lat, user_lon = None, None
if HAS_GPS:
    st.sidebar.write("Click below to ping your chimney:")
    location = streamlit_geolocation()
    if location and location.get('latitude'):
        user_lat = location['latitude']
        user_lon = location['longitude']
        st.sidebar.success("📍 Your position is synced!")

# Fallback if GPS is blocked/not used
if not user_lat:
    st.sidebar.info("Or enter coordinates manually:")
    user_lat = st.sidebar.number_input("Your Latitude", value=51.22)
    user_lon = st.sidebar.number_input("Your Longitude", value=6.77)

# --- Santa Path Logic (Based on Dec 24th) ---
def calculate_santa():
    now = datetime.now(timezone.utc)
    # Santa moves from East (180) to West (-180) over 24 hours
    # This calculates his position based on the current hour/minute
    progress = (now.hour + now.minute/60) / 24
    current_lon = 180 - (progress * 360)
    current_lat = 30 * np.sin(progress * np.pi * 2) # S-curve flight path
    
    # Generate breadcrumbs (last 10 places)
    history = []
    for i in range(10):
        prev_progress = max(0, progress - (i * 0.02))
        h_lon = 180 - (prev_progress * 360)
        h_lat = 30 * np.sin(prev_progress * np.pi * 2)
        history.append({"lat": h_lat, "lon": h_lon, "Label": "Past Path"})
        
    return history, {"lat": current_lat, "lon": current_lon, "Label": "SANTA"}

# --- Display Data ---
history_data, current_santa = calculate_santa()

# Combine all points for the map
map_df = pd.DataFrame(history_data)
map_df = pd.concat([map_df, pd.DataFrame([current_santa])])
map_df = pd.concat([map_df, pd.DataFrame([{"lat": user_lat, "lon": user_lon, "Label": "You"}])])

# Display the Map
st.subheader("🌍 Live Map")
if gps_strength > 10:
    st.map(map_df, color="#FF0000", size=40)
    
    # Fun Distance calculation
    dist = np.sqrt((user_lat - current_santa['lat'])**2 + (user_lon - current_santa['lon'])**2) * 111
    st.metric("Distance from Santa", f"{dist:,.0f} km", delta="He's getting closer!")
else:
    st.error("🚨 Signal Lost! Increase GPS Strength in the sidebar to reconnect.")

# --- Action Buttons ---
if st.button("🔔 Send Sleigh Bell Signal"):
    st.snow()
    st.balloons()
