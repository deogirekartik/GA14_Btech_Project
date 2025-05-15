from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from uuid import uuid4
import os
from model_prediction import predict_image
from database import save_user, verify_user, save_chat,create_chat_session, save_mri_result, get_mri_results,update_chat_session, get_chat_sessions, get_chat_messages
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 1. 🧠 Image Prediction Endpoint
@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to predict tumor type and cancer status from an image."""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    result = predict_image(image_file)
    return jsonify(result)

# 2. MRI result save to db
@app.route('/save_mri_result', methods=['POST'])
def save_mri_result_endpoint():
    data = request.get_json()
    print("Received Data:", data)

    # Extract all required fields including recommended_doctors
    user = data.get("user")
    image_name = data.get("image_name")
    analysis = data.get("analysis")
    recommended_doctors = data.get("recommended_doctors", [])  # Default to empty list

    if not user or not image_name or not analysis:
        return jsonify({"error": "Missing required fields"}), 400

    # Pass all parameters to save function
    save_mri_result(user, image_name, analysis, recommended_doctors)
    return jsonify({"message": "MRI result saved successfully"}), 200

# 3. MRI result get from db
@app.route('/get_mri_results', methods=['GET'])
def get_mri_results_endpoint():
    try:
        user = request.args.get("user")
        if not user:
            return jsonify({'error': 'User parameter required'}), 400

        # Get pre-sorted results
        results = get_mri_results(user)
        
        if not results:
            return jsonify({
                "status": "success",
                "message": "No results found",
                "mri_results": []
            }), 200

        return jsonify({
            "status": "success",
            "count": len(results),
            "mri_results": results
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500

@app.route('/save_chat', methods=['POST'])
def save_chat_endpoint():
    try:
        data = request.json
        user = data.get("user")
        session_id = data.get("session_id")
        messages = data.get("messages", [])
        
        if not user or not session_id:
            return jsonify({'error': 'Missing required fields'}), 400
            
        success = update_chat_session(user, session_id, messages)
        return jsonify({'success': success}), 200 if success else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/chat_sessions', methods=['GET'])
def get_chat_sessions_endpoint():
    try:
        user = request.args.get("user")
        if not user:
            return jsonify({"error": "User parameter required"}), 400
            
        sessions = get_chat_sessions(user)
        return jsonify({"sessions": sessions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_chat', methods=['GET'])
def get_chat_endpoint():
    try:
        user = request.args.get("user")
        session_id = request.args.get("session_id")
        
        if not user or not session_id:
            return jsonify({"error": "Missing parameters"}), 400
            
        messages = get_chat_messages(user, session_id)
        return jsonify({"messages": messages}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





# 5. Gemini API Integration
def generate_gemini_response(user_input, chat_history):
    # Initialize with proper model name
    model = genai.GenerativeModel(
        "gemini-1.5-flash-001",
        generation_config={
            "temperature": 0.5,  # More conservative for medical context
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 1024,
        }
    )

    # Format chat history
    formatted_history = "\n".join(
        [f"{msg.get('sender', 'User')}: {msg.get('message', '')}" 
         for msg in chat_history[-6:]]  # Keep last 6 messages for context
    )

    # Create medical-focused prompt
    prompt = f"""As a neuro-oncology assistant, respond to this query:
    Patient Query: {user_input}
    
    Context from previous conversation:
    {formatted_history}
    
    Provide a concise, medically accurate response in plain language.
    Response:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "I should consult a specialist about that."
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having trouble accessing medical resources. Please try again later."



@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()
    if not data or "user_input" not in data:
        return jsonify({"error": "Invalid input"}), 400

    # Get required parameters
    user_input = data["user_input"]
    session_id = data.get("session_id")
    user = data.get("user")
    
    # Get existing messages from session
    messages = get_chat_messages(user, session_id)
    
    # Generate response
    if "Explain these MRI results" in user_input:
        bot_response = generate_analysis_explanation(user_input)
    else:
        bot_response = generate_gemini_response(user_input, messages)
    
    # Update session with new messages
    updated_messages = messages + [
        {"sender": "user", "text": user_input, "timestamp": datetime.utcnow().isoformat()},
        {"sender": "bot", "text": bot_response, "timestamp": datetime.utcnow().isoformat()}
    ]
    update_chat_session(user, session_id, updated_messages)
    
    return jsonify({"response": bot_response})

def generate_analysis_explanation(prompt: str) -> str:
    """Specialized response for MRI analysis explanations"""
    model = genai.GenerativeModel("gemini-1.5-flash-001")
    response = model.generate_content(
        f"Explain these medical imaging results in simple, compassionate terms "
        f"suitable for a patient. Focus on key findings and next steps. "
        f"Results context: {prompt}"
    )
    return response.text if response else "I should explain your MRI results..."

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
