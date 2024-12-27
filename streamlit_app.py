import streamlit as st
import cv2
import numpy as np
import requests
import time
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="IP Webcam Viewer",
    page_icon="📸",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        margin-bottom: 10px;
    }
    .reportview-container {
        margin-top: -2em;
    }
    .css-1v0mbdj.etr89bj1 {
        margin-top: -60px;
    }
    </style>
""", unsafe_allow_html=True)

class IPWebcamViewer:
    def __init__(self):
        self.default_ip = "http://192.168.10.25:8080"
        self.frame_placeholder = None
        self.status_placeholder = None
        self.current_frame = None
        self.is_running = False

    def check_camera_connection(self, ip_address):
        try:
            response = requests.get(f"{ip_address}/status.json", timeout=5)
            return response.status_code == 200
        except:
            return False

    def capture_frame(self, ip_address):
        try:
            response = requests.get(f"{ip_address}/shot.jpg", timeout=5)
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            st.error(f"Error capturing frame: {e}")
        return None

    def save_snapshot(self, frame):
        if frame is not None:
            # Create 'snapshots' directory if it doesn't exist
            os.makedirs('snapshots', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshots/snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            return filename
        return None

    def main(self):
        st.title("📸 IP Webcam Viewer")

        # Create two columns
        col1, col2 = st.columns([3, 1])

        with col1:
            # Main viewing area
            self.frame_placeholder = st.empty()
            self.status_placeholder = st.empty()

        with col2:
            # Controls sidebar
            st.sidebar.header("Camera Controls")
            
            # IP address input
            ip_address = st.sidebar.text_input(
                "Camera IP Address",
                value=self.default_ip,
                help="Enter the IP address shown in your IP Webcam app"
            )

            # Connection check
            if st.sidebar.button("Test Connection"):
                if self.check_camera_connection(ip_address):
                    st.sidebar.success("✅ Camera connected!")
                else:
                    st.sidebar.error("❌ Cannot connect to camera")

            # Stream quality
            quality = st.sidebar.select_slider(
                "Stream Quality",
                options=["Low", "Medium", "High"],
                value="Medium"
            )

            # Frame rate
            fps = st.sidebar.slider("Frame Rate (FPS)", 1, 30, 10)

            # Control buttons
            start_button = st.sidebar.button("▶️ Start Stream")
            stop_button = st.sidebar.button("⏹️ Stop Stream")
            snapshot_button = st.sidebar.button("📸 Take Snapshot")

            # Display stream stats
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Stream Statistics")
            stats_placeholder = st.sidebar.empty()

        # Main streaming logic
        if start_button:
            self.is_running = True
            frames_count = 0
            start_time = time.time()

            while self.is_running and not stop_button:
                # Capture frame
                frame = self.capture_frame(ip_address)
                
                if frame is not None:
                    # Resize based on quality setting
                    height, width = frame.shape[:2]
                    if quality == "Low":
                        frame = cv2.resize(frame, (width//2, height//2))
                    elif quality == "High":
                        frame = cv2.resize(frame, (width*2, height*2))

                    # Update display
                    self.current_frame = frame
                    self.frame_placeholder.image(frame, channels="RGB", use_column_width=True)
                    
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
            st.sidebar.warning("Stream stopped")

        # Handle snapshot
        if snapshot_button and self.current_frame is not None:
            filename = self.save_snapshot(self.current_frame)
            if filename:
                st.sidebar.success(f"Snapshot saved: {filename}")
            else:
                st.sidebar.error("Failed to save snapshot")

if __name__ == "__main__":
    viewer = IPWebcamViewer()
    viewer.main()
