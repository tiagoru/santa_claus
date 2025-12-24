# Santa Radar HQ — Night Vision ONLY (World map guaranteed) + Signals + PT-BR/EN
# ✅ CARTO basemap (no Mapbox token needed)  ✅ map_provider="carto"
# ✅ Any city in the world (geopy)
# ✅ Hourly ping (once per hour) shows distance
# ✅ Midnight event:
#    - If windy: shows "delay due to winds / atraso por ventos"
#    - If close (<= 1 km): rapid beeps + balloons
# ✅ NEW: Visited cities trail (green dots on map)
# ✅ NEW: City "unlock" sound + toast when a new city gets visited
# ✅ NEW: Progress bar (visited / total)
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
st_autorefresh(interval=30000, key="santa_heartbeat")  # refresh every 30s

# -----------------------------
# ALWAYS-WORKING WORLD MAP (NO TOKEN)
# -----------------------------
CARTO_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

# -----------------------------
# SESSION STATE (prevents repeated pings / repeats)
# -----------------------------
if "last_hour_ping" not in st.session_state:
    st.session_state.last_hour_ping = None  # "YYYY-MM-DD HH"
if "midnight_event_done" not in st.session_state:
    st.session_state.midnight_event_done = False
if "last_visited_count" not in st.session_state:
    st.session_state.last_visited_count = 0

# -----------------------------
# SOUND (simple HTML audio)
# -----------------------------
def play_sound(url: str):
    st.markdown(
        f'<audio autoplay="true"><source src="{url}" type="audio/mpeg"></audio>',
        unsafe_allow_html=True,
    )

# Sounds (public sample URLs)
BEEP_URL = "https://www.soundjay.com/buttons/sounds/beep-07.mp3"
PING_URL = "https://www.soundjay.com/buttons/sounds/button-09.mp3"
UNLOCK_URL = "https://www.soundjay.com/buttons/sounds/button-4.mp3"

# -----------------------------
# LANGUAGE STRINGS
# -----------------------------
TXT = {
    "en": {
        "app_title": "🛷 Santa Radar HQ — Night Vision",
        "lang": "🌍 Language",
        "sidebar_title": "🕶️ Night Vision Radar",
        "city_title": "📍 Enter your city (anywhere)",
        "city_hint": "Example: Berlin, Germany / São Paulo, Brazil",
        "sound": "🔊 Sound on",
        "wind": "💨 Wind",
        "wind_delay": "⚠️ Wind delay – reindeer flying carefully!",
        "wind_ok": "✅ Clear skies!",
        "found": "Found:",
        "not_found": "City not found — try adding a country (e.g. 'Paris, France'). Using Düsseldorf.",
        "target": "📍 Target",
        "dus_time": "🕛 Düsseldorf time",
        "presents": "🎁 Presents Delivered",
        "speed": "🚀 Sleigh Speed",
        "distance": "📏 Distance to You",
        "wind_metric": "💨 Current Wind",
        "stable": "Stable",
        "delay_delta": "Wind Delay",
        "webgl_tip": "If the map is blank on some computers: WebGL may be disabled. Try Chrome/Edge + hardware acceleration.",
        "sector": "📝 Sector Clearance",
        "signals": "🔔 Signals",
        "sig_hourly": "• Hourly ping at :00 shows distance",
        "sig_midnight": "• Midnight beep triggers if distance ≤ 1 km",
        "systems_ok": "✅ Sleigh systems nominal.",
        "midnight_close": "🎊 MIDNIGHT ALERT: Santa is basically at your city! (≤ 1 km)",
        "midnight_delay": "🌬️ MIDNIGHT UPDATE: Strong winds are causing a delay — Santa will arrive a bit later!",
        "hourly_ping": "🛰️ Hourly Radar Ping: Santa is {d} km away!",
        "visited_title": "✅ Cities Visited So Far",
        "visited_none": "⏳ Santa is just getting started!",
        "progress": "🎯 Journey Progress",
        "unlock_toast": "🎄 New city visited: {city}",
    },
    "pt-BR": {
        "app_title": "🛷 Santa Radar HQ — Visão Noturna",
        "lang": "🌍 Idioma",
        "sidebar_title": "🕶️ Radar em Visão Noturna",
        "city_title": "📍 Digite sua cidade (qualquer lugar)",
        "city_hint": "Ex.: Berlin, Germany / São Paulo, Brasil",
        "sound": "🔊 Som ligado",
        "wind": "💨 Vento",
        "wind_delay": "⚠️ Atraso por vento – as renas estão voando com cuidado!",
        "wind_ok": "✅ Céu limpo!",
        "found": "Encontrado:",
        "not_found": "Cidade não encontrada — tente adicionar o país (ex.: 'Paris, França'). Usando Düsseldorf.",
        "target": "📍 Alvo",
        "dus_time": "🕛 Horário de Düsseldorf",
        "presents": "🎁 Presentes Entregues",
        "speed": "🚀 Velocidade do Trenó",
        "distance": "📏 Distância até você",
        "wind_metric": "💨 Vento Atual",
        "stable": "Estável",
        "delay_delta": "Atraso por vento",
        "webgl_tip": "Se o mapa ficar branco em alguns computadores: o WebGL pode estar desativado. Tente Chrome/Edge com aceleração de hardware.",
        "sector": "📝 Liberação de Setores",
        "signals": "🔔 Sinais",
        "sig_hourly": "• Sinal a cada hora em :00 mostrando a distância",
        "sig_midnight": "• Bipe da meia-noite se a distância ≤ 1 km",
        "systems_ok": "✅ Sistemas do trenó OK.",
        "midnight_close": "🎊 ALERTA DE MEIA-NOITE: O Papai Noel está praticamente na sua cidade! (≤ 1 km)",
        "midnight_delay": "🌬️ ATUALIZAÇÃO DA MEIA-NOITE: Ventos fortes causaram atraso — o Papai Noel vai chegar um pouco mais tarde!",
        "hourly_ping": "🛰️ Ping de hora em hora: o Papai Noel está a {d} km!",
        "visited_title": "✅ Cidades Visitadas Até Agora",
        "visited_none": "⏳ O Papai Noel está só começando!",
        "progress": "🎯 Progresso da Viagem",
        "unlock_toast": "🎄 Nova cidade visitada: {city}",
    },
}

