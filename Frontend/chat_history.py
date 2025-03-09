import streamlit as st
import requests

# Backend API URL
BASE_URL = "http://127.0.0.1:5000"

def fetch_chat_history(username):
    """Fetch chat history from the backend for a logged-in user."""
    response = requests.get(f"{BASE_URL}/get_chat_history", params={"user": username})
    
    if response.status_code == 200:
        chat_data = response.json()  # This is a list, not a dictionary
        return chat_data  # Just return the list directly
    
    return []


def chat_history_page():
    """Chat History Page in Streamlit."""
    

    # Ensure user is logged in
    if "username" not in st.session_state or not st.session_state.username:
        st.error("❌ You must be logged in to view chat history.")
        return

    username = st.session_state.username  # Get logged-in username
    st.write(f"**Logged in as:** `{username}`")

    # Fetch chat history automatically on page load
    chat_history = fetch_chat_history(username)
    
    if chat_history:
        st.subheader("📜 Your Chat History")

        # Display messages
        for chat in chat_history:
            sender = "🧑 You" if chat["sender"] == "user" else "🤖 Bot"
            st.markdown(f"**{sender}:** {chat['message']}")
            st.write(f"🕒 {chat['timestamp']}")
            st.write("---")
    else:
        st.warning("⚠️ No chat history found.")

# Run the Chat History Page
if __name__ == "__main__":
    chat_history_page()
