import os
from gps_video_mapping.gpx_video_utils import (
    extract_frames_with_timestamps,
    extract_filtered_gpx_data,
    match_gps_to_frames,
    extract_and_save_frames,
)

def mapped_framesANDgps_points(video_file_path, gpx_file_path):
    # Extract frames and their timestamps from the video file
    df_frames = extract_frames_with_timestamps(video_file_path)
    
    # Extract and filter GPS data from the GPX file
    df_gps = extract_filtered_gpx_data(gpx_file_path)
    
    # Match GPS data to the extracted frames
    df_matched = match_gps_to_frames(df_gps, df_frames)
    
    # Extract and save frames, and save the matched data to a CSV file
    df_matched = extract_and_save_frames(
        video_file_path,
        df_matched,
        output_folder=os.path.join("data", "uploaded_files"),
        csv_output_path=os.path.join("data", "uploaded_files", "data.csv"),
    )

    return df_matched