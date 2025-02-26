import streamlit as st
import folium
from streamlit_folium import st_folium

# Create a Folium map
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Centered on India for example

# Display the map in Streamlit with full width and height
st_folium(m, width=1400, height=700, returned_objects=[])