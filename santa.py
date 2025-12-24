# Santa Radar HQ — Night Vision ONLY (World map guaranteed)
# ✅ Uses CARTO basemap (no Mapbox token needed)
# ✅ Forces map_provider="carto" so the basemap actually loads
# ✅ Any city in the world (geopy)
#
# requirements.txt:
# streamlit
# pandas
# numpy
# pydeck
# streamlit-autorefresh
# geopy

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# -----------------------------
# PAGE + AUTO REFRESH
# -----------------------------
st.set_page_config(page_title="Santa Radar HQ (Night Vision)", layout="wide")
st_autorefresh(interval=30000, key="santa_heartbeat")

# -----------------------------
# ALWAYS-WORKING WORLD MAP (NO TOKEN)
# -----------------------------
CARTO_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

# -----------------------------
# GEO (ANY CITY)
# -----------------------------
@st.cache_data(ttl=60 * 60)
def geocode_city(city_text: str):
    geolocator = Nominatim(user_agent="santa_radar_nightvision")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    loc = geocode(city_text)
    if not loc:
        return None
    return loc.latitude, loc.longitude, loc.address

# -----------------------------
# WIND / TIME
# -----------------------------
now_utc = datetime.now(timezone.utc)
wind_speed = 45 + np.random.randint(-15, 60)
is_delayed = wind_speed > 85

# Düsseldorf midnight check (UTC+1)
now_dus = now_utc + timedelta(hours=1)
is_midnight = (now_dus.hour == 0 and now_dus.minute == 0)

# Journey start
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = max(0, (now_utc - start_time).total_seconds())

base_speed = 24500
current_speed = (base_speed - (wind_speed * 10)) if is_delayed else base_speed + np.random.randint(-200, 200)
presents = int(max(0, seconds_active * 150000))

# Santa path
minutes = int(seconds_active / 60)
path = []
for m in range(0, minutes + 1, 10):
    p_lon = 180 - (m * 0.25)
    if p_lon < -180:
        p_lon += 360
    p_lat = 40 * np.sin(m * 0.01)
    path.append({"lon": p_lon, "lat": p_lat})

s_lat, s_lon = (path[-1]["lat"], path[-1]["lon"]) if path else (0, 0)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("🕶️ Night Vision Radar")

    st.subheader("📍 Enter your city (anywhere)")
    city_input = st.text_input("Example: Berlin, Germany / São Paulo, Brasil", value="Düsseldorf").strip()

    st.divider()
    st.write(f"💨 **Wind:** {wind_speed} km/h")
    if is_delayed:
        st.error("⚠️ Wind delay – reindeer flying carefully!")
    else:
        st.success("✅ Clear skies!")

# City lookup
geo = geocode_city(city_input) if city_input else None
if geo is None:
    target_lat, target_lon = 51.22, 6.77
    pretty_address = "Düsseldorf (fallback)"
    st.sidebar.warning("City not found — try adding a country (e.g. 'Paris, France'). Using Düsseldorf.")
else:
    target_lat, target_lon, pretty_address = geo
    st.sidebar.success(f"Found: {pretty_address}")

# Distance approx
dist_km = np.sqrt((target_lat - s_lat) ** 2 + (target_lon - s_lon) ** 2) * 111

# -----------------------------
# UI
# -----------------------------
st.title("🛷 Santa Radar HQ — Night Vision")
st.caption(f"📍 Target: {pretty_address}")

if is_midnight:
    st.error("🎊 MERRY CHRISTMAS! SANTA HAS ARRIVED IN DÜSSELDORF!")
    st.balloons()

m1, m2, m3, m4 = st.columns(4)
m1.metric("🎁 Presents Delivered", f"{presents:,}")
m2.metric("🚀 Sleigh Speed", f"{current_speed:,} km/h", delta="Wind Delay" if is_delayed else "Stable")
m3.metric("📏 Distance to You", f"{dist_km:,.1f} km")
m4.metric("💨 Current Wind", f"{wind_speed} km/h")

# Helpful note if basemap still blank (WebGL)
st.info("If you still see a blank map: your browser/device may have WebGL disabled. Try Chrome + enable hardware acceleration.")

# -----------------------------
# MAP (CARTO + map_provider='carto' = key!)
# -----------------------------
col_map, col_log = st.columns([3, 1])

with col_map:
    df_path = pd.DataFrame(path) if path else pd.DataFrame([{"lon": 0, "lat": 0}])
    df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": city_input or "Your City"}])

    layer_path = pdk.Layer(
        "ScatterplotLayer",
        data=df_path,
        get_position="[lon, lat]",
        get_color=[0, 255, 65],
        get_radius=250000,
        pickable=False,
    )

    layer_city = pdk.Layer(
        "ScatterplotLayer",
        data=df_city,
        get_position="[lon, lat]",
        get_color=[0, 150, 255],
        get_radius=380000,
        pickable=True,
    )

    deck = pdk.Deck(
        map_style=CARTO_DARK,
        map_provider="carto",  # ✅ guarantees CARTO basemap loads
        initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.6),
        layers=[layer_path, layer_city],
        tooltip={"text": "{name}"},
    )
    st.pydeck_chart(deck, use_container_width=True, height=650)

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

    st.divider()
    if is_delayed:
        st.warning("⚠️ Sleigh reporting a small delay due to wind turbulence.")
    else:
        st.success("✅ Sleigh systems nominal.")

