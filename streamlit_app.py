import streamlit as st
import cv2
import numpy as np
import requests
import time

def main():
    st.title("IP Camera Stream")
    
    # Video stream URL
    url = "http://192.168.10.38:8080"
    
    # Create placeholder for the video frame
    frame_placeholder = st.empty()
    
    # Add start/stop buttons
    col1, col2 = st.columns(2)
    start = col1.button("Start Stream")
    stop = col2.button("Stop Stream")

    if start:
        while not stop:
            try:
                # Get frame from IP camera
                resp = requests.get(f"{url}/shot.jpg")
                
                if resp.status_code == 200:
                    # Convert bytes to image
                    img_array = np.array(bytearray(resp.content), dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Display the frame
                    frame_placeholder.image(frame_rgb)
                    
                    # Add small delay
                    time.sleep(0.1)
                    
                else:
                    st.error(f"Failed to get frame: Status code {resp.status_code}")
                    break
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                break

if __name__ == "__main__":
    main()
