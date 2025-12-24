# Santa Radar HQ (v2.5) — FULL FIXED VERSION
# ✅ Any city in the world (geopy)
# ✅ Infrared looks infrared (heat glow overlay)
# ✅ Satellite view shows labels/borders (satellite-streets) when Mapbox token exists
# ✅ ALWAYS shows a world map even WITHOUT Mapbox token (CARTO fallback)
# ✅ PT-BR / English toggle
#
# requirements.txt (Streamlit Cloud):
# streamlit
# pandas
# numpy
# pydeck
# streamlit-autorefresh
# geopy
#
# Streamlit Cloud → Secrets (optional but recommended for true satellite):
# MAPBOX_API_KEY="YOUR_MAPBOX_TOKEN"

import os
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

APP_VERSION = "2.5"

# -----------------------------
# AUTO-REFRESH + PAGE
# -----------------------------
st.set_page_config(page_title="Santa Radar HQ", layout="wide")
st_autorefresh(interval=30000, key="santa_heartbeat")

# -----------------------------
# SAFE MAPBOX TOKEN HANDLING (NO CRASH)
# -----------------------------
MAPBOX_TOKEN = None
try:
    if hasattr(st, "secrets") and "MAPBOX_API_KEY" in st.secrets:
        MAPBOX_TOKEN = st.secrets["MAPBOX_API_KEY"]
except Exception:
    MAPBOX_TOKEN = None

if not MAPBOX_TOKEN:
    MAPBOX_TOKEN = os.environ.get("MAPBOX_API_KEY")

if MAPBOX_TOKEN:
    pdk.settings.mapbox_api_key = MAPBOX_TOKEN

# Free basemaps (always work, show countries)
CARTO_LIGHT = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
CARTO_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"

# -----------------------------
# LANGUAGE STRINGS
# -----------------------------
STR = {
    "en": {
        "title": "🚀 Santa Flight Command",
        "sidebar_title": "📡 Radar Spectrum",
        "lang": "🌍 Language",
        "vision": "Select Vision Mode",
        "wind": "💨 Anemometer (Wind)",
        "wind_warn": "⚠️ HIGH WIND WARNING: Reindeer adjusting for heavy headwinds.",
        "wind_ok": "🌤️ CLEAR SKIES: Full speed ahead.",
        "seat_title": "💺 Choose your seat",
        "seat_label": "Pick a sleigh seat:",
        "city_title": "📍 Enter your city (anywhere!)",
        "city_help": "Try: 'São Paulo, Brazil', 'Paris, France', 'Tokyo', 'New York'",
        "city_not_found": "❌ City not found — try adding a country (e.g. 'Paris, France').",
        "city_found": "✅ Found:",
        "midnight": "🎊 MERRY CHRISTMAS! SANTA HAS ARRIVED IN DÜSSELDORF!",
        "presents": "🎁 Presents Delivered",
        "speed": "🚀 Sleigh Speed",
        "distance": "📏 Distance to You",
        "wind_metric": "💨 Current Wind",
        "stable": "Stable",
        "wind_delay": "Wind Delay",
        "sector": "📝 Sector Clearance",
        "note_delay": "⚠️ Note: Sleigh reporting 5-minute delay due to jet stream turbulence.",
        "systems_ok": "✅ Sleigh systems nominal.",
        "sat_overlay": "🛰️ Satellite Paths Overlay",
        "infra_glow": "🔥 Infrared Glow Strength",
        "labels": "🗺️ Show country labels",
        "sat_need_token": "🛰️ Satellite imagery needs a Mapbox token. Showing world map instead.",
    },
    "pt-BR": {
        "title": "🚀 Comando de Voo do Papai Noel",
        "sidebar_title": "📡 Espectro do Radar",
        "lang": "🌍 Idioma",
        "vision": "Escolha o Modo de Visão",
        "wind": "💨 Anemômetro (Vento)",
        "wind_warn": "⚠️ ALERTA DE VENTO FORTE: As renas estão ajustando a rota.",
        "wind_ok": "🌤️ CÉU LIMPO: Velocidade máxima!",
        "seat_title": "💺 Escolha seu assento",
        "seat_label": "Selecione um assento no trenó:",
        "city_title": "📍 Digite sua cidade (qualquer lugar!)",
        "city_help": "Ex.: 'São Paulo, Brasil', 'Rio de Janeiro, Brasil', 'Paris, França'",
        "city_not_found": "❌ Cidade não encontrada — tente adicionar o país (ex.: 'Paris, França').",
        "city_found": "✅ Encontrado:",
        "midnight": "🎊 FELIZ NATAL! O PAPAI NOEL CHEGOU EM DÜSSELDORF!",
        "presents": "🎁 Presentes Entregues",
        "speed": "🚀 Velocidade do Trenó",
        "distance": "📏 Distância até você",
        "wind_metric": "💨 Vento Atual",
        "stable": "Estável",
        "wind_delay": "Atraso por vento",
        "sector": "📝 Liberação de Setores",
        "note_delay": "⚠️ Observação: pequeno atraso por turbulência do jato de vento.",
        "systems_ok": "✅ Sistemas do trenó OK.",
        "sat_overlay": "🛰️ Trilhas de Satélites (Overlay)",
        "infra_glow": "🔥 Força do Brilho Infravermelho",
        "labels": "🗺️ Mostrar nomes de países",
        "sat_need_token": "🛰️ Imagem de satélite precisa de token Mapbox. Mostrando mapa-múndi.",
    },
}

