# 🤖 TalentFlow AI

> **AI-Powered HR Recruiter Application**  
> Automate resume screening, generate job descriptions, and conduct AI-driven interviews with voice capabilities

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
- [Voice Features](#voice-features)
- [Contributing](#contributing)

---

## 🎯 Overview

TalentFlow AI is a comprehensive HR recruitment platform that leverages artificial intelligence to streamline the hiring process. The application supports three distinct roles (User, Recruiter, Admin) and provides powerful features for modern talent acquisition with advanced voice capabilities.

### Key Capabilities

1. **Resume Screener & Candidate Matcher** - ATS-like system for automated resume screening
2. **JD Generator** - AI-powered job description creation with PDF export
3. **AI Interview** - Automated initial screening interviews with voice input/output
4. **Voice Processing** - Local GPU-accelerated speech-to-text and cloud text-to-speech

---

## ✨ Features

### For Recruiters

- **📝 JD Generator**
  - Create professional job descriptions using AI
  - Customizable company tone and style
  - Automatic PDF generation and download
  - Save and manage job descriptions

- **🔍 Resume Screener**
  - Batch resume processing (PDF support)
  - AI-powered candidate matching using Ollama
  - Match score calculation (0-100%)
  - Detailed candidate analysis
  - Export results as CSV

- **🎤 Interview Assignment**
  - Assign AI interviews to candidates
  - Auto-generate temporary user accounts
  - Configurable question count
  - Track interview progress
  - View candidate performance

- **📊 Interview Results**
  - View completed interview results
  - Detailed candidate evaluations
  - Performance summaries and recommendations

### For Users/Candidates

- **📊 Dashboard**
  - View assigned interviews
  - Track interview status
  - Review completed interviews

- **🎙️ AI Interview**
  - Interactive AI-powered interviews
  - **Voice Input**: Speak your answers (local Whisper transcription)
  - **Voice Output**: AI speaks questions (Azure Speech Services)
  - Real-time question generation
  - Immediate answer evaluation
  - Comprehensive performance summary

### For Admins

- **⚙️ System Management**
  - Monitor system health
  - View analytics and metrics
  - Manage users and recruiters
  - Access system logs

- **🔧 Debug Configuration**
  - View backend configuration
  - Test API connections
  - Troubleshoot system issues
  - Monitor Azure OpenAI settings

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web interface
- **Audio Recorder** - Voice input capture
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
- **Local Whisper (faster-whisper)** - GPU-accelerated speech-to-text

### Voice Processing
- **Local Whisper** - Speech-to-text (GPU-accelerated, free)
- **Azure Speech Services** - Text-to-speech (high quality)
- **Audio Processing** - Real-time voice capture and playback

### Database
- **MongoDB** - NoSQL document database

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
│   │   ├── interview_assignment.py     # Interview Assignment
│   │   └── interview_results.py        # Interview Results
│   │
│   ├── User/                           # User screens
│   │   ├── user.py                     # Dashboard
│   │   ├── ai_interview.py             # AI Interview Interface
│   │   └── Demo4.py                    # Additional features
│   │
│   ├── images/                         # UI assets
│   ├── debug_config.py                 # Debug configuration (Admin only)
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
│   │   ├── auth_routes.py
│   │   ├── jd_routes.py
│   │   ├── resume_routes.py
│   │   └── interview_routes.py
│   │
│   ├── services/                       # Business logic
│   │   ├── auth_service.py
│   │   ├── jd_service.py
│   │   ├── resume_service.py
│   │   ├── interview_service.py
│   │   └── whisper_service.py          # Local Whisper integration
│   │
│   ├── uploads/                        # File uploads
│   │   ├── jds/                        # Generated JD PDFs
│   │   └── resumes/                    # Uploaded resumes
│   │
│   ├── create_user.py                  # User creation utility
│   └── main.py                         # FastAPI app entry point
│
├── hi.py                               # LangGraph AI Interview (Text)
├── hi2.py                              # LangGraph AI Interview (Voice)
├── hi3.py                              # Azure Speech Services Test
├── test.ipynb                          # Development notebook
├── requirements.txt                    # Python dependencies
├── start_backend.bat                   # Backend startup script
├── start_frontend.bat                  # Frontend startup script
└── README.md                           # This file
```

---

## 🔐 Authentication System

TalentFlow AI uses a secure MongoDB-based authentication system:

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
6. **NVIDIA GPU** (recommended for local Whisper)

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
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_WHISPER_DEPLOYMENT_NAME=whisper-1

# Azure Speech Services (optional)
AZURE_SPEECH_KEY=your_key_here
AZURE_SPEECH_REGION=eastus

# Local Whisper Configuration
WHISPER_USE_LOCAL=true
WHISPER_MODEL_SIZE=medium
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16

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
# Option 1: Use the startup script
start_backend.bat

# Option 2: Manual start
cd Backend
python main.py

# Option 3: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 4. Start the Frontend (Streamlit)
```bash
# Option 1: Use the startup script
start_frontend.bat

# Option 2: Manual start
cd App
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

5. **View Results**
   - Navigate to "Interview Results"
   - Review completed interviews
   - Analyze candidate performance

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
   - **Voice Interview**: Speak your answers (AI transcribes them)
   - **Text Interview**: Type your answers
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

3. **Debug Configuration**
   - Navigate to "Debug Config" (Admin only)
   - View backend configuration
   - Test API connections
   - Troubleshoot issues

---

## 🎙️ Voice Features

### Speech-to-Text (Local Whisper)
- **Technology**: faster-whisper with GPU acceleration
- **Model**: Whisper "medium" model
- **Device**: CUDA (NVIDIA GPU)
- **Speed**: ~0.3 seconds processing time
- **Cost**: Free (local processing)
- **Privacy**: Audio never leaves your machine

### Text-to-Speech (Azure Speech Services)
- **Technology**: Azure Speech Services
- **Quality**: High-quality neural voices
- **Languages**: Multiple language support
- **Cost**: Pay-per-use
- **Reliability**: Enterprise-grade service

### Voice Interview Flow
1. **AI asks question** (text-to-speech)
2. **Candidate speaks answer** (voice recording)
3. **Audio transcribed** (local Whisper)
4. **Answer evaluated** (Azure OpenAI)
5. **Next question generated** (Azure OpenAI)

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
- `GET /api/auth/debug/config` - Get backend configuration (Admin only)

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
- `POST /api/interview/transcribe` - Transcribe audio (local Whisper)
- `GET /api/interview/{id}/status` - Get interview status
- `GET /api/interview/{id}/summary` - Get interview summary
- `GET /api/interview/user/{user_id}` - Get user's interviews

#### Whisper Service
- `GET /api/whisper/health` - Check Whisper service status

---

## 🧪 Testing

### Test Voice Features
```bash
# Test local Whisper
python hi3.py

# Test Azure Speech Services
python hi3.py
```

### Test AI Interview
```bash
# Text-based interview
python hi.py

# Voice-based interview
python hi2.py
```

### Test Backend
```bash
# Check health endpoint
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

---

## 🔧 Troubleshooting

### Common Issues

1. **Login Failed / Invalid Credentials**
   - Ensure you've created a user using `python Backend/create_user.py`
   - Check email and password are correct
   - For candidates: Verify credentials are not expired (24 hours)

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

5. **Whisper Not Working**
   - Ensure NVIDIA GPU is available
   - Check CUDA installation
   - Verify faster-whisper installation
   - Check GPU memory availability

6. **Voice Features Not Working**
   - Check microphone permissions
   - Verify audio drivers
   - Test Azure Speech Services credentials
   - Check network connectivity for TTS

### Debug Tools
- **Admin Debug Page**: Navigate to "Debug Config" in admin sidebar
- **Backend Logs**: Check terminal output for detailed error messages
- **API Health**: Visit `http://localhost:8000/health`

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (including voice features)
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
- OpenAI Whisper for speech recognition
- Azure Speech Services for text-to-speech
- Streamlit for the amazing frontend framework
- FastAPI for the robust backend framework
- MongoDB for flexible data storage

---

**Built with ❤️ for modern HR teams**

*Featuring advanced AI, voice processing, and seamless user experience*