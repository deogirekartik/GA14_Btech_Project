# from pymongo import MongoClient
# import certifi

# try:
#     client = MongoClient("mongodb+srv://deogire:%245kinhand@cluster0.6ohtl.mongodb.net/brain_cancer_chatbot?retryWrites=true&w=majority&authSource=admin&appName=Cluster0",
#                      tlsCAFile=certifi.where())
#     db = client["brain_cancer_chatbot"]
#     print("✅ Connection successful!")
#     print("Collections:", db.list_collection_names())
# except Exception as e:
#     print("❌ Connection failed:", e)


# #app.py
# import streamlit as st
# from chat_ui import display_chat_interface
# from chat_history import display_chat_history
# from image_upload import display_image_upload
# import requests

# # Set up the page
# st.set_page_config(page_title="Brain Cancer Detection Chatbot", layout="wide")
# st.markdown('<link href="styles.css" rel="stylesheet">', unsafe_allow_html=True)

# # Session State Initialization
# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False
# if "username" not in st.session_state:
#     st.session_state.username = ""
# if "messages" not in st.session_state:
#     st.session_state.messages = []  # Initialize messages as an empty list
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []  # Initialize chat history

# # Backend API URL
# API_URL = "http://127.0.0.1:5000"

# # Authentication Pages
# def show_login_page():
#     st.title("🔐 Login")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     if st.button("Login"):
#         response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
#         if response.status_code == 200:
#             st.session_state.authenticated = True
#             st.session_state.username = username
#             st.success("Logged in successfully!")
#             load_chat_history(username)
#             st.experimental_rerun()
#         else:
#             st.error("Invalid credentials. Please try again.")

# def show_signup_page():
#     st.title("📝 Signup")
#     username = st.text_input("Create a Username")
#     password = st.text_input("Create a Password", type="password")
#     if st.button("Signup"):
#         response = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
#         if response.status_code == 200:
#             st.success("Account created successfully! Please login.")
#             st.experimental_rerun()
#         else:
#             try:
#                 error_message = response.json().get("message", "Signup failed")
#             except ValueError:
#                 error_message = "Invalid server response. Please try again."
#             st.error(error_message)

# # Load Chat History
# def load_chat_history(username):
#     response = requests.get(f"{API_URL}/chat_history/{username}")
#     if response.status_code == 200:
#         st.session_state.chat_history = response.json().get("chat_history", [])
#     else:
#         st.session_state.chat_history = []

# # View MRI Results
# def view_mri_results(username: str):
#     response = requests.get(f"{API_URL}/mri_results/{username}")
#     if response.status_code == 200:
#         mri_results = response.json()
#         st.header("Your MRI Results")
#         for result in mri_results:
#             st.write(f"Image: {result['image_name']}")
#             st.write(f"Prediction: {result['analysis']['class']}")
#             st.write(f"Confidence: {result['analysis']['confidence']}%")
#             st.write(f"Cancer Status: {result['analysis']['cancer_status']}")
#             st.write(f"Timestamp: {result['timestamp']}")
#             st.markdown("---")
#     else:
#         st.error("Failed to load MRI results")


# # Main Page
# if not st.session_state.authenticated:
#     auth_option = st.sidebar.selectbox("Select", ["Login", "Signup"])
#     if auth_option == "Login":
#         show_login_page()
#     else:
#         show_signup_page()
# else:
#     st.sidebar.title(f"Welcome, {st.session_state.username}!")
#     st.sidebar.title("Navigation")
#     page = st.sidebar.radio("Go to", ["New Chat", "Chat History", "MRI Results", "Logout"])

#     if page == "New Chat":
#         st.title("🧠 Brain Cancer Detection Chatbot")
#         display_image_upload()
#         display_chat_interface()
#     elif page == "Chat History":
#         st.title("💬 Previous Chats")
#         display_chat_history()
#     elif page == "MRI Results":
#         st.title("📊 MRI Analysis Results")
#         view_mri_results(st.session_state.username)
#     elif page == "Logout":
#         st.session_state.authenticated = False
#         st.session_state.username = ""
#         st.session_state.chat_history = []
#         st.session_state.messages = []  # Clear messages on logout
#         st.success("Logged out successfully!")
#         st.experimental_rerun()

# #chat_history.py
# import streamlit as st
# import requests

# API_URL = "http://localhost:5000/get_chat_history"