# -----------------------------
# AUDIO
# -----------------------------
def play_sound(url: str):
    st.markdown(f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# -----------------------------
# GEOCODING (ANY CITY)
# -----------------------------
@st.cache_data(ttl=60 * 60)
def geocode_city(city_text: str):
    geolocator = Nominatim(user_agent="santa_radar_hq_streamlit_app_v25")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    loc = geocode(city_text)
    if not loc:
        return None
    return loc.latitude, loc.longitude, loc.address

# -----------------------------
# TIME + WIND + TELEMETRY
# -----------------------------
now_utc = datetime.now(timezone.utc)
wind_speed = 45 + np.random.randint(-15, 60)
is_delayed = wind_speed > 85

# Düsseldorf midnight check (UTC+1)
now_dus = now_utc + timedelta(hours=1)
is_midnight = (now_dus.hour == 0 and now_dus.minute == 0)

# Journey start: 12:00 UTC
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
    path.append({"lon": p_lon, "lat": p_lat, "w": 1})

s_lat, s_lon = (path[-1]["lat"], path[-1]["lon"]) if path else (90, 0)

# -----------------------------
# SIDEBAR: LANGUAGE + MODES + CITY + SEAT
# -----------------------------
SEATS_EN = {
    "🎄 Window Seat": 1.00,
    "🦌 Reindeer View": 0.98,
    "🎁 Present Bay": 1.03,
    "🕹️ Pilot Seat": 0.97,
}
SEATS_PT = {
    "🎄 Assento na Janela": 1.00,
    "🦌 Vista das Renas": 0.98,
    "🎁 Baía de Presentes": 1.03,
    "🕹️ Assento do Piloto": 0.97,
}

with st.sidebar:
    lang = st.selectbox(
        STR["en"]["lang"],
        ["en", "pt-BR"],
        format_func=lambda x: "English" if x == "en" else "Português (Brasil)",
    )
    T = STR[lang]

    st.header(T["sidebar_title"])

    vision = st.selectbox(
        T["vision"],
        ["Tactical Night Vision", "Infrared Heat", "Satellite View"],
        index=0
    )

    st.divider()

    st.subheader(T["seat_title"])
    if lang == "pt-BR":
        seat_name = st.radio(T["seat_label"], list(SEATS_PT.keys()), index=0)
        seat_multiplier = SEATS_PT[seat_name]
    else:
        seat_name = st.radio(T["seat_label"], list(SEATS_EN.keys()), index=0)
        seat_multiplier = SEATS_EN[seat_name]

    st.divider()

    st.subheader(T["city_title"])
    default_city = "Düsseldorf" if lang == "en" else "São Paulo, Brasil"
    city_input = st.text_input(T["city_help"], value=default_city).strip()

    st.divider()
    st.write(f'{T["wind"]}: **{wind_speed} km/h**')
    if is_delayed:
        st.error(T["wind_warn"])
    else:
        st.success(T["wind_ok"])

    # Vision extras
    show_sat = True
    show_labels = True
    glow = 1.2

    if vision == "Satellite View":
        show_labels = st.toggle(T["labels"], value=True)
        show_sat = st.toggle(T["sat_overlay"], value=True)

    if vision == "Infrared Heat":
        glow = st.slider(T["infra_glow"], 0.6, 2.5, 1.2, 0.1)

# -----------------------------
# MAP STYLE (ALWAYS SHOW WORLD MAP)
# -----------------------------
if vision == "Satellite View":
    if MAPBOX_TOKEN:
        map_style = "mapbox://styles/mapbox/satellite-streets-v12" if show_labels else "mapbox://styles/mapbox/satellite-v9"
    else:
        map_style = CARTO_LIGHT
        st.warning(T["sat_need_token"])
elif vision == "Infrared Heat":
    # dark base helps infrared glow pop; CARTO is safe fallback
    map_style = "mapbox://styles/mapbox/dark-v11" if MAPBOX_TOKEN else CARTO_DARK
else:
    map_style = "mapbox://styles/mapbox/dark-v11" if MAPBOX_TOKEN else CARTO_DARK

# -----------------------------
# CITY LOOKUP
# -----------------------------
geo = geocode_city(city_input) if city_input else None
if geo is None:
    target_lat, target_lon = 51.22, 6.77
    pretty_address = "Düsseldorf (fallback)"
    city_status = T["city_not_found"]
else:
    target_lat, target_lon, pretty_address = geo
    city_status = f'{T["city_found"]} {pretty_address}'

# Distance approx (degrees->km) + seat fun multiplier
dist_km = np.sqrt((target_lat - s_lat) ** 2 + (target_lon - s_lon) ** 2) * 111
dist_km_seat = dist_km * seat_multiplier

# -----------------------------
# SATELLITE ORBITS OVERLAY (DECORATIVE)
# -----------------------------
def generate_orbits(t: datetime, n_orbits: int = 6, points_per_orbit: int = 160):
    phase = (t.timestamp() / 60.0) % (2 * np.pi)
    orbits = []
    sats = []
    for i in range(n_orbits):
        incl = (i * (np.pi / (n_orbits + 2))) + (np.pi / 12)
        lon_shift = (i * 35) - 90
        coords = []
        for k in range(points_per_orbit):
            a = (2 * np.pi) * (k / points_per_orbit) + phase * (0.25 + i * 0.04)
            lat = 60 * np.sin(a) * np.cos(incl)
            lon = (a * 180 / np.pi) + lon_shift
            lon = ((lon + 180) % 360) - 180
            coords.append([lon, lat])
        sat_idx = int((phase * 11 + i * 23) % points_per_orbit)
        sat_lon, sat_lat = coords[sat_idx]
        sats.append({"lon": sat_lon, "lat": sat_lat})
        orbits.append({"path": coords})
    return pd.DataFrame(orbits), pd.DataFrame(sats)

df_orbits, df_sats = generate_orbits(now_utc)

# -----------------------------
# UI HEADER + MIDNIGHT EVENT
# -----------------------------
st.title(f'{T["title"]}: {vision}  •  v{APP_VERSION}')
st.caption(f"{city_status} • 💺 {seat_name}")

if is_midnight:
    st.error(T["midnight"])
    play_sound("https://www.soundjay.com/holiday/sounds/sleigh-bells-7.mp3")
    st.balloons()

m1, m2, m3, m4 = st.columns(4)
m1.metric(T["presents"], f"{presents:,}")
m2.metric(T["speed"], f"{current_speed:,} km/h", delta=T["wind_delay"] if is_delayed else T["stable"])
m3.metric(T["distance"], f"{dist_km_seat:,.1f} km")
m4.metric(T["wind_metric"], f"{wind_speed} km/h")

# -----------------------------
# MAP + LOG
# -----------------------------
col_map, col_log = st.columns([3, 1])

with col_map:
    df_path = pd.DataFrame(path) if path else pd.DataFrame([{"lon": 0, "lat": 90, "w": 1}])
    df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": (city_input or "Your City")}])

    layers = []

    santa_color = [0, 255, 65] if vision == "Tactical Night Vision" else ([255, 255, 255] if vision == "Satellite View" else [255, 120, 0])
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df_path,
            get_position="[lon, lat]",
            get_color=santa_color,
            get_radius=250000,
            pickable=False,
        )
    )

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

    # Infrared glow overlay
    if vision == "Infrared Heat":
        layers.append(
            pdk.Layer(
                "HeatmapLayer",
                data=df_path,
                get_position="[lon, lat]",
                get_weight="w",
                radiusPixels=80,
                intensity=float(glow),
                threshold=0.03,
                colorRange=[
                    [10, 0, 0],
                    [60, 0, 0],
                    [140, 15, 0],
                    [220, 55, 0],
                    [255, 120, 20],
                    [255, 220, 120],
                ],
            )
        )

    # Satellite paths overlay
    if vision == "Satellite View" and show_sat:
        layers.append(
            pdk.Layer(
                "PathLayer",
                data=df_orbits,
                get_path="path",
                get_width=3,
                get_color=[0, 255, 255],
                width_min_pixels=2,
                pickable=False,
            )
        )
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=df_sats,
                get_position="[lon, lat]",
                get_color=[255, 255, 0],
                get_radius=220000,
                pickable=False,
            )
        )

    st.pydeck_chart(
        pdk.Deck(
            map_style=map_style,
            initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.5),
            layers=layers,
            tooltip={"text": "{name}"},
        )
    )

with col_log:
    st.subheader(T["sector"])

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
        st.warning(T["note_delay"])
    else:
        st.success(T["systems_ok"])
