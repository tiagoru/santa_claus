import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# --- Try to load GPS ---
try:
    from streamlit_geolocation import streamlit_geolocation
    HAS_GPS = True
except ImportError:
    HAS_GPS = False

st.set_page_config(page_title="Santa Command Center", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎅 Real-Time Global Santa Tracker")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🛰️ Satellite Controls")
    radar_val = st.select_slider("Radar Sensitivity", options=["Low", "Medium", "High", "Quantum Scan"])
    gps_stability = st.slider("GPS Link Stability", 0, 100, 95)
    
    st.divider()
    user_lat, user_lon = 51.22, 6.77 # Default to Dusseldorf
    
    if HAS_GPS:
        st.subheader("📍 Your Chimney GPS")
        loc = streamlit_geolocation()
        if loc and loc.get('latitude'):
            user_lat, user_lon = loc['latitude'], loc['longitude']
            st.success("Target Locked!")
    
    st.info(f"Tracking from: {user_lat}, {user_lon}")

# --- Logic: Where is Santa? ---
def get_santa_world_pos():
    now = datetime.now(timezone.utc)
    
    # Santa follows the "Midnight" line. 
    # At 12:00 UTC (Noon), it's midnight at the International Date Line (180°).
    # At 00:00 UTC, it's midnight in London (0°).
    # Formula: Longitude = (UTC_Hour + UTC_Minute/60) * 15 degrees - 180
    
    # We add 12 hours because he starts at the Date Line at the start of the UTC day
    total_hours_utc = now.hour + (now.minute / 60) + (now.second / 3600)
    current_lon = 180 - (total_hours_utc * 15)
    
    # Ensure longitude stays between -180 and 180
    if current_lon < -180:
        current_lon += 360
        
    # Santa zig-zags North to South to hit every house
    current_lat = 40 * np.sin(total_hours_utc * 0.5) 
    
    # Generate the "Tracking Path" (Where he was the last 6 hours)
    path_points = []
    for h in range(1, 13): # Last 12 points
        past_hours = total_hours_utc - (h * 0.5)
        p_lon = 180 - (past_hours * 15)
        if p_lon < -180: p_lon += 360
        p_lat = 40 * np.sin(past_hours * 0.5)
        path_points.append({"lat": p_lat, "lon": p_lon, "Icon": "Past Location"})
        
    return path_points, {"lat": current_lat, "lon": current_lon, "Icon": "SANTA"}

# --- Process Data ---
history, current = get_santa_world_pos()

# --- Display Content ---
col1, col2 = st.columns([3, 1])

with col1:
    if gps_stability > 15:
        # Build DataFrame for Map
        df_history = pd.DataFrame(history)
        df_current = pd.DataFrame([current])
        df_user = pd.DataFrame([{"lat": user_lat, "lon": user_lon, "Icon": "You"}])
        
        # Merge all
        full_map_df = pd.concat([df_history, df_current, df_user])
        
        # Show Map
        st.map(full_map_df, color="#ff0000", size=50)
    else:
        st.error("📡 SIGNAL LOST: Increase GPS Link Stability to recover Santa's coordinates!")

with col2:
    st.metric("Current Longitude", f"{current['lon']:.2f}°")
    st.metric("Current Latitude", f"{current['lat']:.2f}°")
    
    # Calculate Distance
    dist = np.sqrt((user_lat - current['lat'])**2 + (user_lon - current['lon'])**2) * 111
    st.metric("Distance to You", f"{dist:,.0f} km")
    
    if st.button("🔔 Sound Sleigh Bells"):
        st.snow()
        st.toast("Santa heard your bells!")

# --- Status Updates ---
st.divider()
messages = [
    "Checking the list twice...",
    "Speeding over the Pacific Ocean!",
    "Reindeer refueling on magic carrots.",
    "Adjusting for high-altitude winds."
]
st.write(f"**Live Feed:** {messages[int(datetime.now().minute % 4)]}")
