import streamlit as st
import cv2
import numpy as np
import requests
import time

def main():
    # Set page config
    st.set_page_config(
        page_title="IP Webcam Viewer",
        page_icon="📱",
        layout="wide"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 200px;
            height: 50px;
        }
        .reportview-container {
            margin-top: -2em;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("📱 IP Webcam Viewer")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    default_ip = "http://192.168.10.25:8080"
    ip_address = st.sidebar.text_input("IP Webcam Address", value=default_ip)
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("Start Camera Feed", key="start"):
            video_placeholder = st.empty()
            stop = st.button("Stop Camera Feed", key="stop")
            
            while not stop:
                try:
                    # Get image from phone camera
                    img_resp = requests.get(f"{ip_address}/shot.jpg")
                    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
                    img = cv2.imdecode(img_arr, -1)
                    
                    if img is None:
                        st.error("Failed to decode image from camera")
                        break
                    
                    # Convert BGR to RGB for Streamlit display
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    # Display the image
                    video_placeholder.image(img_rgb, caption="Live Feed", use_column_width=True)
                    
                    # Add a small delay to control frame rate
                    time.sleep(0.1)
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {str(e)}")
                    break
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    break
            
            if stop:
                st.success("Camera feed stopped")
    
    with col2:
        st.markdown("""
        ### Instructions
        1. Install IP Webcam app
        2. Start server in app
        3. Enter IP address
        4. Click Start
        """)

if __name__ == '__main__':
    main()
