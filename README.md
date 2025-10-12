# 🤖 TalentFlow AI

> **AI-Powered HR Recruiter Application**  
> Automate resume screening, generate job descriptions, and conduct AI-driven interviews with voice capabilities

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Authentication System](#authentication-system)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Voice Features](#voice-features)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Latest Updates](#latest-updates)
- [Contributing](#contributing)

---

## 🎯 Overview

TalentFlow AI is a comprehensive HR recruitment platform that leverages artificial intelligence to streamline the hiring process. The application supports three distinct roles (User, Recruiter, Admin) and provides powerful features for modern talent acquisition with advanced voice capabilities.

### Key Capabilities

1. **Resume Screener & Candidate Matcher** - ATS-like system for automated resume screening
2. **JD Generator** - AI-powered job description creation with PDF export
3. **AI Interview** - Personalized screening interviews with resume-based question generation
4. **Voice Processing** - Local GPU-accelerated speech-to-text and Google text-to-speech
5. **AI Recruiter Assistant** - Intelligent chatbot to help recruiters navigate the platform
6. **Interview Management** - Complete interview lifecycle tracking and management

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
  - AI-powered candidate matching using Azure OpenAI
  - Match score calculation (0-100%)
  - Detailed candidate analysis
  - Export results as CSV

- **🎤 Interview Assignment**
  - Assign AI interviews to candidates
  - Auto-generate temporary user accounts
  - Configurable question count (3-10 questions)
  - **Resume Upload Required** - Candidates upload resume before interview
  - **Interview Preferences** - Configure Audio/Text modes for both interviewer and candidate
  - **Recently Assigned Interviews** - Real-time tracking with color-coded status
  - Summary metrics (Assigned/In Progress/Completed)

- **📊 Interview Results**
  - View completed interview results
  - Detailed candidate evaluations
  - Performance summaries and recommendations
  - Filter by recruiter and status

- **🤖 AI Recruiter Assistant**
  - **Sidebar Chatbot** - Available on all recruiter pages
  - **Azure OpenAI Powered** - Intelligent responses to recruiting questions
  - **Context-Aware** - Understands TalentFlow AI platform features
  - **No Memory** - Simple, session-based conversations

### For Users/Candidates

- **📊 Dashboard**
  - View assigned interviews
  - Track interview status
  - Review completed interviews

- **🎙️ AI Interview**
  - **Resume-Based Personalization** - Questions generated from candidate's resume + job description
  - **Interview Preferences** - Choose Audio/Text modes for questions and responses
  - **Voice Input**: Speak your answers (local Whisper transcription)
  - **Voice Output**: Play questions as audio (Google Text-to-Speech)
  - **Manual Audio Control** - "Play Question as Audio" button for each question
  - Real-time question generation based on candidate background
  - Immediate answer evaluation with detailed feedback
  - Comprehensive performance summary with hiring recommendation
  - **Resume Upload Required** - Upload PDF resume before starting interview

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
- **Azure OpenAI (GPT-4o-mini)** - JD generation, resume screening, interviews, and recruiter chatbot
- **LangChain** - AI workflow orchestration and prompt management
- **LangGraph** - Interview state management
- **Local Whisper (faster-whisper)** - GPU-accelerated speech-to-text (optional)
- **Dynamic Question Generation** - Resume + JD analysis for personalized interviews

### Voice Processing
- **Local Whisper** - Speech-to-text (GPU-accelerated, free, privacy-focused)
- **Google Text-to-Speech (gTTS)** - High-quality text-to-speech (free, cloud-based)
- **Audio Processing** - Real-time voice capture and playback
- **Manual Audio Control** - User-controlled audio generation and playback

### Database
- **MongoDB** - NoSQL document database

---

## 📁 Project Structure

```
TalentFlow-AI/
│
├── App/                                # Streamlit Frontend
│   ├── Admin/                          # Admin screens
│   │   └── admin.py                    # Main Dashboard (System Health & Activity)
│   │
│   ├── utils/                          # Utility modules
│   │   └── env_loader.py               # Environment variable loader
│   │
│   ├── Recruiter/                      # Recruiter screens
│   │   ├── recruiter.py                # Dashboard with AI Chatbot
│   │   ├── jd_generator.py             # JD Generator
│   │   ├── resume_screener.py          # Resume Screener
│   │   ├── interview_assignment.py     # Interview Assignment with Recently Assigned view
│   │   ├── interview_results.py        # Interview Results
│   │   └── chatbot.py                  # AI Recruiter Assistant (Sidebar Component)
│   │
│   ├── User/                           # User screens
│   │   ├── user.py                     # Dashboard
│   │   ├── ai_interview.py             # AI Interview Interface
│   │   └── user_tools.py               # Additional features
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
│   │   ├── interview_service.py        # Enhanced with resume-based question generation
│   │   ├── whisper_service.py          # Local Whisper integration
│   │   └── tts_service.py              # Google Text-to-Speech integration
│   │
│   ├── uploads/                        # File uploads
│   │   ├── jds/                        # Generated JD PDFs
│   │   ├── resumes/                    # Uploaded resumes (screening)
│   │   ├── interview_resumes/          # Interview candidate resumes
│   │   └── tts/                        # Generated audio files
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

1. **Python 3.10+** (with conda environment recommended)
2. **MongoDB** (local or cloud)
3. **Azure OpenAI Account** (required for all AI features: JD generation, resume screening, interviews, and chatbot)
4. **Internet Connection** (for Google TTS and Azure OpenAI)
5. **NVIDIA GPU** (optional, recommended for local Whisper voice features)

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
   # If using conda (recommended for avoiding environment issues)
   conda create -n talentflow python=3.10
   conda activate talentflow
   pip install -r requirements.txt
   
   # Or using regular pip
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

# Azure OpenAI (Required for JD generation, interviews, and chatbot)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini

# Local Whisper Configuration (Optional - for voice interviews)
WHISPER_USE_LOCAL=true
WHISPER_MODEL_SIZE=medium
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

---

## 🏃 Running the Application

### 1. Start MongoDB
```bash
# If using local MongoDB, ensure it's running
mongod
```

### 2. Start the Backend (FastAPI)
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

### 3. Start the Frontend (Streamlit)
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
   - Select JD from your created job descriptions
   - Enter candidate details (name and username/email)
   - Configure interview settings (3-10 questions)
   - Click "Assign Interview"
   - **System automatically creates temporary user account**
   - Share the generated email and password with candidate
   - **View Recently Assigned Interviews** section shows real-time status with color coding

5. **Use AI Assistant**
   - **Chatbot available in sidebar** on all recruiter pages
   - Ask questions about platform features
   - Get step-by-step guidance for tasks
   - Powered by Azure OpenAI for intelligent responses

6. **View Results**
   - Navigate to "Interview Results" 
   - Review completed interviews with detailed evaluations
   - Analyze candidate performance and AI recommendations
   - Filter results by status and date

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
   - **Configure Preferences**: Choose Audio/Text modes for questions and responses
   - **Upload Resume**: Required PDF upload before starting (for personalized questions)
   - **Start Interview**: Questions are generated based on your resume + job description
   - **Audio Mode**: Questions can be played as audio using "Play Question as Audio" button
   - **Voice Responses**: Speak your answers (local Whisper transcribes them)
   - **Text Responses**: Type your answers directly
   - View real-time evaluation and detailed final summary with hiring recommendation

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

### Text-to-Speech (Google TTS)
- **Technology**: Google Text-to-Speech (gTTS)
- **Quality**: High-quality neural voices
- **Languages**: Multiple language support including English
- **Cost**: Free (cloud-based)
- **Control**: Manual "Play Question as Audio" button for each question

### Voice Interview Flow
1. **Resume Upload & Analysis** - Candidate uploads resume for personalized questions
2. **AI generates personalized question** (Azure OpenAI + resume content + job description)
3. **Question displayed as text** (always visible)
4. **Optional audio playback** (user clicks "Play Question as Audio" button)
5. **Candidate responds** (voice recording or text input)
6. **Audio transcribed** (local Whisper if voice response)
7. **Answer evaluated** (Azure OpenAI with detailed feedback)
8. **Next personalized question generated** (based on resume, previous answers, interview progress)

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
- `POST /api/interview/{id}/upload-resume` - Upload resume and set interview preferences
- `POST /api/interview/{id}/start` - Start interview (with resume-based question generation)
- `POST /api/interview/{id}/answer` - Submit answer
- `GET /api/interview/{id}/details` - Get interview details and preferences
- `POST /api/interview/transcribe` - Transcribe audio (local Whisper)
- `GET /api/interview/{id}/status` - Get interview status
- `GET /api/interview/{id}/summary` - Get interview summary
- `GET /api/interview/user/{user_id}` - Get user's interviews
- `GET /api/interview/recruiter/{recruiter_id}/assigned` - Get assigned interviews by recruiter
- `GET /api/interview/recruiter/{recruiter_id}/results` - Get completed interview results

#### Voice Services
- `GET /api/interview/whisper/health` - Check Whisper service status
- `GET /api/interview/tts/health` - Check Google TTS service status
- `POST /api/interview/tts/generate` - Generate speech from text

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

3. **Azure OpenAI Errors**
   - Verify API key and endpoint in .env file
   - Check deployment name (without quotes): `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini`
   - Ensure deployment exists in Azure Portal
   - Check API version is supported

4. **Whisper Not Working**
   - Ensure NVIDIA GPU is available
   - Check CUDA installation
   - Verify faster-whisper installation
   - Check GPU memory availability

5. **TTS (Audio Questions) Not Working**
   - Install gTTS: `pip install gTTS`
   - Ensure backend is running in correct conda environment
   - Check network connectivity (gTTS requires internet)
   - Click "Play Question as Audio" button to generate audio

6. **Chatbot Not Responding**
   - Check Azure OpenAI configuration
   - Verify deployment name is correct (no quotes in .env)
   - Check backend logs for LLM initialization errors
   - Ensure .env file is loaded from project root

7. **Resume Upload Issues**
   - Ensure file is PDF format
   - Check file size (must be < 10MB)
   - Verify uploads directory exists and is writable
   - Resume is required before starting interview

### Debug Tools
- **Admin Debug Page**: Navigate to "Debug Config" in admin sidebar
- **Backend Logs**: Check terminal output for detailed error messages
- **API Health**: Visit `http://localhost:8000/health`

---

## 🎉 Acknowledgments

- **Azure OpenAI** for powerful GPT-4o-mini capabilities powering all AI features (JD generation, resume screening, interviews, and chatbot)
- **Google** for free, high-quality Text-to-Speech (gTTS) service
- **OpenAI's Whisper** for state-of-the-art speech recognition
- **Streamlit** for the amazing frontend framework enabling rapid UI development
- **FastAPI** for the robust, high-performance backend framework
- **MongoDB** for flexible document-based data storage
- **LangChain** for AI workflow orchestration and prompt management

---


## 🆕 Latest Updates

###  Enhanced Interview Experience
- ✅ **Resume-Based Personalization** - Questions generated from candidate's resume + JD
- ✅ **Interview Preferences** - Audio/Text mode selection for both interviewer and candidate
- ✅ **AI Recruiter Assistant** - Sidebar chatbot powered by Azure OpenAI
- ✅ **Recently Assigned Interviews** - Real-time tracking with color-coded status
- ✅ **Google TTS Integration** - Free, high-quality text-to-speech for questions
- ✅ **Manual Audio Control** - User-controlled question playback
- ✅ **Enhanced UI** - Better interview flow and user experience
- ✅ **Improved Error Handling** - Better diagnostics and user feedback