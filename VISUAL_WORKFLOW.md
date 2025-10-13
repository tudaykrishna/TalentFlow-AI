# 🎨 TalentFlow AI - Visual Workflows

> **Comprehensive visual diagrams for all major system functionalities**

---

## 📋 Table of Contents

- [Resume Screening Architecture](#-resume-screening-architecture)
- [JD Generation Workflow](#-jd-generation-workflow)
- [Interview Assignment Workflow](#-interview-assignment-workflow)
- [AI Interview Workflow](#-ai-interview-workflow)
- [Authentication System](#-authentication-system)
- [AI Recruiter Assistant](#-ai-recruiter-assistant)

---

## 🔍 Resume Screening Architecture

### How the Top-K Ranking System Works

#### **Visual Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│  RECRUITER UPLOADS 15 RESUMES + JOB DESCRIPTION                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Text Extraction (pypdf/PyPDF2)                         │
│  ├─ Resume 1 → "5 years Python, ML engineer..."                 │
│  ├─ Resume 2 → "Java developer, 3 years..."                     │
│  └─ Resume 3-15...                                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Embedding Generation (Azure OpenAI)                    │
│  ├─ JD → [0.23, -0.41, 0.15, ...] (3072 dimensions)            │
│  ├─ Resume 1 → [0.21, -0.39, 0.14, ...]                        │
│  ├─ Resume 2 → [0.05, -0.12, 0.33, ...]                        │
│  └─ Resume 3-15...                                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Vector Storage (ChromaDB)                              │
│  ├─ Store all 15 resume embeddings                              │
│  └─ Persistent storage in resume_db/                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Similarity Search (L2 Distance)                        │
│  ├─ Compare JD embedding with all resume embeddings             │
│  ├─ Resume 1: Distance 0.15 → Similarity 87.3%                 │
│  ├─ Resume 7: Distance 0.22 → Similarity 82.1%                 │
│  ├─ Resume 3: Distance 0.28 → Similarity 78.5%                 │
│  └─ ... (all 15 ranked)                                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Top-K Selection (K=5)                                  │
│  ├─ #1: Resume 1 (87.3%) - Strong Match                        │
│  ├─ #2: Resume 7 (82.1%) - Strong Match                        │
│  ├─ #3: Resume 3 (78.5%) - Potential Fit                       │
│  ├─ #4: Resume 12 (71.2%) - Potential Fit                      │
│  └─ #5: Resume 5 (68.9%) - Potential Fit                       │
│                                                                  │
│  ❌ Resumes 2, 4, 6, 8-11, 13-15: Not in top 5, not saved      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESULT: Top 5 Candidates Returned to Recruiter                 │
│  ✅ Saved to MongoDB + File System                              │
│  ✅ Available for download as CSV                               │
└─────────────────────────────────────────────────────────────────┘
```

### Technical Implementation

1. **Text Extraction**
   - Uses `pypdf` (preferred) or `PyPDF2` (fallback)
   - Extracts all text content from PDF resumes
   - Validates minimum text length (>50 characters)

2. **Embedding Generation**
   - Azure OpenAI `text-embedding-3-large` model
   - Converts resume text → 3072-dimensional vector
   - Converts JD text → 3072-dimensional vector
   - Single JD embedding for batch (efficient)

3. **Vector Storage (ChromaDB)**
   - Stores all resume embeddings in `resume_db/` directory
   - Persistent storage for future queries
   - Fast similarity search with L2 distance

4. **Similarity Calculation**
   - L2 (Euclidean) distance between vectors
   - Converted to similarity score (0-100%)
   - Formula: `similarity = 100 * (1 - min(distance, 2.0) / 2.0)`

5. **Ranking & Selection**
   - All resumes ranked by similarity score
   - Top K candidates selected
   - Sequential ranking assigned (#1, #2, #3...)
   - Status categorization:
     - 80-100%: "Strong Match"
     - 60-79%: "Potential Fit"
     - <60%: "Possible Match"

### Benefits

| Aspect | Old System | New System |
|--------|-----------|------------|
| **Processing** | Sequential | Batch |
| **Results** | All resumes | Top K only |
| **Scoring** | Simple match % | Semantic similarity |
| **Scalability** | Poor (N operations) | Excellent (1 query) |
| **User Experience** | Information overload | Focused on best |
| **Accuracy** | Absolute scores | Relative ranking |

### Performance

- **15 resumes**: ~10-15 seconds
- **50 resumes**: ~30-40 seconds
- **100 resumes**: ~60-90 seconds

*Processing time depends on PDF size, text length, and GPU availability*

---

## 📝 JD Generation Workflow

### Complete Job Description Creation Process

#### **Visual Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│  RECRUITER INPUTS JOB DETAILS                                   │
│  ├─ Job Title: "Senior Python Developer"                        │
│  ├─ Experience: "5-8 years"                                     │
│  ├─ Key Skills: "Python, FastAPI, AI/ML"                       │
│  ├─ Responsibilities: "Lead backend development..."            │
│  └─ Company Tone: "Professional & Innovative"                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Input Validation                                       │
│  ├─ Check required fields                                       │
│  ├─ Validate experience format                                  │
│  └─ Ensure minimum content length                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Azure OpenAI Processing (GPT-4o-mini)                  │
│  ├─ Prompt Engineering                                          │
│  │   └─ "Generate a professional JD for..."                    │
│  ├─ Context Injection (company tone, industry standards)        │
│  └─ Generate comprehensive JD text                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Content Structuring                                    │
│  ├─ Job Title & Overview                                        │
│  ├─ Key Responsibilities (bullet points)                        │
│  ├─ Required Skills & Qualifications                            │
│  ├─ Preferred Skills                                            │
│  ├─ Experience Requirements                                     │
│  └─ Company Culture & Benefits                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: PDF Generation                                         │
│  ├─ Format content with professional styling                    │
│  ├─ Add company branding (if available)                         │
│  ├─ Generate PDF using reportlab/fpdf                           │
│  └─ Save to uploads/jds/                                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Database Storage (MongoDB)                             │
│  ├─ Store JD text content                                       │
│  ├─ Store metadata (recruiter_id, timestamp)                    │
│  ├─ Store PDF file path                                         │
│  └─ Generate unique JD ID                                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESULT: JD Created & Available                                 │
│  ✅ Display in Streamlit UI                                     │
│  ✅ Download PDF button enabled                                 │
│  ✅ Ready for resume screening                                  │
│  ✅ Saved for interview assignment                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Interview Assignment Workflow

### From Assignment to Candidate Access

#### **Visual Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│  RECRUITER ASSIGNS INTERVIEW                                    │
│  ├─ Select Job Description                                      │
│  ├─ Enter Candidate Name: "John Doe"                           │
│  ├─ Enter Candidate Email/Username: "john.doe@email.com"       │
│  └─ Configure: 5 questions, Audio mode                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Temporary User Creation                                │
│  ├─ Generate temp email: candidate_xxxxx_interviewid@...       │
│  ├─ Generate secure password: "TF_xY9#mK2@pL..."              │
│  ├─ Set expiry: 24 hours from now                              │
│  ├─ Hash password (bcrypt)                                      │
│  └─ Save to MongoDB users collection                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Interview Document Creation                            │
│  ├─ Create interview record in MongoDB                          │
│  ├─ Link to JD and recruiter                                    │
│  ├─ Store candidate details                                     │
│  ├─ Set status: "Assigned"                                      │
│  ├─ Store preferences (audio/text modes)                        │
│  └─ Generate unique interview ID                                │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Credentials Display                                    │
│  ├─ Show temp email in UI                                       │
│  ├─ Show temp password (one-time display)                       │
│  ├─ Show expiry time                                            │
│  └─ Provide copy-to-clipboard buttons                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Recruiter Shares Credentials                           │
│  ├─ Send email to candidate (manual or automated)               │
│  ├─ Include login URL: http://localhost:8501                   │
│  ├─ Include temp credentials                                    │
│  └─ Include expiry notice                                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Candidate Login                                        │
│  ├─ Candidate enters temp email & password                      │
│  ├─ System validates credentials                                │
│  ├─ Check expiry (< 24 hours)                                  │
│  ├─ Redirect to User dashboard                                  │
│  └─ Show assigned interview                                     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESULT: Interview Ready for Candidate                          │
│  ✅ Candidate can upload resume                                 │
│  ✅ Candidate can configure preferences                         │
│  ✅ Interview appears in "Recently Assigned" (recruiter view)   │
│  ✅ Status updates in real-time                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎙️ AI Interview Workflow

### Complete Interview Process (Resume-Based)

#### **Visual Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│  CANDIDATE STARTS INTERVIEW                                     │
│  └─ Status: "Assigned" → Clicks "Start Interview"              │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Resume Upload (Required)                               │
│  ├─ Upload PDF resume                                           │
│  ├─ Extract text from resume (pypdf/PyPDF2)                    │
│  ├─ Parse resume content                                        │
│  └─ Store in interview record                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Configure Preferences                                  │
│  ├─ Question Mode: [Audio / Text]                              │
│  ├─ Response Mode: [Voice / Text]                              │
│  └─ Save preferences to interview                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Interview Initialization (LangGraph)                   │
│  ├─ Load JD text                                                │
│  ├─ Load resume text                                            │
│  ├─ Initialize conversation state                               │
│  ├─ Set question count (from assignment)                        │
│  └─ Status: "Assigned" → "In Progress"                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Question Generation (Azure OpenAI)                     │
│  ├─ Context: JD + Resume + Previous Q&A                        │
│  ├─ Prompt: "Generate personalized interview question..."       │
│  ├─ AI analyzes candidate's experience from resume              │
│  ├─ Generate relevant, role-specific question                   │
│  └─ Question: "I see you worked on ML models at XYZ..."        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Question Display                                       │
│  ├─ Show question as text (always visible)                      │
│  │                                                               │
│  ├─ IF Audio Mode Enabled:                                      │
│  │   ├─ "Play Question as Audio" button appears                 │
│  │   ├─ User clicks button                                      │
│  │   ├─ Text-to-Speech (gTTS) generates audio                  │
│  │   └─ Audio plays in browser                                  │
│  │                                                               │
│  └─ Wait for candidate response                                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Candidate Response                                     │
│  │                                                               │
│  ├─ IF Voice Mode:                                              │
│  │   ├─ Record audio via microphone                             │
│  │   ├─ Send audio to backend                                   │
│  │   ├─ Whisper transcribes audio → text                       │
│  │   └─ Display transcribed text                                │
│  │                                                               │
│  └─ IF Text Mode:                                               │
│      ├─ Candidate types answer in text box                      │
│      └─ Submit answer                                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Answer Evaluation (Azure OpenAI)                       │
│  ├─ Context: Question + Answer + JD + Resume                    │
│  ├─ Prompt: "Evaluate this answer for..."                       │
│  ├─ AI analyzes:                                                │
│  │   ├─ Relevance to question                                   │
│  │   ├─ Technical accuracy                                      │
│  │   ├─ Communication clarity                                   │
│  │   └─ Alignment with JD requirements                          │
│  ├─ Generate score (0-10)                                       │
│  └─ Generate detailed feedback                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Feedback Display                                       │
│  ├─ Show score: "8/10"                                          │
│  ├─ Show feedback: "Great explanation of..."                    │
│  └─ Update conversation state                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  LOOP: Repeat Steps 4-8                                         │
│  └─ Until all questions answered (e.g., 5/5 complete)          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: Interview Summary Generation                           │
│  ├─ Aggregate all Q&A pairs                                     │
│  ├─ Calculate overall score                                     │
│  ├─ Azure OpenAI generates:                                     │
│  │   ├─ Performance summary                                     │
│  │   ├─ Strengths & weaknesses                                  │
│  │   ├─ Hiring recommendation                                   │
│  │   └─ Areas for improvement                                   │
│  └─ Status: "In Progress" → "Completed"                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 10: Results Storage                                       │
│  ├─ Save all Q&A to MongoDB                                     │
│  ├─ Save scores and feedback                                    │
│  ├─ Save final summary                                          │
│  └─ Mark interview as complete                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESULT: Interview Complete                                     │
│  ✅ Candidate sees summary and score                            │
│  ✅ Recruiter can view results in "Interview Results"           │
│  ✅ Results available for analysis                              │
│  ✅ Temporary account expires after 24 hours                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Authentication System

### Login & Role-Based Redirection

#### **Visual Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│  USER ACCESSES APPLICATION                                      │
│  └─ URL: http://localhost:8501                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  LOGIN PAGE                                                      │
│  ├─ Enter Email: "recruiter@company.com"                        │
│  └─ Enter Password: "********"                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Credential Validation                                  │
│  ├─ Send credentials to backend API                             │
│  ├─ POST /api/auth/login                                        │
│  └─ Backend queries MongoDB users collection                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Password Verification                                  │
│  ├─ Retrieve hashed password from database                      │
│  ├─ Use bcrypt to verify password                               │
│  ├─ Check if temporary user expired (24 hours)                  │
│  └─ Validation result: [Success / Failure]                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ├─────────────────┬──────────────────┐
                  │                 │                  │
                  ▼                 ▼                  ▼
        ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
        │ ROLE: ADMIN     │ │ ROLE: USER   │ │ ROLE: RECRUITER │
        └────────┬────────┘ └──────┬───────┘ └────────┬────────┘
                 │                 │                   │
                 ▼                 ▼                   ▼
   ┌──────────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
   │  Admin Dashboard     │ │  User Dashboard │ │  Recruiter Dashboard │
   │  ├─ System Health    │ │  ├─ Interviews  │ │  ├─ JD Generator     │
   │  ├─ Analytics        │ │  ├─ Status      │ │  ├─ Resume Screener  │
   │  ├─ User Management  │ │  └─ Results     │ │  ├─ Assign Interview │
   │  └─ Debug Config     │ │                 │ │  ├─ View Results     │
   └──────────────────────┘ └─────────────────┘ │  └─ AI Assistant     │
                                                  └──────────────────────┘
```

### User Types

1. **Admin** (Permanent)
   - Created via: `python create_user.py`
   - Stored permanently in MongoDB
   - No expiry

2. **Recruiter** (Permanent)
   - Created via: `python create_user.py` or registration
   - Stored permanently in MongoDB
   - No expiry

3. **User/Candidate** (Temporary)
   - Created automatically during interview assignment
   - Expires after 24 hours
   - One-time use (auto-deleted after interview or expiry)

---

## 🤖 AI Recruiter Assistant

### Sidebar Chatbot Workflow

#### **Visual Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│  RECRUITER NAVIGATES TO ANY RECRUITER PAGE                      │
│  └─ Dashboard / JD Generator / Resume Screener / etc.           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR: AI RECRUITER ASSISTANT LOADED                         │
│  ├─ Chatbot component rendered                                  │
│  ├─ Chat history displayed (session-based)                      │
│  └─ Input box ready for questions                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  RECRUITER ASKS QUESTION                                        │
│  ├─ "How do I screen resumes?"                                  │
│  ├─ "What's the difference between top-K ranking and scoring?"  │
│  └─ "How do I assign an interview?"                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Query Processing                                       │
│  ├─ Capture user input                                          │
│  ├─ Add to conversation history                                 │
│  └─ Send to backend API                                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Azure OpenAI Processing (GPT-4o-mini)                  │
│  ├─ System Prompt: "You are an AI assistant for TalentFlow..."  │
│  ├─ Context: Platform features, user role, current page         │
│  ├─ User Query: "How do I screen resumes?"                      │
│  ├─ Generate intelligent response                               │
│  └─ Response: "To screen resumes, navigate to..."               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Response Display                                       │
│  ├─ Show AI response in chat interface                          │
│  ├─ Format with markdown (if supported)                         │
│  ├─ Add to conversation history                                 │
│  └─ Wait for next question                                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  FEATURES                                                        │
│  ├─ ✅ Context-Aware: Understands TalentFlow features           │
│  ├─ ✅ Session-Based: No persistent memory                      │
│  ├─ ✅ Always Available: On all recruiter pages                 │
│  ├─ ✅ Real-Time: Instant responses                             │
│  └─ ✅ Helpful: Step-by-step guidance                           │
└─────────────────────────────────────────────────────────────────┘
```

### Chatbot Capabilities

- ✅ **Platform Navigation**: Guide users through features
- ✅ **Feature Explanation**: Explain how each feature works
- ✅ **Troubleshooting**: Help solve common issues
- ✅ **Best Practices**: Suggest optimal workflows
- ✅ **Quick Answers**: Instant responses to common questions

---

## 🔄 System Integration Overview

### How All Components Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Streamlit)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ Admin Pages  │ │Recruiter Pages│ │  User Pages  │           │
│  └──────┬───────┘ └──────┬────────┘ └──────┬───────┘           │
└─────────┼────────────────┼─────────────────┼───────────────────┘
          │                │                 │
          │                │                 │
          └────────────────┴─────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │ Auth Routes  │ │  JD Routes   │ │Resume Routes │           │
│  └──────┬───────┘ └──────┬────────┘ └──────┬───────┘           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │Interview Rtes│ │Voice Services│ │  Chatbot API │           │
│  └──────┬───────┘ └──────┬────────┘ └──────┬───────┘           │
└─────────┼────────────────┼─────────────────┼───────────────────┘
          │                │                 │
          ▼                ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
│   MongoDB       │ │  ChromaDB   │ │  Azure OpenAI    │
│  (User Data)    │ │ (Vectors)   │ │  (AI Services)   │
│                 │ │             │ │                  │
│  ├─ Users       │ │ ├─ Resume   │ │  ├─ GPT-4o-mini  │
│  ├─ JDs         │ │ │  Embeddings│ │  ├─ Embeddings  │
│  ├─ Interviews  │ │ └─ Similarity│ │  ├─ Chat        │
│  └─ Results     │ │   Search    │ │  └─ Evaluation  │
└─────────────────┘ └─────────────┘ └──────────────────┘
```

---

## 🎯 Summary

This visual workflow document provides comprehensive diagrams for:

1. ✅ **Resume Screening** - Top-K ranking with ChromaDB
2. ✅ **JD Generation** - AI-powered job description creation
3. ✅ **Interview Assignment** - Temporary user creation & assignment
4. ✅ **AI Interview** - Resume-based personalized interviews
5. ✅ **Authentication** - Role-based login & redirection
6. ✅ **AI Assistant** - Intelligent recruiter chatbot

Each workflow includes:
- Visual ASCII diagrams showing step-by-step processes
- Technical implementation details
- Key features and capabilities
- Integration points with other system components

For more information, see:
- **README.md** - Complete system documentation
- **CHANGES_SUMMARY.md** - Technical change log
- **API Documentation** - http://localhost:8000/docs
