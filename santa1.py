import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import base64
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

# --- 1. AUTO-REFRESH (Every 30s) ---
st_autorefresh(interval=30000, key="santa_heartbeat")

st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# --- 2. WIND & DELAY LOGIC ---
now_utc = datetime.now(timezone.utc)
# Generate a random wind speed (0 to 120 km/h)
wind_speed = 45 + np.random.randint(-15, 60)
is_delayed = wind_speed > 85  # Threshold for "Wind Delay"

# --- 3. AUDIO LOGIC ---
def play_sound(url):
    md = f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# Düsseldorf Midnight Check (UTC+1)
now_dus = now_utc + timedelta(hours=1)
is_midnight = now_dus.hour == 0 and now_dus.minute == 0

# --- 4. SIDEBAR & VISUALS ---
with st.sidebar:
    st.header("📡 Radar Spectrum")
    vision = st.selectbox("Select Vision Mode", ["Tactical Night Vision", "Infrared Heat", "Satellite View"])
    
    styles = {
        "Tactical Night Vision": {"bg": "dark", "color": [0, 255, 65]},
        "Infrared Heat": {"bg": "road", "color": [255, 69, 0]},
        "Satellite View": {"bg": "satellite", "color": [255, 255, 255]}
    }
    selected = styles[vision]

    st.divider()
    st.write(f"💨 **Anemometer (Wind):** {wind_speed} km/h")
    if is_delayed:
        st.error("⚠️ HIGH WIND WARNING: Reindeer adjusting for heavy headwinds.")
    else:
        st.success("🌤️ CLEAR SKIES: Full speed ahead.")

# --- 5. DATA & TELEMETRY ---
# Journey Start: 12:00 UTC (International Date Line Midnight)
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = (now_utc - start_time).total_seconds()

# Apply a speed penalty if there is high wind
base_speed = 24500
current_speed = (base_speed - (wind_speed * 10)) if is_delayed else base_speed + np.random.randint(-200, 200)
presents = int(max(0, seconds_active * 150000))

# Path Calculation
minutes = int(max(0, seconds_active / 60))
path = []
for m in range(0, minutes + 1, 10):
    p_lon = 180 - (m * 0.25)
    if p_lon < -180: p_lon += 360
    p_lat = 40 * np.sin(m * 0.01)
    path.append({"lon": p_lon, "lat": p_lat})

s_lat, s_lon = (path[-1]['lat'], path[-1]['lon']) if path else (90, 0)
dist = np.sqrt((51.22 - s_lat)**2 + (6.77 - s_lon)**2) * 111

# --- 6. UI & ALERTS ---
st.title(f"🚀 Santa Flight Command: {vision}")

if is_midnight:
    st.error("🎊 MERRY CHRISTMAS! SANTA HAS ARRIVED IN DÜSSELDORF!")
    play_sound("https://www.soundjay.com/holiday/sounds/sleigh-bells-7.mp3")
    st.balloons()

# Top Gauges
m1, m2, m3, m4 = st.columns(4)
m1.metric("🎁 Presents Delivered", f"{presents:,}")
m2.metric("🚀 Sleigh Speed", f"{current_speed:,} km/h", delta="-Wind Delay" if is_delayed else "Stable")
m3.metric("📏 Distance to You", f"{dist:,.1f} km")
m4.metric("💨 Current Wind", f"{wind_speed} km/h")

# Map & Log
col_map, col_log = st.columns([3, 1])

with col_map:
    st.pydeck_chart(pdk.Deck(
        map_style=selected["bg"],
        initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.5),
        layers=[pdk.Layer("ScatterplotLayer", data=pd.DataFrame(path), get_position="[lon, lat]", 
                          get_color=selected["color"], get_radius=250000)]
    ))

with col_log:
    st.subheader("📝 Sector Clearance")
    # Real World Cities Santa has cleared today
    regions = [
        ("Fiji", "12:00 UTC"),
        ("Auckland", "13:00 UTC"),
        ("Sydney", "14:00 UTC"),
        ("Tokyo", "15:00 UTC"),
        ("Beijing", "16:00 UTC")
    ]
    
    for city, time_str in regions:
        # Check if the time has passed
        hour_val = int(time_str.split(":")[0])
        if now_utc.hour >= hour_val:
            st.write(f"✅ **{city}**: Cleared at {time_str}")
        else:
            st.write(f"⏳ **{city}**: Pending...")

    if is_delayed:
        st.warning("⚠️ **Note:** Sleigh reporting 5-minute delay due to jet stream turbulence.")
