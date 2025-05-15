# import streamlit as st
# import requests
# from PIL import Image
# from datetime import datetime

# # BACKEND_URL = "https://b-tech-project.onrender.com/predict"
# # SAVE_MRI_RESULT_URL = "https://b-tech-project.onrender.com/save_mri_result"  # Endpoint for saving MRI results

import streamlit as st
import requests
from PIL import Image
from datetime import datetime
from doctors import DOCTORS
from chat_ui import display_chat_interface
from uuid import uuid4
import uuid
import json
import numpy as np

BACKEND_URL = "http://127.0.0.1:5000/predict"
SAVE_MRI_RESULT_URL = "http://127.0.0.1:5000/save_mri_result"



def display_doctors(recommendation_type):
    """Display doctors in a grid layout"""
    doctors = DOCTORS.get(recommendation_type, [])
    cols = st.columns(3)
    for idx, doctor in enumerate(doctors[:3]):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style='padding:15px; border-radius:10px; background:#f0f2f6; margin:10px;'>
                <h4>{doctor['photo']} {doctor['name']}</h4>
                <p><b>Specialization:</b> {doctor['specialization']}</p>
                <p><b>Hospital:</b> {doctor['hospital']}</p>
                <p><b>Experience:</b> {doctor['experience']}</p>
                <p><b>Contact:</b> <code>{doctor['contact']}</code></p>
            </div>
            """, unsafe_allow_html=True)
    return doctors  # Return doctors list for saving

def display_image_upload():
    # Initialize session state with session-specific keys
    session_id = st.session_state.get('current_session', "default_session")
    result_key = f'mri_results_{session_id}'
    
    def is_grayscale(img, threshold=0):
        """Check if image is grayscale (black and white) using RGB channel analysis."""
        if img.mode == 'L':
            return True
        if img.mode != 'RGB':
            img = img.convert('RGB')
        arr = np.array(img)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        diff_rg = np.abs(r - g)
        diff_rb = np.abs(r - b)
        return np.all(diff_rg <= threshold) and np.all(diff_rb <= threshold)

    if result_key not in st.session_state:
        st.session_state[result_key] = None

    st.header("Upload MRI Image")
    uploaded_file = st.file_uploader("Choose an MRI image...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded MRI Image", use_column_width=True)
        st.success("Image uploaded successfully!")

        if st.button("Analyze"):
            if not is_grayscale(image):
                st.error("This image is not a valid brain scan MRI. Please upload a grayscale MRI scan.")
            else:
                st.info("Analyzing the image...")
                try:
                    files = {"image": uploaded_file.getvalue()}
                    response = requests.post(BACKEND_URL, files=files)

                    if response.status_code == 200:
                        result = response.json()
                        st.session_state[result_key] = result
                        status = result.get('cancer_status', 'N/A')
                        
                        # Get recommended doctors and their names
                        recommendation_type = "cancerous" if status == "Cancerous" else "non_cancerous"
                        recommended_doctors = DOCTORS.get(recommendation_type, [])
                        doctor_names = [doc['name'] for doc in recommended_doctors]

                        # Save results to backend with doctor names
                        save_data = {
                            "user": st.session_state.username,
                            "image_name": uploaded_file.name,
                            "analysis": result,
                            "recommended_doctors": doctor_names,
                            "timestamp": datetime.now().isoformat()
                        }
                        requests.post(SAVE_MRI_RESULT_URL, json=save_data)
                        
                        # Trigger chat with session-specific analysis
                        st.session_state.new_mri_analysis = result

                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # Display results only for current session
    if st.session_state[result_key]:
        result = st.session_state[result_key]
        st.subheader("Analysis Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Prediction:**  \n{result.get('class', 'N/A')}")
        with col2:
            st.markdown(f"**Confidence:**  \n{result.get('confidence', 'N/A')}%")
        with col3:
            status = result.get('cancer_status', 'N/A')
            color = "#ff4b4b" if status == "Cancerous" else "#2ecc71"
            st.markdown(f"**Cancer Status:**  \n<span style='color:{color}'>{status}</span>", 
                       unsafe_allow_html=True)

        st.subheader("Recommended Specialists")
        if status == "Cancerous":
            display_doctors("cancerous")
        else:
            display_doctors("non_cancerous")
        
        if st.button("Clear Results", key=f"clear_{session_id}"):
            del st.session_state[result_key]
            del st.session_state.new_mri_analysis
            st.rerun()