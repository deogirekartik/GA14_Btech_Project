import streamlit as st
import requests
from chat_ui import display_chat_interface
from chat_history import chat_history_page
from image_upload import display_image_upload
from mri_results import mri_results_page  # Import the MRI results page

# Set the page configuration (must be the first Streamlit command)
#st.set_page_config(page_title="Smart Neuro-Oncology Assistant", layout="wide")

# Apply custom styles
st.markdown('<link href="styles.css" rel="stylesheet">', unsafe_allow_html=True)

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialize messages as an empty list
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Initialize chat history

# Backend API URL
API_URL = "http://127.0.0.1:5000"

# Authentication Pages
def show_login_page():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            load_chat_history(username)
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Please try again.")

def show_signup_page():
    st.title("📝 Signup")
    username = st.text_input("Create a Username")
    password = st.text_input("Create a Password", type="password")
    if st.button("Signup"):
        response = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
        if response.status_code == 200:
            st.success("Account created successfully! Please login.")
            st.experimental_rerun()
        else:
            try:
                error_message = response.json().get("message", "Signup failed")
            except ValueError:
                error_message = "Invalid server response. Please try again."
            st.error(error_message)

# Load Chat History
def load_chat_history(username):
    response = requests.get(f"{API_URL}/chat_history/{username}")
    if response.status_code == 200:
        st.session_state.chat_history = response.json().get("chat_history", [])
    else:
        st.session_state.chat_history = []

def view_mri_results(username: str):
    response = requests.get(f"{API_URL}/get_mri_results", params={"user": username})
    
    # Debugging: Print the API response
    print(f"API Response: {response.status_code}, {response.json()}")

    if response.status_code == 200:
        mri_results = response.json().get("mri_results", [])
        st.header("🧠 Your MRI Analysis Results")

        if not mri_results:
            st.warning("⚠️ No MRI results found.")
            return

        for result in mri_results:
            with st.expander(f"📄 Image: {result.get('image_name', 'Unknown')}"):
                analysis = result.get("analysis", {})  # Ensure analysis exists
                st.write(f"**Prediction:** {analysis.get('class', 'N/A')}")
                st.write(f"**Confidence:** {analysis.get('confidence', 'N/A')}%")
                st.write(f"**Cancer Status:** {analysis.get('cancer_status', 'N/A')}")
                st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")
                st.markdown("---")
    else:
        st.error(f"Failed to load MRI results. Response: {response.status_code}, {response.text}")

# Main Page
if not st.session_state.authenticated:
    auth_option = st.sidebar.selectbox("Select", ["Login", "Signup"])
    if auth_option == "Login":
        show_login_page()
    else:
        show_signup_page()
else:
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["New Chat", "Chat History", "MRI Results", "Logout"])

    if page == "New Chat":
        st.title("🧠 Smart Neuro-Oncology Assistant")
        display_image_upload()
        display_chat_interface()
    elif page == "Chat History":
        st.title("💬 Previous Chats")
        chat_history_page()
    elif page == "MRI Results":
        st.title("📊 MRI Analysis Results")
        view_mri_results(st.session_state.username)
    elif page == "Logout":
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.chat_history = []
        st.session_state.messages = []  # Clear messages on logout
        st.success("Logged out successfully!")
        st.experimental_rerun()