# -----------------------------
# WORLD CITIES SANTA VISITS (unlock by UTC hour)
# Use 'hour_utc' in 0..23. Add more anytime.
# -----------------------------
SANTA_CITIES = [
    {"en": "Suva, Fiji", "pt": "Suva, Fiji", "lat": -18.1248, "lon": 178.4501, "hour_utc": 12},
    {"en": "Auckland, New Zealand", "pt": "Auckland, Nova Zelândia", "lat": -36.8485, "lon": 174.7633, "hour_utc": 13},
    {"en": "Sydney, Australia", "pt": "Sydney, Austrália", "lat": -33.8688, "lon": 151.2093, "hour_utc": 14},
    {"en": "Tokyo, Japan", "pt": "Tóquio, Japão", "lat": 35.6762, "lon": 139.6503, "hour_utc": 15},
    {"en": "Beijing, China", "pt": "Pequim, China", "lat": 39.9042, "lon": 116.4074, "hour_utc": 16},
    {"en": "Dubai, UAE", "pt": "Dubai, Emirados Árabes", "lat": 25.2048, "lon": 55.2708, "hour_utc": 18},
    {"en": "Istanbul, Türkiye", "pt": "Istambul, Turquia", "lat": 41.0082, "lon": 28.9784, "hour_utc": 19},
    {"en": "Berlin, Germany", "pt": "Berlim, Alemanha", "lat": 52.5200, "lon": 13.4050, "hour_utc": 20},
    {"en": "Paris, France", "pt": "Paris, França", "lat": 48.8566, "lon": 2.3522, "hour_utc": 22},
    {"en": "London, UK", "pt": "Londres, Reino Unido", "lat": 51.5074, "lon": -0.1278, "hour_utc": 23},
]

# -----------------------------
# GEO (ANY CITY)
# -----------------------------
@st.cache_data(ttl=60 * 60)
def geocode_city(city_text: str):
    geolocator = Nominatim(user_agent="santa_radar_nightvision_visited")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    loc = geocode(city_text)
    if not loc:
        return None
    return loc.latitude, loc.longitude, loc.address

# -----------------------------
# TIME + WIND
# -----------------------------
now_utc = datetime.now(timezone.utc)
wind_speed = 45 + np.random.randint(-15, 60)
is_delayed = wind_speed > 85

# Düsseldorf time (UTC+1) for midnight events
now_dus = now_utc + timedelta(hours=1)
is_midnight_minute = (now_dus.hour == 0 and now_dus.minute == 0)

# -----------------------------
# SIDEBAR (language first)
# -----------------------------
with st.sidebar:
    lang = st.selectbox(
        TXT["en"]["lang"],
        ["en", "pt-BR"],
        format_func=lambda x: "English" if x == "en" else "Português (Brasil)"
    )
    t = TXT[lang]

    st.header(t["sidebar_title"])
    st.subheader(t["city_title"])
    city_default = "Düsseldorf" if lang == "en" else "São Paulo, Brasil"
    city_input = st.text_input(t["city_hint"], value=city_default).strip()

    st.divider()
    sound_on = st.toggle(t["sound"], value=True)

    st.divider()
    st.write(f'{t["wind"]}: **{wind_speed} km/h**')
    if is_delayed:
        st.error(t["wind_delay"])
    else:
        st.success(t["wind_ok"])

# -----------------------------
# TELEMETRY (Santa simulated path)
# -----------------------------
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = max(0, (now_utc - start_time).total_seconds())

base_speed = 24500
current_speed = (base_speed - (wind_speed * 10)) if is_delayed else base_speed + np.random.randint(-200, 200)
presents = int(max(0, seconds_active * 150000))

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
# CITY LOOKUP (kid's city)
# -----------------------------
geo = geocode_city(city_input) if city_input else None
if geo is None:
    target_lat, target_lon = 51.22, 6.77
    pretty_address = "Düsseldorf (fallback)"
    st.sidebar.warning(t["not_found"])
