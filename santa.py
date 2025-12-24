import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh
import random

# -----------------------------
# 0) PAGE + AUTO REFRESH
# -----------------------------
st.set_page_config(page_title="Santa Radar HQ", layout="wide")
st_autorefresh(interval=30000, key="santa_heartbeat")  # every 30s

# -----------------------------
# 1) SESSION STATE (GAME SAVES)
# -----------------------------
if "score" not in st.session_state:
    st.session_state.score = 0
if "badges" not in st.session_state:
    st.session_state.badges = set()
if "last_trivia_answered" not in st.session_state:
    st.session_state.last_trivia_answered = None
if "sound_on" not in st.session_state:
    st.session_state.sound_on = True

# -----------------------------
# 2) TIME + WIND / DELAY
# -----------------------------
now_utc = datetime.now(timezone.utc)
wind_speed = 45 + np.random.randint(-15, 60)  # 30..105-ish
is_delayed = wind_speed > 85

# Düsseldorf Midnight Check (UTC+1)
now_dus = now_utc + timedelta(hours=1)
is_midnight = (now_dus.hour == 0 and now_dus.minute == 0)

# Journey Start: 12:00 UTC (International Date Line Midnight)
start_time = datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)
seconds_active = max(0, (now_utc - start_time).total_seconds())

# Sleigh speed + presents
base_speed = 24500
current_speed = (base_speed - (wind_speed * 10)) if is_delayed else base_speed + np.random.randint(-200, 200)
presents = int(seconds_active * 150000)

# -----------------------------
# 3) FUN HELPERS
# -----------------------------
def play_sound(url):
    if st.session_state.sound_on:
        st.markdown(
            f'<audio autoplay><source src="{url}" type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )

def award_badge(name, points=50):
    """Give badge only once, add points."""
    if name not in st.session_state.badges:
        st.session_state.badges.add(name)
        st.session_state.score += points
        st.toast(f"🏅 Badge earned: {name} (+{points} pts)")

def snow_css():
    # Simple falling "snow" using CSS animation (works in Streamlit)
    st.markdown("""
    <style>
    .snowflake {
      color: white;
      font-size: 18px;
      position: fixed;
      top: -10vh;
      z-index: 9999;
      user-select: none;
      animation-name: fall;
      animation-timing-function: linear;
      animation-iteration-count: infinite;
    }
    @keyframes fall {
      to { transform: translateY(110vh); }
    }
    </style>
    """, unsafe_allow_html=True)

def drop_snow():
    # Create multiple snowflakes with different positions/speeds
    flakes_html = ""
    for i in range(18):
        left = random.randint(0, 100)
        duration = random.uniform(6, 14)
        delay = random.uniform(0, 6)
        size = random.randint(14, 26)
        flakes_html += f"""
        <div class="snowflake" style="
            left:{left}vw;
            animation-duration:{duration}s;
            animation-delay:{delay}s;
            font-size:{size}px;
        ">❄️</div>
        """
    st.markdown(flakes_html, unsafe_allow_html=True)

# -----------------------------
# 4) SIDEBAR: MODES + KID SETTINGS
# -----------------------------
with st.sidebar:
    st.header("🎄 Santa Control Panel")

    vision = st.selectbox(
        "👀 Select Vision Mode",
        ["Tactical Night Vision", "Infrared Heat", "Satellite View"]
    )

    styles = {
        "Tactical Night Vision": {"bg": "dark", "color": [0, 255, 65]},
        "Infrared Heat": {"bg": "road", "color": [255, 69, 0]},
        "Satellite View": {"bg": "satellite", "color": [255, 255, 255]}
    }
    selected = styles[vision]

    st.divider()

    st.session_state.sound_on = st.toggle("🔊 Sound", value=st.session_state.sound_on)
    show_snow = st.toggle("❄️ Snow Animation", value=True)
    kid_mode = st.toggle("🧒 Kid Mode (extra fun)", value=True)

    st.divider()
    st.write(f"💨 **Anemometer (Wind):** {wind_speed} km/h")
    if is_delayed:
        st.error("⚠️ HIGH WIND WARNING: Reindeer adjusting for headwinds!")
    else:
        st.success("🌤️ CLEAR SKIES: Full speed ahead!")

# Snow overlay
if show_snow:
    snow_css()
    drop_snow()

# -----------------------------
# 5) CHOOSE "YOUR CITY" (DISTANCE TARGET)
# -----------------------------
CITY_PRESETS = {
    "Düsseldorf": (51.22, 6.77),
    "Berlin": (52.52, 13.40),
    "Munich": (48.14, 11.58),
    "Hamburg": (53.55, 9.99),
    "Cologne": (50.94, 6.96),
    "London": (51.51, -0.13),
    "New York": (40.71, -74.01),
}
city_name = st.sidebar.selectbox("📍 Choose your city", list(CITY_PRESETS.keys()), index=0)
target_lat, target_lon = CITY_PRESETS[city_name]

# -----------------------------
# 6) PATH CALCULATION
# -----------------------------
minutes = int(seconds_active / 60)
path = []
for m in range(0, minutes + 1, 10):
    p_lon = 180 - (m * 0.25)
    if p_lon < -180:
        p_lon += 360
    p_lat = 40 * np.sin(m * 0.01)
    path.append({"lon": p_lon, "lat": p_lat})

s_lat, s_lon = (path[-1]["lat"], path[-1]["lon"]) if path else (90, 0)
dist = np.sqrt((target_lat - s_lat) ** 2 + (target_lon - s_lon) ** 2) * 111

# -----------------------------
# 7) TITLE + BIG EVENT
# -----------------------------
st.title(f"🛷 Santa Flight Command • {vision}")

if is_midnight and city_name == "Düsseldorf":
    st.error("🎊 MERRY CHRISTMAS! SANTA HAS ARRIVED IN DÜSSELDORF!")
    play_sound("https://www.soundjay.com/holiday/sounds/sleigh-bells-7.mp3")
    st.balloons()
    award_badge("Midnight Witness", points=200)

# -----------------------------
# 8) TOP STATS + FUN BAR
# -----------------------------
m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("🎁 Presents Delivered", f"{presents:,}")
m2.metric("🚀 Sleigh Speed", f"{current_speed:,} km/h", delta="Wind Delay" if is_delayed else "Stable")
m3.metric("📏 Distance to You", f"{dist:,.1f} km")
m4.metric("💨 Current Wind", f"{wind_speed} km/h")
m5.metric("⭐ Santa Points", f"{st.session_state.score}")

# Reindeer mood (kid fun)
if kid_mode:
    mood = "😄 Happy" if not is_delayed else "😬 Wobbly"
    energy = max(0, 100 - max(0, wind_speed - 40))
    st.subheader("🦌 Reindeer Status")
    st.progress(energy / 100)
    st.write(f"**Mood:** {mood} • **Energy:** {energy}/100")

# Badge milestones
if presents > 1_000_000_000:
    award_badge("Billion Presents Club", points=150)
if dist < 2000:
    award_badge("Almost Here!", points=100)
if not is_delayed:
    award_badge("Smooth Skies", points=60)

# -----------------------------
# 9) MAP + MESSAGES + MISSIONS
# -----------------------------
col_map, col_side = st.columns([3, 1])

with col_map:
    # layers: santa path + your city marker
    df_path = pd.DataFrame(path)
    df_city = pd.DataFrame([{"lon": target_lon, "lat": target_lat, "name": city_name}])

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
        get_radius=350000,
        pickable=True
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style=selected["bg"],
            initial_view_state=pdk.ViewState(latitude=s_lat, longitude=s_lon, zoom=1.5),
            layers=[layer_path, layer_city],
            tooltip={"text": "{name}"}
        )
    )

