import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

# --- 1. AUTO-REFRESH (Every 30s) ---
st_autorefresh(interval=30000, key="santa_heartbeat")
st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# --- 2. WIND & DELAY LOGIC ---
now_utc = datetime.now(timezone.utc)
wind_speed = 45 + np.random.randint(-15, 60)
is_delayed = wind_speed > 85  # Threshold for "Wind Delay"

# --- 3. AUDIO LOGIC ---
def play_sound(url):
    md = f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# Düsseldorf Midnight Check (UTC+1)
now_dus = now_utc + timedelta(hours=1)
is_midnight = now_dus.hour == 0 and now_dus.minute == 0

# --- 4. CITY DATABASE (NO EXTRA LIBS) ---
# Kids can type a city, we match it here.
# Add more cities anytime!
CITY_DB = {
    "düsseldorf": (51.22, 6.77),
    "duesseldorf": (51.22, 6.77),
    "berlin": (52.52, 13.40),
    "hamburg": (53.55, 9.99),
    "munich": (48.14, 11.58),
    "münchen": (48.14, 11.58),
    "cologne": (50.94, 6.96),
    "köln": (50.94, 6.96),
    "frankfurt": (50.11, 8.68),
    "stuttgart": (48.78, 9.18),
    "paris": (48.86, 2.35),
    "london": (51.51, -0.13),
    "madrid": (40.42, -3.70),
    "rome": (41.90, 12.50),
    "vienna": (48.21, 16.37),
    "wien": (48.21, 16.37),
    "zurich": (47.37, 8.54),
    "zürich": (47.37, 8.54),
    "new york": (40.71, -74.01),
    "los angeles": (34.05, -118.24),
    "tokyo": (35.68, 139.69),
    "beijing": (39.90, 116.41),
    "sydney": (-33.86, 151.21),
    "auckland": (-36.85, 174.76),
}

# --- 5. SIDEBAR & VISUALS ---
with st.sidebar:
    st.header("📡 Radar Spectrum")
    vision = st.selectbox("Select Vision Mode", ["Tactical Night Vision", "Infrared Heat", "Satellite View"])

    styles = {
        "Tactical Night Vision": {"bg": "dark", "color": [0, 255, 65]},
        "Infrared Heat": {"bg": "road", "color": [255, 69, 0]},
        "Satellite View": {"bg": "satellite", "color": [255, 255, 255]},
    }
    selected = styles[vision]

    st.divider()

    # NEW: Seat select
    st.subheader("💺 Choose your seat")
    SEATS = {
        "🎄 Window Seat": 1.00,
        "🦌 Reindeer View": 0.98,      # tiny “fun bonus”
        "🎁 Present Bay": 1.03,
        "🕹️ Pilot Seat": 0.97,
    }
    seat_name = st.radio("Pick one:", list(SEATS.keys()), index=0)
    seat_multiplier = SEATS[seat_name]

    st.divider()

    # NEW: City input
    st.subheader("📍 Enter your city")
    city_input = st.text_input("Example: Berlin (or Düsseldorf)", value="Düsseldorf")
    city_key = city_input.strip().lower()

    st.divider()

    st.write(f"💨 **Anemometer (Wind):** {wind_speed} km/h")
    if is_delayed:
        st.error("⚠️ HIGH WIND WARNING: Reindeer adjusting for heavy headwinds.")
    else:
        st.success("🌤️ CLEAR SKIES: Full speed ahead.")

# Pick target coords from CITY_DB (fallback Düsseldorf)
if city_key in CITY_DB:
    target_lat, target_lon = CITY_DB[city_key]
    city_status = f"✅ Tracking: {city_input}"
else:
    target_lat, target_lon = CITY_DB["düsseldorf"]
    city_status = "❌ City not found — using Düsseldorf (try a bigger city name)."

# --- 6. DATA & TELEMETRY ---
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = (now_utc - start_time).total_seconds()
seconds_active = max(0, seconds_active)

# Speed penalty if high wind
base_speed = 24500
current_speed = (base_speed - (wind_speed * 10)) if is_delayed else base_speed + np.random.randint(-200, 200)
presents = int(max(0, seconds_active * 150000))

# Path Calculation
minutes = int(max(0, seconds_active / 60))
path = []
for m in range(0, minutes + 1, 10):
    p_lon = 180 - (m * 0.25)
    if p_lon < -180:
        p_lon += 360
    p_lat = 40 * np.sin(m * 0.01)
    path.append({"lon": p_lon, "lat": p_lat})

s_lat, s_lon = (path[-1]["lat"], path[-1]["lon"]) if path else (90, 0)

# Distance to chosen city (simple approx: degrees->km)
dist_km = np.sqrt((target_lat - s_lat) ** 2 + (target_lon - s_lon) ** 2) * 111

# Apply seat multiplier (purely for fun)
dist_km_seat = dist_km * seat_multiplier

# --- 7. UI & ALERTS ---
st.title(f"🚀 Santa Flight Command: {vision}")
st.caption(f"{city_status} • 💺 Seat: **{seat_name}**")

if is_midnight:
    st.error("🎊 MERRY CHRISTMAS! SANTA HAS ARRIVED IN DÜSSELDORF!")
    play_sound("https://www.soundjay.com/holiday/sounds/sleigh-bells-7.mp3")
    st.balloons()

# Top Gauges
m1, m2, m3, m4 = st.columns(4)
m1.metric("🎁 Presents Delivered", f"{presents:,}")
m2.metric("🚀 Sleigh Speed", f"{current_speed:,} km/h", delta="-Wind Delay" if is_delayed else "Stable")
m3.metric("📏 Distance to You", f"{dist_km_seat:,.1f} km")
m4.metric("💨 Current Wind", f"{wind_speed} km/h")

# --- 8. MAP & LOG ---
col_map, col_log = st.columns([3, 1])

with col_map:
    df_path = pd.DataFrame(path) if path else pd.DataFrame([{"lon": 0, "lat": 90}])
    df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": city_input.title()}])

    layer_path = pdk.Layer(
        "ScatterplotLayer",
        data=df_path,
        get_position="[lon, lat]",
        get_color=selected["color"],
        get_radius=250000,
        pickable=False,
    )

    # NEW: City marker layer
    layer_city = pdk.Layer(
        "ScatterplotLayer",
        data=df_city,
        get_position="[lon, lat]",
        get_color=[0, 150, 255],
        get_radius=380000,
        pickable=True,
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style=selected["bg"],
            initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.5),
            layers=[layer_path, layer_city],
            tooltip={"text": "{name}"},
        )
    )

with col_log:
    st.subheader("📝 Sector Clearance")

    regions = [
        ("Fiji", "12:00 UTC"),
        ("Auckland", "13:00 UTC"),
        ("Sydney", "14:00 UTC"),
        ("Tokyo", "15:00 UTC"),
        ("Beijing", "16:00 UTC"),
    ]

    for city, time_str in regions:
        hour_val = int(time_str.split(":")[0])
        if now_utc.hour >= hour_val:
            st.write(f"✅ **{city}**: Cleared at {time_str}")
        else:
            st.write(f"⏳ **{city}**: Pending...")

    if is_delayed:
        st.warning("⚠️ **Note:** Sleigh reporting 5-minute delay due to jet stream turbulence.")
    else:
        st.success("✅ Sleigh systems nominal.")
