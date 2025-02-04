import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import sqlite3
import io
from folium.plugins import LocateControl


# Initialize SQLite database
conn = sqlite3.connect('building_survey.db')
c = conn.cursor()

st.title("Reviewed Listings")

st.write("Select a listing from the list.")
