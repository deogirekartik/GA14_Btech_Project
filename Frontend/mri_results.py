import streamlit as st
import requests

# Backend API URL
BASE_URL = "https://ga14-btech-project.onrender.com"
# BASE_URL = "http://127.0.0.1:5000"

def fetch_mri_results(username):
    """Fetch MRI results from the backend for a given user."""
    response = requests.get(f"{BASE_URL}/get_mri_results", params={"user": username})
    if response.status_code == 200:
        return response.json().get("mri_results", [])
    return []

def mri_results_page():
    """MRI Results Page in Streamlit."""
    st.title("🧠 MRI Analysis Results")

    # User input for username
    username = st.text_input("🔹 Enter your username to view MRI results")

    if st.button("🔍 Fetch MRI Results"):
        if username:
            results = fetch_mri_results(username)
            
            if results:
                st.subheader("📂 Your MRI Analysis History")

                # Display each result in an expandable section
                for result in results:
                    with st.expander(f"📄 Image: {result.get('image_name', 'Unknown')}"):
                        st.write(f"**Analysis:** {result.get('analysis', {})}")
                        st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")
                        st.write("---")
            else:
                st.warning("⚠️ No MRI results found for this user.")
        else:
            st.error("❌ Please enter a username.")

# Run the MRI Results Page
if __name__ == "__main__":
    mri_results_page()
