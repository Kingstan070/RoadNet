# Road Condition Monitoring with Geographic Visualization

## DEVELOPMENT

## 📌 Project Overview
This project aims to monitor road conditions using machine learning models, GPS data, and video recordings. The system processes video footage and GPS tracks, extracts frames, maps them to GPS coordinates, and applies machine learning models to classify road surfaces and detect potholes. The results are then stored and visualized through an interactive dashboard.

---

## 🚀 Features
- **Video Processing**: Extract frames and metadata from uploaded videos.
- **GPS Integration**: Match GPS data to video frames for geospatial mapping.
- **Machine Learning Models**:
  - TensorFlow-based classification model for paved/unpaved road detection.
  - PyTorch-based detection model for pothole identification.
- **Database Storage**: Uses SQLite with SQLAlchemy for structured data management.
- **Streamlit Dashboard**: Displays real-time road condition analysis with filtering options.
- **Time-Based Analysis**: Allows historical data retrieval and time-based filtering.

---

## ♻️ Processing Workflow
### 1️⃣ Video Preprocessing
- Extract metadata (creation time, frame rate, duration)
- Extract frames at predefined intervals
- Save frames to storage

### 2️⃣ GPS Data Handling
- Filter GPS points within video duration
- Match frames to GPS using timestamp offset
- Extract and save relevant GPS data

### 3️⃣ Machine Learning Inference
- Classification Model predicts paved/unpaved roads
- Detection Model identifies potholes
- Store results with timestamps and locations

### 4️⃣ Data Storage & Retrieval
- Store processed data in a structured format
- Ensure latest data is always available
- Query results dynamically for analysis and visualization

---

## ♻️ Business Logic for Route Processing
### 📍 Route-Based Data Handling
- A route is defined as a sequence of GPS points with the same video creation time.
- Routes are stored uniquely, ensuring duplicates are not reprocessed.
- If two routes intersect, the newest data is prioritized.
- Union of intersecting routes ensures continuity in road monitoring.
- Timestamps are compared to maintain recent data accuracy.
- While extracting for display, the most recent route data is shown.
- Redundant or outdated data is ignored to optimize performance.
- This ensures a seamless and up-to-date representation of road conditions.

### 🗄️ Database Storage & Querying
- Each extracted frame is stored with GPS coordinates, timestamp, and processed results.
- Images are converted to Base64 and stored in the database.
- Queries retrieve the latest available road conditions and pothole detections.
- Time-slider filtering allows historical analysis of road conditions.

---

## ♻️ User Workflow
### 👤 User Flow
1. **💾 Upload Video & GPX**
   - User uploads 🎥 & GPX.
   - System extracts metadata & 🌍 points.
   - Frames are extracted from 🎥.
2. **⚙️ Processing & Analysis**
   - Frames mapped to GPS.
   - ML models classify & detect.
   - Data stored in 📚.
3. **📊 Dashboard & Reports**
   - User views results.
   - Reports provide insights.
   - ⏳ Slider filters by time.

---

## 🗄️ Database Model (SQLAlchemy & SQLite)
The system uses **SQLite** as the database, with **SQLAlchemy** for ORM-based interaction.

### 📌 Key Tables
1. **RoadConditions**
   - Stores the combined results of road classification and pothole detection.

### RoadConditions Table Schema
| id  | latitude | longitude | timestamp           | frame_path    | road_type | road_condition | pothole_data |
|-----|----------|-----------|---------------------|---------------|-----------|----------------|--------------|
| 1   | 9.71469  | 76.68943  | 2025-01-29 17:17:22 | frame_0000.jpg| Asphalt   | Good           | []           |

---

## 📊 Dashboard & Reports
### Dashboard
- A single map is plotted with the newest points or portions of the route.
- Older parts of the route are displayed if newer data is not available.
- Each point is plotted with an approximation distance set.

### Reports
- Users can select different routes and view their details.
- Routes are identified using timestamps, as a single route can have different data points with the same timestamps.

### Time Slider
- Allows users to filter and view data based on time.
- Provides historical analysis of road conditions.
