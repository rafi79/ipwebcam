import streamlit as st
import cv2
import numpy as np
import requests
import time
from urllib.parse import urljoin

def main():
    st.title("IP Webcam Viewer")

    # Camera URL input
    base_url = st.text_input(
        "IP Webcam URL",
        value="http://192.168.10.25:8080",
        help="Enter the URL from your IP Webcam app"
    )

    # Test connection first
    if st.button("Test Connection"):
        try:
            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                st.success("Successfully connected to IP Webcam!")
            else:
                st.error(f"Connection failed with status code: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

    # Stream settings
    st.sidebar.header("Stream Settings")
    quality = st.sidebar.selectbox(
        "Quality",
        ["HD", "SD", "Low"],
        index=1
    )

    # Create placeholders
    frame_placeholder = st.empty()
    status_placeholder = st.sidebar.empty()

    # Control buttons
    start = st.sidebar.button("Start Stream")
    stop = st.sidebar.button("Stop Stream")

    if start:
        st.sidebar.info("Starting stream...")
        
        # Initialize session state for streaming
        streaming = True
        frames_received = 0
        start_time = time.time()

        while streaming and not stop:
            try:
                # Construct URL for video frame
                frame_url = urljoin(base_url, "shot.jpg")
                
                # Get frame with increased timeout
                response = requests.get(frame_url, timeout=10)
                
                if response.status_code == 200:
                    # Convert image from bytes to numpy array
                    image_bytes = np.frombuffer(response.content, dtype=np.uint8)
                    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        # Convert BGR to RGB
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Apply quality settings
                        if quality == "Low":
                            frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
                        elif quality == "HD":
                            frame = cv2.resize(frame, None, fx=1.5, fy=1.5)
                        
                        # Display frame
                        frame_placeholder.image(frame, channels="RGB", use_column_width=True)
                        
                        # Update statistics
                        frames_received += 1
                        elapsed_time = time.time() - start_time
                        fps = frames_received / elapsed_time
                        
                        status_placeholder.markdown(f"""
                            ### Stream Stats
                            - Time: {elapsed_time:.1f}s
                            - Frames: {frames_received}
                            - FPS: {fps:.1f}
                        """)
                    else:
                        st.warning("Received empty frame")
                        
                else:
                    st.error(f"Failed to get frame: HTTP {response.status_code}")
                    break
                
                # Add small delay to control frame rate
                time.sleep(0.1)
                
            except requests.exceptions.Timeout:
                st.warning("Frame capture timed out. Retrying...")
                time.sleep(1)  # Wait before retry
                continue
                
            except requests.exceptions.ConnectionError:
                st.error("Connection lost. Please check your network connection.")
                break
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                break

        st.sidebar.warning("Stream stopped")

if __name__ == "__main__":
    main()
