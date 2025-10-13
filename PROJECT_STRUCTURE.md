# TalentFlow AI - Project Structure Documentation

## 📁 Complete Project Structure Overview

This document provides detailed explanations of every folder and file in the TalentFlow AI project, including their purpose, functionality, and interactions.

---

## 🏗️ Root Directory

### Main Files

**`.env`**
- **Purpose**: Environment variables configuration
- **Contains**: API keys, database connections, service configurations
- **Key Variables**: Azure OpenAI credentials, MongoDB URI, Whisper settings
- **Used By**: All services for configuration loading

**`requirements.txt`**
- **Purpose**: Python package dependencies
- **Contains**: All required packages with specific versions
- **Key Dependencies**: FastAPI, Streamlit, LangChain, PyTorch, gTTS
- **Usage**: `pip install -r requirements.txt`

**`start_backend.bat`**
- **Purpose**: Windows batch script to start the backend server
- **Functionality**: Launches FastAPI server with uvicorn
- **Usage**: Double-click or run from command line

**`start_frontend.bat`**
- **Purpose**: Windows batch script to start the frontend
- **Functionality**: Launches Streamlit application
- **Usage**: Double-click or run from command line

### Development Files

**`hi.py`**
- **Purpose**: LangGraph AI Interview testing (Text-based)
- **Functionality**: Standalone interview testing without web interface
- **Used For**: Development and debugging interview logic

**`hi2.py`**
- **Purpose**: LangGraph AI Interview testing (Voice-based)
- **Functionality**: Tests voice input/output capabilities
- **Used For**: Voice feature development and testing

**`hi3.py`**
- **Purpose**: Azure Speech Services testing
- **Functionality**: Tests TTS and STT capabilities
- **Used For**: Voice service debugging

**`test.ipynb`**
- **Purpose**: Jupyter notebook for development and testing
- **Contains**: Code experiments, API testing, feature prototyping
- **Used For**: Interactive development and debugging

**`new.py`**
- **Purpose**: Temporary development file
- **Contains**: Quick tests or code snippets
- **Status**: Development utility file

---

## 📱 App Directory - Frontend (Streamlit)

### Purpose
Contains all Streamlit-based user interfaces for different user roles.

### Core Files

**`streamlit_app.py`**
- **Purpose**: Main entry point for the Streamlit application
- **Functionality**: 
  - User authentication and login
  - Role-based routing (Admin/Recruiter/User)
  - Session state management
  - Navigation between different user interfaces
- **Key Features**: Automatic role detection, secure authentication

**`settings.py`**
- **Purpose**: Application-wide settings and configuration
- **Contains**: UI settings, API endpoints, global configurations
- **Used By**: All other frontend components

**`debug_config.py`**
- **Purpose**: Debug configuration interface (Admin only)
- **Functionality**: 
  - Display backend configuration
  - Test API connections
  - Show environment variables
  - System health monitoring
- **Access Level**: Admin users only

### `images/` Directory
- **Purpose**: Static assets for the UI
- **Files**:
  - `horizontal_blue.png` - Logo/branding image
  - `icon_blue.png` - Application icon
- **Used By**: All frontend pages for branding

### `utils/` Directory

**`env_loader.py`**
- **Purpose**: Centralized environment variable loading utility
- **Functionality**: 
  - Loads .env file from project root regardless of execution location
  - Ensures consistent environment variable access across all components
- **Used By**: All frontend components that need API configurations

---

## 👨‍💼 Admin Directory

### Purpose
Administrative interfaces for system management and monitoring.

**`admin.py`**
- **Purpose**: Main admin dashboard with system monitoring
- **Functionality**: 
  - System health monitoring (Backend API, MongoDB status)
  - Recent system activity display
  - Configuration overview
  - Database collections information
  - Navigation to settings and debug config
- **Features**: 
  - Real-time health checks
  - Recent job descriptions display via API
  - System configuration reference
  - Database collections list
- **Access Level**: Admin only

---

## 👨‍💻 Recruiter Directory

### Purpose
Recruiter-specific interfaces for managing the entire recruitment process.

