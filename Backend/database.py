import pymongo 
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

# Save Chat History
def save_chat(user: str, message: str, timestamp: str):
    chat_data = {
        "user": user,
        "message": message,
        "timestamp": timestamp
    }
    chats_collection.insert_one(chat_data)

def get_chat_history(user):
    chats = chats_collection.find({"user": user}).sort("timestamp", pymongo.ASCENDING)
    return [{"user": chat["user"], "message": chat["message"], "timestamp": chat["timestamp"]} for chat in chats]


# Save MRI Analysis Result (Now stores results as a list per user)
def save_mri_result(user: str, image_name: str, analysis: dict):
    # Ensure analysis is a dictionary
    if not isinstance(analysis, dict):
        print(f"⚠️ Warning: Analysis is missing or not a dict for {image_name}")
        return {"error": "Analysis data required"}

    new_mri_entry = {
        "_id": str(ObjectId()),  # Generate a new MongoDB ObjectId
        "user": user,
        "image_name": image_name,
        "analysis": analysis,  # Store as an object
        "timestamp": datetime.utcnow().isoformat()  # Standardized timestamp
    }

    # Insert into MongoDB
    mri_results_collection.insert_one(new_mri_entry)

    print(f"✅ Saved MRI result: {new_mri_entry}")
    return {"status": "success", "message": "MRI result saved"}


# Retrieve MRI Analysis Results in List Format
from bson import ObjectId

# Get MRI Analysis Results
def get_mri_results(user: str):
    results = list(mri_results_collection.find({"user": user}).sort("timestamp", 1))

    # Convert MongoDB ObjectId to string for JSON response
    for result in results:
        result["_id"] = str(result["_id"])  # Convert ObjectId
        if "results" in result:  # If results are stored as a list
            for item in result["results"]:
                item["_id"] = str(item.get("_id", ""))  # Convert nested ObjectId

    return results





