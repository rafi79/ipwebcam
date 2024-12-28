import streamlit as st
import cv2
import time
from datetime import datetime

def main():
    st.title('Using Mobile Camera with Streamlit')

    # Initialize video capture
    vid = cv2.VideoCapture('http://192.168.10.38:8080/video')

    # Create a placeholder for the video frame
    frame_window = st.image([])

    # Create take picture button
    take_picture_button = st.button('Take Picture')
    
    # Create stop button
    stop_button = st.button('Stop')

    try:
        while not stop_button:
            got_frame, frame = vid.read()
            if got_frame:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display the frame
                frame_window.image(frame_rgb)
                
                # Handle picture taking
                if take_picture_button:
                    # Save the picture
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"captured_image_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    st.success(f"Picture saved as {filename}")
                    break
                
                # Add a small delay
                time.sleep(0.1)
            else:
                st.error("Failed to get frame from camera")
                break

    except Exception as e:
        st.error(f"Error: {str(e)}")

    finally:
        # Release video capture
        vid.release()
        st.warning("Stream stopped")

if __name__ == "__main__":
    main()
