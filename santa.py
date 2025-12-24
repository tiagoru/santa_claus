import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

# --- Setup ---
st.set_page_config(page_title="NORAD Global Command", layout="wide", page_icon="🎯")

# --- Interactive Sidebar ---
with st.sidebar:
    st.header("📡 Sensor Calibration")
    
    # 1. Vision Spectrum - Now changes the color of EVERYTHING
    vision = st.selectbox(
        "Switch Vision Spectrum", 
        ["Standard Radar", "Night Vision", "Heat Seeker", "Magic Flare"]
    )
    
    # Configuration for Visuals
    vis_config = {
        "Standard Radar": {"color": "#FFFFFF", "size": 25, "bg": "light"},
        "Night Vision": {"color": "#00FF41", "size": 40, "bg": "dark"},
        "Heat Seeker": {"color": "#FF4500", "size": 70, "bg": "dark"},
        "Magic Flare": {"color": "#9D00FF", "size": 100, "bg": "dark"}
    }
    
    selected = vis_config[vision]
    
    st.divider()
    
    # 2. Christmas Spirit Gauge (35% to 95%)
    # Logic: Increases as we approach midnight
    now_utc = datetime.now(timezone.utc)
    # 13:47 UTC is roughly 57% of the way through the day
    day_progress = (now_utc.hour * 3600 + now_utc.minute * 60) / 86400
    spirit_val = 35 + (60 * day_progress) + np.random.randint(-2, 3)
    
    st.write(f"✨ **Christmas Spirit Level**")
    st.progress(min(spirit_val/100, 1.0))
    st.write(f"Current Signal: **{spirit_val:.1f}%**")

# --- Time Zone Accurate Tracking Logic ---
# Santa starts at Longitude 180 (Fiji/New Zealand) at 12:00 UTC on the 24th
# He reaches Longitude 0 (London) at 00:00 UTC on the 25th
def get_time_accurate_path():
    # Every minute since the start of the journey (Fiji Midnight)
    # Journey starts at 12:00 UTC on the 24th
    start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    
    duration = current_time - start_time
    minutes_passed = int(duration.total_seconds() / 60)
    
    path = []
    # If he hasn't started yet (before 12:00 UTC), he's at the North Pole
    if minutes_passed < 0:
        return [{"lat": 90, "lon": 0, "size": 50}], 90, 0

    for m in range(minutes_passed + 1):
        # Earth rotates 0.25 degrees per minute
        # Lon moves from 180 Westwards
        p_lon = 180 - (m * 0.25)
        if p_lon < -180: p_lon += 360
        
        # Flight path curve
        p_lat = 45 * np.sin(m * 0.01)
        path.append({"lat": p_lat, "lon": p_lon, "size": 10 if m < minutes_passed else 100})
        
    return path, path[-1]['lat'], path[-1]['lon']

path_data, s_lat, s_lon = get_time_accurate_path()
df_path = pd.DataFrame(path_data)

# --- Distance Calculation (Düsseldorf) ---
user_lat, user_lon = 51.22, 6.77
dist = np.sqrt((user_lat - s_lat)**2 + (user_lon - s_lon)**2) * 111

# Force 1km minimum if it's very close or past midnight
if dist < 1.0: dist = 1.0

# --- Main Dashboard ---
st.title(f"🚀 NORAD Santa Tracker | {vision} Mode")

# Alert Logic
if datetime.now().hour >= 23:
    st.error("🚨 LOCAL ALERT: Santa entering Düsseldorf Airspace! Prepare cookies.")
elif dist < 500:
    st.warning("⚠️ PROXIMITY WARNING: Sleigh detected in neighboring sector.")

col1, col2 = st.columns([3, 1])

with col1:
    # The Map! Note: Streamlit's native st.map doesn't support background color changes,
    # but the dots now update their intensity and size based on your selection.
    st.map(df_path, color=selected["color"], size="size")

with col2:
    st.metric("Distance from Düsseldorf", f"{dist:,.1f} km")
    st.metric("Current Latitude", f"{s_lat:.2f}")
    st.metric("Current Longitude", f"{s_lon:.2f}")
    
    st.divider()
    st.subheader("📋 Status Report")
    if dist < 500:
        st.write("🛑 **Status:** Delay - Heavy Cookie Intake")
    else:
        st.write("✅ **Status:** On Schedule")

# --- Footer System Log ---
st.divider()
st.info(f"System Log: Tracking {len(df_path)} data points across active time zones.")