**`recruiter.py`**
- **Purpose**: Main recruiter dashboard with AI chatbot
- **Functionality**: 
  - Quick stats and metrics
  - Recent activity overview
  - Navigation to all recruiter tools
  - **AI Chatbot Sidebar**: Intelligent assistant for platform help
- **Enhanced Features**: 
  - Real-time metrics
  - AI assistant integration
  - Quick action buttons

**`chatbot.py`**
- **Purpose**: AI-powered recruiter assistant component
- **Functionality**: 
  - Azure OpenAI powered conversational AI
  - Context-aware responses about platform features
  - Step-by-step guidance for recruiting tasks
  - Session-based conversations (no memory persistence)
- **Technical Details**: 
  - Uses Azure OpenAI GPT-4o-mini
  - LangChain prompt templates
  - Dynamic environment loading
  - Error handling with user-friendly messages

**`jd_generator.py`**
- **Purpose**: AI-powered Job Description Generator
- **Functionality**: 
  - Create professional job descriptions using AI
  - Customizable parameters (title, tone, skills, responsibilities)
  - PDF generation and download
  - View previously generated JDs
- **AI Integration**: Azure OpenAI for content generation, FPDF for PDF creation

**`resume_screener.py`**
- **Purpose**: Batch resume screening with top-K ranking system
- **Functionality**: 
  - Upload multiple PDF resumes
  - AI-powered semantic similarity ranking using Azure OpenAI embeddings + ChromaDB
  - Top-K selection slider (1-20 candidates, default: 5)
  - Similarity score calculation (0-100% with decimals)
  - Returns only the most similar candidates
  - Detailed analysis and recommendations
  - CSV export for top candidates
- **AI Integration**: Azure OpenAI embeddings (text-embedding-3-large) + ChromaDB vector search

**`interview_assignment.py`**
- **Purpose**: Interview assignment and management interface
- **Functionality**: 
  - Assign AI interviews to candidates
  - Configure interview parameters (3-10 questions)
  - Auto-generate temporary candidate accounts
  - **Recently Assigned Interviews**: Real-time tracking with color-coded status
  - Summary metrics and progress monitoring
- **Enhanced Features**: 
  - Live status updates
  - Color-coded interview states
  - Comprehensive candidate tracking

**`interview_results.py`**
- **Purpose**: Interview results analysis and review
- **Functionality**: 
  - View completed interview results
  - Detailed candidate evaluations
  - Performance summaries with AI recommendations
  - Filter and sort results
- **Features**: Interview transcripts, rating analysis, hiring recommendations

---

## 👤 User Directory

### Purpose
Candidate-facing interfaces for taking interviews and viewing assignments.

**`user.py`**
- **Purpose**: User/Candidate dashboard
- **Functionality**: 
  - View assigned interviews
  - Track interview status and progress
  - Access completed interview summaries
  - Navigation to interview interface
- **Features**: Interview history, status tracking, results viewing

**`ai_interview.py`**
- **Purpose**: Enhanced AI Interview interface with voice and personalization
- **Functionality**: 
  - **Interview Configuration**: Audio/Text mode selection for questions and responses
  - **Resume Upload**: Required PDF upload for personalized questions
  - **Dynamic Question Display**: Questions generated from resume + job description
  - **Manual Audio Control**: "Play Question as Audio" button for each question
  - **Dual Response Modes**: Voice recording or text input
  - **Real-time Evaluation**: Immediate feedback on answers
  - **Progress Tracking**: Accurate question counting and completion status
- **Technical Features**: 
  - Google TTS integration for question audio
  - Local Whisper for voice transcription
  - Session state management
  - Real-time API communication
  - Audio player integration

**`user_tools.py`**
- **Purpose**: Additional user features and demonstrations
- **Functionality**: Extended user capabilities and feature testing
- **Used For**: Feature demonstrations and testing

---

## 🔧 Backend Directory

### Purpose
FastAPI-based REST API backend providing all business logic and data processing.