# def display_chat_history():
#     st.header("Chat History")
#     user = st.text_input("Enter user ID to fetch chat history")
#     if st.button("Fetch History"):
#         if user:
#             response = requests.get(API_URL, params={"user": user})
#             if response.status_code == 200:
#                 chat_history = response.json()
#                 for chat in chat_history:
#                     with st.expander(chat.get("timestamp", "Unknown")):
#                         st.write(chat.get("message", "No message"))
# #image_upload.py
# import streamlit as st
# import requests
# from PIL import Image
# from datetime import datetime

# BACKEND_URL = "http://127.0.0.1:5000/predict"
# SAVE_MRI_RESULT_URL = "http://127.0.0.1:5000/save_mri_result"  # Endpoint for saving MRI results

# def display_image_upload():
#     st.header("Upload MRI Image")
#     uploaded_file = st.file_uploader("Choose an MRI image...", type=["png", "jpg", "jpeg"])
    
#     if uploaded_file:
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded MRI Image", use_column_width=True)
#         st.success("Image uploaded successfully!")

#         if st.button("Analyze"):
#             st.info("Analyzing the image...")

#             try:
#                 # Send image to backend API
#                 files = {"image": uploaded_file.getvalue()}
#                 response = requests.post(BACKEND_URL, files=files)

#                 if response.status_code == 200:
#                     result = response.json()

#                     # Check if there is an error message in the result
#                     if "error" in result:
#                         st.error(f"Error: {result['error']}")
#                     else:
#                         # Display prediction results if no error
#                         st.success(f"Prediction: {result.get('class', 'N/A')}")
#                         st.write(f"Confidence: {result.get('confidence', 'N/A')}%")
#                         st.write(f"Cancer Status: {result.get('cancer_status', 'N/A')}")

#                         # Save the MRI results to the backend
#                         save_data = {
#                             "user": st.session_state.username,  # Make sure the user is authenticated
#                             "image_name": uploaded_file.name,
#                             "analysis": {
#                                 "class": result.get("class", "N/A"),
#                                 "confidence": result.get("confidence", "N/A"),
#                                 "cancer_status": result.get("cancer_status", "N/A")
#                             },
#                             "comparison": {"timestamp": datetime.now().isoformat()}  # Optional: Add comparison data if needed
#                         }

#                         # Send MRI result data to backend
#                         save_response = requests.post(SAVE_MRI_RESULT_URL, json=save_data)

#                         if save_response.status_code == 200:
#                             st.success("MRI results saved successfully!")
#                         else:
#                             st.error(f"Error saving MRI results: {save_response.text}")
                
#                 else:
#                     st.error(f"Error {response.status_code}: {response.text}")
            
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")

# #chat_ui.py
# import streamlit as st
# import requests
# from PIL import Image
# from datetime import datetime

# BACKEND_URL = "http://127.0.0.1:5000/predict"
# SAVE_MRI_RESULT_URL = "http://127.0.0.1:5000/save_mri_result"  # Endpoint for saving MRI results

# def display_image_upload():
#     st.header("Upload MRI Image")
#     uploaded_file = st.file_uploader("Choose an MRI image...", type=["png", "jpg", "jpeg"])
    
#     if uploaded_file:
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded MRI Image", use_column_width=True)
#         st.success("Image uploaded successfully!")

#         if st.button("Analyze"):
#             st.info("Analyzing the image...")

#             try:
#                 # Send image to backend API
#                 files = {"image": uploaded_file.getvalue()}
#                 response = requests.post(BACKEND_URL, files=files)

#                 if response.status_code == 200:
#                     result = response.json()

#                     # Check if there is an error message in the result
#                     if "error" in result:
#                         st.error(f"Error: {result['error']}")
#                     else:
#                         # Display prediction results if no error
#                         st.success(f"Prediction: {result.get('class', 'N/A')}")
#                         st.write(f"Confidence: {result.get('confidence', 'N/A')}%")
#                         st.write(f"Cancer Status: {result.get('cancer_status', 'N/A')}")

#                         # Save the MRI results to the backend
#                         save_data = {
#                             "user": st.session_state.username,  # Make sure the user is authenticated
#                             "image_name": uploaded_file.name,
#                             "analysis": {
#                                 "class": result.get("class", "N/A"),
#                                 "confidence": result.get("confidence", "N/A"),
#                                 "cancer_status": result.get("cancer_status", "N/A")
#                             },
#                             "comparison": {"timestamp": datetime.now().isoformat()}  # Optional: Add comparison data if needed
#                         }

