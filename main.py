from fastapi import FastAPI, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import requests
import os
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
import hashlib
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR

# MongoDB Connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "red_forest"
COLLECTION_NAME = "signup"
SECRET_KEY = "your-secret-key-change-this-in-production"

try:
    mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    # Test connection
    mongo_client.admin.command('ping')
    db = mongo_client[DB_NAME]
    users_collection = db[COLLECTION_NAME]
    chat_history_collection = db["chat_history"]
    # Create unique index on email and username
    users_collection.create_index("email", unique=True)
    users_collection.create_index("username", unique=True)
    # Create index for chat history
    chat_history_collection.create_index("username")
    chat_history_collection.create_index("created_at")
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"⚠ MongoDB not available: {e}")
    print("⚠ Auth endpoints will not work. Start MongoDB with: mongod")
    mongo_client = None
    chat_history_collection = None

# Request models
class SingleRequest(BaseModel):
    prompt: str
    model: str

class MultiRequest(BaseModel):
    prompt: str
    models: list[str]

class SmartRequest(BaseModel):
    prompt: str

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    model: Optional[str] = None
    timestamp: Optional[str] = None

class SaveChatRequest(BaseModel):
    username: Optional[str] = None  # Optional - backend extracts from token
    title: str
    messages: list
    mode: str = "smart"

class LoadChatRequest(BaseModel):
    username: str
    chat_id: str

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"

# Available models (only load when selected)
AVAILABLE_MODELS = [
    "llama3:latest",
    "llama3:8b",
    "phi3:latest",
    "deepseek-coder:latest",
    "nous-hermes2:latest"
]

# ============== AUTHENTICATION FUNCTIONS ==============

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    """Create JWT token"""
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception as e:
        return None

def get_current_user(authorization: str = Header(None)) -> str:
    """Extract and verify username from token"""
    if not authorization:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided"
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        username = payload.get("username")
        if not username:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token does not contain username"
            )
        
        return username
        
    except ValueError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

# ============== AUTHENTICATION ENDPOINTS ==============

@app.post("/auth/signup")
def signup(request: SignupRequest):
    """User signup endpoint"""
    try:
        if not mongo_client:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Validate input
        if len(request.username) < 3:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters"
            )
        
        if "@" not in request.email:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        if len(request.password) < 6:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        # Check if user already exists
        existing_user = users_collection.find_one({
            "$or": [
                {"username": request.username},
                {"email": request.email}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Create new user
        hashed_password = hash_password(request.password)
        user_data = {
            "username": request.username,
            "email": request.email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        
        result = users_collection.insert_one(user_data)
        
        # Create token
        token = create_token(request.username)
        
        return {
            "message": "Signup successful",
            "username": request.username,
            "token": token
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/auth/login")
def login(request: LoginRequest):
    """User login endpoint"""
    try:
        if not mongo_client:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Find user by username or email
        user = users_collection.find_one({
            "$or": [
                {"username": request.username},
                {"email": request.username}
            ]
        })
        
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        hashed_password = hash_password(request.password)
        if user["password"] != hashed_password:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create token
        token = create_token(user["username"])
        
        return {
            "message": "Login successful",
            "username": user["username"],
            "token": token
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Function to call model (only runs when selected)
def call_model(model, prompt):
    """Call model only when explicitly selected - lazy loading"""
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Model {model} not available. Available models: {AVAILABLE_MODELS}")
    
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt + " give the as small as answer possible",
        "stream": False
    })
    return response.json()["response"]

# Serve the frontend
@app.get("/")
def home():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    home_path = os.path.join(current_dir, "templates", "home.html")
    return FileResponse(home_path)

@app.get("/templates/home.html")
def serve_home():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    home_path = os.path.join(current_dir, "templates", "home.html")
    return FileResponse(home_path)

@app.get("/templates/signup.html")
def serve_signup():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "templates", "signup.html")
    return FileResponse(path)

@app.get("/templates/login.html")
def serve_login():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "templates", "login.html")
    return FileResponse(path)

@app.get("/templates/models.html")
def serve_models():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "templates", "models.html")
    return FileResponse(path)

@app.get("/chat")
def serve_chat():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "templates", "index.html")
    return FileResponse(index_path)

# Home route info
@app.get("/api/status")
def api_status():
    return {
        "message": "Multi Model AI Running 🚀",
        "mongodb": "connected" if mongo_client else "not connected"
    }

# Get available models (hardcoded, lazy-loaded)
@app.get("/models")
def get_models():
    """Get list of available models - models load only when selected"""
    return AVAILABLE_MODELS

