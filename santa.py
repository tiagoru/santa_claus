import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=30000, key="santa_heartbeat")
st.set_page_config(page_title="Santa Radar HQ", layout="wide")

# -----------------------------
# WIND & TIME
# -----------------------------
now_utc = datetime.now(timezone.utc)
wind_speed = 45 + np.random.randint(-15, 60)
is_delayed = wind_speed > 85

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("🎄 Santa Control Panel")

    vision = st.selectbox(
        "👀 Vision Mode",
        ["Tactical Night Vision", "Infrared Heat", "Satellite View"]
    )

    styles = {
        "Tactical Night Vision": {"bg": "dark", "color": [0, 255, 65]},
        "Infrared Heat": {"bg": "road", "color": [255, 69, 0]},
        "Satellite View": {"bg": "satellite", "color": [255, 255, 255]},
    }
    selected = styles[vision]

    st.divider()

    st.subheader("💺 Choose your seat")
    seat = st.radio(
        "Pick a seat:",
        ["🎄 Window Seat", "🦌 Reindeer View", "🎁 Present Bay", "🕹️ Pilot Seat"]
    )

    st.divider()
    st.subheader("📍 Enter your city")
    city_input = st.text_input(
        "Type your city (example: Berlin)",
        value="Düsseldorf"
    )

    st.divider()
    st.write(f"💨 **Wind:** {wind_speed} km/h")
    if is_delayed:
        st.error("⚠️ Wind delay – reindeer flying carefully!")
    else:
        st.success("✅ Clear skies!")

# -----------------------------
# CITY DATABASE (SAFE + FAST)
# -----------------------------
CITY_DB = {
    "düsseldorf": (51.22, 6.77),
    "berlin": (52.52, 13.40),
    "munich": (48.14, 11.58),
    "hamburg": (53.55, 9.99),
    "cologne": (50.94, 6.96),
    "london": (51.51, -0.13),
    "paris": (48.86, 2.35),
    "new york": (40.71, -74.01),
    "tokyo": (35.68, 139.69),
    "sydney": (-33.86, 151.21),
}

city_key = city_input.strip().lower()

if city_key in CITY_DB:
    target_lat, target_lon = CITY_DB[city_key]
    city_status = f"📍 Tracking **{city_input.title()}**"
else:
    target_lat, target_lon = 51.22, 6.77  # fallback Düsseldorf
    city_status = "❌ City not found – using Düsseldorf"

# -----------------------------
# SANTA FLIGHT PATH
# -----------------------------
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = max(0, (now_utc - start_time).total_seconds())
minutes = int(seconds_active / 60)

path = []
for m in range(0, minutes + 1, 10):
    lon = 180 - (m * 0.25)
    if lon < -180:
        lon += 360
    lat = 40 * np.sin(m * 0.01)
    path.append({"lon": lon, "lat": lat})

s_lat, s_lon = path[-1]["lat"], path[-1]["lon"]

# -----------------------------
# DISTANCE CALCULATION
# -----------------------------
distance_km = np.sqrt((target_lat - s_lat) ** 2 + (target_lon - s_lon) ** 2) * 111

# -----------------------------
# UI HEADER
# -----------------------------
st.title("🛷 Santa Radar HQ")
st.subheader(city_status)

# -----------------------------
# METRICS
# -----------------------------
m1, m2, m3 = st.columns(3)

m1.metric("🎁 Presents Delivered", f"{int(seconds_active * 150000):,}")
m2.metric("🚀 Sleigh Speed", "24,500 km/h" if not is_delayed else "22,000 km/h")
m3.metric("📏 Distance to You", f"{distance_km:,.1f} km")

st.caption(f"💺 Seat: **{seat}**")

# -----------------------------
# MAP
# -----------------------------
df_path = pd.DataFrame(path)
df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": city_input.title()}])

layer_path = pdk.Layer(
    "ScatterplotLayer",
    data=df_path,
    get_position="[lon, lat]",
    get_color=selected["color"],
    get_radius=250000,
)

layer_city = pdk.Layer(
    "ScatterplotLayer",
    data=df_city,
    get_position="[lon, lat]",
    get_color=[0, 150, 255],
    get_radius=350000,
)

st.pydeck_chart(
    pdk.Deck(
        map_style=selected["bg"],
        initial_view_state=pdk.ViewState(
            latitude=s_lat,
            longitude=s_lon,
            zoom=1.5,
        ),
        layers=[layer_path, layer_city],
        tooltip={"text": "{name}"},
    )
)

# -----------------------------
# FUN MESSAGE
# -----------------------------
if distance_km < 2000:
    st.success("🎅 Santa is very close to you!")
elif distance_km < 6000:
    st.info("🔔 Santa is on your continent!")
else:
    st.info("🧭 Santa is flying across the world!")