#                         # Send MRI result data to backend
#                         save_response = requests.post(SAVE_MRI_RESULT_URL, json=save_data)

#                         if save_response.status_code == 200:
#                             st.success("MRI results saved successfully!")
#                         else:
#                             st.error(f"Error saving MRI results: {save_response.text}")
                
#                 else:
#                     st.error(f"Error {response.status_code}: {response.text}")
            
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")


# #api.py
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from datetime import datetime

# from model_prediction import predict_image
# from database import save_user, verify_user, save_chat, get_chat_history, save_mri_result
# from openai import generate_openai_response

# app = Flask(__name__)
# CORS(app)

# # 1. 🧠 **Image Prediction Endpoint**
# @app.route('/predict', methods=['POST'])
# def predict():
#     """Endpoint to predict tumor type and cancer status from an image."""
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image provided'}), 400

#     image_file = request.files['image']
#     result = predict_image(image_file)
#     return jsonify(result)

# # Save MRI Analysis Result Endpoint
# @app.route('/save_mri_result', methods=['POST'])
# def save_mri_result_endpoint():
#     data = request.json
#     user = data.get("user")
#     image_name = data.get("image_name")
#     analysis = data.get("analysis")
#     comparison = data.get("comparison")

#     if not user or not analysis:
#         return jsonify({'error': 'Invalid input'}), 400

#     # Save MRI result data to the database
#     save_mri_result(user, image_name, analysis, comparison)
#     return jsonify({'message': 'MRI results saved successfully'})



# # 2. 💾 **Save Chat History Endpoint**
# @app.route('/save_chat', methods=['POST'])
# def save_chat_endpoint():
#     data = request.json
#     user = data.get("user")
#     message = data.get("message")
#     timestamp = datetime.now().isoformat()

#     if not user or not message:
#         return jsonify({'error': 'Invalid input'}), 400

#     save_chat(user, message, timestamp)
#     return jsonify({'message': 'Chat history saved successfully'})

# # 3. 📜 **Retrieve Chat History Endpoint**
# @app.route('/get_chat_history', methods=['GET'])
# def get_chat_history_endpoint():
#     user = request.args.get("user")
#     if user:
#         history = get_chat_history(user)
#         return jsonify(history), 200
#     return jsonify({'error': 'User not specified'}), 400

# # 4. 🤖 **Generate Chatbot Response via OpenAI API**
# @app.route('/generate_response', methods=['POST'])
# def generate_response():
#     data = request.json
#     user_message = data.get("message")
#     user = data.get("user")

#     if not user_message or not user:
#         return jsonify({'error': 'Invalid input'}), 400

#     try:
#         response = generate_openai_response(user_message)
#         timestamp = datetime.now().isoformat()

#         save_chat(user, user_message, timestamp)
#         save_chat("bot", response, timestamp)

#         return jsonify({"response": response}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Signup Endpoint
# @app.route("/signup", methods=["POST"])
# def signup():
#     data = request.json
#     username = data.get("username")
#     password = data.get("password")
#     if not username or not password:
#         return jsonify({"status": "error", "message": "Username and password are required"}), 400
#     if save_user(username, password):
#         return jsonify({"status": "success", "message": "User created successfully"}), 200
#     else:
#         return jsonify({"status": "error", "message": "User already exists"}), 400

# # Login Endpoint
# @app.route("/login", methods=["POST"])
# def login():
#     data = request.json
#     username = data.get("username")
#     password = data.get("password")
#     if verify_user(username, password):
#         return jsonify({"status": "success", "message": "Login successful"}), 200
#     else:
#         return jsonify({"status": "error", "message": "Invalid username or password"}), 401

# # Get Chat History
# @app.route("/chat_history/<username>", methods=["GET"])
# def get_chat_history_route(username):
#     chat_history = get_chat_history(username)
#     return jsonify({"status": "success", "chat_history": chat_history}), 200

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

# # database.py
# from pymongo import MongoClient
# from werkzeug.security import generate_password_hash, check_password_hash
# import ssl
# import certifi
# from pymongo import MongoClient

# client = MongoClient("mongodb+srv://deogire:%245kinhand@cluster0.6ohtl.mongodb.net/brain_cancer_chatbot?retryWrites=true&w=majority&authSource=admin&appName=Cluster0",
#                      tlsCAFile=certifi.where())

