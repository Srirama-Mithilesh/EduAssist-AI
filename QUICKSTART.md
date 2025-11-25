# 🚀 EduAssist AI - Quick Start Guide

Get your project running in 5 minutes!

---

## ⚡ Step 1: Get Your API Key (2 minutes)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key" or "Create API Key"
3. Copy your API key (starts with `AIza...`)

---

## ⚡ Step 2: Create Project Structure (1 minute)

```bash
# Create project directory
mkdir eduassist-ai
cd eduassist-ai

# Create subdirectories
mkdir agents memory utils logs memory_bank

# Create __init__.py files
touch agents/__init__.py
touch memory/__init__.py
touch utils/__init__.py
```

---

## ⚡ Step 3: Save All Files (2 minutes)

Copy these files from artifacts into your project:

```
eduassist-ai/
├── agents/
│   ├── __init__.py (empty file)
│   ├── coordinator_agent.py
│   ├── research_agent.py
│   ├── tutor_agent.py
│   └── memory_agent.py
├── memory/
│   ├── __init__.py (empty file)
│   ├── session_manager.py
│   └── memory_bank.py
├── utils/
│   ├── __init__.py (empty file)
│   ├── logging_config.py
│   └── context_manager.py
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── test_comprehensive.py
├── DEMO_SCRIPT.md
├── SUBMISSION_CHECKLIST.md
└── QUICKSTART.md (this file)
```

---

## ⚡ Step 4: Install & Run (2 minutes)

```bash
# Install dependencies
pip install google-genai

# Set your API key
export GOOGLE_API_KEY="your_api_key_here"

# Test the system!
python test_comprehensive.py
```

If all tests pass ✅, you're ready!

---

## 🎮 **Try It Out**

### **Interactive Mode:**
```bash
python main.py

# Try these commands:
You: What is photosynthesis? I'm in high school.
You: Can you explain the light-dependent reactions?
You: practice photosynthesis
[Answer the question]
You: summary
You: quit
```

### **Demo Mode:**
```bash
python main.py --demo
# Runs pre-programmed showcase
```

---

## 🎯 **What to Do Next**

1. **Test Everything**
   ```bash
   python test_comprehensive.py
   ```

2. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: EduAssist AI"
   # Create repo on GitHub, then:
   git remote add origin your-github-url
   git push -u origin main
   ```

3. **Record Demo Video** (3 minutes max)
   - Use DEMO_SCRIPT.md as guide
   - Show problem, solution, live demo, impact
   - Upload to YouTube

4. **Submit on Kaggle**
   - Follow SUBMISSION_CHECKLIST.md
   - Add GitHub link
   - Add video link
   - Submit before Dec 1, 11:59 AM PT

---

## 🚨 **Before Submitting**

✅ Remove ALL API keys from code
✅ Add .gitignore file
✅ Test from clean install
✅ All tests passing
✅ Video uploaded
✅ README complete

---

## 💡 **Common Issues**

**"Module not found"**
```bash
pip install google-genai
# Make sure __init__.py files exist in all folders
```

**"API key not found"**
```bash
export GOOGLE_API_KEY="your_key_here"
# Or create .env file with: GOOGLE_API_KEY=your_key_here
```

**"Tests failing"**
- Check API key is valid (starts with AIza)
- Check internet connection
- Read error message carefully

---

## 📞 **Need Help?**

1. Check the detailed README.md
2. Review code comments
3. Run with --demo mode first
4. Check SUBMISSION_CHECKLIST.md

---

## 🏆 **You've Built Something Amazing!**

Features in your system:
- ✅ 4 specialized AI agents
- ✅ Persistent memory & learning profiles
- ✅ Adaptive difficulty system
- ✅ Practice question generation
- ✅ Automated grading
- ✅ Progress tracking
- ✅ Web search integration
- ✅ Context management
- ✅ Complete observability

**Now submit it and win! 🚀**

---

**Deadline:** December 1, 2025, 11:59 AM PT

**Good luck!** 🎉