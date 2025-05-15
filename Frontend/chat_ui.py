import streamlit as st
import requests
from datetime import datetime
import uuid
import pytz 

def display_chat_interface():
    # Get persistent session ID from main app
    session_id = st.session_state.get("current_session", "default_session")
    CHAT_API_URL = st.session_state.get("API_URL", "https://ga14-btech-project.onrender.com")
    
    # Session-specific message storage
    message_key = f"messages_{session_id}"
    init_key = f"init_chat_{session_id}"
    
    # Initialize session state
    if message_key not in st.session_state:
        st.session_state[message_key] = []
    if init_key not in st.session_state:
        st.session_state[init_key] = True

    # Handle MRI analysis integration
    if "new_mri_analysis" in st.session_state:
        handle_mri_analysis(session_id, message_key, CHAT_API_URL)

    # Initialize chat from backend
    if st.session_state[init_key]:
        initialize_chat_session(session_id, message_key, init_key, CHAT_API_URL)

    # Display chat interface
    st.title("👨‍💻 Chat Here ")
    
    # Chat container with proper scrolling
    chat_container = st.container(height=500)
    with chat_container:
        display_chat_messages(message_key)

    # Message input without form
    user_input = st.chat_input(
        "Type your message...", 
        key=f"chat_input_{session_id}"
    )
    
    if user_input:
        process_user_message(
            user_input, 
            session_id, 
            message_key, 
            CHAT_API_URL, 
            chat_container
        )
        # Trigger rerun to update UI immediately
        st.rerun()

def handle_mri_analysis(session_id, message_key, api_url):
    try:
        analysis = st.session_state.new_mri_analysis
        prompt = (
            f"As a compassionate doctor speaking directly to the patient, start with a short Precautionary Note reminding the patient to stay calm and that further consultation is important.\n\n"
            f"Then, explain these MRI results in simple, patient-friendly language:\n"
            f"- Tumor Type: {analysis['class']}\n"
            f"- Confidence Level: {analysis['confidence']}%\n"
            f"- Status: {analysis['cancer_status']}\n\n"
            f"After explaining the results, provide a brief summary of possible treatment options tailored to the type and status, keeping the language reassuring and easy to understand.\n\n"
            f"Finally, end the message with a short disclaimer stating that these are AI-assisted interpretations and not a replacement for in-person consultation with a medical professional.\n\n"
            f"Make the entire message feel like it's coming from a caring and experienced doctor who wants to make the patient feel safe and well-informed."
        )

        with st.spinner("Generating MRI explanation..."):
            response = requests.post(
                f"{api_url}/generate_response",
                json={
                    "user_input": prompt,
                    "user": st.session_state.username,
                    "session_id": session_id,
                    "chat_history": st.session_state[message_key]
                }
            )
        
        bot_response = {
            "sender": "bot", 
            "text": response.json().get("response", "I've analyzed your MRI scan..."),
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id
        }
        
        st.session_state[message_key].append(bot_response)
        save_chat_to_backend(api_url, session_id, message_key)
        del st.session_state.new_mri_analysis

    except Exception as e:
        st.error(f"MRI analysis integration failed: {str(e)}")

def initialize_chat_session(session_id, message_key, init_key, api_url):
    try:
        response = requests.get(
            f"{api_url}/get_chat",
            params={
                "user": st.session_state.username,
                "session_id": session_id
            },
            timeout=5
        )
        
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            valid_messages = [msg for msg in messages if msg.get("session_id") == session_id]
            
            if valid_messages:
                st.session_state[message_key] = valid_messages
            else:
                st.session_state[message_key] = [{
                    "sender": "bot",
                    "text": "How can I assist you today?",
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_id": session_id
                }]
        
        st.session_state[init_key] = False

    except Exception as e:
        st.error(f"Initial chat load failed: {str(e)}")
        st.session_state[init_key] = False


def display_chat_messages(message_key):
    # Set up timezone converter
    ist = pytz.timezone('Asia/Kolkata')
    
    for msg in st.session_state[message_key]:
        try:
            # Convert stored UTC timestamp to IST
            utc_time = datetime.fromisoformat(msg.get('timestamp', ''))
            
            # Handle both naive and aware timestamps
            if utc_time.tzinfo is None:  # If timestamp is naive
                utc_time = pytz.utc.localize(utc_time)
            
            ist_time = utc_time.astimezone(ist)
            display_time = ist_time.strftime("%d %b %Y %H:%M IST")
        except Exception as e:
            display_time = "Time unavailable"
            print(f"Time conversion error: {str(e)}")

        # Display message with proper avatar and converted time
        with st.chat_message(name=msg["sender"], avatar="🤖" if msg["sender"] == "bot" else "👤"):
            st.markdown(msg["text"])
            st.caption(f"_{display_time}_")


def process_user_message(user_input, session_id, message_key, api_url, container):
    try:
        # Add user message
        user_msg = {
            "sender": "user",
            "text": user_input.strip(),
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id
        }
        st.session_state[message_key].append(user_msg)
        
        # Generate bot response
        with st.spinner("Analyzing your query..."):
            response = requests.post(
                f"{api_url}/generate_response",
                json={
                    "user_input": user_input,
                    "user": st.session_state.username,
                    "session_id": session_id,
                    "chat_history": st.session_state[message_key]
                }
            )
        
        # Add bot response
        bot_msg = {
            "sender": "bot",
            "text": response.json().get("response", "Could not generate response"),
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id
        }
        st.session_state[message_key].append(bot_msg)
        
        # Update display
        with container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
                st.caption(f"_{user_msg['timestamp']}_")
            with st.chat_message("bot", avatar="🤖"):
                st.markdown(bot_msg["text"])
                st.caption(f"_{bot_msg['timestamp']}_")
        
        save_chat_to_backend(api_url, session_id, message_key)

    except Exception as e:
        st.error(f"Message processing failed: {str(e)}")

def save_chat_to_backend(api_url, session_id, message_key):
    try:
        requests.post(
            f"{api_url}/save_chat",
            json={
                "user": st.session_state.username,
                "session_id": session_id,
                "messages": st.session_state[message_key]
            },
            timeout=1
        )
    except Exception:
        pass