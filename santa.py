import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone

# --- Setup ---
st.set_page_config(page_title="NORAD Santa Command", layout="wide", page_icon="🎯")

# --- Custom Styles ---
st.markdown("""
    <style>
    .stMetric { background-color: #0e1117; border: 1px solid #333; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: The Radar Station ---
with st.sidebar:
    st.header("🎯 Sector Control")
    
    # Live Radar Dial Emoji logic
    radar_chars = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
    radar_idx = datetime.now().second % 12
    st.title(f" {radar_chars[radar_idx]} RADAR ACTIVE")
    
    st.divider()
    
    # Vision Modes
    vision = st.radio(
        "Switch Vision Spectrum",
        ["Night Vision", "Heat Seeker", "Magic Pulse", "Classic Radar"]
    )
    
    # Configure Map Styles based on Vision
    if vision == "Night Vision":
        map_color = "#00FF41" # Matrix Green
        point_size = 40
        status_msg = "🟢 LOW LIGHT ENHANCEMENT ACTIVE"
    elif vision == "Heat Seeker":
        map_color = "#FF4500" # Glowing Orange
        point_size = 70
        status_msg = "🔴 INFRARED HEAT SIGNATURE DETECTED"
    elif vision == "Magic Pulse":
        map_color = "#9D00FF" # Purple Magic
        point_size = 110
        status_msg = "🔮 DETECTING HIGH MAGIC CONCENTRATIONS"
    else:
        map_color = "#FFFFFF" # White
        point_size = 30
        status_msg = "⚪ STANDARD SATELLITE LINK"

    st.info(status_msg)

# --- Tracking Logic (NORAD Accurate) ---
now = datetime.now(timezone.utc)
# 13:36 CET is roughly 12:36 UTC.
# Santa is currently moving across Asia/Europe area!
total_hours_utc = now.hour + (now.minute / 60) + (now.second / 3600)

# Calculate Santa's Current Position
current_lon = 180 - (total_hours_utc * 15)
if current_lon < -180: current_lon += 360
current_lat = 45 * np.sin(total_hours_utc * 0.3) # Simulated flight curves

# Create "Breadcrumb" Path (The last 24 hours of flight)
path_points = []
for i in range(48): # 48 pings (every 30 mins)
    p_hours = total_hours_utc - (i * 0.5)
    p_lon = 180 - (p_hours * 15)
    if p_lon < -180: p_lon += 360
    p_lat = 45 * np.sin(p_hours * 0.3)
    path_points.append({"lat": p_lat, "lon": p_lon, "Size": 10 if i > 0 else 50})

# Prepare Data
df_path = pd.DataFrame(path_points)

# --- Main Dashboard ---
st.title("🛰️ NORAD SANTA TRACKING SYSTEM")

col1, col2 = st.columns([4, 1])

with col1:
    # High-Contrast Map
    st.map(df_path, color=map_color, size="Size")
    
with col2:
    st.subheader("📊 Telemetry")
    st.metric("Latitude", f"{current_lat:.2f} N")
    st.metric("Longitude", f"{current_lon:.2f} E")
    st.metric("Altitude", "42,000 ft")
    st.metric("Speed", "Mach 12")
    
    if st.button("📡 PING SLIEGH"):
        st.snow()
        st.success("Sleigh Response: 'Ho Ho Ho!'")

# --- Interactive Log ---
st.divider()
st.subheader("📝 Live Intelligence Log")
log_col1, log_col2 = st.columns(2)

with log_col1:
    st.write(f"**[{now.strftime('%H:%M:%S')}]** Satellite lock confirmed on Sector 7G.")
    st.write(f"**[{now.strftime('%H:%M:%S')}]** Fueling reindeer with magic oats.")

with log_col2:
    st.write(f"**[{now.strftime('%H:%M:%S')}]** {vision} is scanning for chimneys.")
    st.write(f"**[{now.strftime('%H:%M:%S')}]** Estimated presents delivered: {int(total_hours_utc * 100000000):,}")
