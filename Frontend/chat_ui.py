import streamlit as st
import requests

# Backend API endpoint
CHAT_API_URL = "http://127.0.0.1:5000/generate_response"

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"sender": "bot", "text": "Welcome! How can I assist you with brain cancer detection today?"}
    ]

def display_chat_interface():
    st.title("🧠 Brain Cancer Detection Chatbot")

    # Display chat messages
    for message in st.session_state.messages:
        if message["sender"] == "bot":
            st.markdown(f"**🤖 Bot:** {message['text']}")
        else:
            st.markdown(f"**👤 You:** {message['text']}")

    # User input
    user_input = st.text_input("Type your message...", key="user_input")

    if st.button("Send"):
        if user_input:
            st.session_state.messages.append({"sender": "user", "text": user_input})
            
            # Send user input to chatbot API
            try:
                payload = {
                    "user_input": user_input,
                    "chat_history": [{"sender": msg["sender"], "text": msg["text"]} for msg in st.session_state.messages]
}

                response = requests.post(CHAT_API_URL, json=payload)

                if response.status_code == 200:
                    try:
                        bot_response = response.json().get("response", "Sorry, I didn't understand that.")
                    except ValueError:
                        bot_response = "Invalid response from server."
                else:
                    bot_response = f"Chatbot Error: {response.status_code}"

                # Append bot response to chat
                st.session_state.messages.append({"sender": "bot", "text": bot_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")

            # Refresh UI
            st.experimental_rerun()

# Run the chat interface
display_chat_interface()
