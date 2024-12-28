import streamlit as st
import cv2
import numpy as np
import time

def main():
    st.title("IP Webcam Stream")
    
    # URL input for IP webcam
    url = st.text_input(
        "IP Webcam URL",
        value="http://192.168.10.38:8080/video",
        help="Enter the URL from your IP Webcam app"
    )
    
    # Create video capture object
    if st.button("Start Stream"):
        try:
            # Construct video URL - this is the direct video feed from IP Webcam
            video_url = f"{url}/video"
            st.info(f"Connecting to: {video_url}")
            
            # Create OpenCV video capture object
            cap = cv2.VideoCapture(video_url)
            
            if not cap.isOpened():
                st.error("Could not open video stream")
                return
                
            # Create a placeholder for the video frame
            frame_placeholder = st.empty()
            
            # Add stop button
            stop = st.button("Stop Stream")
            
            while not stop:
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Display the frame
                    frame_placeholder.image(frame)
                    # Add a small delay
                    time.sleep(0.1)
                else:
                    st.error("Error reading frame")
                    break
                    
            cap.release()
            st.warning("Stream stopped")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
