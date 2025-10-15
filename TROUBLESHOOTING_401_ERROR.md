# 🔧 Azure OpenAI 401 Error - Troubleshooting & Solution

## ❌ Problem
Getting 401 error: "Access denied due to invalid subscription key or wrong API endpoint" when using JD Generator in Streamlit UI.

## ✅ Root Cause Identified
**Multiple backend processes running with old/stale configuration**

## 🔍 Diagnosis Results

### 1. Environment Variables - ✅ CORRECT
```
AZURE_OPENAI_API_KEY=FeN3JKDVOevPq74wTeVaImdtWDgDEBXUwAH3TvGjn3WoWu3zASdcJQQJ99BJACHYHv6XJ3w3AAAAACOGfEFW
AZURE_OPENAI_ENDPOINT=https://mazen-mgpk90ba-eastus2.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_EMBEDDING_MODEL=text-embedding-3-large
```

### 2. Direct Azure OpenAI Connection - ✅ WORKS
Test showed successful connection using native `openai` library.

### 3. LangChain Connection - ✅ WORKS
Test showed successful connection using `langchain_openai.AzureChatOpenAI`.

### 4. Backend Processes - ❌ PROBLEM FOUND
```
Two Python processes running on port 8000:
- PID 28532: Started October 10, 2025 (OLD - 4 days old!)
- PID 27172: Started October 14, 2025 (Today)
```

**The old process from October 10th might have:**
- Old .env configuration
- Expired API keys
- Old code before fixes
- Stale Azure OpenAI settings

## 🛠️ Solution

### Step 1: Kill ALL Backend Processes
```powershell
# Find processes on port 8000
netstat -ano | findstr :8000

# Kill all Python processes (use the PIDs from above)
taskkill /F /PID 28532
taskkill /F /PID 27172

# Or kill all Python processes
Get-Process python | Stop-Process -Force

# Verify port is free
netstat -ano | findstr :8000
# (Should return nothing)
```

### Step 2: Activate Correct Environment
```powershell
# Activate your conda environment with all dependencies
conda activate uday
```

### Step 3: Start Fresh Backend
```powershell
cd C:\Users\udayt\OneDrive\Desktop\TalentFlow-AI\Backend
python main.py
```

### Step 4: Verify Backend Startup
Look for these logs:
```
✅ Application started successfully
✅ JD Generator Service initialized successfully
✅ MongoDB connected successfully
```

### Step 5: Restart Streamlit (if needed)
```powershell
# In a new terminal
conda activate uday
cd C:\Users\udayt\OneDrive\Desktop\TalentFlow-AI\App
streamlit run streamlit_app.py
```

### Step 6: Test JD Generator
1. Login as recruiter
2. Go to JD Generator
3. Fill in job details
4. Click "Generate Job Description"
5. Should work now! ✅

## 🚨 Common Mistakes to Avoid

### ❌ Don't:
1. Run multiple backend instances simultaneously
2. Run backend without activating conda environment
3. Edit .env file while backend is running (needs restart)
4. Use base conda environment (missing dependencies)

### ✅ Do:
1. Always activate `uday` environment first
2. Check if port 8000 is free before starting backend
3. Restart backend after changing .env file
4. Monitor backend logs for errors

## 🔍 How to Check if Problem Persists

### Quick Test
```python
# Run this test script
python test_azure_connection.py

# Should show:
# ✅ SUCCESS! Response: Connection successful!
```

### Full Test
```python
# Test LangChain (what JD service uses)
python test_langchain_connection.py

# Should show:
# ✅ SUCCESS with deployment_name: Test 1 works!
```

## 📝 Prevention Checklist

Before starting work:
- [ ] Check for running backend: `netstat -ano | findstr :8000`
- [ ] Kill old processes if any
- [ ] Activate conda environment: `conda activate uday`
- [ ] Verify .env file exists and is correct
- [ ] Start fresh backend
- [ ] Check backend logs for ✅ messages
- [ ] Test with Streamlit UI

## 🎯 Expected Behavior After Fix

### Backend Logs Should Show:
```
2025-10-14 XX:XX:XX - INFO - Loading .env from: C:\Users\udayt\OneDrive\Desktop\TalentFlow-AI\.env
2025-10-14 XX:XX:XX - INFO - .env file exists: True
2025-10-14 XX:XX:XX - INFO - 🚀 Starting TalentFlow AI Backend...
2025-10-14 XX:XX:XX - INFO - Initializing JD Generator with:
2025-10-14 XX:XX:XX - INFO -   Endpoint: https://mazen-mgpk90ba-eastus2.openai.azure.com/
2025-10-14 XX:XX:XX - INFO -   Deployment: gpt-4o-mini
2025-10-14 XX:XX:XX - INFO -   API Version: 2024-12-01-preview
2025-10-14 XX:XX:XX - INFO -   API Key: ********...fEFW
2025-10-14 XX:XX:XX - INFO - ✅ JD Generator Service initialized successfully
2025-10-14 XX:XX:XX - INFO - ✅ Application started successfully
```

### Streamlit Should Show:
- No 401 errors
- JD generates successfully
- PDF downloads work
- Resume screening works
- Interview assignment works

## 💡 Additional Troubleshooting

If problem persists after following above steps:

### Check 1: Verify Azure Deployment Exists
1. Login to Azure Portal
2. Go to your Azure OpenAI resource
3. Navigate to "Model deployments"
4. Verify deployment named `gpt-4o-mini` exists
5. Check if it's in the same region as endpoint (eastus2)

### Check 2: Verify API Key
1. In Azure Portal, go to your Azure OpenAI resource
2. Click "Keys and Endpoint"
3. Copy Key 1 or Key 2
4. Compare with your .env file
5. If different, update .env and restart backend

### Check 3: Check API Version
The API version `2024-12-01-preview` is very recent. Try using:
```
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```
or
```
AZURE_OPENAI_API_VERSION=2023-12-01-preview
```

### Check 4: Verify Endpoint URL
Ensure endpoint has trailing slash:
```
✅ CORRECT: https://mazen-mgpk90ba-eastus2.openai.azure.com/
❌ WRONG: https://mazen-mgpk90ba-eastus2.openai.azure.com
```

## 🎉 Success Indicators

You'll know it's fixed when:
- ✅ Backend starts without errors
- ✅ All services initialize successfully
- ✅ JD Generator creates job descriptions
- ✅ No 401 errors in Streamlit UI
- ✅ PDF downloads work
- ✅ Resume screening works
- ✅ Interview features work

## 📞 Still Having Issues?

If you still see 401 errors after:
1. Killing all old backend processes
2. Activating correct conda environment
3. Starting fresh backend
4. Verifying all logs show ✅

Then check:
- Azure Portal for API key validity
- Azure Portal for deployment existence
- Firewall/network settings
- Azure subscription status (not expired/suspended)

---

**Summary:** The issue was multiple stale backend processes. Kill them all, start fresh, and it should work!
