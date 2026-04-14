# 🧪 Testing & Debugging Guide

Use this guide to test all API endpoints and verify chat history is working correctly.

---

## ✅ Pre-Check

Before testing, ensure:
```bash
# Terminal 1 - Backend running?
✅ http://127.0.0.1:8000 should be accessible
Output should show: "Uvicorn running on..."

# Terminal 2 - MongoDB running?
✅ mongod should be running
Backend output should show: "✓ MongoDB connected successfully"
```

---

## 🧪 Test Sequence

### 1️⃣ Test Backend Health
```bash
curl http://localhost:8000/api/status
```

**Expected:**
```json
{
  "message": "Multi Model AI Running 🚀",
  "mongodb": "connected"
}
```

---

### 2️⃣ Test Signup (Create User)
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }
```

**Expected:**
```json
{
  "message": "Signup successful",
  "username": "testuser",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Save the token!** You'll need it for next steps.

---

### 3️⃣ Test Login (Get Token)
If user already exists:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d {
    "username": "testuser",
    "password": "password123"
  }
```

**Expected:**
```json
{
  "message": "Login successful",
  "username": "testuser",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4️⃣ Test Save Chat ✅ KEY TEST

This is where chat history gets saved:

```bash
curl -X POST http://localhost:8000/chat/save \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d {
    "title": "My First Chat",
    "messages": [
      {
        "role": "user",
        "content": "What is Python?"
      },
      {
        "role": "assistant",
        "content": "Python is a programming language..."
      }
    ],
    "mode": "smart"
  }
```

**Expected:**
```json
{
  "message": "Chat saved successfully",
  "chat_id": "507f1f77bcf86cd799439011",
  "title": "My First Chat"
}
```

**If you get error:** ❌ 401 Unauthorized
- Check token is correct
- Token must start with: `Bearer ` (with space)

**If you get error:** ❌ No authorization token
- Include header: `Authorization: Bearer TOKEN`

---

### 5️⃣ Test Load Chat History ✅ KEY TEST

This loads all your saved chats:

```bash
curl http://localhost:8000/chat/history \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected:**
```json
{
  "message": "Chat history retrieved",
  "chats": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "username": "testuser",
      "title": "My First Chat",
      "messages": [...],
      "mode": "smart",
      "created_at": "2026-04-14T10:30:00",
      "updated_at": "2026-04-14T10:30:00"
    }
  ]
}
```

**If chats array is empty [] - HERE'S THE ISSUE:**
1. Make sure you ran step 4 (Save Chat)
2. Check chat_id from step 4 response
3. Verify token is valid

---

### 6️⃣ Test Load Specific Chat

Replace `{chat_id}` with ID from step 5:

```bash
curl http://localhost:8000/chat/load/507f1f77bcf86cd799439011 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected:**
```json
{
  "message": "Chat loaded successfully",
  "chat": {
    "_id": "507f1f77bcf86cd799439011",
    "username": "testuser",
    "title": "My First Chat",
    "messages": [...]
  }
}
```

---

### 7️⃣ Test Delete Chat

```bash
curl -X DELETE http://localhost:8000/chat/delete/507f1f77bcf86cd799439011 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected:**
```json
{
  "message": "Chat deleted successfully"
}
```

After deletion, try step 5 again - chat should be gone.

---

### 8️⃣ Test Cross-User Security (Ownership)

1. Create user_a and get token_a
2. Create user_b and get token_b
3. User_a saves chat → gets chat_id
4. Try user_b loading user_a's chat:

```bash
curl http://localhost:8000/chat/load/user_a_chat_id \
  -H "Authorization: Bearer user_b_token"
```

**Expected:** ❌ 403 Forbidden
```json
{
  "detail": "You do not have permission to access this chat"
}
```

This proves security is working! ✅

---

## 🧪 Browser Console Testing

### Check Token Stored
Open browser DevTools (F12):
```javascript
// In console:
localStorage.getItem('token')

// Should return: "eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Check History Loaded
```javascript
// In console:
console.log(chatHistory)

// Should show array of chats from MongoDB
```

### Check If Saving Works
1. Open DevTools Network tab
2. Send a message in chat
3. Look for POST request to: `/chat/save`
4. Should see 200 response with chat_id

---

## 🐛 Debugging Tips

### Problem: "No chats loading"
```javascript
// Open console (F12) and run:
await loadChatHistory(localStorage.getItem('username'))

// Check output:
// ✅ Shows "📥 Loading chat history..."
// ✅ Shows "✅ Loaded X chats"
// ❌ Shows error → copy error to stack trace
```

### Problem: "Chat not saving"
```javascript
// Check in console:
console.log('conversationHistory =', conversationHistory)

// If empty → add a message first
// If has messages → check network tab for /chat/save request
```

### Problem: Token Invalid
```javascript
// In console:
const token = localStorage.getItem('token')
const payload = JSON.parse(atob(token.split('.')[1]))
console.log('Token expires at:', new Date(payload.exp * 1000))

// If past current time → token expired, need to login again
```

---

## 📊 MongoDB Direct Check

If installed mongo shell:

```bash
mongosh
> use red_forest
> db.chat_history.find()  # Shows all chats
> db.chat_history.find({username: "testuser"})  # Shows testuser's chats
> db.signup.find()  # Shows all users
```

---

## 🔍 Detailed Flow Debugging

### When you send a message, this should happen:

```
1. DOMContentLoaded → loadChatHistory() called
   Check: Console shows "📥 Loading chat history..."
   
2. Send message → sendMessage() called
   Check: Message appears in chat
   
3. Get AI response → displayResponse() called
   Check: Response appears with model info
   
4. Auto-save: saveChatHistory() called
   Check: Console shows "💾 Saving chat:"
   Check: Network tab shows POST /chat/save
   
5. Reload history: loadChatHistory() called again
   Check: New chat appears in sidebar
   Check: Console shows "✅ Loaded X chats"
```

If any step fails → check console for error message

---

## ✅ Success Checklist

After going through all 8 tests:

- [ ] Backend health check passes
- [ ] Can create user
- [ ] Can login and get token
- [ ] Can save chat (chat_id returned)
- [ ] Can load all chats (chats array has items)
- [ ] Can load specific chat (full messages shown)
- [ ] Can delete chat (removed from history)
- [ ] Cross-user access denied (403 received)
- [ ] History shows in sidebar after refresh
- [ ] New messages auto-save to MongoDB

**If all ✅ → System is working perfectly! 🎉**

---

## 🆘 Quick Fixes

| Error | Fix |
|-------|-----|
| 401 Unauthorized | Add token to Authorization header |
| 403 Forbidden | Expected for cross-user access (security working) |
| 404 Not Found | chat_id doesn't exist, check ID spelling |
| 500 Server Error | Check MongoDB running, check logs in terminal |
| Empty chats array | Make sure you saved a chat in step 4 |
| Token invalid | Login again to get fresh token |

---

## 📝 Notes

- Tokens expire after **24 hours** → Login again
- Each user has **separate** chat history (privacy)
- Deleting chat is **permanent** (no recovery)
- MongoDB stores **raw messages** (not processed)
- All timestamps in **ISO 8601** format

---

**Ready to test? Start with step 1! 🧪**
