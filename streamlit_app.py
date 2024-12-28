import streamlit as st
import av
import cv2
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import numpy as np

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.ip_camera = cv2.VideoCapture("http://192.168.10.25:8080/video")

    def recv(self, frame):
        ret, frame = self.ip_camera.read()
        if ret:
            return av.VideoFrame.from_ndarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            return None

    def __del__(self):
        if self.ip_camera is not None:
            self.ip_camera.release()

def main():
    st.title("IP Webcam WebRTC Stream")
    
    # Camera URL input
    camera_url = st.text_input(
        "IP Camera URL",
        value="http://192.168.10.38:8080/video",
        help="Enter the complete URL from your IP Webcam app"
    )

    # WebRTC Configuration
    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    # Create the WebRTC streamer
    webrtc_ctx = webrtc_streamer(
        key="ip-camera",
        video_processor_factory=VideoProcessor,
        rtc_configuration=rtc_configuration,
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )

    # Add some instructions
    st.markdown("""
    ### Instructions:
    1. Make sure IP Webcam app is running on your phone
    2. Enter the correct camera URL above
    3. Click 'Start' to begin streaming
    
    ### Troubleshooting:
    - Verify you can access the camera URL in your browser
    - Make sure both devices are on the same network
    - Check if the IP Webcam app shows 'Server running'
    """)

    # Display status
    if webrtc_ctx.video_processor:
        st.success("Stream is active")
    
    # Add a snapshot button
    if webrtc_ctx.video_receiver and st.button("Take Snapshot"):
        try:
            frame = webrtc_ctx.video_receiver.get_frame()
            if frame is not None:
                # Save the snapshot
                img = frame.to_ndarray(format="bgr24")
                cv2.imwrite("snapshot.jpg", img)
                st.success("Snapshot saved as snapshot.jpg")
        except Exception as e:
            st.error(f"Failed to take snapshot: {str(e)}")

if __name__ == "__main__":
    main()
