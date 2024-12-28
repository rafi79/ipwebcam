import streamlit as st
import cv2
import numpy as np
import time

def main():
    st.title("IP Camera Stream")

    # Create status container
    status_container = st.empty()
    
    # Create frame container
    frame_container = st.empty()
    
    # Add a debug info section
    debug_container = st.empty()

    # Control buttons
    col1, col2 = st.columns(2)
    start = col1.button("Start Stream")
    stop = col2.button("Stop Stream")

    if start:
        # Initialize video capture
        status_container.info("Initializing camera connection...")
        
        # Use the URL that works in your browser
        video_url = "http://192.168.10.38:8080/video"
        cap = cv2.VideoCapture(video_url)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            status_container.error("Failed to open camera stream!")
            debug_container.error(f"Could not open: {video_url}")
            return

        status_container.success("Camera connected! Starting stream...")
        
        frame_count = 0
        start_time = time.time()

        while not stop:
            try:
                # Read frame
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Display the frame
                    frame_container.image(frame_rgb, caption="Live Feed")
                    
                    # Update stats
                    frame_count += 1
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time
                    
                    # Show debug info
                    debug_container.info(f"""
                        Stream Statistics:
                        - Frames received: {frame_count}
                        - Time elapsed: {elapsed_time:.2f} seconds
                        - FPS: {fps:.2f}
                        - Frame size: {frame_rgb.shape}
                    """)
                    
                    # Short delay
                    time.sleep(0.1)
                else:
                    status_container.warning("No frame received!")
                    time.sleep(1)  # Wait before retry
                    
            except Exception as e:
                status_container.error(f"Error reading frame: {str(e)}")
                break
        
        # Clean up
        cap.release()
        status_container.warning("Stream stopped")
        
        # Clear displays
        frame_container.empty()
        debug_container.empty()

if __name__ == "__main__":
    main()
