import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone

# Setup page
st.set_page_config(page_title="Santa Command Center", layout="wide", page_icon="🦌")

# --- Custom Styling for a "Dark Mode" Radar Look ---
st.markdown("""
    <style>
    .metric-container { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- App Title ---
st.title("🛰️ Santa Command Center: Global Tracking 2025")

# --- Sidebar: Technical Calibrations ---
with st.sidebar:
    st.header("⚙️ Flight Systems")
    # Interactive Buttons for Kids
    boost = st.button("🚀 Boost Reindeer Speed!")
    gps_fix = st.button("📡 Re-calibrate Sleigh GPS")
    cookie_scan = st.button("🍪 Scan for Cookies")
    
    st.divider()
    radar_mode = st.radio("Radar Mode", ["Satellite", "Infrared (Rudolph-Vision)", "Magic Wave"])
    
    if boost:
        st.success("SPEED BOOST ACTIVE! Mach 10 engaged.")
    if gps_fix:
        st.info("GPS Signal Locked. Precision: 0.001 meters.")

# --- Logic: Dynamic Data ---
def get_live_stats():
    # Base stats that grow based on the time of day
    now = datetime.now(timezone.utc)
    seconds_today = now.hour * 3600 + now.minute * 60 + now.second
    
    # Simulate billions of presents
    presents = int(seconds_today * 55000) 
    cookies = int(seconds_today * 1200)
    speed = 5800000 + (np.random.randint(-5000, 5000)) # 5.8 million km/h
    
    if boost: speed *= 1.5
    
    return presents, cookies, speed

presents, cookies, speed = get_live_stats()

# --- Main Dashboard Metrics ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎁 Presents Delivered", f"{presents:,}", delta="Fast")
with col2:
    st.metric("🍪 Cookies Consumed", f"{cookies:,}", delta="Yum!")
with col3:
    st.metric("💨 Sleigh Speed", f"{speed:,} km/h")
with col4:
    st.metric("🦌 Active Reindeer", "9/9", delta="Healthy")

# --- Map & Tracking ---
st.subheader("🌍 Live Tracking Path")

# Logic for Time-Based Geography
total_hours_utc = datetime.now(timezone.utc).hour + (datetime.now(timezone.utc).minute / 60)
current_lon = 180 - (total_hours_utc * 15)
if current_lon < -180: current_lon += 360
current_lat = 40 * np.sin(total_hours_utc * 0.1)

# Create historical tracking path
path_data = []
for i in range(20):
    p_hours = total_hours_utc - (i * 0.4)
    p_lon = 180 - (p_hours * 15)
    if p_lon < -180: p_lon += 360
    p_lat = 40 * np.sin(p_hours * 0.1)
    path_data.append({"lat": p_lat, "lon": p_lon, "type": "Path"})

# Combine Data
map_df = pd.DataFrame(path_data)
map_df = pd.concat([map_df, pd.DataFrame([{"lat": current_lat, "lon": current_lon, "type": "Santa"}])])

# Display Map
st.map(map_df, color="#ff4b4b", size=40)

# --- Interactive Radar "Beeps" ---
st.divider()
st.subheader("📡 Radar Detection Log")

funny_logs = [
    "Detected high concentrations of gingerbread in Germany!",
    "Santa spotted taking a 3-second nap over the Atlantic.",
    "Rudolph's nose is glowing at 500 Watts of brightness.",
    "Sleigh weight decreased: 50,000 bicycles delivered in Japan.",
    "Emergency stop: Reindeer found a bowl of magic carrots in Canada!"
]

# When kids click "Scan", show a random log
if st.button("🛰️ Run Radar Pulse"):
    log = np.random.choice(funny_logs)
    st.warning(f"**ALERT:** {log}")
    st.snow()
else:
    st.info("Click the 'Run Radar Pulse' button to scan for Santa's activity!")
