import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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

# --- 4. GEOCODING (ANY CITY IN THE WORLD) ---
@st.cache_data(ttl=60 * 60)  # cache results for 1 hour
def geocode_city(city_text: str):
    # Nominatim requires a unique user_agent string
    geolocator = Nominatim(user_agent="santa_radar_hq_streamlit_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    loc = geocode(city_text)
    if not loc:
        return None
    return loc.latitude, loc.longitude, loc.address

# --- 5. SIDEBAR & VISUALS ---
SEATS = {
    "🎄 Window Seat": 1.00,
    "🦌 Reindeer View": 0.98,      # tiny “bonus” just for fun
    "🎁 Present Bay": 1.03,
    "🕹️ Pilot Seat": 0.97,
}

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
    st.subheader("💺 Choose your seat")
    seat_name = st.radio("Pick a sleigh seat:", list(SEATS.keys()), index=0)
    seat_multiplier = SEATS[seat_name]

    st.divider()
    st.subheader("📍 Enter your city (anywhere!)")
    city_input = st.text_input(
        "Try: 'Düsseldorf', 'Paris, France', 'New York', 'Tokyo'",
        value="Düsseldorf"
    ).strip()

    st.divider()
    st.write(f"💨 **Anemometer (Wind):** {wind_speed} km/h")
    if is_delayed:
        st.error("⚠️ HIGH WIND WARNING: Reindeer adjusting for heavy headwinds.")
    else:
        st.success("🌤️ CLEAR SKIES: Full speed ahead.")

# --- 6. DATA & TELEMETRY ---
# Journey Start: 12:00 UTC (International Date Line Midnight)
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = max(0, (now_utc - start_time).total_seconds())

# Apply a speed penalty if there is high wind
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

s_lat, s_lon = (path[-1]['lat'], path[-1]['lon']) if path else (90, 0)

# --- 7. CITY LOOKUP ---
geo = geocode_city(city_input) if city_input else None

# Fallback if not found (Düsseldorf)
if geo is None:
    target_lat, target_lon = 51.22, 6.77
    pretty_address = "Düsseldorf (fallback)"
    city_status = "❌ City not found — try adding a country, like 'Paris, France'."
else:
    target_lat, target_lon, pretty_address = geo
    city_status = f"✅ Found: {pretty_address}"

# Distance (simple approx: degrees to km)
dist_km = np.sqrt((target_lat - s_lat)**2 + (target_lon - s_lon)**2) * 111

# Optional seat multiplier (just for fun)
dist_km_seat = dist_km * seat_multiplier

# --- 8. UI & ALERTS ---
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

# --- 9. MAP & LOG ---
col_map, col_log = st.columns([3, 1])

with col_map:
    df_path = pd.DataFrame(path) if path else pd.DataFrame([{"lon": 0, "lat": 90}])
    df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": (city_input or "Your City")}])

    layer_path = pdk.Layer(
        "ScatterplotLayer",
        data=df_path,
        get_position="[lon, lat]",
        get_color=selected["color"],
        get_radius=250000,
        pickable=False
    )

    layer_city = pdk.Layer(
        "ScatterplotLayer",
        data=df_city,
        get_position="[lon, lat]",
        get_color=[0, 150, 255],
        get_radius=380000,
        pickable=True
    )

    st.pydeck_chart(pdk.Deck(
        map_style=selected["bg"],
        initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.5),
        layers=[layer_path, layer_city],
        tooltip={"text": "{name}"}
    ))

with col_log:
    st.subheader("📝 Sector Clearance")

    regions = [
        ("Fiji", "12:00 UTC"),
        ("Auckland", "13:00 UTC"),
        ("Sydney", "14:00 UTC"),
        ("Tokyo", "15:00 UTC"),
        ("Beijing", "16:00 UTC")
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
