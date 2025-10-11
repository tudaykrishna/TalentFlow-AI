# 🤖 TalentFlow AI

> **AI-Powered HR Recruiter Application**  
> Automate resume screening, generate job descriptions, and conduct AI-driven interviews

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)

---

## 🎯 Overview

TalentFlow AI is a comprehensive HR recruitment platform that leverages artificial intelligence to streamline the hiring process. The application supports three distinct roles (User, Recruiter, Admin) and provides powerful features for modern talent acquisition.

### Key Capabilities

1. **Resume Screener & Candidate Matcher** - ATS-like system for automated resume screening
2. **JD Generator** - AI-powered job description creation
3. **AI Interview** - Automated initial screening interviews with candidates

---

## ✨ Features

### For Recruiters

- **📝 JD Generator**
  - Create professional job descriptions using AI
  - Customizable company tone and style
  - Automatic PDF generation
  - Save and reuse templates

- **🔍 Resume Screener**
  - Batch resume processing (PDF support)
  - AI-powered candidate matching
  - Match score calculation (0-100%)
  - Detailed candidate analysis
  - Export results as CSV

- **🎤 Interview Assignment**
  - Assign AI interviews to candidates
  - Configurable question count
  - Track interview progress
  - View candidate performance

### For Users/Candidates

- **📊 Dashboard**
  - View assigned interviews
  - Track interview status
  - Review completed interviews

- **🎙️ AI Interview**
  - Interactive AI-powered interviews
  - Real-time question generation
  - Immediate answer evaluation
  - Comprehensive performance summary

### For Admins

- **⚙️ System Management**
  - Monitor system health
  - View analytics and metrics
  - Manage users and recruiters
  - Access system logs

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web interface
- **Pandas** - Data manipulation
- **Requests** - API communication

### Backend
- **FastAPI** - High-performance REST API
- **Motor** - Async MongoDB driver
- **Uvicorn** - ASGI server

### AI/ML
- **Azure OpenAI (GPT-4)** - JD generation and interviews
- **Ollama (Llama 3.1)** - Resume screening
- **LangChain** - AI workflow orchestration
- **LangGraph** - Interview state management

### Database
- **MongoDB** - NoSQL document database

### Additional Services
- **Azure Speech Services** - Text-to-Speech (optional)
- **Azure Whisper** - Speech-to-Text (optional)

---

## 📁 Project Structure

```
TalentFlow-AI/
│
├── App/                                # Streamlit Frontend
│   ├── Admin/                          # Admin screens
│   │   ├── admin.py                    # Dashboard
│   │   ├── Demo1.py                    # User Management
│   │   ├── Demo2.py                    # Analytics
│   │   └── Demo3.py                    # System Logs
│   │
│   ├── Recruiter/                      # Recruiter screens
│   │   ├── recruiter.py                # Dashboard
│   │   ├── jd_generator.py             # JD Generator
│   │   ├── resume_screener.py          # Resume Screener
│   │   └── interview_assignment.py     # Interview Assignment
│   │
│   ├── User/                           # User screens
│   │   ├── user.py                     # Dashboard
│   │   └── ai_interview.py             # AI Interview Interface
│   │
│   ├── images/                         # UI assets
│   ├── settings.py                     # Settings page
│   └── streamlit_app.py                # Main app entry point
│
├── Backend/                            # FastAPI Backend
│   ├── db/                             # Database layer
│   │   └── mongodb.py                  # MongoDB connection
│   │
│   ├── models/                         # Data models
│   │   ├── user_model.py
│   │   ├── jd_model.py
│   │   ├── resume_model.py
│   │   └── interview_model.py
│   │
│   ├── routes/                         # API routes
│   │   ├── jd_routes.py
│   │   ├── resume_routes.py
│   │   └── interview_routes.py
│   │
│   ├── services/                       # Business logic
│   │   ├── jd_service.py
│   │   ├── resume_service.py
│   │   └── interview_service.py
│   │
│   └── main.py                         # FastAPI app entry point
│
├── uploads/                            # File uploads
│   ├── jds/                           # Generated JD PDFs
│   └── resumes/                       # Uploaded resumes
│
├── requirements.txt                    # Python dependencies
├── env.example                         # Environment variables template
└── README.md                           # This file
```

---

## 🔐 Authentication System

TalentFlow AI now uses a secure MongoDB-based authentication system:

- **Username/Password Login** - No more role selection dropdowns
- **Persistent Accounts** - For Admins and Recruiters (stored permanently)
- **Temporary Accounts** - Auto-generated for Candidates (24-hour validity, one-time use)
- **Bcrypt Password Hashing** - Secure password storage
- **Automatic Role Detection** - Smart role-based dashboard redirection

### Quick Start

1. **Create your first admin user:**
   ```bash
   cd Backend
   python create_user.py
   ```

2. **Login with your credentials** on the Streamlit frontend

3. **For candidates:** Temporary accounts are automatically created when recruiters assign interviews

📖 **Detailed Guide:** See [AUTH_SETUP_GUIDE.md](AUTH_SETUP_GUIDE.md) for complete authentication documentation.

---

## 🚀 Installation

### Prerequisites

