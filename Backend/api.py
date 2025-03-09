from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

from model_prediction import predict_image
from database import save_user, verify_user, save_chat, get_chat_history, save_mri_result, get_mri_results
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

genai.configure(api_key="AIzaSyAR1iBqukVjljunUW1ZnkmPfXyvv4IGHc4")

# 1. 🧠 **Image Prediction Endpoint**
@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to predict tumor type and cancer status from an image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    result = predict_image(image_file)
    return jsonify(result)
#ss
@app.route('/save_mri_result', methods=['POST'])
def save_mri_result_endpoint():
    data = request.get_json()
    print("Received Data:", data)  # Debugging Output

    user = data.get("user")
    image_name = data.get("image_name")
    analysis = data.get("analysis")
    comparison = data.get("comparison")

    if not user or not image_name or not analysis:
        return jsonify({"error": "Missing required fields"}), 400

    save_mri_result(user, image_name, analysis)
    return jsonify({"message": "MRI result saved successfully"}), 200

#retrieve
@app.route('/get_mri_results', methods=['GET'])
def get_mri_results_endpoint():
    user = request.args.get("user")
    if not user:
        return jsonify({'error': 'User not specified'}), 400

    results = get_mri_results(user)

    if not results:
        return jsonify({'message': 'No MRI results found for this user'}), 404

    return jsonify({"status": "success", "mri_results": results}), 200






# 2. 💾 **Save Chat History Endpoint**
@app.route('/save_chat', methods=['POST'])
def save_chat_endpoint():
    data = request.json
    user = data.get("user")
    message = data.get("message")
    timestamp = datetime.now().isoformat()

    if not user or not message:
        return jsonify({'error': 'Invalid input'}), 400

    save_chat(user, message, timestamp)
    return jsonify({'message': 'Chat history saved successfully'})

# 3. 📜 **Retrieve Chat History Endpoint**
@app.route('/get_chat_history', methods=['GET'])
def get_chat_history_endpoint():
    user = request.args.get("user")
    if user:
        history = get_chat_history(user)
        return jsonify(history), 200
    return jsonify({'error': 'User not specified'}), 400

def generate_gemini_response(user_input, chat_history):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    
    # Format chat history for better context
    formatted_history = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in chat_history])
    
    full_prompt = f"{formatted_history}\nUser: {user_input}\nAssistant:"

    response = model.generate_content(full_prompt)

    if response and hasattr(response, 'text'):
        return response.text.strip()
    else:
        return "Sorry, I am having trouble responding right now."


# 4. 🤖 **Generate Chatbot Response via gemini API**
@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()

    if not data or "user_input" not in data or "chat_history" not in data:
        return jsonify({"error": "Invalid input"}), 400

    user_input = data["user_input"]
    chat_history = data["chat_history"]

    # Get response from Gemini API
    bot_response = generate_gemini_response(user_input, chat_history)

    return jsonify({"response": bot_response})


# Signup Endpoint
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400
    if save_user(username, password):
        return jsonify({"status": "success", "message": "User created successfully"}), 200
    else:
        return jsonify({"status": "error", "message": "User already exists"}), 400

# Login Endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if verify_user(username, password):
        return jsonify({"status": "success", "message": "Login successful"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401




if __name__ == '__main__':
    app.run(debug=True, port=5000)
