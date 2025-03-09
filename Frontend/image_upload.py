import streamlit as st
import requests
from PIL import Image
from datetime import datetime

BACKEND_URL = "https://b-tech-project.onrender.com/predict"
SAVE_MRI_RESULT_URL = "https://b-tech-project.onrender.com/save_mri_result"  # Endpoint for saving MRI results

def display_image_upload():
    st.header("Upload MRI Image")
    uploaded_file = st.file_uploader("Choose an MRI image...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded MRI Image", use_column_width=True)
        st.success("Image uploaded successfully!")

        if st.button("Analyze"):
            st.info("Analyzing the image...")

            try:
                # Send image to backend API
                files = {"image": uploaded_file.getvalue()}
                response = requests.post(BACKEND_URL, files=files)

                if response.status_code == 200:
                    result = response.json()

                    # Check if there is an error message in the result
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        # Display prediction results if no error
                        st.success(f"Prediction: {result.get('class', 'N/A')}")
                        st.write(f"Confidence: {result.get('confidence', 'N/A')}%")
                        st.write(f"Cancer Status: {result.get('cancer_status', 'N/A')}")

                        # Save the MRI results to the backend
                        save_data = {
                            "user": st.session_state.username,  # Make sure the user is authenticated
                            "image_name": uploaded_file.name,
                            "analysis": {
                                "class": result.get("class", "N/A"),
                                "confidence": result.get("confidence", "N/A"),
                                "cancer_status": result.get("cancer_status", "N/A")
                            },
                            "comparison": {"timestamp": datetime.now().isoformat()}  # Optional: Add comparison data if needed
                        }

                        # Send MRI result data to backend
                        save_response = requests.post(SAVE_MRI_RESULT_URL, json=save_data)

                        if save_response.status_code == 200:
                            st.success("MRI results saved successfully!")
                        else:
                            st.error(f"Error saving MRI results: {save_response.text}")
                
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
