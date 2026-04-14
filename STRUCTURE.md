# 🌲 Forest AI - Project Structure

## Project Layout

```
MultimodelAI_01/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
│
├── templates/             # HTML pages
│   ├── home.html          # Home/landing page
│   ├── login.html         # Login page
│   ├── signup.html        # Signup page
│   ├── models.html        # Chat interface
│   └── index.html         # Redirect page
│
├── static/                # CSS & JavaScript
│   ├── styles.css         # Global styling (dark theme with cyan accents)
│   ├── script.js          # Frontend logic & chat functionality
│   └── auth.js            # Authentication utilities
│
├── config/                # Setup & configuration
│   ├── setup.bat          # Windows setup script
│   └── setup.sh           # Linux/Mac setup script
│
├── docs/                  # Documentation
│   ├── SETUP.md           # Setup instructions
│   └── README.md          # Additional docs
│
└── venv/                  # Python virtual environment (ignored in git)
```

## Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: MongoDB (pymongo)
- **Authentication**: JWT + SHA-256
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Port**: 8000
- **Color Scheme**: Cyan (#00d4ff), Dark Navy (#0a0e27)

## Dependencies

All required packages are listed in `requirements.txt`:
- fastapi==0.104.1
- uvicorn==0.24.0
- requests==2.31.0
- python-multipart==0.0.6
- pydantic==2.5.0
- pymongo==4.6.0
- PyJWT==2.8.0

## Key Features

✅ User authentication (signup/login)
✅ Multi-model AI chat interface
✅ Dark theme UI with modern styling
✅ Chat history persistence
✅ MongoDB integration

## Running the Application

```bash
# Start server
uvicorn main:app --reload

# Server runs on http://127.0.0.1:8000
```
