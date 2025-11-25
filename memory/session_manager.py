"""
Session Manager - Handles short-term session memory

This is the InMemorySessionService equivalent that maintains:
- Current conversation state
- Recent interactions within a session
- Temporary context that doesn't need long-term storage

This demonstrates: Sessions & state management (InMemorySessionService concept)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages short-term session state for active conversations
    
    This is an in-memory session service that keeps track of:
    - Active conversations
    - Recent queries and responses
    - Session metadata (start time, interaction count, etc.)
    """
    
    def __init__(self):
        """Initialize the session manager with in-memory storage"""
        # In-memory storage: session_id -> session_data
        self._sessions: Dict[str, Dict[str, Any]] = defaultdict(lambda: self._create_new_session())
        
        # Track active sessions
        self._active_sessions: set = set()
        
        logger.info("✓ SessionManager initialized (in-memory)")
    
    def _create_new_session(self) -> Dict[str, Any]:
        """
        Create a new session data structure
        
        Returns:
            dict with initial session state
        """
        return {
            'start_time': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'interactions': [],  # List of {query, response, timestamp, topics}
            'topics_discussed': [],  # Running list of topics
            'student_level': 'high_school',  # Default
            'interaction_count': 0,
            'context_summary': ''
        }
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session data for a given session ID
        
        Creates new session if it doesn't exist
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            dict with session data
        """
        # Mark session as active
        self._active_sessions.add(session_id)
        
        # Update last active time
        session = self._sessions[session_id]
        session['last_active'] = datetime.now().isoformat()
        
        logger.debug(f"[SessionManager] Retrieved session: {session_id}")
        
        return session
    
    async def add_interaction(self,
                        session_id: str,
                        query: str = None,
                        response: str = None,
                        topics: List[str] = None,
                        student_level: str = None) -> None:
        """
        Add a new interaction to the session
        
        An interaction can be:
        - Just a query (when receiving student input)
        - Just a response (when providing answer)
        - Both query and response (complete interaction)
        
        Args:
            session_id: Session identifier
            query: Student's query (optional)
            response: Agent's response (optional)
            topics: Topics covered in this interaction (optional)
        """
        session = self._sessions[session_id]
        
        if student_level:
            session['student_level'] = student_level
        
        # Get or create current interaction
        if session['interactions'] and not session['interactions'][-1].get('response'):
            # Update existing interaction with response
            current_interaction = session['interactions'][-1]
            if response:
                current_interaction['response'] = response
                current_interaction['response_time'] = datetime.now().isoformat()
        else:
            # Create new interaction
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'response': response,
                'topics': topics or []
            }
            session['interactions'].append(interaction)
            session['interaction_count'] += 1
        
        # Update topics discussed
        if topics:
            for topic in topics:
                if topic not in session['topics_discussed']:
                    session['topics_discussed'].append(topic)
        
        # Update context summary periodically (every 5 interactions)
        if session['interaction_count'] % 5 == 0:
            session['context_summary'] = self._summarize_session(session)
        
        logger.debug(f"[SessionManager] Added interaction to session: {session_id}")
    
    def _summarize_session(self, session: Dict[str, Any]) -> str:
        """
        Create a brief summary of the session for context management
        
        This helps manage context window by providing a condensed version
        of the conversation history
        """
        topics = session.get('topics_discussed', [])
        interaction_count = session.get('interaction_count', 0)
        
        if not topics:
            return "New session, no topics discussed yet."
        
        summary = f"Session with {interaction_count} interactions. "
        summary += f"Topics covered: {', '.join(topics[:5])}"  # Top 5 topics
        
        if len(topics) > 5:
            summary += f" and {len(topics) - 5} more."
        
        return summary
    
    def get_recent_interactions(self, 
                               session_id: str, 
                               count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent interactions from a session
        
        Useful for providing recent context to agents
        
        Args:
            session_id: Session identifier
            count: Number of recent interactions to return
            
        Returns:
            List of recent interactions
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return []
        
        interactions = session.get('interactions', [])
        return interactions[-count:] if interactions else []
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics about a session
        
        Returns:
            dict with session statistics
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return {}
        
        start_time = datetime.fromisoformat(session['start_time'])
        duration_minutes = (datetime.now() - start_time).total_seconds() / 60
        
        return {
            'duration_minutes': round(duration_minutes, 2),
            'interaction_count': session['interaction_count'],
            'topics_count': len(session['topics_discussed']),
            'topics': session['topics_discussed'],
            'start_time': session['start_time'],
            'last_active': session['last_active']
        }
    
    async def reset_session(self, session_id: str) -> None:
        """
        Reset a session (clear all data but keep the session ID active)
        
        Useful for starting fresh on a new topic
        
        Args:
            session_id: Session identifier to reset
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        # Session will be recreated on next access
        logger.info(f"[SessionManager] Reset session: {session_id}")
    
    def cleanup_inactive_sessions(self, hours: int = 24) -> int:
        """
        Clean up sessions that have been inactive for a specified time
        
        This helps manage memory in long-running applications
        
        Args:
            hours: Number of hours of inactivity before cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        sessions_to_remove = []
        
        for session_id, session in self._sessions.items():
            last_active = datetime.fromisoformat(session['last_active'])
            if last_active < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self._sessions[session_id]
            self._active_sessions.discard(session_id)
        
        if sessions_to_remove:
            logger.info(f"[SessionManager] Cleaned up {len(sessions_to_remove)} inactive sessions")
        
        return len(sessions_to_remove)
    
    def get_active_session_count(self) -> int:
        """Get count of currently active sessions"""
        return len(self._active_sessions)
    
    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export session data as JSON string
        
        Useful for saving session data or transferring to long-term storage
        
        Args:
            session_id: Session identifier
            
        Returns:
            JSON string of session data or None if session doesn't exist
        """
        import json
        
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        try:
            return json.dumps(session, indent=2)
        except Exception as e:
            logger.error(f"[SessionManager] Error exporting session: {str(e)}")
            return None
    
    def import_session(self, session_id: str, session_data: str) -> bool:
        """
        Import session data from JSON string
        
        Args:
            session_id: Session identifier to import to
            session_data: JSON string of session data
            
        Returns:
            bool indicating success
        """
        import json
        
        try:
            session = json.loads(session_data)
            self._sessions[session_id] = session
            self._active_sessions.add(session_id)
            
            logger.info(f"[SessionManager] Imported session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"[SessionManager] Error importing session: {str(e)}")
            return False