**`main.py`**
- **Purpose**: FastAPI application entry point
- **Functionality**: 
  - Application initialization and configuration
  - CORS middleware setup
  - Static file serving (uploads, TTS audio)
  - Route registration
  - Database connection management
  - Health check endpoint
- **Features**: Auto-reload, logging, error handling

**`create_user.py`**
- **Purpose**: User creation utility script
- **Functionality**: 
  - Interactive user creation (Admin/Recruiter)
  - Password hashing and secure storage
  - Database user insertion
  - Role assignment
- **Usage**: `python create_user.py`

---

## 🗄️ Database Layer (`db/`)

**`mongodb.py`**
- **Purpose**: MongoDB connection and management
- **Functionality**: 
  - Async MongoDB client setup using Motor
  - Database connection lifecycle management
  - Connection pooling and error handling
  - Database health checking
- **Used By**: All backend services for data persistence

---

## 📊 Models Directory (`models/`)

### Purpose
Pydantic data models for request/response validation and database schemas.

**`user_model.py`**
- **Purpose**: User authentication and profile models
- **Contains**: 
  - User registration/login requests
  - User profile data structures
  - Authentication response models
  - Role-based user schemas
- **Features**: Password hashing, role validation, session management

**`jd_model.py`**
- **Purpose**: Job Description data models
- **Contains**: 
  - JD generation request schemas
  - JD response and database models
  - PDF file handling
  - Validation rules for job parameters
- **Used For**: API validation, database storage, response formatting

**`resume_model.py`**
- **Purpose**: Resume screening and candidate data models
- **Contains**: 
  - Resume screening request schemas
  - Candidate profile extraction models
  - Screening result with similarity_score and rank fields
  - Batch processing models with top_k parameter
- **AI Integration**: Structured data extraction models for LLM parsing

**`interview_model.py`**
- **Purpose**: AI Interview data models and schemas
- **Contains**: 
  - Interview assignment requests
  - Interview session management
  - **Enhanced Fields**: `interviewer_mode`, `user_mode`, `resume_path`, `resume_content`
  - Conversation history and evaluation models
  - Interview status and progress tracking
- **New Features**: Interview preferences, resume integration, audio mode support

---

## 🛠️ Routes Directory (`routes/`)

### Purpose
FastAPI route handlers for all API endpoints.

**`auth_routes.py`**
- **Purpose**: Authentication and user management API endpoints
- **Endpoints**: 
  - `POST /auth/login` - User authentication
  - `POST /auth/register` - User registration
  - `GET /auth/user/{user_id}` - User profile retrieval
  - `POST /auth/cleanup-expired` - Temporary user cleanup
- **Features**: JWT handling, password validation, role-based access

**`jd_routes.py`**
- **Purpose**: Job Description generation and management
- **Endpoints**: 
  - `POST /jd/generate` - AI-powered JD generation
  - `GET /jd/{jd_id}` - Retrieve specific JD
  - `GET /jd/recruiter/{recruiter_id}` - Get recruiter's JDs
  - `GET /jd/all` - Get all JDs (admin)
- **Features**: PDF generation, file storage, recruiter filtering

**`resume_routes.py`**
- **Purpose**: Resume screening with top-K ranking
- **Endpoints**: 
  - `POST /resume/screen` - Batch resume screening with top_k parameter
  - `GET /resume/results/{recruiter_id}` - Get screening results
  - `GET /resume/detail/{resume_id}` - Detailed screening result
- **Features**: PDF processing, ChromaDB vector storage, top-K selection, batch ranking

**`interview_routes.py`**
- **Purpose**: Enhanced AI Interview management and voice services
- **Core Endpoints**: 
  - `POST /interview/assign` - Assign interview to candidate
  - `POST /interview/{id}/upload-resume` - **New**: Upload resume and set preferences
  - `POST /interview/{id}/start` - Start interview with resume-based questions
  - `POST /interview/{id}/answer` - Submit answer and get next question
  - `GET /interview/{id}/details` - **New**: Get interview preferences and details
  - `GET /interview/{id}/status` - Get current interview status
  - `GET /interview/{id}/summary` - Get final interview summary
