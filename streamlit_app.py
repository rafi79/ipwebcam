import streamlit as st
import cv2
import numpy as np
import requests
import time

def main():
    st.title("IP Webcam Feed")
    
    # Camera address input
    ip_address = "http://192.168.10.25:8080"  # Your IP address
    st.write(f"Connecting to: {ip_address}")
    
    # Add test button to check connection
    if st.button("Test Camera Connection"):
        try:
            # Try to get a single image
            response = requests.get(f"{ip_address}/shot.jpg")
            if response.status_code == 200:
                st.success("Successfully connected to camera!")
            else:
                st.error(f"Could not connect to camera. Status code: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
    
    # Create placeholder for video feed
    frame_placeholder = st.empty()
    
    # Control buttons
    start = st.button("Start")
    stop = st.button("Stop")
    
    if start:
        st.write("Starting camera feed...")
        while not stop:
            try:
                # Get frame from IP webcam
                resp = requests.get(f"{ip_address}/shot.jpg")
                
                # Convert to image
                image_bytes = np.asarray(bytearray(resp.content), dtype=np.uint8)
                frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display the frame
                frame_placeholder.image(frame_rgb, channels="RGB")
                
                # Short delay
                time.sleep(0.1)
                
            except Exception as e:
                st.error(f"Error getting camera feed: {str(e)}")
                break

if __name__ == "__main__":
    main()
