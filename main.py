"""
EduAssist AI - Educational Research Assistant Agent
Main entry point for the multi-agent system

This file orchestrates the entire agent system and provides the interface
for students to interact with the educational assistant.
"""

import os
import asyncio
from datetime import datetime
from typing import Optional

# ADK imports (make sure to install: pip install google-genai)
from google import genai
from google.genai import types

# Import our custom agents (we'll create these next)
from agents.coordinator_agent import CoordinatorAgent
from agents.research_agent import ResearchAgent
from agents.tutor_agent import TutorAgent
from agents.memory_agent import MemoryAgent

# Memory and session management
from memory.session_manager import SessionManager
from memory.memory_bank import MemoryBank

# Utilities
from utils.logging_config import setup_logging
from utils.context_manager import ContextManager

# set colours
class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Set up logging for observability
logger = setup_logging()


class EduAssistAI:
    """
    Main orchestrator for the EduAssist AI system.
    Manages all agents, memory, and coordinates the learning experience.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the EduAssist AI system
        
        Args:
            api_key: Google AI API key (or set GOOGLE_API_KEY env variable)
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "❌ GOOGLE_API_KEY not found!\n\n"
                "Please set your API key:\n"
                "  1. Get a key at: https://aistudio.google.com/app/apikey\n"
                "  2. Set it: export GOOGLE_API_KEY='your_key_here'\n"
                "  3. Or create a .env file with: GOOGLE_API_KEY=your_key_here\n"
            )
        
        # Validate API key format (should start with 'AIza')
        if not self.api_key.startswith('AIza'):
            logger.warning("⚠️ API key doesn't look like a valid Gemini key (should start with 'AIza')")
        
        try:
            # Initialize the Gemini client
            self.client = genai.Client(api_key=self.api_key)
            
            # Initialize memory systems
            self.session_manager = SessionManager()
            self.memory_bank = MemoryBank()
            self.context_manager = ContextManager()
            
            # Initialize all agents
            logger.info("Initializing EduAssist AI agents...")
            self._initialize_agents()
            
            logger.info("✓ EduAssist AI initialized successfully!")
            
        except Exception as e:
            raise RuntimeError(
                f"❌ Failed to initialize EduAssist AI: {str(e)}\n\n"
                "Common issues:\n"
                "  1. Invalid API key\n"
                "  2. Network connection problems\n"
                "  3. Missing dependencies (run: pip install google-genai)\n"
            )
    
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        # Each agent gets access to the client and necessary tools
        self.memory_agent = MemoryAgent(
            client=self.client,
            memory_bank=self.memory_bank,
            session_manager=self.session_manager
        )
        
        self.research_agent = ResearchAgent(
            client=self.client
        )
        
        self.tutor_agent = TutorAgent(
            client=self.client
        )
        
        self.coordinator_agent = CoordinatorAgent(
            client=self.client,
            memory_agent=self.memory_agent,
            research_agent=self.research_agent,
            tutor_agent=self.tutor_agent,
            context_manager=self.context_manager
        )
    
    async def process_query(self, 
                           student_query: str, 
                           session_id: str = "default",
                           student_level: str = "high_school") -> dict:
        """
        Process a student query through the multi-agent system
        
        Args:
            student_query: The student's question
            session_id: Unique identifier for this learning session
            student_level: Student's education level (elementary, middle_school, 
                          high_school, college, graduate)
        
        Returns:
            dict containing:
                - answer: The final response
                - sources: List of sources used
                - agent_trace: How agents processed the query
                - topics_covered: Topics identified in this interaction
        """
        logger.info(f"Processing query for session {session_id}: {student_query[:50]}...")
        
        start_time = datetime.now()
        
        try:
            # Get session context from memory
            session_context = await self.memory_agent.get_session_context(
                session_id=session_id
            )
            
            # Update session with current query
            await self.session_manager.add_interaction(
                session_id=session_id,
                query=student_query,
                student_level=student_level
            )
            
            # Pass to coordinator agent for orchestration
            result = await self.coordinator_agent.process(
                query=student_query,
                session_id=session_id,
                session_context=session_context,
                student_level=student_level
            )
            
            # Update memory with the interaction results
            await self.memory_agent.update_learning_profile(
                session_id=session_id,
                query=student_query,
                topics_covered=result.get('topics_covered', []),
                response_quality=result.get('quality_score', 0.8)
            )
            
            # Add response to session
            await self.session_manager.add_interaction(
                session_id=session_id,
                response=result['answer']
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result['processing_time'] = processing_time
            
            logger.info(f"✓ Query processed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                'answer': "I encountered an error processing your question. Please try rephrasing it.",
                'error': str(e),
                'sources': [],
                'agent_trace': []
            }
    
    async def get_learning_summary(self, session_id: str) -> dict:
        """
        Get a summary of the student's learning progress
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict containing learning statistics and recommendations
        """
        return await self.memory_agent.get_learning_summary(session_id)
    
    async def reset_session(self, session_id: str):
        """Reset a learning session (useful for testing or new topics)"""
        await self.session_manager.reset_session(session_id)
        logger.info(f"Session {session_id} reset")


async def interactive_mode():
    """
    Interactive CLI mode for testing the agent
    Run this to have a conversation with EduAssist AI
    """
    # Clear visual separator
    print(f"\n{Colors.OKBLUE}{'='*60}{Colors.END}")
    # Main Title with Header Color and Bold
    print(f"{Colors.HEADER}{Colors.BOLD}🎓  Welcome to EduAssist AI - Your Educational Assistant{Colors.END}")
    # Closing separator
    print(f"{Colors.OKBLUE}{'='*60}{Colors.END}")
    # Subheading with Underline
    print(f"\n{Colors.UNDERLINE}Available Commands:{Colors.END}")
    # Commands list - formatted for readability
    # Green for the command itself, Cyan/Warning for arguments
    print(f"  {Colors.OKGREEN}quit{Colors.END} / {Colors.OKGREEN}exit{Colors.END}       - Exit the program")
    print(f"  {Colors.OKGREEN}summary{Colors.END}            - View your learning progress")
    print(f"  {Colors.OKGREEN}reset{Colors.END}              - Start a new learning session")
    print(f"  {Colors.OKGREEN}level{Colors.END} {Colors.WARNING}<level>{Colors.END}      - Set your education level")
    print(f"      {Colors.OKCYAN}(elementary, middle_school, high_school, college, graduate){Colors.END}")
    print(f"  {Colors.OKGREEN}practice{Colors.END} {Colors.WARNING}<topic>{Colors.END}   - Get a practice question on a topic")
    # Footer separator
    print(f"\n{Colors.OKBLUE}{'='*60}{Colors.END}\n")
    
    # Initialize the system
    try:
        eduassist = EduAssistAI()
    except Exception as e:
        print(f"\n❌ Failed to initialize: {str(e)}")
        print("\nPlease check:")
        print("  1. GOOGLE_API_KEY is set correctly")
        print("  2. Internet connection is working")
        print("  3. Dependencies are installed: pip install google-genai")
        return
    
    # Session configuration
    import time
    session_id = f"session_{int(time.time())}"
    student_level = "high_school"  # Default level
    
    print(f"Session ID: {session_id}")
    print(f"Education Level: {student_level}")
    print("\nAsk me anything! I'm here to help you learn.\n")
    
    while True:
        try:
            # Get student input
            query = input("You: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ['quit', 'exit']:
                print("\n👋 Happy learning! Goodbye!")
                break
            
            elif query.lower() == 'summary':
                print("\n📊 Generating learning summary...\n")
                summary = await eduassist.get_learning_summary(session_id)
                print(f"Topics Covered: {', '.join(summary.get('topics', ['None yet']))}")
                print(f"Questions Asked: {summary.get('question_count', 0)}")
                print(f"Session Duration: {summary.get('duration', 'N/A')}")
                print()
                continue
            
            elif query.lower() == 'reset':
                await eduassist.reset_session(session_id)
                import time
                session_id = f"session_{int(time.time())}"
                print(f"\n🔄 New session started: {session_id}\n")
                continue
            
            elif query.lower().startswith('level '):
                new_level = query.split(' ', 1)[1].strip()
                valid_levels = ['elementary', 'middle_school', 'high_school', 'college', 'graduate']
                if new_level in valid_levels:
                    student_level = new_level
                    print(f"\n✓ Education level set to: {student_level}\n")
                else:
                    print(f"\n❌ Invalid level. Choose from: {', '.join(valid_levels)}\n")
                continue
            
            elif query.lower().startswith('practice '):
                # NEW: Practice mode - generate and grade questions
                topic = query.split(' ', 1)[1].strip()
                print(f"\n📝 Generating practice question on: {topic}\n")
                
                # Get student's current progress on this topic
                profile = await eduassist.memory_agent.memory_bank.get_profile(session_id)
                topic_data = profile.get('topics_studied', {}).get(topic, {})
                
                difficulty = topic_data.get('difficulty_level', 'basic')
                mastery = topic_data.get('mastery_level', 'introduced')
                
                # Generate practice question
                question_data = await eduassist.tutor_agent.generate_practice_question(
                    topic=topic,
                    difficulty_level=difficulty,
                    student_level=student_level,
                    mastery_level=mastery
                )
                
                if 'error' in question_data:
                    print(f"❌ Error generating question: {question_data['error']}\n")
                    continue
                
                print(f"🎯 Difficulty: {difficulty}")
                print(f"📚 Question:\n{question_data['question']}\n")
                print("─" * 60)
                
                # Get student's answer
                student_answer = input("Your Answer: ").strip()
                
                if not student_answer:
                    print("\n⚠️ No answer provided. Skipping grading.\n")
                    continue
                
                print("\n⏳ Grading your answer...\n")
                
                # Grade the answer
                grading_result = await eduassist.tutor_agent.grade_answer(
                    question=question_data['question'],
                    student_answer=student_answer,
                    ideal_answer=question_data.get('ideal_answer', ''),
                    key_points=question_data.get('key_points', ''),
                    student_level=student_level
                )
                
                # Display results
                score = grading_result['score']
                print(f"📊 Score: {score:.2f} / 1.00 ({int(score * 100)}%)\n")
                
                if grading_result.get('correct_points'):
                    print(f"✅ What you got right:\n{grading_result['correct_points']}\n")
                
                if grading_result.get('areas_to_improve'):
                    print(f"📈 Areas to improve:\n{grading_result['areas_to_improve']}\n")
                
                if grading_result.get('next_steps'):
                    print(f"🎯 Next steps:\n{grading_result['next_steps']}\n")
                
                if grading_result.get('overall_feedback'):
                    print(f"💬 Overall:\n{grading_result['overall_feedback']}\n")
                
                # Update memory with this practice session
                await eduassist.memory_agent.memory_bank.update_topic_mastery(
                    session_id=session_id,
                    topic=topic,
                    performance_score=score
                )
                
                print(f"✓ Your progress has been saved!\n")
                continue
            
            # Process the query
            print("\n🤔 Thinking...\n")
            result = await eduassist.process_query(
                student_query=query,
                session_id=session_id,
                student_level=student_level
            )

            # Display the answer with nice formatting
            print("─" * 70)
            print(f"\n💡 {Colors.BOLD}EduAssist AI:{Colors.END}\n")
            print(f"{result['answer']}\n")
            print("─" * 70)

            # Show sources if available
            if result.get('sources'):
                print(f"\n📚 {Colors.BOLD}Sources Used:{Colors.END}")
                for idx, source in enumerate(result['sources'], 1):
                    print(f"  {Colors.OKBLUE}{idx}.{Colors.END} {source}")
                print()

            # Show processing time
            if result.get('processing_time'):
                print(f"⏱️  {Colors.OKCYAN}Processed in {result['processing_time']:.2f}s{Colors.END}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            logger.error(f"Error in interactive mode: {str(e)}", exc_info=True)


async def demo_mode():
    """
    Demo mode - runs through example queries to showcase capabilities
    Perfect for video demonstrations!
    """
    print("\n" + "="*60)
    print("🎬 EduAssist AI - DEMO MODE")
    print("="*60 + "\n")
    
    eduassist = EduAssistAI()
    session_id = "demo_session"
    
    # Demo queries that showcase different features
    demo_queries = [
        {
            "query": "Can you explain photosynthesis? I'm in high school biology.",
            "level": "high_school",
            "note": "Showcases: Adaptive explanation, research verification"
        },
        {
            "query": "What's the latest research on climate change?",
            "level": "college",
            "note": "Showcases: Web search, current information, source citation"
        },
        {
            "query": "I'm confused about the photosynthesis you mentioned earlier. Can you explain the light-dependent reactions more simply?",
            "level": "high_school",
            "note": "Showcases: Memory recall, adaptive simplification"
        }
    ]
    
    for idx, demo in enumerate(demo_queries, 1):
        print(f"\n{'─'*60}")
        print(f"Demo Query {idx}/{len(demo_queries)}")
        print(f"Note: {demo['note']}")
        print(f"{'─'*60}\n")
        
        print(f"Student: {demo['query']}\n")
        print("🤔 Processing...\n")
        
        result = await eduassist.process_query(
            student_query=demo['query'],
            session_id=session_id,
            student_level=demo['level']
        )
        
        print(f"EduAssist: {result['answer']}\n")
        
        if result.get('sources'):
            print("📚 Sources Used:")
            for source in result['sources']:
                print(f"  • {source}")
        
        print(f"\n⏱️  Processed in {result.get('processing_time', 0):.2f}s")
        
        # Pause between demos
        if idx < len(demo_queries):
            await asyncio.sleep(2)
    
    # Show learning summary
    print(f"\n{'='*60}")
    print("📊 Learning Session Summary")
    print(f"{'='*60}\n")
    
    summary = await eduassist.get_learning_summary(session_id)
    print(f"Topics Covered: {', '.join(summary.get('topics', []))}")
    print(f"Questions Asked: {summary.get('question_count', 0)}")
    print(f"\n✨ Demo complete!")


def main():
    """Main entry point"""
    import sys
    
    # Check for demo flag
    if '--demo' in sys.argv:
        asyncio.run(demo_mode())
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()