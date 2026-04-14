# 🌲 Forest AI - Complete Architecture & API Guide

## Project Structure

```
MultimodelAI_01/
├── main.py                    # FastAPI backend (all endpoints)
├── requirements.txt           # Python dependencies
├── README.md                  # Quick start guide
├── ARCHITECTURE.md            # This file - full API & structure
│
├── templates/                 # Frontend HTML pages
│   ├── home.html              # Landing page
│   ├── login.html             # User login
│   ├── signup.html            # User registration
│   ├── models.html            # Chat interface (main app)
│   └── index.html             # Redirect to home
│
├── static/                    # CSS & JavaScript
│   ├── styles.css             # Dark theme styling
│   ├── script.js              # Chat logic + API calls
│   └── auth.js                # Authentication helpers
│
├── config/                    # Setup scripts
│   ├── setup.bat              # Windows setup
│   └── setup.sh               # Linux/Mac setup
│
├── venv/                      # Python virtual environment
└── .gitignore                 # Git ignore rules
```

## Backend API Endpoints

### 🔐 Authentication Endpoints

#### 1. **POST /auth/signup**
Register a new user
```json
Request:
{
  "username": "john",
  "email": "john@example.com",
  "password": "secure123"
}

Response:
{
  "message": "Signup successful",
  "username": "john",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. **POST /auth/login**
Login existing user
```json
Request:
{
  "username": "john",
  "password": "secure123"
}

