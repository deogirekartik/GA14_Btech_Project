from bson import ObjectId
import pymongo 
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
import ssl
import certifi
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb+srv://deogire:%245kinhand@cluster0.6ohtl.mongodb.net/brain_cancer_chatbot?retryWrites=true&w=majority&authSource=admin&appName=Cluster0",
                     tlsCAFile=certifi.where())

db = client["brain_cancer_chatbot"]

# Collection references
users_collection = db["users"]  # For user authentication and profiles
chats_collection = db["chats"]  # For chat history
mri_results_collection = db["mri_results"]  # For MRI analysis results


# Save User (Signup)
def save_user(username: str, password: str) -> bool:
    if users_collection.find_one({"username": username}):
        return False  # User already exists
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# Verify User (Login)
def verify_user(username: str, password: str) -> bool:
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return True
    return False


def save_chat(user: str, session_id: str, messages: list) -> dict:
    """
    Save or update a chat session with new messages.
    
    Args:
        user (str): The username
        session_id (str): Unique session identifier
        messages (list): List of message dictionaries
        
    Returns:
        dict: Operation status
    """
    try:
        # Validate input
        if not user or not session_id or not isinstance(messages, list):
            return {"status": "error", "message": "Invalid input parameters"}
        
        # Prepare update operation
        update_data = {
            "$set": {
                "messages": messages,
                "last_updated": datetime.utcnow()
            }
        }
        
        # Add created_at timestamp for new sessions
        if not chats_collection.find_one({"session_id": session_id}):
            update_data["$set"]["created_at"] = datetime.utcnow()
        
        # Perform upsert operation
        result = chats_collection.update_one(
            {"user": user, "session_id": session_id},
            update_data,
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            return {"status": "success", "message": "Chat session saved"}
        else:
            return {"status": "error", "message": "No changes made"}
            
    except Exception as e:
        print(f"Error saving chat: {str(e)}")
        return {"status": "error", "message": f"Database error: {str(e)}"}

def create_chat_session(user: str) -> str:
    """Create new chat session with validation"""
    try:
        if not user or not isinstance(user, str):
            raise ValueError("Invalid user parameter")

        session_id = str(uuid4())
        result = chats_collection.insert_one({
            "user": user,
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        })
        
        if not result.inserted_id:
            raise Exception("Failed to create session")
            
        return session_id

    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return ""

# database.py (partial fix)
def update_chat_session(user: str, session_id: str, messages: list) -> bool:
    """Enhanced chat session updater with validation"""
    try:
        # Validate input parameters
        if not all([user, session_id]) or not isinstance(messages, list):
            return False
            
        # Prepare validated messages with fallbacks
        validated_messages = []
        for msg in messages:
            # Ensure required fields exist
            validated_msg = {
                "sender": str(msg.get("sender", "unknown")),
                "text": str(msg.get("text", "")),
                "timestamp": msg.get("timestamp", datetime.utcnow().isoformat())
            }
            # Add session ID to each message
            validated_msg["session_id"] = session_id
            validated_messages.append(validated_msg)
        
        # Atomic update operation
        result = chats_collection.update_one(
            {"user": user, "session_id": session_id},
            {
                "$set": {
                    "messages": validated_messages,
                    "last_updated": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return result.acknowledged
        
    except Exception as e:
        print(f"Database update error: {str(e)}")
        return False
def get_chat_sessions(user: str) -> list:
    """Retrieve chat sessions with safe data handling"""
    try:
        sessions = list(chats_collection.find(
            {"user": user},
            {"_id": 0, "user": 0}
        ).sort("created_at", -1))

        for session in sessions:
            # Ensure default values
            session["created_at"] = session.get("created_at", datetime.utcnow()).isoformat()
            session["last_updated"] = session.get("last_updated", datetime.utcnow()).isoformat()
            
            # Handle empty messages safely
            messages = session.get("messages", [])
            session["message_count"] = len(messages)
            
            # Add preview text safely
            if len(messages) > 0:
                first_msg = messages[0]
                session["preview"] = first_msg.get("text", "")[:50] + "..."
            else:
                session["preview"] = "No messages yet"

        return sessions

    except Exception as e:
        print(f"Database error in get_chat_sessions: {str(e)}")
        return []

def get_chat_messages(user: str, session_id: str) -> list:
    """Get messages with validation"""
    try:
        chat = chats_collection.find_one(
            {"user": user, "session_id": session_id},
            {"_id": 0, "messages": 1}
        )
        return chat.get("messages", []) if chat else []
    
    except Exception as e:
        print(f"Database error in get_chat_messages: {str(e)}")
        return []
    

# Save MRI Analysis Result (Now stores results as a list per user)
def save_mri_result(user: str, image_name: str, analysis: dict, recommended_doctors:list):
    # Ensure analysis is a dictionary
    if not isinstance(analysis, dict):
        print(f"⚠️ Warning: Analysis is missing or not a dict for {image_name}")
        return {"error": "Analysis data required"}

    new_mri_entry = {
        "_id": str(ObjectId()),  # Generate a new MongoDB ObjectId
        "user": user,
        "image_name": image_name,
        "analysis": analysis,  # Store as an object
        "recommended_doctors": recommended_doctors, 
        "timestamp": datetime.utcnow().isoformat()  # Standardized timestamp
    }

    # Insert into MongoDB
    mri_results_collection.insert_one(new_mri_entry)

    print(f"✅ Saved MRI result: {new_mri_entry}")
    return {"status": "success", "message": "MRI result saved"}


# Retrieve MRI Analysis Results in List Format
from bson import ObjectId


def get_mri_results(user: str):
    """Retrieve MRI results sorted by timestamp (newest first) with proper ID conversion"""
    try:
        # Get results sorted in DESCENDING order (newest first)
        results = list(mri_results_collection.find(
            {"user": user}
        ).sort("timestamp", pymongo.DESCENDING))  # Changed to DESCENDING

        # Convert MongoDB ObjectIds to strings
        for result in results:
            result["_id"] = str(result["_id"])
            # Handle nested results if present
            if "results" in result:
                for item in result["results"]:
                    if "_id" in item:
                        item["_id"] = str(item["_id"])
        
        return results

    except Exception as e:
        print(f"Database error: {str(e)}")
        return []



