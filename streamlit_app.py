import streamlit as st
import av
import cv2
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import numpy as np
import requests

class VideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        # Initialize without opening camera immediately
        self.ip_camera = None
        self.camera_url = None

    def setup_camera(self, url):
        """Setup camera with given URL"""
        try:
            # Close existing camera if any
            if self.ip_camera is not None:
                self.ip_camera.release()
            
            # Try to verify camera access first
            response = requests.get(f"{url}/status", timeout=5)
            if response.status_code == 200:
                # Open video capture
                self.camera_url = f"{url}/video"
                self.ip_camera = cv2.VideoCapture(self.camera_url)
                
                if not self.ip_camera.isOpened():
                    st.error(f"Failed to open camera at {self.camera_url}")
                    return False
                return True
            else:
                st.error("Camera not accessible")
                return False
        except Exception as e:
            st.error(f"Error connecting to camera: {str(e)}")
            return False

    def recv(self, frame):
        if self.ip_camera is None:
            # Try to set up camera if not initialized
            if not self.setup_camera("http://192.168.10.38:8080/video"):
                return None

        try:
            ret, frame = self.ip_camera.read()
            if ret:
                return av.VideoFrame.from_ndarray(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                )
        except Exception as e:
            st.error(f"Error reading frame: {str(e)}")
        return None

    def __del__(self):
        if self.ip_camera is not None:
            self.ip_camera.release()

def check_camera_access(url):
    """Test camera access before starting stream"""
    try:
        # First try main URL
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        
        # Try video URL
        video_response = requests.get(f"{url}/video", timeout=5)
        if video_response.status_code == 200:
            return True
            
        return False
    except Exception:
        return False

def main():
    st.title("IP Webcam Viewer")
    
    # Add descriptive text
    st.markdown("""
    ### Setup Instructions:
    1. Open IP Webcam app on your phone
    2. Start server
    3. Note the IP address (e.g., http://192.168.10.25:8080)
    4. Make sure phone and computer are on same network
    """)

    # Camera URL input
    camera_url = st.text_input(
        "IP Camera URL",
        value="http://192.168.10.38:8080/video",
        help="Enter the URL shown in your IP Webcam app"
    )

    # Test connection button
    if st.button("Test Connection"):
        if check_camera_access(camera_url):
            st.success("✅ Successfully connected to camera!")
        else:
            st.error("❌ Cannot connect to camera. Please check the URL and network connection.")
            st.info("Make sure you can access the camera URL in your web browser")
            return

    # WebRTC Configuration
    rtc_config = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    # Create WebRTC streamer
    webrtc_ctx = webrtc_streamer(
        key="ip-camera",
        video_processor_factory=VideoProcessor,
        rtc_configuration=rtc_config,
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )

    # Show status and controls
    if webrtc_ctx.video_processor:
        st.success("Stream started")
        
        # Add snapshot button
        if st.button("Take Snapshot"):
            try:
                if webrtc_ctx.video_receiver:
                    frame = webrtc_ctx.video_receiver.get_frame()
                    if frame is not None:
                        img = frame.to_ndarray(format="bgr24")
                        cv2.imwrite("snapshot.jpg", img)
                        st.success("Snapshot saved as snapshot.jpg")
                    else:
                        st.warning("No frame available")
            except Exception as e:
                st.error(f"Failed to take snapshot: {str(e)}")

    # Add troubleshooting help
    with st.expander("Troubleshooting"):
        st.markdown("""
        If you're having issues:
        1. Check if you can access the camera URL in your browser
        2. Verify both devices are on same network
        3. Try stopping and restarting the stream
        4. Make sure no other app is using the camera
        """)

if __name__ == "__main__":
    main()