# Single model endpoint
@app.post("/ask-single")
def ask_single(request: SingleRequest):
    """Get response from a single selected model"""
    try:
        result = call_model(request.model, request.prompt)
        return {
            "response": result,
            "model": request.model
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "model": request.model
        }

# Multi-model selection endpoint
@app.post("/ask-multi-select")
def ask_multi_select(request: MultiRequest):
    """Get responses from multiple selected models"""
    try:
        answers = {}
        
        # Parallel execution for multiple models
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda m: get_model_response(m, request.prompt), request.models)
        
        for model, response in results:
            answers[model] = response
        
        # Judge the answers using Llama3
        final_answer = judge_multi_answers(request.prompt, answers)
        
        return {
            "individual_answers": answers,
            "final_answer": final_answer
        }
    except Exception as e:
        return {
            "error": str(e),
            "individual_answers": {},
            "final_answer": f"Error: {str(e)}"
        }

# JUDGE FUNCTION FOR MULTI-ANSWER SYNTHESIS

def judge_multi_answers(prompt, answers):
    """Synthesize multiple model answers using Llama3"""
    
    # Build the prompt with all answers
    answers_text = ""
    for idx, (model, answer) in enumerate(answers.items(), 1):
        answers_text += f"\nModel {idx} ({model}):\n{answer}\n"
    
    combined_prompt = f"""You are an expert AI that synthesizes multiple answers into one final, accurate response.

Question: {prompt}

Different Model Responses:
{answers_text}

Your task:
- Analyze all responses
- Identify the most accurate information
- Synthesize them into ONE comprehensive final answer
- Be concise but thorough
- Only provide the final answer, no explanations

Final Synthesized Answer:"""

    return call_model("llama3:latest", combined_prompt)


# OLD SINGLE-MODEL JUDGE FUNCTION

def judge_answers(prompt, answers):
    """Judge and synthesize answers from multiple models"""
    combined_prompt = f"""You are an AI that synthesizes multiple answers into one final, accurate response.

Question: {prompt}

Different responses:
{chr(10).join(f"- {answer}" for answer in answers.values())}

Your task:
- Analyze all responses
- Identify the most accurate information
- Synthesize into ONE final comprehensive answer
- Be concise and thorough
- Only provide the final answer

Final Answer:"""

    return call_model("llama3:latest", combined_prompt)

def get_model_response(model, prompt):
    """Get response from a model - lazy loads only when called"""
    try:
        print(f"[MODEL] Loading {model}...")
        return model, call_model(model, prompt)
    except Exception as e:
        print(f"[ERROR] {model}: {str(e)}")
        return model, f"Error: {str(e)}"


def is_complex(prompt):
    """Detect if question needs multiple models or single fast model"""
    prompt = prompt.lower()
    
    # Simple rules for complexity detection
    if len(prompt) > 60:
        return True
    if "explain" in prompt or "why" in prompt or "how" in prompt or ("what" in prompt and len(prompt) > 30):
        return True
    if "compare" in prompt or "difference" in prompt:
        return True
    
    return False


@app.post("/ask-smart")
def ask_smart(request: SmartRequest):
    """Smart mode - analyzes complexity and uses appropriate model(s)
    
    Models load ONLY when needed (lazy loading):
    - Simple questions: phi3:latest only (⚡ Fast)
    - Complex questions: phi3:latest + llama3:latest (🧠 Detailed)
    """
    
    # Detect complexity
    if not is_complex(request.prompt):
        # ⚡ FAST MODE - phi3 only (models don't load until now)
        print(f"[SMART] Fast Mode - Question is simple")
        print(f"[SMART] Loading phi3:latest...")
        fast_answer = call_model("phi3:latest", request.prompt)
        
        return {
            "mode": "fast",
            "final_answer": fast_answer,
            "model_used": "phi3:latest"
        }

    # 🧠 COMPLEX MODE - Multiple models (load now)
    print(f"[SMART] Detailed Mode - Question is complex")
    models = ["phi3:latest", "llama3:latest"]
    answers = {}

    # Parallel execution - models load here
    print(f"[SMART] Loading models in parallel: {models}")
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(lambda m: get_model_response(m, request.prompt), models)

    for model, response in results:
        answers[model] = response

    print(f"[SMART] All models loaded. Synthesizing answer with llama3:latest...")
    final_answer = judge_answers(request.prompt, answers)

    return {
        "mode": "detailed",
        "individual_answers": answers,
        "final_answer": final_answer,
        "models_used": list(answers.keys())
    }

# ============== CHAT HISTORY ENDPOINTS ==============

