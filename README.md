# EduAssist AI - Educational Research Assistant Agent

> A multi-agent AI system designed to revolutionize student learning through reliable, verified, and adaptive educational assistance.

**Track:** Agents for Good (Education)  
**Capstone Project:** 5-Day AI Agents Intensive Course with Google

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Our Solution](#our-solution)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Implementation](#technical-implementation)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)

---

## Overview

**EduAssist AI** is a sophisticated multi-agent system that helps students get accurate, verified, and contextually relevant answers to their academic questions. Unlike traditional chatbots, EduAssist AI combines:

- **Web Search** for current information
- **Source Verification** for reliability
- **Adaptive Tutoring** tailored to student level
- **Persistent Memory** for personalized learning

---

## The Problem

Students today face several challenges when seeking educational help:

1. **Lack of Reliable Information**: Chat models often provide outdated or unverified information
2. **Generic Responses**: One-size-fits-all answers don't account for different learning levels
3. **No Continuity**: Each interaction starts fresh with no memory of previous questions
4. **Source Verification Gap**: Difficulty verifying the accuracy of AI-generated responses
5. **Information Overload**: Overwhelmed by sources without guidance on credibility

### Impact:
- Students waste hours searching for reliable answers
- Misinformation leads to poor academic performance  
- Lack of personalized guidance reduces learning effectiveness
- Students lose trust in AI tools for academic work

---

## 💡 Our Solution

### Why Agents?

An **agent-based approach** uniquely solves student learning problems because:

1. **Specialized Intelligence**: Different agents handle research, tutoring, and verification with expert-level focus
2. **Tool Integration**: Agents actively search the web and verify sources
3. **Adaptive Behavior**: Adjusts approach based on student responses and progress
4. **Persistent Memory**: Maintains context across sessions, building personalized profiles
5. **Reliable Orchestration**: Ensures the right agent handles each task efficiently

### Core Capabilities:

**Real-time Research** with verified sources  
**Multi-Source Verification** across credible sources  
**Adaptive Learning** adjusted to student level  
**Session Memory** remembering previous topics  
**Source Transparency** with citations  
**Progress Tracking** monitoring learning over time

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     STUDENT INTERFACE                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              COORDINATOR AGENT (Orchestrator)                │
│  • Routes queries to specialized agents                      │
│  • Manages sequential/parallel execution                     │
│  • Synthesizes final responses                               │
│  • Powered by: Gemini 2.0 Flash                             │
└─────┬───────────────────┬──────────────────┬────────────────┘
      │                   │                  │
      ▼                   ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
│  RESEARCH   │   │    TUTOR     │   │  MEMORY         │
│   AGENT     │   │    AGENT     │   │  AGENT          │
│             │   │              │   │                 │
│ • Web       │   │ • Explains   │   │ • Session       │
│   Search    │   │   concepts   │   │   history       │
│ • Source    │   │ • Adapts to  │   │ • Learning      │
│   verify    │   │   level      │   │   profile       │
│ • Fact      │   │ • Examples   │   │ • Progress      │
│   check     │   │ • Analogies  │   │   tracking      │
└─────────────┘   └──────────────┘   └─────────────────┘
      │                   │                  │
      └───────────────────┴──────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   SHARED MEMORY       │
              │   • InMemorySession   │
              │   • Memory Bank       │
              │   • Context Storage   │
              └───────────────────────┘
```

### Agent Descriptions:

#### 1. **Coordinator Agent** (Orchestrator)
- Main entry point and decision-maker
- Routes queries to appropriate agents
- Manages execution flow (sequential/parallel)
- Synthesizes responses from multiple agents

#### 2. **Research Agent** (Information Retrieval)
- Searches web for current information
- Verifies source credibility
- Cross-references facts across sources
- Returns cited, verified information

#### 3. **Tutor Agent** (Pedagogical Expert)
- Breaks down complex concepts
- Adapts to student's education level
- Provides examples and analogies
- Identifies and addresses misconceptions

#### 4. **Memory Agent** (Context Manager)
- Maintains session state
- Tracks learning progress
- Records preferences and patterns
- Identifies knowledge gaps

---

##  Key Features

### 1. Multi-Agent Orchestration
- **Sequential execution** for dependent tasks
- **Parallel execution** for independent searches
- Dynamic routing based on query analysis

### 2. Tool Integration
- Google Search API for web research
- Custom source credibility scoring
- Fact verification across multiple sources

### 3. Sessions & Memory
- **InMemorySessionService**: Short-term conversation state
- **Memory Bank**: Long-term student profiles
- Context compaction for efficient token usage

### 4. Context Engineering
- Smart context window management
- Relevant history retrieval
- Dynamic prompt construction

### 5. Observability
- Comprehensive logging system
- Agent action tracing
- Performance metrics tracking

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Google AI API key (Gemini)

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/Srirama-Mithilesh/EduAssist-AI.git
cd eduassist-ai
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

Or export directly:
```bash
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

5. **Verify installation:**
```bash
python main.py --demo
```

---

## 📖 Usage

### Interactive Mode

Start a conversation with EduAssist AI:

```bash
python main.py
```

**Commands:**
- `quit` or `exit` - Exit the program
- `summary` - View learning progress
- `reset` - Start a new session
- `level <level>` - Set education level (elementary, middle_school, high_school, college, graduate)

**Example session:**
```
You: Can you explain photosynthesis? I'm in high school biology.

EduAssist: Photosynthesis is the process by which plants convert light 
energy into chemical energy... [detailed explanation]

📚 Sources:
  1. https://khanacademy.org/biology/photosynthesis
  2. https://nature.com/articles/photosynthesis-review

⏱️ Processed in 2.34s
```

### Demo Mode

Run pre-programmed demo (perfect for presentations):

```bash
python main.py --demo
```

This runs through showcase queries demonstrating:
- Adaptive explanations
- Web search integration
- Memory recall
- Source citation

### Programmatic Usage

```python
from main import EduAssistAI
import asyncio

async def main():
    # Initialize
    eduassist = EduAssistAI(api_key="your_key")
    
    # Process query
    result = await eduassist.process_query(
        student_query="What is quantum entanglement?",
        session_id="user_123",
        student_level="high_school"
    )
    
    print(result['answer'])
    print(f"Sources: {result['sources']}")

asyncio.run(main())
```

---

## 🔧 Technical Implementation

### Technologies Used

- **Framework**: Google Agent Development Kit (ADK-Python)
- **LLM**: Gemini 2.0 Flash (fast, efficient)
- **Memory**: InMemorySessionService + Memory Bank (local JSON storage)
- **Tools**: Gemini web search, custom verification tools
- **Observability**: Python logging with structured traces

### Design Decisions

**Memory Storage**: For this hackathon, we use local JSON file storage for the Memory Bank. This approach:
- Clearly demonstrates the Memory Bank concept
- Works perfectly for demo and evaluation
- Allows judges to inspect stored profiles easily
- Keeps implementation focused on agent architecture

**Production Note**: For production deployment, this would be replaced with:
- Cloud database (Firestore, MongoDB, PostgreSQL)
- Vector database for semantic search (Pinecone, Weaviate)
- Caching layer (Redis) for performance

### Key Concepts Demonstrated

**Multi-agent System**
- Coordinator orchestrates 3 specialized agents
- Sequential and parallel execution strategies
- Dynamic agent routing based on query analysis

**Tools Integration**
- Google Search for web research
- Custom source credibility scoring
- Fact verification tools

**Sessions & Memory**
- InMemorySessionService for short-term state
- Memory Bank for long-term profiles
- Context compaction for efficiency

**Context Engineering**
- Dynamic prompt construction
- Token limit management
- Relevant history retrieval

**Observability**
- Structured logging across all agents
- Agent action tracing
- Performance metrics

**Gemini Usage**
- All agents powered by Gemini 2.0 Flash

---

## 📁 Project Structure

```
eduassist-ai/
├── agents/
│   ├── __init__.py
│   ├── coordinator_agent.py    # Main orchestrator
│   ├── research_agent.py        # Web search & verification
│   ├── tutor_agent.py           # Adaptive explanations
│   └── memory_agent.py          # Session & profile management
├── memory/
│   ├── __init__.py
│   ├── session_manager.py       # Short-term session memory
│   └── memory_bank.py           # Long-term profile storage
├── utils/
│   ├── __init__.py
│   ├── logging_config.py        # Observability setup
│   └── context_manager.py       # Context engineering
├── memory_bank/                 # Persistent profile storage
├── logs/                        # Application logs
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── .env.example                 # Environment template
└── .gitignore
```

### Adding __init__.py Files

Create empty `__init__.py` files in each directory:

```bash
touch agents/__init__.py
touch memory/__init__.py
touch utils/__init__.py
```

## 🔮 Future Enhancements

### Phase 2 Features:
- Integration with learning management systems (Canvas, Moodle)
- Visual diagram generation for complex concepts
- Practice problem generation
- Collaborative study groups
- Teacher dashboard for monitoring
- Mobile app for on-the-go learning

### Advanced Capabilities:
- Multimodal input (image uploads of homework)
- Voice interaction for accessibility
- Academic database integration (JSTOR, Google Scholar)
- Spaced repetition for long-term retention
- A2A protocol for inter-agent communication

---

## 👥 Contributing

This is a capstone project submission, but feedback and suggestions are welcome!

### How to Contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 🙏 Acknowledgments

- **Google & Kaggle** for the AI Agents Intensive Course
- **Gemini Team** for providing powerful AI capabilities
- **All students** who struggle with educational AI and inspired this project
- **Delegation** AI assistance was used during the development of this project.
---

## 🏆 Competition Submission

**Track:** Agents for Good (Education)  
**Submission Date:** December 1, 2025  
**GitHub:** [[Repository Link]](https://github.com/Srirama-Mithilesh/EduAssist-AI.git) 
**Kaggle Profile:** [[Your Profile]](https://www.kaggle.com/sriramamithilesh)

---

*Built with ❤️ for students everywhere who deserve better learning tools.*
