import os
import cv2
import datetime
import subprocess
import pandas as pd
import numpy as np
from tqdm import tqdm
import base64
import streamlit as st
import gpxpy
import tempfile

# Function to get video creation time
def get_video_creation_time(video_file):
    try:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "format_tags=creation_time",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        creation_time_str = result.stdout.strip()

        if not creation_time_str:
            raise ValueError("Could not find creation time in video metadata.")

        return datetime.datetime.strptime(creation_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    except Exception as e:
        print(f"Error extracting creation time: {e}")
        return None

# Function to extract frames and timestamps
def extract_frames_with_timestamps(video_file, update_progress):
    video_creation_time = get_video_creation_time(video_file)
    if video_creation_time is None:
        print("Could not determine video creation time.")
        return None

    ist_offset = datetime.timedelta(hours=5, minutes=30)
    video_creation_time_ist = video_creation_time + ist_offset

    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_data = []
    first_frame_time = None

    for frame_number in tqdm(range(total_frames), desc="Processing Frames"):
        ret, _ = cap.read()
        if not ret:
            break

        frame_time_seconds = frame_number / fps
        frame_timestamp = video_creation_time_ist + datetime.timedelta(seconds=frame_time_seconds)

        if frame_number == 0:
            first_frame_time = frame_timestamp

        relative_timestamp = (frame_timestamp - first_frame_time).total_seconds()

        frame_data.append([frame_number, relative_timestamp, video_creation_time_ist])

        # Update progress bar
        update_progress((frame_number + 1) / total_frames)

    cap.release()
    df = pd.DataFrame(frame_data, columns=["frame", "relative_timestamp", "video_creation_time"])
    return df

# Function to extract and filter GPS data
def extract_filtered_gpx_data(gpx_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)

    gps_data = []
    first_timestamp = None
    seen_points = set()

    for track in gpx.tracks:
        for segment in track.segments:
            for point in tqdm(segment.points, desc="Processing GPX Points"):
                lat, lon = round(point.latitude, 5), round(point.longitude, 5)
                timestamp = point.time
                
                if first_timestamp is None:
                    first_timestamp = timestamp
                
                relative_timestamp = timestamp.timestamp() - first_timestamp.timestamp()
                
                if (lat, lon, relative_timestamp) in seen_points:
                    continue  # Remove duplicate points
                seen_points.add((lat, lon, relative_timestamp))
                
                gps_data.append([lat, lon, relative_timestamp])

    df = pd.DataFrame(gps_data, columns=["latitude", "longitude", "relative_timestamp"])
    if not df.empty:
        df = df[df["relative_timestamp"] >= 0]  # Remove GPS points with timestamps before the video starts
        df["relative_timestamp"] -= df["relative_timestamp"].min()  # Adjust timestamps to start from zero
    return df

def match_gps_to_frames(df_gps, df_frames):
    matched_data = []
    video_start = df_frames["relative_timestamp"].min()
    video_end = df_frames["relative_timestamp"].max()
    video_creation_time = df_frames["video_creation_time"].iloc[0]

    for _, (lat, lon, gps_time) in tqdm(df_gps.iterrows(), total=len(df_gps), desc="Matching GPS to Frames"):
        # Ensure the GPS time is within the video’s time range
        if gps_time < video_start or gps_time > video_end:
            continue  # Skip this GPS point if it’s out of the video’s time range

        # Perform binary search to find the closest frame to the GPS time
        idx = np.searchsorted(df_frames["relative_timestamp"].values, gps_time, side="left")
        if idx > 0 and idx < len(df_frames):
            # Choose the frame with the timestamp closest to the GPS timestamp
            if abs(df_frames.iloc[idx]["relative_timestamp"] - gps_time) > abs(df_frames.iloc[idx - 1]["relative_timestamp"] - gps_time):
                idx -= 1

        frame_number = df_frames.iloc[idx]["frame"]
        matched_data.append([lat, lon, gps_time, video_creation_time, frame_number])

    # Create a DataFrame with the matched data
    df_matched = pd.DataFrame(matched_data, columns=["latitude", "longitude", "relative_timestamp", "video_creation_time", "frame_number"])

    # Remove duplicate latitude and longitude pairs
    df_matched = df_matched.drop_duplicates(subset=["latitude", "longitude"])

    return df_matched

def extract_and_save_frames(video_file, df_matched, output_folder, csv_output_path, update_progress):
    # Open the video file using OpenCV
    cap = cv2.VideoCapture(video_file)

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Initialize an empty list to store the frame image paths
    frame_image_paths = []

    # Initialize progress bar
    total_frames = len(df_matched)

    # Iterate through the matched frames
    for i, (_, row) in enumerate(tqdm(df_matched.iterrows(), total=total_frames, desc="Extracting and Saving Frames")):
        frame_number = row['frame_number']
        frame_location = os.path.join(output_folder, f"frame_{frame_number:04d}.jpg")

        # Set the video capture to the specific frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame
        ret, frame = cap.read()
        if ret:
            # Save the frame as an image
            cv2.imwrite(frame_location, frame)
        
        # Add the image path to the list
        frame_image_paths.append(frame_location)

        # Update progress bar
        update_progress((i + 1) / total_frames)

    # Release the video capture object
    cap.release()

    # Add the 'frame_image_path' column to df_matched
    df_matched['frame_image_path'] = frame_image_paths

    # Save the matched data to a CSV file
    df_matched.to_csv(csv_output_path, index=False)
    print(f"Frames have been saved to {output_folder}")
    print(f"CSV file has been saved to {csv_output_path}")

    # Return the updated df_matched
    return df_matched

# Function to convert an image file to base64 string for embedding in the popup
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string