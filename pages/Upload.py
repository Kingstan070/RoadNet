import streamlit as st
import os
from pipeline.process_new_data import mapped_framesANDgps_points

# Title of the Upload page
st.title("Upload and Process Files")

st.markdown("""
    ### Instructions:
    1. Upload a video file in .mp4, .avi, or .mov format.
    2. Upload a GPX file in .gpx format.
    3. Click the "Process Files" button to start the analysis.
""")

# Apply CSS to center the file uploaders and set their width
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
    }
    .file-uploader {
        width: 500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# File uploader for video file
st.markdown('<div class="centered"><div class="file-uploader">', unsafe_allow_html=True)
video_file = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
st.markdown('</div></div>', unsafe_allow_html=True)

# File uploader for GPX file
st.markdown('<div class="centered"><div class="file-uploader">', unsafe_allow_html=True)
gpx_file = st.file_uploader("Upload GPX File", type=["gpx"])
st.markdown('</div></div>', unsafe_allow_html=True)

# Button to process the uploaded files
if st.button("Process Files"):
    if video_file is not None and gpx_file is not None:
        # Save the uploaded files to a temporary location
        video_file_path = f"temp_{video_file.name}"
        gpx_file_path = f"temp_{gpx_file.name}"
        
        with open(video_file_path, "wb") as f:
            f.write(video_file.getbuffer())
        
        with open(gpx_file_path, "wb") as f:
            f.write(gpx_file.getbuffer())
        
        # Display progress bar
        progress_bar = st.progress(0)
        
        # Define a callback function to update the progress bar
        def update_progress(progress):
            progress_bar.progress(progress)
        
        # Process the files and get the matched data
        df_matched = mapped_framesANDgps_points(video_file_path, gpx_file_path, update_progress)
        
        # Display the matched data
        st.markdown("### Matched Data:")
        st.dataframe(df_matched)
        
        # Clean up temporary files
        os.remove(video_file_path)
        os.remove(gpx_file_path)
    else:
        st.error("Please upload both a video file and a GPX file.")