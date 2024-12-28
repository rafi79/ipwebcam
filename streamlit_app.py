import streamlit as st
import cv2
import time
import requests
from datetime import datetime

def check_camera_connection(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.title('Mobile Camera Stream')

    # Input for IP address
    camera_ip = st.text_input(
        "Enter IP Webcam Address",
        value="http://192.168.10.38:8080/video",
        help="Enter the complete URL shown in your IP Webcam app"
    )

    # Test connection button
    if st.button("Test Connection"):
        if check_camera_connection(camera_ip):
            st.success("✅ Successfully connected to camera!")
        else:
            st.error("❌ Could not connect to camera. Please check the IP address and make sure the IP Webcam app is running.")
            return

    # Create buttons
    col1, col2, col3 = st.columns(3)
    start_button = col1.button('Start Stream')
    take_picture_button = col2.button('Take Picture')
    stop_button = col3.button('Stop')

    # Create a placeholder for the video frame
    frame_window = st.empty()

    if start_button:
        try:
            # Initialize video capture with the provided IP
            video_url = f"{camera_ip}/video"
            st.info(f"Connecting to: {video_url}")
            
            vid = cv2.VideoCapture(video_url)
            
            if not vid.isOpened():
                st.error("Failed to open video stream")
                return

            st.success("Stream started!")

            while not stop_button:
                got_frame, frame = vid.read()
                
                if got_frame:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Display the frame
                    frame_window.image(frame_rgb)
                    
                    # Handle picture taking
                    if take_picture_button:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"captured_image_{timestamp}.jpg"
                        cv2.imwrite(filename, frame)
                        st.success(f"Picture saved as {filename}")
                        break
                    
                    # Small delay to prevent high CPU usage
                    time.sleep(0.1)
                else:
                    st.warning("No frame received")
                    break

        except Exception as e:
            st.error(f"Error: {str(e)}")

        finally:
            try:
                vid.release()
            except:
                pass
            st.warning("Stream stopped")

if __name__ == "__main__":
    main()
