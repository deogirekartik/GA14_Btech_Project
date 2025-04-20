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