else:
    target_lat, target_lon, pretty_address = geo
    st.sidebar.success(f'{t["found"]} {pretty_address}')

# Distance approx (degrees->km)
dist_km = np.sqrt((target_lat - s_lat) ** 2 + (target_lon - s_lon) ** 2) * 111
close_enough = dist_km <= 1.0

# -----------------------------
# VISITED CITIES (based on UTC time)
# -----------------------------
def city_label(city):
    return city["pt"] if lang == "pt-BR" else city["en"]

visited = []
for c in SANTA_CITIES:
    if now_utc.hour > c["hour_utc"] or (now_utc.hour == c["hour_utc"] and now_utc.minute >= 0):
        visited.append({
            "name": city_label(c),
            "lat": c["lat"],
            "lon": c["lon"],
            "hour_utc": c["hour_utc"],
        })

df_visited = pd.DataFrame(visited)

# Unlock sound + toast when a new city appears
visited_count = len(visited)
if visited_count > st.session_state.last_visited_count:
    # New city unlocked!
    new_city_name = visited[-1]["name"] if visited else None
    st.session_state.last_visited_count = visited_count
    if new_city_name:
        st.toast(t["unlock_toast"].format(city=new_city_name))
        if sound_on:
            play_sound(UNLOCK_URL)

# -----------------------------
# SIGNAL: HOURLY PING (ONCE PER HOUR)
# -----------------------------
hour_key = now_dus.strftime("%Y-%m-%d %H")
is_top_of_hour = (now_dus.minute == 0)

if is_top_of_hour and st.session_state.last_hour_ping != hour_key:
    st.session_state.last_hour_ping = hour_key
    st.toast(t["hourly_ping"].format(d=f"{dist_km:,.1f}"))
    if sound_on:
        play_sound(PING_URL)

# -----------------------------
# SIGNAL: MIDNIGHT EVENT (ONCE PER MIDNIGHT MINUTE)
# -----------------------------
if not is_midnight_minute:
    st.session_state.midnight_event_done = False

if is_midnight_minute and not st.session_state.midnight_event_done:
    st.session_state.midnight_event_done = True

    if is_delayed:
        st.warning(t["midnight_delay"])

    if close_enough:
        st.error(t["midnight_close"])
        st.balloons()
        if sound_on:
            play_sound(BEEP_URL)
            play_sound(BEEP_URL)
            play_sound(BEEP_URL)

# -----------------------------
# UI
# -----------------------------
st.title(t["app_title"])
st.caption(f'{t["target"]}: {pretty_address} • {t["dus_time"]}: {now_dus.strftime("%H:%M")}')

m1, m2, m3, m4 = st.columns(4)
m1.metric(t["presents"], f"{presents:,}")
m2.metric(t["speed"], f"{current_speed:,} km/h", delta=t["delay_delta"] if is_delayed else t["stable"])
m3.metric(t["distance"], f"{dist_km:,.2f} km")
m4.metric(t["wind_metric"], f"{wind_speed} km/h")

# Progress bar (visited cities)
st.subheader(t["progress"])
total_cities = len(SANTA_CITIES)
progress = 0 if total_cities == 0 else visited_count / total_cities
st.progress(progress)
st.write(f"**{visited_count} / {total_cities}**")

st.info(t["webgl_tip"])

# -----------------------------
# MAP (CARTO + map_provider='carto' = key!)
# -----------------------------
col_map, col_log = st.columns([3, 1])

with col_map:
    df_path = pd.DataFrame(path) if path else pd.DataFrame([{"lon": 0, "lat": 0}])
    df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": city_input or "Your City"}])

    layers = []

    # Santa path
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df_path,
            get_position="[lon, lat]",
            get_color=[0, 255, 65],
            get_radius=250000,
            pickable=False,
        )
    )

    # Your city marker
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df_city,
            get_position="[lon, lat]",
            get_color=[0, 150, 255],
            get_radius=380000,
            pickable=True,
        )
    )

    # Visited cities markers (green)
    if not df_visited.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=df_visited,
                get_position="[lon, lat]",
                get_color=[0, 255, 120],
                get_radius=320000,
                pickable=True,
            )
        )

    deck = pdk.Deck(
        map_style=CARTO_DARK,
        map_provider="carto",
        initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.6),
        layers=layers,
        tooltip={"text": "{name}"},
    )
    st.pydeck_chart(deck, use_container_width=True, height=650)

with col_log:
    st.subheader(t["sector"])
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
    st.subheader(t["visited_title"])
    if df_visited.empty:
        st.write(t["visited_none"])
    else:
        # show newest first
        for name in list(df_visited["name"])[::-1]:
            st.write(f"🟢 {name}")

    st.divider()
    st.write(f"**{t['signals']}**")
    st.write(t["sig_hourly"])
    st.write(t["sig_midnight"])

    if is_delayed:
        st.warning(t["wind_delay"])
    else:
        st.success(t["systems_ok"])
