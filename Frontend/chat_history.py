import streamlit as st
import requests
from datetime import datetime
import pytz


# Backend API URL
BASE_URL = "http://127.0.0.1:5000"
#BASE_URL = "https://b-tech-project.onrender.com"
def fetch_chat_history(username):
    """Fetch chat history from the backend for a logged-in user."""
    response = requests.get(f"{BASE_URL}/get_chat_history", params={"user": username})
    
    print(f"DEBUG: Fetching chat history for {username} - Status Code: {response.status_code}")
    print(f"DEBUG: API Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        return data.get("chat_history", [])  # Ensure we get the correct key from JSON
    
    return []




def chat_history_page():
    """Chat History Page in Streamlit with Session Support."""
    ist = pytz.timezone('Asia/Kolkata')  # Timezone setup
    
    if "username" not in st.session_state or not st.session_state.username:
        st.error("❌ You must be logged in to view chat history.")
        return

    username = st.session_state.username
    st.write(f"**Logged in as:** `{username}`")

    if "viewing_session" not in st.session_state:
        st.session_state.viewing_session = None

    try:
        with st.spinner("Loading your chat sessions..."):
            response = requests.get(
                f"{BASE_URL}/chat_sessions",
                params={"user": username},
                timeout=5
            )

        if response.status_code != 200:
            st.error(f"❌ Server error: {response.text}")
            return

        sessions = response.json().get("sessions", [])

        if not sessions:
            st.warning("🌟 No chat sessions found. Start a new chat to begin!")
            return

        st.subheader("📂 Your Chat Sessions")

        for session in sessions:
            session_id = session.get("session_id", "unknown_session")
            try:
                # Handle both UTC-aware and naive timestamps
                raw_time = session.get("created_at", "")
                if 'Z' in raw_time:  # UTC-aware format
                    utc_time = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
                else:  # Assume UTC if no timezone
                    utc_time = datetime.fromisoformat(raw_time)
                
                utc_time = pytz.utc.localize(utc_time)  # Make timezone-aware
                ist_time = utc_time.astimezone(ist)
                created_at = ist_time.strftime("%d %b %Y %H:%M IST")
            except Exception as e:
                created_at = "Unknown time"
                print(f"Time error: {str(e)}")
            
            messages = session.get("messages", [])
            preview_text = "No messages yet"
            if messages:
                first_message = messages[0] if len(messages) > 0 else {}
                preview_text = first_message.get("text", "Empty conversation")[:50]
            
            with st.expander(f"🗓️ {created_at} - {preview_text}..."):
                col1, col2 = st.columns([0.7, 0.3])
                
                with col1:
                    st.caption(f"Session ID: `{session_id}`")
                    st.write(f"**Started:** {created_at}")
                
                with col2:
                    if st.button("Open Session", key=f"open_{session_id}"):
                        st.session_state.current_session = session_id
                        st.session_state.page = "New Chat"
                        st.rerun()

                if st.button("View Full Conversation", key=f"view_{session_id}"):
                    st.session_state.viewing_session = session_id

                if st.session_state.viewing_session == session_id:
                    try:
                        with st.spinner("Loading conversation..."):
                            msg_response = requests.get(
                                f"{BASE_URL}/get_chat",
                                params={
                                    "user": username.strip(),
                                    "session_id": session_id.strip()
                                },
                                timeout=10
                            )
                        
                        if msg_response.status_code == 200:
                            messages = msg_response.json().get("messages", [])
                            
                            if messages:
                                st.subheader("Full Conversation History")
                                with st.container(height=400):
                                    for msg in messages:
                                        try:
                                            # Convert message timestamp to IST
                                            raw_msg_time = msg.get("timestamp", "")
                                            if 'Z' in raw_msg_time:
                                                msg_utc = datetime.fromisoformat(raw_msg_time.replace('Z', '+00:00'))
                                            else:
                                                msg_utc = datetime.fromisoformat(raw_msg_time)
                                            msg_utc = pytz.utc.localize(msg_utc)
                                            msg_ist = msg_utc.astimezone(ist)
                                            timestamp = msg_ist.strftime("%d %b %Y %H:%M IST")
                                        except:
                                            timestamp = "Unknown time"
                                        
                                        sender = "🧑 You" if msg.get("sender") == "user" else "🤖 Bot"
                                        text = msg.get("text", "Message content unavailable")
                                        
                                        col1, col2 = st.columns([0.1, 0.9])
                                        with col1:
                                            st.markdown(f"**{sender}**")
                                        with col2:
                                            st.markdown(f"{text}")
                                            st.caption(f"🕒 {timestamp}")
                                        st.divider()
                                
                                if st.button("Close Conversation", key=f"close_{session_id}"):
                                    st.session_state.viewing_session = None
                                    st.rerun()
                            else:
                                st.info("📭 This conversation is empty")
                                
                        elif msg_response.status_code == 400:
                            st.error("🔍 Invalid request parameters")
                        elif msg_response.status_code == 404:
                            st.error("🗃️ Conversation not found")
                        else:
                            st.error(f"⚠️ Server error ({msg_response.status_code})")
                            
                    except requests.exceptions.Timeout:
                        st.error("⏳ Request timed out")
                    except requests.exceptions.ConnectionError:
                        st.error("🌐 Connection failed")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")