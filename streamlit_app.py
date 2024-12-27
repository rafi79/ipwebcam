import streamlit as st
import cv2
import numpy as np
import requests
import time
from datetime import datetime
import os

class IPWebcamViewer:
    def __init__(self):
        # Initialize Streamlit page configuration
        st.set_page_config(
            page_title="IP Webcam Viewer",
            page_icon="📸",
            layout="wide"
        )
        
        # Add custom CSS
        st.markdown("""
            <style>
            .stButton > button {
                width: 200px;
            }
            .reportview-container {
                margin-top: -2em;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize variables
        self.default_url = "http://192.168.10.25:8080"
        self.frame_placeholder = None
        self.status_placeholder = None
        self.is_running = False
        self.current_frame = None

    def test_connection(self, url):
        """Test connection to IP Webcam"""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def capture_frame(self, url):
        """Capture a single frame from IP Webcam"""
        try:
            response = requests.get(f"{url}/shot.jpg", timeout=5)
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            st.error(f"Frame capture error: {e}")
            return None

    def save_snapshot(self, frame):
        """Save a snapshot of the current frame"""
        if frame is not None:
            try:
                os.makedirs('snapshots', exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"snapshots/snapshot_{timestamp}.jpg"
                cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                return filepath
            except Exception as e:
                st.error(f"Error saving snapshot: {e}")
                return None
        return None

    def run(self):
        """Main application loop"""
        st.title("📸 IP Webcam Viewer")

        # Create main layout
        col1, col2 = st.columns([3, 1])

        with col1:
            # Main viewing area
            self.frame_placeholder = st.empty()
            self.status_placeholder = st.empty()

        with col2:
            # Control panel
            st.sidebar.header("Camera Controls")
            
            # Camera URL input
            camera_url = st.sidebar.text_input(
                "Camera URL",
                value=self.default_url,
                help="Enter the IP Webcam URL"
            )

            # Connection test
            if st.sidebar.button("Test Connection"):
                if self.test_connection(camera_url):
                    st.sidebar.success("✅ Connected to camera!")
                else:
                    st.sidebar.error("❌ Connection failed")

            # Quality control
            quality = st.sidebar.select_slider(
                "Stream Quality",
                options=["Low", "Medium", "High"],
                value="Medium"
            )

            # Frame rate control
            fps = st.sidebar.slider("Frame Rate (FPS)", 1, 30, 10)

            # Control buttons
            col1, col2 = st.sidebar.columns(2)
            start = col1.button("Start Stream")
            stop = col2.button("Stop Stream")
            
            # Snapshot button
            if st.sidebar.button("Take Snapshot"):
                if self.current_frame is not None:
                    filepath = self.save_snapshot(self.current_frame)
                    if filepath:
                        st.sidebar.success(f"Saved: {filepath}")

            # Statistics display
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Statistics")
            stats_placeholder = st.sidebar.empty()

        # Main streaming loop
        if start:
            self.is_running = True
            frames_count = 0
            start_time = time.time()

            while self.is_running and not stop:
                # Capture frame
                frame = self.capture_frame(camera_url)
                
                if frame is not None:
                    # Apply quality settings
                    height, width = frame.shape[:2]
                    if quality == "Low":
                        frame = cv2.resize(frame, (width//2, height//2))
                    elif quality == "High":
                        frame = cv2.resize(frame, (width*2, height*2))

                    # Store current frame
                    self.current_frame = frame
                    
                    # Display frame
                    self.frame_placeholder.image(
                        frame,
                        channels="RGB",
                        use_column_width=True
                    )

                    # Update statistics
                    frames_count += 1
                    elapsed_time = time.time() - start_time
                    current_fps = frames_count / elapsed_time

                    stats_placeholder.markdown(f"""
                        - Runtime: {elapsed_time:.1f}s
                        - Frames: {frames_count}
                        - FPS: {current_fps:.1f}
                    """)

                    # Control frame rate
                    time.sleep(1/fps)
                else:
                    st.error("Failed to capture frame")
                    break

            self.is_running = False
            st.warning("Stream stopped")

if __name__ == "__main__":
    viewer = IPWebcamViewer()
    viewer.run()
