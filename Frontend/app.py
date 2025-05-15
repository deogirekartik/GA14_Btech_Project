import streamlit as st
import requests
from chat_ui import display_chat_interface
from chat_history import chat_history_page
from image_upload import display_image_upload
from mri_results import mri_results_page  # Import the MRI results page
from uuid import uuid4
import uuid
from datetime import datetime
import pytz  

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
#API_URL = "https://b-tech-project.onrender.com"
API_URL ="http://127.0.0.1:5000"

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
            st.rerun()
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
            st.rerun()
        else:
            try:
                error_message = response.json().get("message", "Signup failed")
            except ValueError:
                error_message = "Invalid server response. Please try again."
            st.error(error_message)

# Load Chat History
def load_chat_history(username):
    response = requests.get(f"{API_URL}/get_chat_history", params={"user": username})  # Fixed endpoint
    if response.status_code == 200:
        st.session_state.chat_history = response.json().get("chat_history", [])
    else:
        st.session_state.chat_history = []


from datetime import datetime
import pytz  # Make sure to install: pip install pytz

def view_mri_results(username: str):
    try:
        response = requests.get(
            f"{API_URL}/get_mri_results",
            params={"user": username},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        mri_results = data.get("mri_results", [])
        
        st.header(f"🧠 MRI Analysis History ({len(mri_results)} scans)")
        
        if not mri_results:
            st.info("No MRI analyses found in your account")
            return

        # Timezone setup
        utc_zone = pytz.utc
        ist_zone = pytz.timezone('Asia/Kolkata')

        for idx, result in enumerate(mri_results, 1):
            with st.container():
                timestamp_str = result.get("timestamp", "")
                try:
                    # Convert UTC timestamp to IST
                    naive_utc = datetime.fromisoformat(timestamp_str)
                    aware_utc = utc_zone.localize(naive_utc)
                    ist_time = aware_utc.astimezone(ist_zone)
                    formatted_time = ist_time.strftime("%d %b %Y · %H:%M IST")
                except Exception as e:
                    formatted_time = "Date unknown"
                    print(f"Time conversion error: {str(e)}")
                
                with st.expander(f"{formatted_time} · {result.get('image_name', 'Unnamed scan')}"):
                    col1, col2 = st.columns(2)
                    analysis = result.get("analysis", {})
                    
                    with col1:
                        st.markdown(f"**🧠 Prediction**  \n{analysis.get('class', 'N/A')}")
                        st.markdown(f"**📈 Confidence**  \n{analysis.get('confidence', 'N/A')}%")
                    
                    with col2:
                        status = analysis.get('cancer_status', 'N/A')
                        status_color = "#ef4444" if status == "Cancerous" else "#22c55e"
                        st.markdown(
                            f"**🩺 Status**  \n"
                            f"<span style='color:{status_color}'>◉ {status}</span>", 
                            unsafe_allow_html=True
                        )
                    
                    st.divider()
                    st.subheader("Recommended Specialists", anchor=False)
                    doctors = result.get('recommended_doctors', [])
                    
                    if doctors:
                        for doc in doctors:
                            st.markdown(f"· {doc}")
                    else:
                        st.markdown("_No specialist recommendations available_")
                    
                    st.divider()
                    st.caption(f"Original image: {result.get('image_name', 'Unnamed scan')}")

    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")

    except requests.exceptions.RequestException as e:
        st.error(f"""
        **❗ Connection Error**  
        Failed to retrieve MRI results:  
        `{str(e)}`
        """)
    except ValueError as e:
        st.error(f"""
        **❗ Data Error**  
        Invalid response format:  
        `{str(e)}`
        """)
    except Exception as e:
        st.error(f"""
        **❗ Unexpected Error**  
        {str(e)}
        """)


def main():
    # Initial session state setup
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.session_state.chat_history = []

    # Show auth pages if not logged in
    if not st.session_state.authenticated:
        auth_page = st.sidebar.selectbox("Select", ["Login", "Signup"])
        if auth_page == "Login":
            show_login_page()
        else:
            show_signup_page()
        return

    # Main UI after login
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    
    # Add new chat button before radio
    if st.sidebar.button("🆕 Start New Chat"):
        if "current_session" in st.session_state:
            del st.session_state.current_session
        st.rerun()

    # Updated radio options
    page = st.sidebar.radio("Go to", ["Current Chat", "Chat History", "MRI Results", "Logout"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='background-color: #ffd2d2; padding: 10px; border-radius: 5px; margin-top: 20px;'>
        ⚠️ **Important Notice**  
        This system provides preliminary assessments only.  
        Always consult a qualified neuro-oncologist for medical decisions.         
    </div>
    """, unsafe_allow_html=True)

    # Page routing
    if page == "Current Chat":
        handle_current_chat_page()
    elif page == "Chat History":
        st.title("💬 Previous Chats")
        chat_history_page()
    elif page == "MRI Results":
        st.title("📊 MRI Analysis Results")
        view_mri_results(st.session_state.username)
    elif page == "Logout":
        handle_logout()

def handle_current_chat_page():
    st.title("🧠 Smart Neuro-Oncology Assistant")
    
    # Session initialization
    if "current_session" not in st.session_state:
        new_session_id = str(uuid.uuid4())
        st.session_state.current_session = new_session_id
        try:
            requests.post(
                f"{API_URL}/create_chat_session",
                json={
                    "user": st.session_state.username,
                    "session_id": new_session_id
                },
                timeout=2
            )
        except Exception as e:
            st.toast("⚠️ Session tracking limited to this browser", icon="⚠️")

    # Persistent components
    with st.container(key="persistent_upload"):
        try:
            display_image_upload()
        except Exception as e:
            st.error(f"Image upload error: {str(e)}")

    with st.container(key=f"chat_{st.session_state.current_session}"):
        try:
            display_chat_interface()
        except Exception as e:
            st.error(f"Chat initialization failed: {str(e)}")

def handle_logout():
    keys_to_clear = ['current_session', 'messages', 'new_chat_triggered', 'chat_history']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.authenticated = False
    st.rerun()

if __name__ == "__main__":
    main()