- **Management Endpoints**:
  - `GET /interview/user/{user_id}` - Get user's interviews
  - `GET /interview/recruiter/{recruiter_id}/assigned` - **New**: Get assigned interviews
  - `GET /interview/recruiter/{recruiter_id}/results` - Get completed results
- **Voice Service Endpoints**:
  - `POST /interview/transcribe` - Audio-to-text using local Whisper
  - `GET /interview/whisper/health` - Check Whisper service
  - `POST /interview/tts/generate` - **New**: Text-to-speech using Google TTS
  - `GET /interview/tts/health` - **New**: Check TTS service status
- **Enhanced Features**: Resume processing, preference management, voice integration

---

## ⚙️ Services Directory (`services/`)

### Purpose
Business logic layer containing all AI and processing services.

**`auth_service.py`**
- **Purpose**: Authentication and user management business logic
- **Functionality**: 
  - User registration and login validation
  - Password hashing using bcrypt
  - Temporary user account creation for interviews
  - Session management and role validation
  - Account cleanup for expired temporary users
- **Database Integration**: MongoDB user collection operations

**`jd_service.py`**
- **Purpose**: Job Description generation service
- **Functionality**: 
  - AI-powered JD content generation using Azure OpenAI
  - PDF creation with professional formatting
  - Template-based prompt engineering
  - File management and storage
- **AI Integration**: 
  - Uses Azure OpenAI GPT-4o-mini
  - LangChain prompt templates
  - Structured output generation
- **Enhanced Features**: Improved .env loading from project root

**`resume_service.py`**
- **Purpose**: Resume screening with top-K ranking system
- **Functionality**: 
  - PDF text extraction using pypdf/PyPDF2
  - Embedding generation using Azure OpenAI (text-embedding-3-large)
  - Vector storage in ChromaDB
  - Semantic similarity search with L2 distance
  - Top-K candidate selection and ranking
  - Candidate name extraction and recommendation generation
- **AI Integration**: 
  - Azure OpenAI embeddings (3072 dimensions)
  - ChromaDB for vector storage and similarity search
  - Batch processing for efficient ranking
- **Enhanced Features**: rank_resumes(), process_resume(), similarity scoring

**`interview_service.py`**
- **Purpose**: Enhanced AI Interview orchestration with resume personalization
- **Functionality**: 
  - **Resume-Based Interview Planning**: Generates interview topics from resume + JD
  - **Personalized Question Generation**: References specific resume content
  - **Dynamic Question Flow**: Adapts questions based on candidate background
  - **Answer Evaluation**: Detailed feedback and scoring (1-5 scale)
  - **Interview Summarization**: Final recommendations (Proceed/Hold/Reject)
- **AI Integration**: 
  - Azure OpenAI GPT-4o-mini for all AI operations
  - LangChain prompt templates for consistency
  - Structured output using Pydantic models
- **Enhanced Features**: 
  - Resume content analysis (up to 2000 chars)
  - Project root environment loading
  - Context-aware question generation

**`whisper_service.py`**
- **Purpose**: Local speech-to-text processing
- **Functionality**: 
  - GPU-accelerated voice transcription
  - Local privacy-focused processing
  - Multiple audio format support
  - Real-time transcription capabilities
- **Technical Details**: 
  - Uses faster-whisper library
  - CUDA GPU acceleration
  - Medium model for balance of speed/accuracy
  - No API costs - completely local

**`tts_service.py`** *(New)*
- **Purpose**: Text-to-speech service for interview questions
- **Functionality**: 
  - Convert interview questions to audio using Google TTS
  - Audio file generation and storage
  - Service health monitoring
  - Dynamic availability checking
- **Technical Details**: 
  - Uses Google TTS (gTTS) - free, cloud-based
  - Generates MP3 audio files
  - Saves to uploads/tts/ directory
  - Internet connection required
- **Integration**: Called when users click "Play Question as Audio"

---

## 🛣️ Admin Interface Details

