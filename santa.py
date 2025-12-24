import streamlit as st
import pandas as pd
import numpy as np

# This prevents the "ModuleNotFoundError" from stopping the app
try:
    from streamlit_geolocation import streamlit_geolocation
    HAS_GPS = True
except ImportError:
    HAS_GPS = False

st.title("🎅 Santa Tracker")

if HAS_GPS:
    location = streamlit_geolocation()
    st.write("GPS System: Online 📡")
else:
    st.warning("GPS Plugin not found. Please install streamlit-geolocation.")
    # Fallback: Let kids type their city instead
    city = st.text_input("Enter your City to sync manually:")