# db = client["brain_cancer_chatbot"]

# # Collection references
# users_collection = db["users"]  # For user authentication and profiles
# chats_collection = db["chats"]  # For chat history
# mri_results_collection = db["mri_results"]  # For MRI analysis results


# # Save User (Signup)
# def save_user(username: str, password: str) -> bool:
#     if users_collection.find_one({"username": username}):
#         return False  # User already exists
#     hashed_password = generate_password_hash(password)
#     users_collection.insert_one({"username": username, "password": hashed_password})
#     return True

# # Verify User (Login)
# def verify_user(username: str, password: str) -> bool:
#     user = users_collection.find_one({"username": username})
#     if user and check_password_hash(user["password"], password):
#         return True
#     return False

# # Save Chat History
# def save_chat(user: str, message: str, timestamp: str):
#     chat_data = {
#         "user": user,
#         "message": message,
#         "timestamp": timestamp
#     }
#     chats_collection.insert_one(chat_data)

# # Get Chat History
# def get_chat_history(user: str):
#     return list(chats_collection.find({"user": user}).sort("timestamp", 1))

# # Save MRI Analysis Result
# def save_mri_result(user: str, image_name: str, analysis: dict, comparison: dict):
#     mri_data = {
#         "user": user,
#         "image_name": image_name,
#         "analysis": analysis,
#         "timestamp": comparison.get("timestamp")
#     }
#     mri_results_collection.insert_one(mri_data)


# # Get MRI Analysis Results
# def get_mri_results(user: str):
#     return list(mri_results_collection.find({"user": user}).sort("timestamp", 1))

# #model_prediction.py
# import numpy as np
# from tensorflow import keras
# from PIL import Image, UnidentifiedImageError
# import io

# # Load the saved model (replace with your actual model path)
# model = keras.models.load_model('/Users/deogirekartik/Vscode/The_Final_Project/model/the_xception_model.keras')

# # Class labels for tumor types
# CLASS_LABELS = ["No Tumor", "Glioma", "Meningioma", "Pituitary", "Metastasis"]

# def predict_image(image_file):
#     """Predict the tumor type and cancer status from an uploaded image."""
#     try:
#         # Ensure the image is opened correctly and resized
#         image = Image.open(image_file).convert("RGB").resize((299, 299))
#         img_array = np.array(image) / 255.0
#         img_array = np.expand_dims(img_array, axis=0)

#         # Perform the prediction
#         predictions = model.predict(img_array)
#         predicted_class = np.argmax(predictions, axis=1)[0]
#         confidence = np.max(predictions)

#         # Determine cancer status
#         cancer_status = "Cancerous" if predicted_class > 0 else "Non-Cancerous"

#         return {
#             "class": CLASS_LABELS[predicted_class],
#             "confidence": round(float(confidence) * 100, 2),
#             "cancer_status": cancer_status
#         }

#     except UnidentifiedImageError:
#         return {"error": "Uploaded file is not a valid image."}

#     except Exception as e:
#         # Catch other exceptions and return an error message
#         return {"error": f"Prediction failed: {str(e)}"}

# #openai.py
# import openai
# import os

# # Set your OpenAI API key here
# openai.api_key = os.getenv("OPENAI_API_KEY")

# def generate_openai_response(user_input, chat_history=None):
#     """Generate a response from OpenAI based on user input and chat history."""
#     messages = [{"role": "system", "content": "You are a helpful medical assistant."}]
    
#     if chat_history:
#         for msg in chat_history:
#             messages.append({"role": "user" if msg["sender"] == "user" else "assistant", "content": msg["text"]})
    
#     messages.append({"role": "user", "content": user_input})

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             max_tokens=150
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         print(f"OpenAI API Error: {e}")
#         return "Sorry, I am having trouble responding right now."

import requests

# API URL (Change if necessary)
CHAT_API_URL = "http://127.0.0.1:5000/generate_response"

# Sample user input
test_input = "Hi, how does brain cancer affect the body?"

# Payload for API request
payload = {
    "user_input": test_input,
    "chat_history": []  # Empty history for testing
}

try:
    # Send request
    response = requests.post(CHAT_API_URL, json=payload)

    # Check response
    if response.status_code == 200:
        print("✅ Chatbot Response:", response.json().get("response"))
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"⚠️ Exception occurred: {e}")
