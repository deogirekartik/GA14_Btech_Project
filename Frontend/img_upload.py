import streamlit as st
from PIL import Image

# def display_image_upload():
#     st.header("Upload MRI Image")
#     uploaded_file = st.file_uploader("Choose an MRI image...", type=["png", "jpg", "jpeg"])
#     if uploaded_file:
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded MRI Image", use_column_width=True)
#         st.success("Image uploaded successfully!")
# img_upload.py

def display_image_upload():
    uploaded_file = st.file_uploader("Upload an MRI Image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded MRI Image", use_column_width=True)
        return uploaded_file
    return None
