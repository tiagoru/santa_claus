import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone

# --- Setup ---
st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# --- Interactive Sidebar ---
with st.sidebar:
    st.header("📡 Command Console")
    
    # 1. Radar Dial Simulation
    st.subheader("Radar Sweep Angle")
    # This creates a "moving" dial effect
    angle = (datetime.now().second * 6) # 360 degrees over 60 seconds
    st.write(f"🧭 Bearing: **{angle}°**")
    st.progress(datetime.now().second / 60) # Visual sweep bar
    
    st.divider()
    
    # 2. Radar Modes (Now affects the Map!)
    radar_mode = st.radio(
        "Select Tracking Spectrum", 
        ["Standard Satellite", "Rudolph-Vision (Infrared)", "Magic Quantum Wave"]
    )
    
    # Map colors and sizes based on mode
    if radar_mode == "Standard Satellite":
        map_color = "#00FF00" # Classic Green
        point_size = 30
    elif radar_mode == "Rudolph-Vision (Infrared)":
        map_color = "#FF4B4B" # Heat Map Red
        point_size = 60
    else:
        map_color = "#7F00FF" # Magic Purple
        point_size = 100

    st.divider()
    if st.button("🔄 Full System Reboot"):
        st.toast("Rebooting North Pole Servers...")
        time.sleep(1)
        st.rerun()

# --- Santa Location Logic ---
now = datetime.now(timezone.utc)
total_hours_utc = now.hour + (now.minute / 60) + (now.second / 3600)

# Calculate Santa (Longitude based on Earth's rotation)
current_lon = 180 - (total_hours_utc * 15)
if current_lon < -180: current_lon += 360
current_lat = 35 * np.sin(total_hours_utc * 0.2)

# Calculate History Trail
path_data = []
for i in range(15):
    p_hours = total_hours_utc - (i * 0.5)
    p_lon = 180 - (p_hours * 15)
    if p_lon < -180: p_lon += 360
    p_lat = 35 * np.sin(p_hours * 0.2)
    path_data.append({"lat": p_lat, "lon": p_lon, "Signal": "Past Ping"})

# --- Main Dashboard ---
st.title(f"🛰️ Santa Radar: {radar_mode} Mode")

col1, col2 = st.columns([3, 1])

with col1:
    # Build Map Data
    df_path = pd.DataFrame(path_data)
    df_santa = pd.DataFrame([{"lat": current_lat, "lon": current_lon, "Signal": "SANTA"}])
    full_df = pd.concat([df_path, df_santa])
    
    # The Map now uses the 'map_color' and 'point_size' from the Radar Mode selection
    st.map(full_df, color=map_color, size=point_size)
    
with col2:
    st.markdown("### 🔍 Scan Details")
    st.write(f"**Target:** Kris Kringle")
    st.write(f"**Altitude:** 30,000 ft")
    st.write(f"**Spectrum:** {radar_mode}")
    
    # Distance Logic
    st.metric("Signal Strength", f"{90 + np.random.randint(1,10)}%", delta="Strong")
    
    if st.button("🔊 Ping Sleigh"):
        st.write("📢 *Beep... Beep... Ho Ho Ho!*")
        st.balloons()

# --- Bottom Status Bar ---
st.divider()
st.markdown(f"**System Log [{now.strftime('%H:%M:%S')} UTC]:** Scanning Sector {int(current_lon)}... Santa is currently over a snowy region!")
