"""
Memory Agent - Manages session state and long-term learning profiles

This agent is responsible for:
1. Maintaining session state across conversations
2. Tracking topics the student has studied
3. Recording learning preferences and patterns
4. Identifying knowledge gaps
5. Suggesting review topics
6. Building comprehensive student learning profiles over time

This demonstrates: Sessions & Memory, context management, personalization
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MemoryAgent:
    """
    Specialized agent for memory and context management
    Maintains both short-term (session) and long-term (student profile) memory
    """
    
    def __init__(self, client, memory_bank, session_manager):
        """
        Initialize the Memory Agent
        
        Args:
            client: Gemini client for LLM calls
            memory_bank: Long-term memory storage
            session_manager: Short-term session management
        """
        self.client = client
        self.model_name = "gemini-2.5-flash"
        self.memory_bank = memory_bank
        self.session_manager = session_manager
        
        logger.info("✓ MemoryAgent initialized")
    
    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve complete context for a session
        
        Combines:
        - Recent conversation history (short-term)
        - Student's learning profile (long-term)
        - Identified knowledge gaps
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict with complete context
        """
        logger.info(f"[Memory Agent] Retrieving context for session: {session_id}")
        
        try:
            # Get short-term session memory
            session_data = self.session_manager.get_session(session_id)
            
            # Get long-term student profile
            student_profile = await self.memory_bank.get_profile(session_id)
            
            # Combine into comprehensive context
            context = {
                'session_data': session_data,
                'student_profile': student_profile,
                'recent_topics': session_data.get('topics_discussed', []),
                'knowledge_level': student_profile.get('estimated_level', 'high_school'),
                'learning_preferences': student_profile.get('preferences', {}),
                'previous_interactions': session_data.get('interactions', [])[-5:]  # Last 5
            }
            
            logger.info(f"[Memory Agent] ✓ Retrieved context with {len(context['previous_interactions'])} recent interactions")
            
            return context
            
        except Exception as e:
            logger.error(f"[Memory Agent] Error retrieving context: {str(e)}")
            return {
                'session_data': {},
                'student_profile': {},
                'recent_topics': [],
                'knowledge_level': 'high_school',
                'learning_preferences': {},
                'previous_interactions': []
            }
    
    async def retrieve_relevant_context(self,
                                       query: str,
                                       session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve context items relevant to the current query
        
        Uses semantic similarity to find relevant past interactions
        
        Args:
            query: Current query
            session_context: Full session context
            
        Returns:
            dict with relevant past interactions and topics
        """
        logger.info("[Memory Agent] Finding relevant context...")
        
        previous_interactions = session_context.get('previous_interactions', [])
        
        if not previous_interactions:
            return {'relevant_items': []}
        
        # Use Gemini to identify relevant past interactions
        relevance_prompt = f"""Given this student query: "{query}"

Previous interactions:
{json.dumps(previous_interactions, indent=2)}

Identify which previous interactions are relevant to answering the current query.
Consider:
- Related topics
- Building on previous explanations
- Clarifying previous confusions

Respond with a JSON list of relevant interaction indices (0-based).
Example: [0, 2, 4]

If nothing is relevant, respond with: []"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=relevance_prompt
            )
            
            # Parse response
            response_text = response.text.strip()
            if response_text.startswith('['):
                relevant_indices = json.loads(response_text)
            else:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\[[\d,\s]*\]', response_text)
                relevant_indices = json.loads(json_match.group(0)) if json_match else []
            
            # Get relevant items
            relevant_items = [
                previous_interactions[i] 
                for i in relevant_indices 
                if i < len(previous_interactions)
            ]
            
            logger.info(f"[Memory Agent] Found {len(relevant_items)} relevant items")
            
            return {
                'relevant_items': relevant_items,
                'relevance_count': len(relevant_items)
            }
            
        except Exception as e:
            logger.warning(f"[Memory Agent] Could not determine relevance: {str(e)}")
            # Fallback: return last 2 interactions
            return {
                'relevant_items': previous_interactions[-2:],
                'relevance_count': min(2, len(previous_interactions))
            }
    
    async def update_learning_profile(self,
                                     session_id: str,
                                     query: str,
                                     topics_covered: List[str],
                                     response_quality: float) -> None:
        """
        Update the student's long-term learning profile
        
        Tracks:
        - Topics mastered over time
        - Learning patterns and preferences
        - Areas that need review
        - Estimated knowledge level
        
        Args:
            session_id: Session identifier
            query: The query asked
            topics_covered: Topics in this interaction
            response_quality: Quality score of the response (0-1)
        """
        logger.info(f"[Memory Agent] Updating learning profile for session: {session_id}")
        
        try:
            # Get current profile
            profile = await self.memory_bank.get_profile(session_id)
            
            # Update topics mastered
            if 'topics_studied' not in profile:
                profile['topics_studied'] = {}
            
            for topic in topics_covered:
                if topic not in profile['topics_studied']:
                    profile['topics_studied'][topic] = {
                        'first_encountered': datetime.now().isoformat(),
                        'times_reviewed': 1,
                        'last_reviewed': datetime.now().isoformat(),
                        'mastery_level': 'introduced'
                    }
                else:
                    profile['topics_studied'][topic]['times_reviewed'] += 1
                    profile['topics_studied'][topic]['last_reviewed'] = datetime.now().isoformat()
                    
                    # Update mastery level based on repetition
                    times = profile['topics_studied'][topic]['times_reviewed']
                    if times >= 5:
                        profile['topics_studied'][topic]['mastery_level'] = 'mastered'
                    elif times >= 3:
                        profile['topics_studied'][topic]['mastery_level'] = 'familiar'
                    elif times >= 2:
                        profile['topics_studied'][topic]['mastery_level'] = 'learning'
            
            # Update statistics
            if 'statistics' not in profile:
                profile['statistics'] = {
                    'total_questions': 0,
                    'total_sessions': 1,
                    'average_response_quality': 0
                }
            
            profile['statistics']['total_questions'] += 1
            
            # Update average response quality (running average)
            old_avg = profile['statistics']['average_response_quality']
            old_count = profile['statistics']['total_questions'] - 1
            new_avg = ((old_avg * old_count) + response_quality) / profile['statistics']['total_questions']
            profile['statistics']['average_response_quality'] = new_avg
            
            # Save updated profile
            await self.memory_bank.save_profile(session_id, profile)
            
            logger.info(f"[Memory Agent] ✓ Profile updated. Total topics: {len(profile['topics_studied'])}")
            
        except Exception as e:
            logger.error(f"[Memory Agent] Error updating profile: {str(e)}")
    
    async def get_learning_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Generate a summary of the student's learning progress
        
        Useful for showing students what they've learned
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict with learning statistics and insights
        """
        logger.info(f"[Memory Agent] Generating learning summary for: {session_id}")
        
        try:
            # Get session and profile data
            session_data = self.session_manager.get_session(session_id)
            profile = await self.memory_bank.get_profile(session_id)
            
            # Extract statistics
            topics_studied = profile.get('topics_studied', {})
            statistics = profile.get('statistics', {})
            
            # Categorize topics by mastery
            mastered_topics = [
                topic for topic, data in topics_studied.items()
                if data.get('mastery_level') == 'mastered'
            ]
            
            learning_topics = [
                topic for topic, data in topics_studied.items()
                if data.get('mastery_level') in ['introduced', 'learning', 'familiar']
            ]
            
            # Calculate session duration
            session_start = session_data.get('start_time')
            if session_start:
                duration = (datetime.now() - datetime.fromisoformat(session_start)).total_seconds() / 60
                duration_str = f"{int(duration)} minutes"
            else:
                duration_str = "N/A"
            
            summary = {
                'topics': list(topics_studied.keys()),
                'mastered_topics': mastered_topics,
                'learning_topics': learning_topics,
                'question_count': statistics.get('total_questions', 0),
                'session_count': statistics.get('total_sessions', 1),
                'average_quality': statistics.get('average_response_quality', 0),
                'duration': duration_str,
                'recommendations': await self._generate_recommendations(profile)
            }
            
            logger.info("[Memory Agent] ✓ Learning summary generated")
            
            return summary
            
        except Exception as e:
            logger.error(f"[Memory Agent] Error generating summary: {str(e)}")
            return {
                'topics': [],
                'mastered_topics': [],
                'learning_topics': [],
                'question_count': 0,
                'session_count': 0,
                'duration': 'N/A',
                'error': str(e)
            }
    
    async def _generate_recommendations(self, profile: Dict[str, Any]) -> List[str]:
        """
        Generate personalized learning recommendations
        
        Based on:
        - Topics studied
        - Mastery levels
        - Time since last review
        """
        topics_studied = profile.get('topics_studied', {})
        
        if not topics_studied:
            return ["Start by asking a question about something you're curious about!"]
        
        recommendations = []
        
        # Find topics that need review (studied but not recently)
        for topic, data in topics_studied.items():
            last_reviewed = datetime.fromisoformat(data.get('last_reviewed', datetime.now().isoformat()))
            days_since = (datetime.now() - last_reviewed).days
            
            if days_since >= 7 and data.get('mastery_level') != 'mastered':
                recommendations.append(f"Review: {topic} (last studied {days_since} days ago)")
        
        # Suggest related advanced topics for mastered concepts
        mastered_topics = [
            topic for topic, data in topics_studied.items()
            if data.get('mastery_level') == 'mastered'
        ]
        
        if mastered_topics:
            recommendations.append(f"Explore advanced concepts related to: {', '.join(mastered_topics[:2])}")
        
        # Encourage completing partially learned topics
        learning_topics = [
            topic for topic, data in topics_studied.items()
            if data.get('mastery_level') in ['introduced', 'learning']
        ]
        
        if learning_topics:
            recommendations.append(f"Continue learning: {learning_topics[0]}")
        
        return recommendations[:3]  # Top 3 recommendations