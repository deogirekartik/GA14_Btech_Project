import google.generativeai as genai
import os

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please export it or set it in the script.")
    genai.configure(api_key=api_key)

def generate_gemini_response(user_input, chat_history=None):
    """Generate a response from Gemini based on user input and chat history."""
    configure_gemini()
    
    messages = [{"role": "user", "content": user_input}]
    if chat_history:
        for msg in chat_history:
            role = "user" if msg["sender"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["text"]})
    
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content([m["content"] for m in messages])
        return response.text.strip() if response else "Sorry, I couldn't generate a response."
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Sorry, I am having trouble responding right now."
