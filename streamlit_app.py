import streamlit as st
import cv2
import imutils
from imutils.video import VideoStream
from PIL import Image
import numpy as np

# Function to fetch the frame from the IP webcam
def get_frame(camera_url):
    vs = VideoStream(src=camera_url).start()
    while True:
        frame = vs.read()
        if frame is not None:
            frame = imutils.resize(frame, width=600)
            yield frame
        else:
            st.error("Failed to capture frame from the IP webcam.")
            break

# Streamlit app
def main():
    st.title("IP Webcam Viewer")

    # Input for the IP webcam URL
    camera_url = st.text_input("Enter the IP webcam URL", "http://192.168.10.38:8080/video")

    if st.button("Start"):
        stframe = st.empty()
        try:
            for frame in get_frame(camera_url):
                # Convert the frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert the frame to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                # Display the frame in Streamlit
                stframe.image(pil_image)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
