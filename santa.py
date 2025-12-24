import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone, timedelta

# --- Setup ---
st.set_page_config(page_title="Official Santa Radar 2025", layout="wide", page_icon="🎯")

# --- Logic: Time and Coordinates ---
now = datetime.now(timezone.utc)
# Local Midnight Calculation (Düsseldorf)
local_midnight = datetime(2025, 12, 25, 0, 0, 0, tzinfo=timezone.utc)
time_to_midnight = local_midnight - now
seconds_to_midnight = time_to_midnight.total_seconds()

# User Location (Düsseldorf)
user_lat, user_lon = 51.22, 6.77

# Santa Logic: 1 spot per minute since 00:00 UTC
minutes_passed = now.hour * 60 + now.minute
path_points = []
for m in range(minutes_passed + 1):
    # Santa moves 0.25 degrees per minute (360 degrees / 1440 mins)
    p_lon = 180 - (m * 0.25)
    if p_lon < -180: p_lon += 360
    # Sinuous flight path
    p_lat = 40 * np.sin(m * 0.01)
    path_points.append({"lat": p_lat, "lon": p_lon})

df_path = pd.DataFrame(path_points)
current_santa = path_points[-1]

# Distance Logic: Approaches 1km as we hit midnight
if seconds_to_midnight > 0:
    # Linear interpolation to 1km at midnight
    base_dist = np.sqrt((user_lat - current_santa['lat'])**2 + (user_lon - current_santa['lon'])**2) * 111
    display_dist = max(1.0, (seconds_to_midnight / 86400) * base_dist)
else:
    display_dist = 1.0 # He's here!

# --- Sidebar: Controls ---
with st.sidebar:
    st.header("📡 Command Center")
    vision = st.selectbox("Switch Vision Spectrum", ["Standard (White)", "Night Vision (Green)", "Heat Map (Orange)", "Magic Flare (Purple)"])
    
    # Map Styling
    styles = {
        "Standard (White)": {"color": "#FFFFFF", "size": 20},
        "Night Vision (Green)": {"color": "#00FF41", "size": 35},
        "Heat Map (Orange)": {"color": "#FF4500", "size": 60},
        "Magic Flare (Purple)": {"color": "#9D00FF", "size": 90}
    }
    
    st.divider()
    # Christmas Spirit Gauge
    spirit_val = 35 + (60 * (minutes_passed / 1440)) + np.random.randint(-5, 5)
    st.write(f"✨ **Christmas Spirit Gauge**")
    st.progress(min(spirit_val/100, 1.0))
    st.write(f"Current Level: **{spirit_val:.1f}%**")

# --- Main Dashboard ---
st.title("🎯 Live Global Tracking: 2025 Mission")

# Midnight Alert
if seconds_to_midnight <= 0:
    st.error("🚨 ALERT: LOCAL DELIVERY IN PROGRESS! Santa is in your airspace.")
    st.balloons()
elif seconds_to_midnight < 3600:
    st.warning(f"⚠️ HIGH ALERT: {int(seconds_to_midnight/60)} minutes until chimney arrival!")

col1, col2 = st.columns([3, 1])

with col1:
    # Adding User Location to map
    df_user = pd.DataFrame([{"lat": user_lat, "lon": user_lon}])
    # Display the Full Path + Santa + User
    st.map(df_path, color=styles[vision]["color"], size=styles[vision]["size"])

with col2:
    st.metric("Distance to You", f"{display_dist:,.2f} km")
    st.metric("Flight Time", f"{now.strftime('%H:%M:%S')} UTC")
    st.metric("Presents to Go", f"{max(0, 100 - (minutes_passed/14.4)):.1f}%")
    
    st.divider()
    if st.button("🔔 Signal Chimney Light"):
        st.snow()
        st.success("Signal Sent! Santa has been notified.")

# --- Bottom Status Log ---
st.divider()
log_msg = "Sleigh on schedule." if seconds_to_midnight > 3600 else "DELIVERY DELAY: High cookie volume detected in nearby sector!"
st.markdown(f"**NORAD LOG:** {log_msg}")