**`Admin/admin.py`**
- **Purpose**: Central admin dashboard with system monitoring
- **Main Features**: 
  - **System Health Monitoring**: Real-time checks for Backend API and MongoDB connection
  - **Recent Activity**: Display of recent job descriptions via API
  - **System Configuration**: Overview of configured services (Azure OpenAI, Google TTS, Whisper)
  - **Database Collections**: List of active MongoDB collections
  - **Navigation**: Quick access to Settings and Debug Config
- **Technical Details**: 
  - API health checks with error handling
  - Dynamic recent JDs fetching from backend
  - Expandable configuration and database information sections
- **Access Level**: Admin only

---

## 📋 Recruiter Interface Details

**`Recruiter/recruiter.py`**
- **Purpose**: Enhanced recruiter dashboard with AI assistant
- **Main Sections**: 
  - Quick stats (JDs, resumes screened, active interviews)
  - Recent activity feed
  - Quick action navigation
  - **AI Chatbot Sidebar**: Intelligent assistant
- **Chatbot Features**: 
  - Azure OpenAI powered responses
  - Platform-specific guidance
  - Step-by-step help for recruiter tasks

**`Recruiter/jd_generator.py`**
- **Purpose**: Professional job description creation
- **Interface Sections**: 
  - Job details input form
  - Company tone selection
  - Responsibilities and skills definition
  - Generated JD display with formatting
  - PDF download and clipboard copy
  - Previous JDs history
- **Workflow**: Input → AI Generation → Preview → Download/Save