Response:
{
  "message": "Login successful",
  "username": "john",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 💬 Chat History Endpoints (Requires Bearer Token)

**All requests must include Authorization header:**
```
Authorization: Bearer <your_jwt_token>
```

#### 3. **GET /chat/history** ⭐ PRIMARY
Load ALL chat history for authenticated user
```
Response:
{
  "message": "Chat history retrieved",
  "chats": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "username": "john",
      "title": "How to learn Python",
      "messages": [...],
      "mode": "smart",
      "created_at": "2026-04-14T10:30:00",
      "updated_at": "2026-04-14T10:30:00"
    }
  ]
}
```

#### 4. **GET /chat/load/{chat_id}**
Load specific chat by ID
```
Response:
{
  "message": "Chat loaded successfully",
  "chat": {
    "_id": "507f1f77bcf86cd799439011",
    "username": "john",
    "title": "How to learn Python",
    "messages": [
      {"role": "user", "content": "What is Python?"},
      {"role": "assistant", "content": "Python is..."}
    ],
    ...
  }
}
```

#### 5. **POST /chat/save** ⭐ PRIMARY
Save chat history (auto-called after each message)
```json
Request:
{
  "title": "Python Tutorial",
  "messages": [
    {"role": "user", "content": "What is a list?"},
    {"role": "assistant", "content": "..."}
  ],
  "mode": "smart"
}

Response:
{
  "message": "Chat saved successfully",
  "chat_id": "507f1f77bcf86cd799439011",
  "title": "Python Tutorial"
}
```

#### 6. **DELETE /chat/delete/{chat_id}**
Delete a chat permanently
```
Response:
{
  "message": "Chat deleted successfully"
}
```

#### 7. **POST /chat/update/{chat_id}**
Update chat title and messages
```json
Request:
{
  "title": "Updated Title",
  "messages": [...],
  "mode": "smart"
}

Response:
{
  "message": "Chat updated successfully",
  "chat_id": "507f1f77bcf86cd799439011"
}
```

### 🤖 AI Model Endpoints

#### 8. **GET /models**
Get available AI models
```
Response: ["llama3:latest", "llama3:8b", "phi3:latest", ...]
```

#### 9. **POST /ask-single**
Query single model
```json
Request:
{
  "prompt": "What is AI?",
  "model": "llama3:latest"
}

Response:
{
  "response": "AI is...",
  "model": "llama3:latest"
}
```

#### 10. **POST /ask-multi-select**
Query multiple models + synthesize answer
```json
Request:
{
  "prompt": "What is AI?",
  "models": ["llama3:latest", "phi3:latest"]
}

Response:
{
  "individual_answers": {
    "llama3:latest": "AI is...",
    "phi3:latest": "AI stands for..."
  },
  "final_answer": "Synthesized answer combining both..."
}
```

#### 11. **POST /ask-smart**
Auto-detect complexity and choose appropriate model(s)
```json
Request:
{
  "prompt": "Explain machine learning"
}

Response:
{
  "mode": "detailed",
  "individual_answers": {...},
  "final_answer": "...",
  "models_used": ["phi3:latest", "llama3:latest"]
}
```

### 📋 Utility Endpoints

#### 12. **GET /**
Serve home page

#### 13. **GET /api/status**
Health check
```
Response:
{
  "message": "Multi Model AI Running 🚀",
  "mongodb": "connected"
}
```

## Database Schema

### MongoDB Collections

#### **signup** (Users)
```json
{
  "_id": ObjectId,
  "username": "john",
  "email": "john@example.com",
  "password": "hashed_password",
  "created_at": ISODate
}
```

#### **chat_history** (Chats)
```json
{
  "_id": ObjectId,
  "username": "john",
  "title": "Python Tutorial",
  "messages": [
    {
      "role": "user",
      "content": "What is Python?",
      "model": null,
      "timestamp": "2026-04-14T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Python is a programming language...",
      "model": "llama3:latest",
      "timestamp": "2026-04-14T10:30:05Z"
    }
  ],
  "mode": "smart",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

## Authentication Flow

```
1. User signs up/logs in
   ↓
2. Server generates JWT token
   ↓
3. Frontend stores token in localStorage
   ↓
4. Every API request includes token in Authorization header
   ↓
5. Backend verifies token using get_current_user() dependency
   ↓
6. Extract username from token
   ↓
7. Return user's data only (privacy + security)
```

## Frontend Flow

### Page Load → models.html
```
1. DOMContentLoaded event
   ↓
2. Check token exists in localStorage
   ↓
3. If no token → Redirect to login
   ↓
4. If token exists:
   - Fetch available models
   - Load chat history from backend ✅
   - Display history in sidebar
   - Show previous chats
```

### User Sends Message
```
1. Input message + select mode (smart/single/multi)
   ↓
2. Call appropriate endpoint (/ask-smart, /ask-single, /ask-multi-select)
   ↓
3. Display AI response
   ↓
4. Auto-save to backend via /chat/save ✅
   ↓
5. Reload history sidebar
   ↓
6. Show chat in history list
```

### User Clicks History Item
```
1. Frontend calls /chat/load/{chat_id}
   ↓
2. Backend verifies user owns chat (403 if not)
   ↓
3. Return chat messages
   ↓
4. Display messages in chat window
```

## Security Features

✅ **Token-Based Auth**
- JWT tokens with 24-hour expiry
- Token required for all chat endpoints
- Automatic token refresh on login

✅ **Ownership Verification**
- Users can only access their own chats
- Delete/Update only by owner (403 Forbidden if not)
- Username extracted from token (not user input)

✅ **Input Validation**
- Username length check (3+ chars)
- Email format validation
- Password length check (6+ chars)

✅ **Error Handling**
- 401 Unauthorized - no/invalid token
- 403 Forbidden - accessing other user's chat
- 404 Not Found - chat doesn't exist
- 500 Server Error - database failures

## How to Test

### 1. Start Backend
```bash
cd MultimodelAI_01
.\venv\Scripts\uvicorn main:app --reload
```

### 2. Open Frontend
```
http://localhost:8000
```

### 3. Test Flow
```
Step 1: Sign up → Get token
Step 2: Open chat (models.html)
Step 3: Send message → Should auto-save
Step 4: Refresh page → History should load
Step 5: Click history item → Chat loads
Step 6: Delete chat → Should disappear
```

## Troubleshooting

### ❌ "No token provided" Error
```
Solution:
1. Make sure you logged in
2. Check localStorage has 'token' key
3. Token must be sent as: Authorization: Bearer <token>
```

### ❌ History Not Showing
```
Solution:
1. Check console for errors
2. Verify /chat/history endpoint returns data
3. Ensure token is valid (check expiry: 24 hours)
4. Check MongoDB is running
```

### ❌ Chat Not Saving
```
Solution:
1. Check /chat/save endpoint is called (check console)
2. Verify token is valid
3. Ensure message has content
4. Check MongoDB connection status
```

### ❌ 403 Forbidden When Loading Chat
```
Solution:
This is expected - you're trying to access another user's chat
Only the owner can view/edit/delete their chats
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI 0.104.1 + Uvicorn |
| **Database** | MongoDB 4.6.0 |
| **Auth** | JWT + SHA-256 |
| **API Calls** | Python Requests |
| **Frontend** | HTML5 + CSS3 + Vanilla JS |
| **AI Models** | Ollama (llama3, phi3, deepseek, etc.) |

## Environment Variables

```
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "red_forest"
SECRET_KEY = "your-secret-key-change-this-in-production"
OLLAMA_URL = "http://localhost:11434/api/generate"
```

## Next Steps / Improvements

- [ ] Add rate limiting to prevent abuse
- [ ] Implement chat search functionality
- [ ] Add chat categories/tagging
- [ ] Export chat as PDF/JSON
- [ ] Share chat with other users
- [ ] Dark/Light theme toggle
- [ ] Multiple language support
- [ ] Better error messages for users
- [ ] Pagination for large chat history
- [ ] Chat analytics/dashboard
