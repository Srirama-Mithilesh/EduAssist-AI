# 📦 EduAssist AI - Complete Setup Guide
## Step-by-Step Instructions (20 Minutes Total)

---

## 🎯 **OVERVIEW**

You'll be doing 4 main steps:
1. **Get API Key** (5 min)
2. **Create Project Structure** (5 min)
3. **Copy Code Files** (5 min)
4. **Test & Run** (5 min)

Let's go! 🚀

---

## 📋 **PREREQUISITES**

Before starting, ensure you have:
- [ ] **Python 3.9+** installed ([Download here](https://www.python.org/downloads/))
- [ ] **Internet connection** (for API calls)
- [ ] **Text editor** (VS Code, Sublime, or any editor)
- [ ] **Terminal/Command Prompt** access

### **Check Python Version:**
```bash
python --version
# or
python3 --version
```
Should show: `Python 3.9.x` or higher

---

## 🔑 **STEP 1: Get Your Google AI API Key (5 minutes)**

### **1.1 Go to Google AI Studio**
- Open browser: https://aistudio.google.com/app/apikey
- Sign in with your Google account

### **1.2 Create API Key**
1. Click **"Create API Key"** button
2. Select project or create new one
3. Click **"Create API Key in new project"**
4. **COPY** the key (starts with `AIza...`)
5. Save it somewhere safe (you'll need it soon)

⚠️ **IMPORTANT**: Keep this key secret! Never share it or commit it to GitHub.

---

## 📁 **STEP 2: Create Project Structure (5 minutes)**

### **2.1 Create Main Project Folder**

**On Mac/Linux:**
```bash
# Open Terminal
cd ~  # Go to home directory
mkdir eduassist-ai
cd eduassist-ai
```

**On Windows:**
```cmd
# Open Command Prompt
cd %USERPROFILE%\Documents
mkdir eduassist-ai
cd eduassist-ai
```

### **2.2 Create Subdirectories**

**On Mac/Linux:**
```bash
mkdir -p agents memory utils logs memory_bank
```

**On Windows:**
```cmd
mkdir agents
mkdir memory
mkdir utils
mkdir logs
mkdir memory_bank
```

### **2.3 Create __init__.py Files**

These files tell Python these folders are packages.

**On Mac/Linux:**
```bash
touch agents/__init__.py
touch memory/__init__.py
touch utils/__init__.py
```

**On Windows:**
```cmd
type nul > agents\__init__.py
type nul > memory\__init__.py
type nul > utils\__init__.py
```

### **2.4 Verify Structure**

Your folder should look like this:
```
eduassist-ai/
├── agents/
│   └── __init__.py
├── memory/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── logs/
└── memory_bank/
```

---

## 💾 **STEP 3: Copy Code Files (5 minutes)**

Now you'll copy all the code files from the artifacts. I'll tell you which file goes where.

### **3.1 Root Directory Files**

Create these files in the `eduassist-ai/` folder:

1. **main.py** - Copy from "main.py - EduAssist AI Entry Point" artifact
2. **requirements.txt** - Copy from "requirements.txt" artifact
3. **README.md** - Copy from "README.md" artifact
4. **.gitignore** - Copy from ".gitignore" artifact
5. **.env.example** - Copy from ".env.example" artifact
6. **test_comprehensive.py** - Copy from "test_comprehensive.py" artifact
7. **QUICKSTART.md** - Copy from "QUICKSTART.md" artifact
8. **DEMO_SCRIPT.md** - Copy from "DEMO_SCRIPT.md" artifact
9. **SUBMISSION_CHECKLIST.md** - Copy from "SUBMISSION_CHECKLIST.md" artifact
10. **setup.sh** - Copy from "setup.sh" artifact (Mac/Linux)
11. **setup.bat** - Copy from "setup.bat" artifact (Windows)

### **3.2 Agents Folder Files**

Create these files in `eduassist-ai/agents/`:

1. **coordinator_agent.py** - Copy from "coordinator_agent.py" artifact
2. **research_agent.py** - Copy from "research_agent.py" artifact
3. **tutor_agent.py** - Copy from "tutor_agent.py" artifact
4. **memory_agent.py** - Copy from "memory_agent.py" artifact

### **3.3 Memory Folder Files**

Create these files in `eduassist-ai/memory/`:

1. **session_manager.py** - Copy from "session_manager.py" artifact
2. **memory_bank.py** - Copy from "memory_bank.py" artifact

### **3.4 Utils Folder Files**

Create these files in `eduassist-ai/utils/`:

1. **logging_config.py** - Copy from "logging_config.py" artifact
2. **context_manager.py** - Copy from "context_manager.py" artifact

### **3.5 Verify All Files**

Check you have all files:
```bash
# On Mac/Linux:
ls -la

# On Windows:
dir
```

You should see ~21 files total.

---

## 🔧 **STEP 4: Install Dependencies (3 minutes)**

### **4.1 Install Python Package**

**On Mac/Linux:**
```bash
pip3 install google-genai
```

**On Windows:**
```cmd
pip install google-genai
```

### **4.2 Verify Installation**
```bash
python -c "import genai; print('✓ google-genai installed')"
```

Should print: `✓ google-genai installed`

---

## 🔐 **STEP 5: Set API Key (2 minutes)**

### **Option A: Environment Variable (Recommended for testing)**

**On Mac/Linux:**
```bash
export GOOGLE_API_KEY="your_actual_api_key_here"
```

**On Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your_actual_api_key_here
```

**On Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_actual_api_key_here"
```

### **Option B: Create .env File (Recommended for development)**

1. Create a file named `.env` in `eduassist-ai/` folder
2. Add this line:
```
GOOGLE_API_KEY=your_actual_api_key_here
```
3. Save the file

⚠️ **CRITICAL**: Never commit `.env` to Git! The `.gitignore` file prevents this.

---

## ✅ **STEP 6: Test Everything (5 minutes)**

### **6.1 Run Comprehensive Tests**

```bash
python test_comprehensive.py
```

**Expected Output:**
```
==============================================================
              EDUASSIST AI - COMPREHENSIVE TEST SUITE
==============================================================

▶ System Initialization...
✓ System Initialization - PASSED

▶ Basic Query Processing...
✓ Basic Query Processing - PASSED

...

Total: 8/8 tests passed
🎉 ALL TESTS PASSED! System is ready for submission!
```

### **6.2 If Tests Fail**

**Common Issue 1: "API key not found"**
```bash
# Make sure you set the key:
export GOOGLE_API_KEY="your_key"  # Mac/Linux
set GOOGLE_API_KEY=your_key       # Windows

# Then try again
python test_comprehensive.py
```

**Common Issue 2: "Module not found"**
```bash
# Install dependencies again
pip install google-genai

# Make sure __init__.py files exist
ls agents/__init__.py  # Should not error
```

**Common Issue 3: "Network error"**
```bash
# Check internet connection
ping google.com

# Check API key is valid (starts with AIza)
echo $GOOGLE_API_KEY
```

---

## 🎮 **STEP 7: Try Interactive Mode (5 minutes)**

### **7.1 Start Interactive Mode**
```bash
python main.py
```

**You should see:**
```
============================================================
🎓 Welcome to EduAssist AI - Your Educational Assistant
============================================================

Commands:
  'quit' or 'exit' - Exit the program
  'summary' - View your learning progress
  ...

Session ID: session_1234567890
Education Level: high_school

Ask me anything! I'm here to help you learn.

You: 
```

### **7.2 Try These Commands**

**Test 1: Basic Question**
```
You: What is photosynthesis? I'm in high school.
```
Wait for response (10-20 seconds)

**Test 2: Follow-up Question**
```
You: Can you explain the light-dependent reactions in more detail?
```

**Test 3: Practice Mode**
```
You: practice photosynthesis
```
Answer the question that appears

**Test 4: Check Progress**
```
You: summary
```

**Test 5: Exit**
```
You: quit
```

---

## 🎬 **STEP 8: Try Demo Mode (2 minutes)**

```bash
python main.py --demo
```

This runs a pre-programmed demonstration showing all features.

---

## 🎉 **SUCCESS! You're Ready!**

If you got here, your system is working! 

### **What You've Accomplished:**
✅ Complete multi-agent AI system
✅ All 8 tests passing
✅ Interactive mode working
✅ Demo mode working
✅ Ready for video recording
✅ Ready for GitHub upload
✅ Ready for Kaggle submission

---

## 🚀 **NEXT STEPS**

Now you're ready for:

1. **Record Demo Video**
   - Follow `DEMO_SCRIPT.md`
   - Under 3 minutes
   - Show the system working

2. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: EduAssist AI"
   # Create repo on GitHub, then:
   git remote add origin your-github-url
   git push -u origin main
   ```

3. **Submit to Kaggle**
   - Follow `SUBMISSION_CHECKLIST.md`
   - Add GitHub link
   - Add video link
   - Submit!

---

## 🆘 **TROUBLESHOOTING**

### **"Python not found"**
- Install Python from python.org
- Make sure to check "Add to PATH" during installation
- Restart terminal after installation

### **"Permission denied" on Mac/Linux**
```bash
chmod +x setup.sh
./setup.sh
```

### **Virtual environment (Optional but recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Then install dependencies
pip install google-genai
```

### **"Import Error" in tests**
Make sure you're in the `eduassist-ai` directory when running:
```bash
pwd  # Should show: .../eduassist-ai
```

### **Still stuck?**
1. Check all files are in correct folders
2. Verify __init__.py files exist
3. Confirm API key is set correctly
4. Try running individual agent files to isolate the issue

---

## 📞 **GETTING HELP**

If you're stuck:
1. Re-read the error message carefully
2. Check the troubleshooting section above
3. Verify your folder structure matches exactly
4. Make sure API key is valid

---

## ✅ **FINAL CHECKLIST**

Before moving to submission:
- [ ] All tests pass (8/8)
- [ ] Interactive mode works
- [ ] Demo mode works
- [ ] Can answer questions
- [ ] Practice mode works
- [ ] Progress tracking works
- [ ] No errors in terminal

**If all checked ✅ - YOU'RE READY TO SUBMIT! 🎊**

---

*Setup time: ~20 minutes*
*Video recording: ~30 minutes*
*GitHub setup: ~10 minutes*
*Kaggle submission: ~10 minutes*

**Total: ~70 minutes to complete submission! Let's go! 🚀**