**`Recruiter/resume_screener.py`**
- **Purpose**: Batch resume analysis with top-K ranking
- **Features**: 
  - Multiple resume upload (PDF)
  - JD selection or manual input
  - Top-K slider (1-20, default: 5)
  - Batch processing with progress indicators
  - Similarity score display with decimals (e.g., 87.3%)
  - Ranking positions (#1, #2, #3...)
  - Detailed candidate analysis
  - CSV export for top candidates only
- **AI Processing**: Azure OpenAI embeddings + ChromaDB semantic similarity ranking

**`Recruiter/interview_assignment.py`**
- **Purpose**: Interview assignment with enhanced tracking
- **Main Features**: 
  - Interview assignment form
  - JD selection from recruiter's library
  - Candidate details input
  - Question count configuration (3-10)
  - Automatic temporary account creation
  - **Recently Assigned Interviews Section**: 
    - Real-time status tracking
    - Color-coded display (Green=Completed, Yellow=In Progress, Blue=Assigned)
    - Progress metrics (questions completed/total)
    - Summary statistics
- **Enhanced UI**: Interactive table, status indicators, progress tracking

**`Recruiter/interview_results.py`**
- **Purpose**: Comprehensive interview results analysis
- **Features**: 
  - Completed interview results display
  - Candidate performance analysis
  - AI hiring recommendations
  - Interview transcript viewing
  - Filtering and sorting options
- **Data Display**: Detailed evaluations, scoring, recommendations

---

## 👥 User Interface Details

**`User/user.py`**
- **Purpose**: Candidate dashboard and interview access
- **Features**: 
  - View assigned interviews
  - Interview status tracking
  - Access to interview interface
  - Completed interview summaries
- **User Experience**: Clean, simple interface focused on interview tasks

**`User/ai_interview.py`**
- **Purpose**: Advanced AI Interview interface with personalization and voice
- **Core Features**: 
  - **Interview Configuration**: Preference selection (Audio/Text modes)
  - **Resume Upload**: Required PDF upload before starting
  - **Personalized Questions**: Generated from resume + job description
  - **Audio Integration**: Manual "Play Question as Audio" button
  - **Dual Response Modes**: Voice recording or text input
  - **Real-time Progress**: Accurate question counting and completion tracking
- **Voice Features**: 
  - Google TTS for question audio
  - Local Whisper for voice answer transcription
  - Audio player integration
  - Manual audio control
- **Enhanced UI**: 
  - Preference indicators
  - Progress bars
  - Tab-based input methods
  - Error handling and feedback
- **Technical Integration**: 
  - Resume text extraction and analysis
  - Dynamic question generation API calls
  - Audio file handling and playback
  - Session state management

**`User/user_tools.py`**
- **Purpose**: Additional user features and capabilities
- **Functionality**: Extended user interface features
- **Used For**: Feature testing and additional user tools

---

## 🔌 Backend Services Deep Dive

### Data Flow Architecture

**Authentication Flow:**
```
streamlit_app.py → auth_routes.py → auth_service.py → mongodb.py
```

**Interview Flow:**
```
ai_interview.py → interview_routes.py → interview_service.py → mongodb.py
                                    ↓
                      tts_service.py (for audio)
                                    ↓
                      whisper_service.py (for voice input)
```

**JD Generation Flow:**
```
jd_generator.py → jd_routes.py → jd_service.py → Azure OpenAI → PDF Generation
```

**Resume Screening Flow:**
```
resume_screener.py → resume_routes.py → resume_service.py → Azure OpenAI Embeddings → ChromaDB → Top-K Ranking
```

### AI Service Integration

**Azure OpenAI Usage:**
- **JD Generation**: Creative content generation with customizable tone
- **Interview Questions**: Personalized question generation based on resume analysis
- **Answer Evaluation**: Detailed feedback and scoring
- **Interview Summary**: Final recommendations with reasoning
- **Recruiter Chatbot**: Intelligent platform assistance

**Azure OpenAI Integration:**
- **Resume Screening**: Semantic similarity using text-embedding-3-large embeddings + ChromaDB
- **Top-K Ranking**: Vector search for finding most similar candidates
- **Candidate Analysis**: Recommendation generation using GPT-4o-mini

---

## 📁 Uploads Directory Structure

**`uploads/`** *(Backend root)*
- **Purpose**: Central file storage for all uploaded and generated content
- **Access**: Served as static files by FastAPI at `/uploads/`

**`uploads/jds/`**
- **Purpose**: Generated job description PDF files
- **File Format**: `jd_JobTitle_YYYYMMDD_HHMMSS.pdf`
- **Generated By**: JD Generator service
- **Access**: Download links in recruiter interface

**`uploads/resumes/`**
- **Purpose**: Resume PDFs uploaded for screening
- **File Format**: `CandidateName_YYYYMMDD_HHMMSS.pdf`
- **Used By**: Resume screening service
- **Processing**: Text extraction and AI analysis

**`uploads/interview_resumes/`** *(New)*
- **Purpose**: Resume PDFs uploaded by interview candidates
- **File Format**: `resume_CandidateName_YYYYMMDD_HHMMSS.pdf`
- **Used By**: Interview service for personalized question generation
- **Processing**: Text extraction and context analysis

**`uploads/tts/`** *(New)*
- **Purpose**: Generated audio files for interview questions
- **File Format**: `tts_randomhex.mp3`
- **Generated By**: Google TTS service
- **Access**: Served directly to frontend audio players
- **Cleanup**: Files are temporary (could implement cleanup job)

---

## 🔄 Data Models and Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String,
  password_hash: String (bcrypt),
  name: String,
  role: "Admin" | "Recruiter" | "User",
  is_temp: Boolean,
  expires_at: Date (for temp users),
  interview_id: String (for temp users),
  created_at: Date,
  updated_at: Date
}
```

### Interviews Collection (Enhanced)
```javascript
{
  _id: ObjectId,
  user_id: String,
  candidate_name: String,
  candidate_username: String,
  jd_id: String,
  recruiter_id: String,
  status: "Assigned" | "In Progress" | "Completed" | "Cancelled",
  interview_plan: [String],
  conversation_history: [{question: String, answer: String}],
  evaluations: [{rating: Number, feedback: String}],
  final_summary: {recommendation: String, summary_text: String},
  max_questions: Number,
  
  // NEW ENHANCED FIELDS
  interviewer_mode: "Audio" | "Text",
  user_mode: "Audio" | "Text", 
  resume_path: String,
  resume_content: String,
  
  started_at: Date,
  completed_at: Date,
  created_at: Date,
  updated_at: Date
}
```

### Job Descriptions Collection
```javascript
{
  _id: ObjectId,
  job_title: String,
  company_tone: String,
  responsibilities: String,
  skills: String,
  experience: String,
  recruiter_id: String,
  generated_content: String,
  pdf_path: String,
  created_at: Date,
  updated_at: Date
}
```

### Resume Screening Results Collection
```javascript
{
  _id: ObjectId,
  recruiter_id: String,
  jd_id: String,
  jd_text: String,
  candidate_name: String,
  candidate_email: String,
  resume_path: String,
  similarity_score: Number (0-100, with decimals),
  rank: Number (1, 2, 3...),
  summary: String,
  status: "Strong Match" | "Potential Fit" | "Possible Match",
  candidate_data: Object,
  created_at: Date
}
```

---

## 🎯 Key Integration Points

### Environment Variable Loading
- **Root Level**: All services now use consistent .env loading from project root
- **Utility**: `App/utils/env_loader.py` ensures consistent environment access
- **Problem Solved**: Eliminates path-dependent environment variable issues

### Cross-Service Communication
- **Frontend to Backend**: RESTful API calls with proper error handling
- **Service to Service**: Internal Python imports and function calls
- **Database Access**: Async MongoDB operations using Motor
- **File Storage**: FastAPI static file serving for uploads and audio

### AI Service Orchestration
- **Interview Flow**: interview_service.py orchestrates all AI operations
- **Resume Analysis**: resume_service.py handles embedding generation, vector storage, and top-K ranking
- **Voice Processing**: Separate services for STT (whisper) and TTS (Google)
- **Prompt Engineering**: Consistent LangChain templates across services

---

## 🚀 Feature Interaction Map

### Interview Assignment → Candidate Experience
```
Recruiter assigns interview
    ↓
