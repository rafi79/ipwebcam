import streamlit as st
import cv2
import numpy as np

# Replace this with your IP webcam URL
ip_camera_url = "http://192.168.10.38:8080/video"

st.title("IP Webcam Stream in Streamlit")

# Function to fetch and display frames
def get_frame_from_ip_camera():
    cap = cv2.VideoCapture(ip_camera_url)  # Open the IP camera stream

    if not cap.isOpened():
        st.error("Error: Unable to access the video stream. Please check the URL or your network.")
        return None

    ret, frame = cap.read()
    cap.release()

    if ret:
        # Convert the frame from BGR (OpenCV default) to RGB (Streamlit compatible)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
    else:
        st.error("Error: Unable to fetch video frame. Stream might be down.")
        return None

# Display the video feed
st.text("Displaying the live feed from the IP webcam...")
frame = get_frame_from_ip_camera()

if frame is not None:
    st.image(frame, caption="Live Webcam Feed", use_column_width=True)