1. **Python 3.10+**
2. **MongoDB** (local or cloud)
3. **Ollama** (for resume screening)
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.1:8b
   ```
4. **Azure OpenAI Account** (for JD generation and interviews)
5. **Azure Speech Services** (optional, for voice interviews)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TalentFlow-AI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   ```bash
   # Local MongoDB
   # Make sure MongoDB is running on localhost:27017
   
   # Or use MongoDB Atlas (cloud)
   # Get connection string from MongoDB Atlas
   ```

5. **Configure environment variables**
   ```bash
   # Copy the example env file
   cp env.example .env
   
   # Edit .env and fill in your credentials
   ```

6. **Create your first user (Admin/Recruiter)**
   ```bash
   cd Backend
   python create_user.py
   # Follow the interactive prompts
   ```

---

## ⚙️ Configuration

Edit the `.env` file with your credentials:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
DB_NAME=talentflow_db

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_WHISPER_DEPLOYMENT_NAME=whisper

# Azure Speech Services (optional)
AZURE_SPEECH_KEY=your_key_here
AZURE_SPEECH_REGION=eastus

# Ollama
OLLAMA_MODEL=llama3.1:8b
```

---

## 🏃 Running the Application

### 1. Start MongoDB
```bash
# If using local MongoDB, ensure it's running
mongod
```

### 2. Start Ollama
```bash
# Ensure Ollama is running
ollama serve
```

### 3. Start the Backend (FastAPI)
```bash
# Navigate to Backend directory
cd Backend

# Run FastAPI server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 4. Start the Frontend (Streamlit)
```bash
# In a new terminal, navigate to App directory
cd App

# Run Streamlit app
streamlit run streamlit_app.py
```

The frontend will be available at: `http://localhost:8501`

---

## 📖 Usage Guide

### Login (All Users)

1. **Access the application** at `http://localhost:8501`
2. **Enter your credentials:**
   - **Admins/Recruiters:** Use your registered email and password
   - **Candidates:** Use temporary credentials provided by recruiter
3. **Automatic redirect** to your role-specific dashboard

### Recruiter Workflow

1. **Login with your credentials**
   - Email: `your.email@company.com`
   - Password: Your registered password

2. **Create a Job Description**
   - Navigate to "JD Generator"
   - Fill in job details
   - Generate and download PDF

3. **Screen Resumes**
   - Navigate to "Resume Screener"
   - Select or enter JD
   - Upload resume PDFs
   - View match scores and analysis
   - Download results as CSV

4. **Assign Interviews**
   - Navigate to "Interview Assignment"
   - Select JD
   - Configure interview settings (number of questions)
   - Click "Assign Interview"
   - **System automatically creates temporary user account**
   - Share the generated email and password with candidate

### Candidate (User) Workflow

1. **Receive credentials from recruiter**
   - Temporary email: `candidate_xxxxxxxx_interviewid@talentflow.temp`
   - Temporary password: Auto-generated secure password
   - Valid for 24 hours only

2. **Login with temporary credentials**
   - Enter email and password on login page
   - System automatically redirects to User dashboard

3. **Take Interview**
   - View assigned interviews on dashboard
   - Click "Start Interview"
   - Answer questions one by one
   - View evaluation and final summary

### Admin Workflow

1. **Login with admin credentials**
   - Email: `admin@company.com`
   - Password: Your registered password

2. **Monitor System**
   - View system health
   - Check analytics
   - Manage users
   - Review system logs

---

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

#### Authentication
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/register` - Register new admin/recruiter
- `GET /api/auth/user/{user_id}` - Get user information
- `POST /api/auth/cleanup-expired` - Clean up expired temporary users

#### Job Descriptions
- `POST /api/jd/generate` - Generate a job description
- `GET /api/jd/{jd_id}` - Get a specific JD
- `GET /api/jd/recruiter/{recruiter_id}` - Get all JDs by recruiter

#### Resume Screening
- `POST /api/resume/screen` - Screen multiple resumes
- `GET /api/resume/results/{recruiter_id}` - Get screening results
- `GET /api/resume/detail/{resume_id}` - Get detailed result

#### AI Interviews
- `POST /api/interview/assign` - Assign interview (auto-creates temp user)
- `POST /api/interview/{id}/start` - Start interview
- `POST /api/interview/{id}/answer` - Submit answer
- `GET /api/interview/{id}/status` - Get interview status
- `GET /api/interview/{id}/summary` - Get interview summary
- `GET /api/interview/user/{user_id}` - Get user's interviews

---

## 🧪 Testing

### Test the Authentication System
```bash
# Run the automated test suite
python test_auth_system.py

# This will test:
# - User registration
# - Login (admin, recruiter, temporary user)
# - Interview assignment with temp user creation
# - Invalid login handling
```

### Test the Backend
```bash
# Check health endpoint
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "yourpassword"}'
```

### Test Resume Screening
1. Ensure Ollama is running with llama3.1:8b model
2. Use the Streamlit UI to upload test resumes
3. Check the console for processing logs

### Test JD Generation
1. Ensure Azure OpenAI credentials are configured
2. Use the JD Generator in Streamlit
3. Verify PDF generation in `uploads/jds/`

---

## 🔧 Troubleshooting

### Common Issues

1. **Login Failed / Invalid Credentials**
   - Ensure you've created a user using `python Backend/create_user.py`
   - Check email and password are correct
   - For candidates: Verify credentials are not expired (24 hours)
   - For candidates: Ensure interview hasn't been attempted already

2. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check MONGODB_URI in .env
   - Verify network connectivity

3. **Ollama Not Found**
   - Install Ollama from https://ollama.ai
   - Run `ollama pull llama3.1:8b`
   - Ensure Ollama service is running

4. **Azure OpenAI Errors**
   - Verify API key and endpoint
   - Check deployment names
   - Ensure quota is not exceeded

5. **File Upload Errors**
   - Check file size limits
   - Verify PDF format
   - Ensure uploads directory exists

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Contact the development team

---

## 🎉 Acknowledgments

- Azure OpenAI for powerful AI capabilities
- Ollama for local LLM support
- Streamlit for the amazing frontend framework
- FastAPI for the robust backend framework
- MongoDB for flexible data storage

---

**Built with ❤️ for modern HR teams**

