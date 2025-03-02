import streamlit as st
import os
import pandas as pd
import folium
from streamlit_folium import folium_static
from pipeline.process_new_data import mapped_framesANDgps_points
from pipeline.run_pipeline import run_pipeline
from gps_video_mapping.gpx_video_utils import image_to_base64
import matplotlib.pyplot as plt
import json
from data.data_loader import insert_data

# Title of the Upload page
st.title("Upload and Process Files")

st.markdown("""
    ### Instructions:
    1. Upload a video file in .mp4, .avi, or .mov format.
    2. Upload a GPX file in .gpx format.
    3. Alternatively, upload a CSV file containing the matched data.
    4. Click the "Process Files" button to start the analysis.
""")

# File uploader for video file
video_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])

# File uploader for GPX file
gpx_file = st.file_uploader("Upload GPX File", type=["gpx"])

# File uploader for CSV file
csv_file = st.file_uploader("Upload CSV File", type=["csv"])

# Display progress bar
progress_bar = st.progress(0)
progress_text = st.empty()

# Define a callback function to update the progress bar
def update_progress(progress, message):
    progress_bar.progress(progress)
    progress_text.text(message)

# Button to process the uploaded files
if st.button("Process Files"):
    if csv_file is not None:
        # Load the matched data from the CSV file
        df_matched = pd.read_csv(csv_file)
    elif video_file is not None and gpx_file is not None:
        # Save the uploaded files to a temporary location
        video_file_path = f"temp_{video_file.name}"
        gpx_file_path = f"temp_{gpx_file.name}"
        
        with open(video_file_path, "wb") as f:
            f.write(video_file.getbuffer())
        
        with open(gpx_file_path, "wb") as f:
            f.write(gpx_file.getbuffer())
        
        # Process the files and get the matched data
        df_matched = mapped_framesANDgps_points(video_file_path, gpx_file_path, update_progress)
        
        # Clean up temporary files
        os.remove(video_file_path)
        os.remove(gpx_file_path)
    else:
        st.error("Please upload either a CSV file or both a video file and a GPX file.")
        st.stop()
    
    # Extract image paths from the matched DataFrame
    image_paths = df_matched["frame_image_path"].tolist()
    
    # Update progress bar
    update_progress(50, "Processing images with TensorFlow and PyTorch models...")
    
    # Run the pipeline
    df_results = run_pipeline(image_paths)
    
    # Update progress bar
    update_progress(100, "Processing complete.")
    
    # Combine data from df_matched and df_results
    combined_data = []
    for _, row in df_results.iterrows():
        matched_row = df_matched[df_matched["frame_image_path"] == row["image_path"]].iloc[0]
        latitude = matched_row["latitude"]
        longitude = matched_row["longitude"]
        video_creation_time = matched_row["video_creation_time"]
        road_type = row["road_type"]
        road_condition = row["road_condition"]
        pothole_data = json.loads(row["pothole_data"])
        frame_base64 = image_to_base64(row["image_path"])

        combined_data.append({
            "latitude": latitude,
            "longitude": longitude,
            "video_creation_time": video_creation_time,
            "road_type": road_type,
            "road_condition": road_condition,
            "pothole_data": pothole_data,
            "frame_base64": frame_base64
        })

    df_combined = pd.DataFrame(combined_data)
        
    # Display the combined results
    st.markdown("### Raw Data:")
    st.dataframe(df_combined)

    # Create columns for map and bar chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Plot the points in Folium with information
        st.subheader("Road Condition Map")
        m = folium.Map(location=[df_combined['latitude'].mean(), df_combined['longitude'].mean()], zoom_start=18)

        # Add markers to the map
        for _, row in df_combined.iterrows():
            latitude = row["latitude"]
            longitude = row["longitude"]
            road_condition = row["road_condition"]

            # Determine marker color based on road condition
            if road_condition == "good":
                color = "green"
            elif road_condition == "moderate":
                color = "orange"
            else:
                color = "red"

            # Create a popup HTML with the image to display on marker click
            popup_html = f"""
                <strong>Lat: {latitude} Long: {longitude}</strong><br>
                <strong>Road Type: {row['road_type']}</strong><br>
                <strong>Road Condition: {road_condition}</strong><br>
                <img src="data:image/jpeg;base64,{row['frame_base64']}" width="200">
            """
            popup = folium.Popup(popup_html, max_width=300)

            # Add marker with the popup containing the image
            folium.Marker([latitude, longitude], popup=popup, icon=folium.Icon(color=color)).add_to(m)

        # Display the map
        folium_static(m)
    
    with col2:
        # Display bar chart of road types and conditions
        st.subheader("Road Type and Condition Distribution")
        road_type_counts = df_combined['road_type'].value_counts()
        road_condition_counts = df_combined['road_condition'].value_counts()

        fig, ax = plt.subplots(1, 2, figsize=(10, 6))
        
        road_type_counts.plot(kind='bar', ax=ax[0], color='skyblue')
        ax[0].set_title('Road Type Distribution')
        ax[0].set_xlabel('Road Type')
        ax[0].set_ylabel('Count')
        
        road_condition_counts.plot(kind='bar', ax=ax[1], color='lightgreen')
        ax[1].set_title('Road Condition Distribution')
        ax[1].set_xlabel('Road Condition')
        ax[1].set_ylabel('Count')
        
        st.pyplot(fig)

    if "df_combined" not in st.session_state:
        st.session_state.df_combined = df_combined


if st.button("Save to Database"):
    print('Working on saving data to the database...')
    try:
        for _, data in st.session_state.df_combined.iterrows():
            print(f"Inserting data: {data.to_dict()}")  # Debugging: Print data to be inserted
            insert_data(data.to_dict())
        st.success("Data saved to the database successfully.")
    except Exception as e:
        st.error(f"An error occurred while saving to the database: {e}")