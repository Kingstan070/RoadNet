import streamlit as st
import folium
from streamlit_folium import st_folium
from data.data_loader import retrieve_routes

# Retrieve the processed routes
routes = retrieve_routes()

# Create a Folium map centered on Kerala, India
m = folium.Map(location=[10.8505, 76.2711], zoom_start=7)  # Centered on Kerala

# Add the routes to the map
for point in routes:
    folium.Marker(
        location=[point['latitude'], point['longitude']],
        popup=folium.Popup(f"""
            <strong>Lat: {point['latitude']} Long: {point['longitude']}</strong><br>
            <strong>Road Type: {point['road_type']}</strong><br>
            <strong>Road Condition: {point['road_condition']}</strong><br>
            <img src="data:image/jpeg;base64,{point['frame_base64']}" width="200">
        """, max_width=300),
        icon=folium.Icon(color='green' if point['road_condition'] == 'good' else 'orange' if point['road_condition'] == 'moderate' else 'red')
    ).add_to(m)

# Display the map in Streamlit with full width and height
st_folium(m, width=1400, height=700, returned_objects=[])