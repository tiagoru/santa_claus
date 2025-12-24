import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone
from streamlit_autorefresh import st_autorefresh

# --- 1. AUTO-REFRESH (Updates numbers & map every 60s) ---
st_autorefresh(interval=60000, key="santa_heartbeat")

st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# --- 2. SIDEBAR & SPECTRUM LOGIC ---
with st.sidebar:
    st.header("📡 Radar Spectrum")
    vision = st.selectbox(
        "Select Vision Mode", 
        ["Tactical Night Vision", "Infrared Heat", "Satellite View", "Standard Radar"]
    )
    
    # We use simpler map_style names that PyDeck always recognizes
    if vision == "Tactical Night Vision":
        map_bg = "dark"
        dot_color = [0, 255, 65, 200] # Matrix Green
    elif vision == "Infrared Heat":
        map_bg = "road" # High contrast
        dot_color = [255, 69, 0, 220] # Heat Orange
    elif vision == "Satellite View":
        map_bg = "satellite"
        dot_color = [255, 255, 255, 250] # White
    else:
        map_bg = "light"
        dot_color = [255, 0, 0, 200] # Red

    st.divider()
    # Spirit Gauge
    now_utc = datetime.now(timezone.utc)
    day_progress = (now_utc.hour * 3600 + now_utc.minute * 60) / 86400
    spirit = 35 + (60 * day_progress)
    st.write(f"✨ **Christmas Spirit Level**")
    st.progress(min(spirit/100, 1.0))
    st.write(f"Power: {spirit:.1f}%")

# --- 3. TELEMETRY LOGIC ---
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = (now_utc - start_time).total_seconds()

if seconds_active > 0:
    presents = int(seconds_active * 150000) # 150k gifts per second
    speed = 24500 + np.random.randint(-300, 300) # Mach 20
else:
    presents, speed = 0, 0

# --- 4. MAP DATA ---
def get_santa_path():
    minutes = int(max(0, seconds_active / 60))
    path = []
    # Create breadcrumb trail (one dot every 10 mins)
    for m in range(0, minutes + 1, 10):
        p_lon = 180 - (m * 0.25)
        if p_lon < -180: p_lon += 360
        p_lat = 40 * np.sin(m * 0.01)
        path.append({"lon": p_lon, "lat": p_lat})
    
    # Current Position
    c_lon = 180 - (minutes * 0.25)
    if c_lon < -180: c_lon += 360
    c_lat = 40 * np.sin(minutes * 0.01)
    return path, c_lat, c_lon

history, s_lat, s_lon = get_santa_path()

# Distance to Düsseldorf
dist = np.sqrt((51.22 - s_lat)**2 + (6.77 - s_lon)**2) * 111

# --- 5. UI LAYOUT ---
st.title(f"🌍 Santa Tracker: {vision}")

# Top Row: Tracking Numbers
c1, c2, c3 = st.columns(3)
c1.metric("🎁 Presents Delivered", f"{presents:,}")
c2.metric("🚀 Sleigh Speed", f"{speed:,} km/h")
c3.metric("📏 Distance to You", f"{dist:,.1f} km")

# Main View
col_map, col_log = st.columns([3, 1])

with col_map:
    # High-reliability PyDeck configuration
    st.pydeck_chart(pdk.Deck(
        map_style=map_bg,
        initial_view_state=pdk.ViewState(
            latitude=s_lat, longitude=s_lon, zoom=1.5, pitch=0
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(history),
                get_position="[lon, lat]",
                get_color=dot_color,
                get_radius=250000,
            ),
        ],
    ))

with col_log:
    st.subheader("📝 Past Locations Log")
    regions = ["North Pole", "Fiji", "New Zealand", "Australia", "Japan", "Asia"]
    visited_idx = int(min(len(regions), max(1, seconds_active // 3600)))
    for place in reversed(regions[:visited_idx]):
        st.write(f"✅ {place} - **CLEARED**")
