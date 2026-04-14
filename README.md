# 🌲 Forest AI - Multi-Model AI Assistant

A full-featured AI chat application with user authentication, persistent history, and multi-model support.

**Status:** ✅ Running | **Database:** MongoDB | **Backend:** FastAPI | **Frontend:** HTML + JS

---

## 🚀 Quick Start (3 Steps)

### 1️⃣ Install Dependencies
```bash
cd MultimodelAI_01
.\venv\Scripts\pip install -r requirements.txt
```

### 2️⃣ Start Services

**Terminal 1 - Backend:**
```bash
.\venv\Scripts\uvicorn main:app --reload
```
✅ Should print: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 - MongoDB:**
```bash
mongod
```
✅ Check backend output for: `✓ MongoDB connected successfully`

**Terminal 3 - Ollama (optional for AI features):**
```bash
ollama serve
```

### 3️⃣ Open App
```
http://localhost:8000
```

---

## 📦 Project Structure

```
MultimodelAI_01/
├── main.py                 # Backend - all API endpoints
├── requirements.txt        # Python dependencies
├── ARCHITECTURE.md         # Full API documentation  ⭐ READ THIS
│
├── templates/              # HTML pages
│   ├── models.html         # 💬 Chat interface (main app)
│   ├── login.html          # 🔐 User login
│   ├── signup.html         # 📝 User registration
│   └── home.html           # 🏠 Landing page
│
├── static/                 # Frontend (CSS + JS)
│   ├── script.js           # Chat logic + API calls
│   └── styles.css          # Dark theme styling
│
└── config/                 # Setup scripts
    ├── setup.bat           # Windows installer
    └── setup.sh            # Mac/Linux installer
```

---

## 🔐 Authentication

### Login / Signup
1. Visit `http://localhost:8000`
2. Click "Sign Up" or "Login"
3. Enter username, email, password
4. Token auto-stored in `localStorage['token']`
5. All requests automatically include token

---

## 💬 Chat Features

### Smart Mode ⚡ (Recommended)
- Auto-detects question complexity
- Simple questions → Fast response (phi3)
- Complex questions → Detailed response (multi-model)

### Single Model 📦
- Direct query to chosen model
- Fast, lightweight responses

### Multi-Model Compare ⚖️
- Get responses from multiple models
- AI synthesizes best answer
- See individual model responses

---

## 💾 Chat History

✅ **Auto-Saving**
- Every message → Auto-saved to MongoDB
- Persistent across sessions
- Load history on page refresh

✅ **Sidebar Features**
- See all your previous chats
- Click to load entire conversation
- Delete chat permanently
- View creation date

---

## 🔒 Security

| Feature | Status |
|---------|--------|
| User Authentication | ✅ JWT tokens |
| Password Hashing | ✅ SHA-256 |
| Ownership Verification | ✅ Can only access own chats |
| Token Expiry | ✅ 24 hours |
| Authorization Checks | ✅ All endpoints verified |

---

## 🛠️ Troubleshooting

### ❌ Backend won't start
```
Error: ModuleNotFoundError: No module named 'pymongo'
Fix: .\venv\Scripts\pip install -r requirements.txt
```

### ❌ MongoDB connection failed
```
Error: ⚠ MongoDB not available
Fix: Start MongoDB in another terminal: mongod
```

### ❌ History not showing
```
Check:
1. Refresh page
2. Open browser console (F12)
3. Check for error messages
4. Verify token exists (F12 → Application → localStorage)
```

### ❌ Chat not saving
```
Check:
1. Token is valid
2. MongoDB is running
3. Console shows "💾 Saving chat..."
4. No error messages in console
```

---

## 📚 Full Documentation

For complete API documentation, database schema, and architecture details:

👉 **[See ARCHITECTURE.md](./ARCHITECTURE.md)**

Contains:
- All API endpoints with examples
- MongoDB schema
- Authentication flow
- Security features
- Advanced troubleshooting

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI 0.104.1 |
| Server | Uvicorn |
| Database | MongoDB 4.6.0 |
| Authentication | JWT + SHA-256 |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| AI Models | Ollama (llama3, phi3, deepseek, etc.) |

---

## 🔄 Development Workflow

**Hot Reload Enabled:** Changes to `main.py` auto-reload server

```bash
# Update code → Auto-refresh backend
# Update frontend → Manual refresh browser (F5)
```

---

## 📝 Environment Config

**Default Settings (main.py):**
```python
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "red_forest"
SECRET_KEY = "your-secret-key-change-this-in-production"
OLLAMA_URL = "http://localhost:11434/api/generate"
```

⚠️ **For Production:** Change `SECRET_KEY` to a secure random string

---

## ✅ Status Checklist

- [x] User authentication ✅
- [x] Chat history storage ✅
- [x] Multi-model support ✅
- [x] Smart mode routing ✅
- [x] Token-based security ✅
- [x] Ownership verification ✅
- [x] History auto-load ✅
- [x] Chat persistence ✅

---

## 🎯 Next Features

- [ ] Chat search
- [ ] Export to PDF
- [ ] Chat sharing
- [ ] User preferences
- [ ] Analytics dashboard

---

## 📧 Support

**Need help?**
1. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed docs
2. Open browser console (F12) for error messages
3. Check MongoDB is running: `mongod`
4. Check backend is running: `uvicorn main:app --reload`

---

**Made with ❤️ using FastAPI + MongoDB**
