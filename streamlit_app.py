import streamlit as st
import cv2
import numpy as np
import requests
import time

def main():
    st.title("IP Camera Stream")
    
    # Create containers
    status = st.empty()
    video = st.empty()
    debug = st.empty()
    
    # Control buttons
    col1, col2 = st.columns(2)
    start = col1.button("Start Stream")
    stop = col2.button("Stop Stream")

    if start:
        status.info("Starting stream...")
        frame_count = 0
        start_time = time.time()
        
        while not stop:
            try:
                # Get single frame as JPEG
                response = requests.get("http://192.168.10.38:8080/video", timeout=5)
                
                if response.status_code == 200:
                    # Convert image from bytes to numpy array
                    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Display frame
                        video.image(frame_rgb, caption="Live Stream")
                        
                        # Update statistics
                        frame_count += 1
                        elapsed_time = time.time() - start_time
                        fps = frame_count / elapsed_time
                        
                        debug.info(f"""
                            Stream Info:
                            - Frames: {frame_count}
                            - Time: {elapsed_time:.1f}s
                            - FPS: {fps:.1f}
                        """)
                    else:
                        status.warning("Received empty frame")
                        
                else:
                    status.error(f"HTTP Error: {response.status_code}")
                    break
                
                # Small delay
                time.sleep(0.1)
                
            except Exception as e:
                status.error(f"Stream error: {str(e)}")
                break
        
        status.warning("Stream stopped")
        video.empty()
        debug.empty()

if __name__ == "__main__":
    main()
