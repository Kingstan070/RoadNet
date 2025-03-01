import streamlit as st
import os
import pandas as pd
from pipeline.process_new_data import mapped_framesANDgps_points
from pipeline.run_pipeline import run_pipeline

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
    
    # Display the matched data
    st.markdown("### Matched Data:")
    st.dataframe(df_matched)
    
    # Extract image paths from the matched DataFrame
    image_paths = df_matched["frame_image_path"].tolist()
    
    # Update progress bar
    update_progress(50, "Processing images with TensorFlow and PyTorch models...")
    
    # Run the pipeline
    df_results = run_pipeline(image_paths)
    
    # Update progress bar
    update_progress(100, "Processing complete.")
    
    # Display the results
    st.markdown("### Results:")
    st.dataframe(df_results)
    
    # Display statistics
    st.markdown("### Statistics:")
    st.write(df_results.describe())