@app.post("/chat/save")
def save_chat(request: SaveChatRequest, username: str = Depends(get_current_user)):
    """Save a chat session to history (requires authentication)"""
    try:
        if chat_history_collection is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Create chat document with authenticated username
        chat_doc = {
            "username": username,  # Use username from token, not from request
            "title": request.title or "Untitled Chat",
            "messages": request.messages,
            "mode": request.mode,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = chat_history_collection.insert_one(chat_doc)
        
        return {
            "message": "Chat saved successfully",
            "chat_id": str(result.inserted_id),
            "title": chat_doc["title"]
        }
    except Exception as e:
        print(f"Save chat error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/chat/history")
def get_chat_history(username: str = Depends(get_current_user)):
    """Get chat history for authenticated user"""
    try:
        if chat_history_collection is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Find all chats for the authenticated user
        chats = list(chat_history_collection.find(
            {"username": username}
        ).sort("created_at", -1).limit(50))
        
        # Convert ObjectId and datetime to strings
        for chat in chats:
            chat["_id"] = str(chat["_id"])
            # Convert datetime to ISO format string
            if "created_at" in chat and hasattr(chat["created_at"], "isoformat"):
                chat["created_at"] = chat["created_at"].isoformat()
            if "updated_at" in chat and hasattr(chat["updated_at"], "isoformat"):
                chat["updated_at"] = chat["updated_at"].isoformat()
        
        return {
            "message": "Chat history retrieved",
            "chats": chats
        }
    except Exception as e:
        print(f"❌ Get chat history error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(e).__name__}: {str(e)[:100]}"
        )

# Keep old endpoint for backward compatibility (deprecated)
@app.get("/chat/history/{username}")
def get_chat_history_legacy(username: str):
    """Get chat history for a user (DEPRECATED - use /chat/history with token)"""
    try:
        if chat_history_collection is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Find all chats for the user
        chats = list(chat_history_collection.find(
            {"username": username}
        ).sort("created_at", -1).limit(50))
        
        # Convert ObjectId and datetime to strings
        for chat in chats:
            chat["_id"] = str(chat["_id"])
            # Convert datetime to ISO format string
            if "created_at" in chat and hasattr(chat["created_at"], "isoformat"):
                chat["created_at"] = chat["created_at"].isoformat()
            if "updated_at" in chat and hasattr(chat["updated_at"], "isoformat"):
                chat["updated_at"] = chat["updated_at"].isoformat()
        
        return {
            "message": "Chat history retrieved",
            "chats": chats
        }
    except Exception as e:
        print(f"❌ Get chat history error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(e).__name__}: {str(e)[:100]}"
        )

@app.get("/chat/load/{chat_id}")
def load_chat(chat_id: str, username: str = Depends(get_current_user)):
    """Load a specific chat (requires authentication and ownership)"""
    try:
        if chat_history_collection is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Find the chat
        chat = chat_history_collection.find_one({"_id": ObjectId(chat_id)})
        
        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )
        
        # Verify ownership - user can only load their own chats
        if chat.get("username") != username:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this chat"
            )
        
        # Convert ObjectId to string
        chat["_id"] = str(chat["_id"])
        
        # Convert datetime to ISO format string
        if "created_at" in chat and hasattr(chat["created_at"], "isoformat"):
            chat["created_at"] = chat["created_at"].isoformat()
        if "updated_at" in chat and hasattr(chat["updated_at"], "isoformat"):
            chat["updated_at"] = chat["updated_at"].isoformat()
        
        return {
            "message": "Chat loaded successfully",
            "chat": chat
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Load chat error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(e).__name__}: {str(e)[:100]}"
        )

@app.delete("/chat/delete/{chat_id}")
def delete_chat(chat_id: str, username: str = Depends(get_current_user)):
    """Delete a chat (requires authentication and ownership)"""
    try:
        if chat_history_collection is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Verify ownership before deletion
        chat = chat_history_collection.find_one({"_id": ObjectId(chat_id)})
        
        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )
        
        if chat.get("username") != username:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this chat"
            )
        
        result = chat_history_collection.delete_one({"_id": ObjectId(chat_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )
        
        return {
            "message": "Chat deleted successfully"
        }
    except Exception as e:
        print(f"Delete chat error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/chat/update/{chat_id}")
def update_chat(chat_id: str, request: SaveChatRequest, username: str = Depends(get_current_user)):
    """Update an existing chat (requires authentication and ownership)"""
    try:
        if chat_history_collection is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        # Verify ownership before updating
        chat = chat_history_collection.find_one({"_id": ObjectId(chat_id)})
        
        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )
        
        if chat.get("username") != username:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this chat"
            )
        
        result = chat_history_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {
                "$set": {
                    "title": request.title,
                    "messages": request.messages,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )
        
        return {
            "message": "Chat updated successfully",
            "chat_id": chat_id
        }
    except Exception as e:
        print(f"Update chat error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