Temporary account created
    ↓
Candidate receives credentials
    ↓
Login → Configure preferences → Upload resume
    ↓
Start interview → Personalized questions generated
    ↓
Answer questions (text/voice) → Get evaluations
    ↓
Complete interview → Recruiter sees results
```

### Voice Feature Integration
```
User clicks "Play Question as Audio"
    ↓
Frontend calls /api/interview/tts/generate
    ↓
Backend uses Google TTS service
    ↓
Audio file saved to uploads/tts/
    ↓
Frontend displays audio player
    ↓
User hears question spoken
```

### Resume-Based Personalization
```
Candidate uploads resume PDF
    ↓
Backend extracts text using PyPDF2
    ↓
Text stored in interview record
    ↓
Interview starts → AI generates plan using resume + JD
    ↓
Each question references specific resume content
    ↓
Questions become highly personalized and relevant
```

---

## 📊 Performance Considerations

### File Storage
- **PDFs**: Stored locally, served via FastAPI static files
- **Audio**: Temporary MP3 files, could implement cleanup
- **Resume Text**: Stored in MongoDB for quick access

### AI Service Usage
- **Azure OpenAI**: Used for all AI features (JD generation, resume screening, interviews, and chatbot)
- **Google TTS**: Free tier has usage limits
- **Local Whisper**: GPU-intensive but free (optional for voice interviews)

### Database Performance
- **Indexes**: Recommended on user_id, recruiter_id, interview_id
- **Aggregation**: Used for statistics and filtering
- **Async Operations**: All database calls are non-blocking

---

## 🔍 Development Workflow

### Adding New Features
1. **Define Pydantic Models** (`models/` directory)
2. **Create Service Logic** (`services/` directory)
3. **Add API Routes** (`routes/` directory)
4. **Build Frontend Interface** (`App/` directory)
5. **Update Documentation** (this file and README.md)

### Testing New Features
1. **Unit Testing**: Test individual services
2. **API Testing**: Use FastAPI docs at `/docs`
3. **Integration Testing**: Test full user workflows
4. **Voice Testing**: Test audio generation and transcription

### Debugging Process
1. **Backend Logs**: Check FastAPI terminal output
2. **Frontend Errors**: Check Streamlit browser console
3. **Database Queries**: Use MongoDB Compass or logs
4. **API Testing**: Use curl or Postman for endpoint testing

---

This documentation covers every folder and file in the TalentFlow AI project, providing complete understanding of the system architecture, data flow, and feature implementation.
