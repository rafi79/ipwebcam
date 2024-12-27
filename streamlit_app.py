import streamlit as st
import cv2
import numpy as np
import requests
import time
from datetime import datetime
import os

class RemoteWebcamViewer:
    def __init__(self):
        st.set_page_config(
            page_title="Remote IP Webcam Viewer",
            page_icon="🌐",
            layout="wide"
        )
        
        # Custom CSS
        st.markdown("""
            <style>
            .stButton > button {
                width: 200px;
            }
            .connection-info {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        self.frame_placeholder = None
        self.status_placeholder = None
        self.is_running = False

    def test_connection(self, url, timeout=5):
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200, None
        except requests.exceptions.ConnectTimeout:
            return False, "Connection timed out. If using external IP, make sure you're not on the same network."
        except requests.exceptions.ConnectionError:
            return False, "Connection failed. Check IP address and port forwarding settings."
        except Exception as e:
            return False, str(e)

    def capture_frame(self, url):
        try:
            response = requests.get(f"{url}/shot.jpg", timeout=5)
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            st.error(f"Frame capture error: {e}")
            return None

    def run(self):
        st.title("🌐 Remote IP Webcam Viewer")

        # Connection setup
        st.markdown("""
        <div class="connection-info">
        <h3>Connection Setup</h3>
        <p>Choose connection type and enter appropriate IP address:</p>
        </div>
        """, unsafe_allow_html=True)

        # Connection type selector
        conn_type = st.radio(
            "Connection Type",
            ["Local Network", "Remote Access"],
            help="Select 'Local Network' if phone is on same WiFi, 'Remote Access' for external IP"
        )

        # IP input based on connection type
        if conn_type == "Local Network":
            default_ip = "http://192.168.10.25:8080"
            help_text = "Enter local IP address from IP Webcam app"
        else:
            default_ip = "http://your-external-ip:8080"
            help_text = "Enter your router's external IP and forwarded port"

        camera_url = st.text_input("Camera URL", value=default_ip, help=help_text)

        # Main layout
        col1, col2 = st.columns([3, 1])

        with col1:
            # Main viewing area
            self.frame_placeholder = st.empty()
            self.status_placeholder = st.empty()

        with col2:
            st.sidebar.header("Controls")
            
            # Connection test
            if st.sidebar.button("Test Connection"):
                success, error_msg = self.test_connection(camera_url)
                if success:
                    st.sidebar.success("✅ Connected successfully!")
                else:
                    st.sidebar.error(f"❌ Connection failed: {error_msg}")

            # Quality and FPS controls
            quality = st.sidebar.select_slider(
                "Stream Quality",
                options=["Low", "Medium", "High"],
                value="Medium"
            )
            
            fps = st.sidebar.slider("Frame Rate", 1, 30, 10)

            # Stream controls
            start = st.sidebar.button("Start Stream")
            stop = st.sidebar.button("Stop Stream")

            # Stats display
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Statistics")
            stats_placeholder = st.sidebar.empty()

        # Streaming loop
        if start:
            self.is_running = True
            frames_count = 0
            start_time = time.time()

            while self.is_running and not stop:
                frame = self.capture_frame(camera_url)
                
                if frame is not None:
                    # Apply quality settings
                    height, width = frame.shape[:2]
                    if quality == "Low":
                        frame = cv2.resize(frame, (width//2, height//2))
                    elif quality == "High":
                        frame = cv2.resize(frame, (width*2, height*2))

                    # Display frame
                    self.frame_placeholder.image(frame, channels="RGB", use_column_width=True)

                    # Update stats
                    frames_count += 1
                    elapsed_time = time.time() - start_time
                    current_fps = frames_count / elapsed_time

                    stats_placeholder.markdown(f"""
                        - Runtime: {elapsed_time:.1f}s
                        - Frames: {frames_count}
                        - FPS: {current_fps:.1f}
                    """)

                    time.sleep(1/fps)
                else:
                    st.error("Failed to capture frame")
                    break

            self.is_running = False
            st.warning("Stream stopped")

if __name__ == "__main__":
    viewer = RemoteWebcamViewer()
    viewer.run()