with col_side:
    st.subheader("🛰️ Santa Comms")

    messages = []
    if dist > 8000:
        messages.append("📡 Santa says: “Warming up the sleigh engines!”")
    elif dist > 3000:
        messages.append("🎅 Santa says: “I can see your continent from here!”")
    elif dist > 1000:
        messages.append("🔔 Santa says: “Getting closer… keep listening!”")
    else:
        messages.append("✨ Santa says: “Almost there! Get ready!”")

    if is_delayed:
        messages.append("🌬️ Elf update: “Windy skies! Hold on tight!”")
    else:
        messages.append("✅ Elf update: “Green lights across the radar!”")

    for msg in messages:
        st.info(msg)

    st.divider()
    st.subheader("🎯 Mini Missions")

    # Missions (buttons give points)
    if st.button("🔎 Scan for candy-cane signal"):
        st.session_state.score += 10
        st.success("Signal found! +10 pts")
    if st.button("🧭 Calibrate the North Pole compass"):
        st.session_state.score += 15
        st.success("Compass aligned! +15 pts")
    if st.button("🛠️ Tighten sleigh bolts"):
        st.session_state.score += 12
        st.success("Bolts tightened! +12 pts")

    # Award badge if they do missions a bunch
    if st.session_state.score >= 100:
        award_badge("Junior Elf Engineer", points=80)

# -----------------------------
# 10) TRIVIA GAME (SUPER KID FRIENDLY)
# -----------------------------
st.divider()
st.header("🧠 Santa Trivia Challenge")

TRIVIA = [
    ("What do reindeer eat?", ["Candy", "Lichen", "Pizza"], 1),
    ("Where does Santa live (in stories)?", ["North Pole", "Moon", "Jungle"], 0),
    ("What do you hang by the fireplace?", ["A sock/stocking", "A shoe", "A hat"], 0),
]

q_idx = (now_utc.minute // 1) % len(TRIVIA)  # changes often
question, options, correct = TRIVIA[q_idx]

choice = st.radio(question, options, horizontal=True, key=f"trivia_{q_idx}")
answer_button = st.button("✅ Submit Answer")

if answer_button:
    if st.session_state.last_trivia_answered == q_idx:
        st.warning("You already answered this one! Wait for the next question ✨")
    else:
        st.session_state.last_trivia_answered = q_idx
        if options.index(choice) == correct:
            st.session_state.score += 25
            st.success("Correct! +25 pts 🎉")
            play_sound("https://www.soundjay.com/human/sounds/applause-8.mp3")
            award_badge("Trivia Star", points=40)
        else:
            st.session_state.score += 5
            st.info(f"Nice try! The answer was **{options[correct]}**. +5 pts")

# -----------------------------
# 11) SECTOR CLEARANCE LOG (YOUR ORIGINAL IDEA)
# -----------------------------
st.divider()
st.subheader("📝 Sector Clearance")

regions = [
    ("Fiji", "12:00 UTC"),
    ("Auckland", "13:00 UTC"),
    ("Sydney", "14:00 UTC"),
    ("Tokyo", "15:00 UTC"),
    ("Beijing", "16:00 UTC"),
    ("Dubai", "17:00 UTC"),
    ("Istanbul", "18:00 UTC"),
    ("Berlin", "19:00 UTC"),
    ("Paris", "20:00 UTC"),
    ("London", "21:00 UTC"),
]

for city, time_str in regions:
    hour_val = int(time_str.split(":")[0])
    if now_utc.hour >= hour_val:
        st.write(f"✅ **{city}**: Cleared at {time_str}")
    else:
        st.write(f"⏳ **{city}**: Pending...")

if is_delayed:
    st.warning("⚠️ **Note:** Sleigh reporting a small delay due to wind turbulence.")
