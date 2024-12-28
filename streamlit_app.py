import streamlit as st
import cv2
import numpy as np
import time

def main():
    st.title("IP Webcam Stream")
    
    # Input for IP address
    ip_address = st.text_input(
        "IP Webcam URL",
        value="http://192.168.10.38:8080",
        help="Enter the URL shown in your IP Webcam app"
    )

    # Create placeholders for video and status
    frame_placeholder = st.empty()
    status_placeholder = st.empty()

    # Control buttons in columns
    col1, col2 = st.columns(2)
    start_button = col1.button('Start Camera')
    stop_button = col2.button('Stop Camera')

    if start_button:
        # Construct the exact video URL that IP Webcam uses
        video_url = f"{ip_address}/videofeed"
        status_placeholder.info(f"Connecting to: {video_url}")

        try:
            # Open video capture
            cap = cv2.VideoCapture(video_url)
            
            if not cap.isOpened():
                # Try alternative URL format
                video_url2 = f"{ip_address}/video"
                status_placeholder.info(f"Retrying with: {video_url2}")
                cap = cv2.VideoCapture(video_url2)
                
                if not cap.isOpened():
                    status_placeholder.error("Could not connect to camera stream")
                    return

            status_placeholder.success("Connected to camera!")

            while not stop_button:
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Display the frame
                    frame_placeholder.image(frame_rgb)
                    time.sleep(0.1)  # Small delay
                else:
                    status_placeholder.warning("No frame received")
                    break

            cap.release()
            status_placeholder.warning("Stream stopped")
            
        except Exception as e:
            status_placeholder.error(f"Error: {str(e)}")
            
if __name__ == "__main__":
    main()
