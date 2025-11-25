"""
Memory Bank - Long-term persistent memory storage

This stores:
- Student learning profiles across sessions
- Historical topic mastery data
- Learning preferences and patterns
- Knowledge graphs of what students know

This demonstrates: Long-term memory (Memory Bank concept)
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryBank:
    """
    Long-term memory storage for student learning profiles
    
    In a production system, this would use:
    - A database (PostgreSQL, MongoDB)
    - Vector database for semantic search (Pinecone, Weaviate)
    - Cloud storage (Firebase, DynamoDB)
    
    For this hackathon implementation, we use local JSON files
    that persist across sessions.
    """
    
    def __init__(self, storage_dir: str = "./memory_bank"):
        """
        Initialize the memory bank
        
        Args:
            storage_dir: Directory to store profile files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # In-memory cache for faster access
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"✓ MemoryBank initialized at: {self.storage_dir}")
    
    def _get_profile_path(self, session_id: str) -> Path:
        """Get file path for a profile"""
        # Sanitize session_id for filename
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ('_', '-'))
        return self.storage_dir / f"profile_{safe_id}.json"
    
    async def get_profile(self, session_id: str) -> Dict[str, Any]:
        """
        Get a student's learning profile
        
        Args:
            session_id: Session/student identifier
            
        Returns:
            dict with learning profile
        """
        # Check cache first
        if session_id in self._cache:
            logger.debug(f"[MemoryBank] Profile retrieved from cache: {session_id}")
            return self._cache[session_id]
        
        # Load from file
        profile_path = self._get_profile_path(session_id)
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                
                # Update cache
                self._cache[session_id] = profile
                
                logger.debug(f"[MemoryBank] Profile loaded from disk: {session_id}")
                return profile
                
            except Exception as e:
                logger.error(f"[MemoryBank] Error loading profile: {str(e)}")
        
        # Return new profile if doesn't exist
        profile = self._create_new_profile()
        self._cache[session_id] = profile
        
        return profile
    
    def _create_new_profile(self) -> Dict[str, Any]:
        """
        Create a new student learning profile
        
        Returns:
            dict with initial profile structure
        """
        return {
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'topics_studied': {},  # topic -> {first_encountered, times_reviewed, mastery_level}
            'statistics': {
                'total_questions': 0,
                'total_sessions': 0,
                'average_response_quality': 0
            },
            'preferences': {
                'preferred_explanation_style': 'balanced',  # visual, text-heavy, example-driven, balanced
                'preferred_length': 'moderate',  # concise, moderate, detailed
                'difficulty_preference': 'auto'  # easy, moderate, challenging, auto
            },
            'estimated_level': 'high_school',
            'strong_areas': [],  # Topics where student excels
            'areas_for_improvement': [],  # Topics needing more work
            'learning_velocity': 0.5,  # How quickly student picks up new concepts (0-1)
            'knowledge_graph': {}  # Relationships between topics student knows
        }
    
    async def save_profile(self, session_id: str, profile: Dict[str, Any]) -> bool:
        """
        Save a student's learning profile
        
        Args:
            session_id: Session/student identifier
            profile: Profile data to save
            
        Returns:
            bool indicating success
        """
        try:
            # Update timestamp
            profile['last_updated'] = datetime.now().isoformat()
            
            # Update cache
            self._cache[session_id] = profile
            
            # Save to disk
            profile_path = self._get_profile_path(session_id)
            
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            logger.debug(f"[MemoryBank] Profile saved: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"[MemoryBank] Error saving profile: {str(e)}")
            return False
    
    async def update_topic_mastery(self,
                              session_id: str,
                              topic: str,
                              performance_score: float) -> None:
        """
        Update mastery level for a specific topic with advanced learning analytics
        
        Features:
        - Weighted scoring (recent performance matters more)
        - Fast learner detection
        - Progressive difficulty tracking
        
        Args:
            session_id: Session/student identifier
            topic: Topic being studied
            performance_score: How well student is doing (0-1)
        """
        profile = await self.get_profile(session_id)
        
        topics_studied = profile.get('topics_studied', {})
        
        if topic not in topics_studied:
            # Detect fast learners FIRST (high score on first try)
            is_fast_learner = performance_score >= 0.8
            initial_mastery = 'familiar' if is_fast_learner else 'introduced'
            initial_pace = 'fast_learner' if is_fast_learner else 'unknown'
            
            # First time encountering this topic
            topics_studied[topic] = {
                'first_encountered': datetime.now().isoformat(),
                'times_reviewed': 1,
                'last_reviewed': datetime.now().isoformat(),
                'mastery_level': initial_mastery,  # 'familiar' for fast learners, 'introduced' for others
                'performance_scores': [performance_score],
                'difficulty_level': 'basic',
                'learning_pace': initial_pace
            }
            
            if is_fast_learner:
                logger.info(f"[MemoryBank] Fast learner detected for {topic} - mastery set to: {initial_mastery}")
            
            # Save immediately after first encounter
            profile['topics_studied'] = topics_studied
            await self.save_profile(session_id, profile)
            
            logger.debug(f"[MemoryBank] New topic mastery for {topic}: {initial_mastery} (score: {performance_score:.2f})")
            
        else:
            # Subsequent reviews
            topics_studied[topic]['times_reviewed'] += 1
            topics_studied[topic]['last_reviewed'] = datetime.now().isoformat()
            topics_studied[topic]['performance_scores'].append(performance_score)
            
            # Calculate WEIGHTED average (recent scores matter more)
            weighted_avg = self._calculate_weighted_score(
                topics_studied[topic]['performance_scores']
            )
            
            # Update difficulty level based on progression
            topics_studied[topic]['difficulty_level'] = self._determine_next_difficulty(
                topics_studied[topic]
            )
            
            times_reviewed = topics_studied[topic]['times_reviewed']
            
            # Enhanced mastery determination with weighted scoring
            if weighted_avg >= 0.85 and times_reviewed >= 4:
                topics_studied[topic]['mastery_level'] = 'mastered'
            elif weighted_avg >= 0.75 and times_reviewed >= 3:
                topics_studied[topic]['mastery_level'] = 'proficient'
            elif weighted_avg >= 0.65 and times_reviewed >= 2:
                topics_studied[topic]['mastery_level'] = 'familiar'
            elif times_reviewed >= 2:
                topics_studied[topic]['mastery_level'] = 'learning'
            else:
                topics_studied[topic]['mastery_level'] = 'introduced'
            
            # Detect learning pace if not already set
            if topics_studied[topic].get('learning_pace') == 'unknown':
                topics_studied[topic]['learning_pace'] = self._detect_learning_pace(
                    topics_studied[topic]['performance_scores']
                )
            
            # Save after subsequent reviews
            profile['topics_studied'] = topics_studied
            await self.save_profile(session_id, profile)
            
            logger.debug(f"[MemoryBank] Updated mastery for {topic}: {topics_studied[topic]['mastery_level']} "
                        f"(weighted avg: {weighted_avg:.2f})")
    
    def _calculate_weighted_score(self, scores: List[float]) -> float:
        """
        Calculate weighted average where recent scores matter more
        
        Uses exponential weighting: most recent = 1.0, second recent = 0.8, etc.
        
        Args:
            scores: List of performance scores (oldest to newest)
            
        Returns:
            Weighted average score
        """
        if not scores:
            return 0.0
        
        if len(scores) == 1:
            return scores[0]
        
        # Exponential weights: [0.5, 0.65, 0.8, 0.9, 1.0] for last 5 scores
        weights = [0.5 + (i * 0.15) for i in range(len(scores))]
        weights = [min(1.0, w) for w in weights]  # Cap at 1.0
        
        # Only use last 5 scores to avoid too much history
        recent_scores = scores[-5:]
        recent_weights = weights[-len(recent_scores):]
        
        # Calculate weighted sum
        weighted_sum = sum(s * w for s, w in zip(recent_scores, recent_weights))
        weight_total = sum(recent_weights)
        
        # Prevent division by zero
        if weight_total == 0:
            logger.warning("[MemoryBank] Weight total is zero, returning simple average")
            return sum(recent_scores) / len(recent_scores)
        
        return weighted_sum / weight_total
    
    def _determine_next_difficulty(self, topic_data: Dict[str, Any]) -> str:
        """
        Determine next question difficulty based on student progress
        
        Progressive difficulty: basic → intermediate → advanced → expert
        
        Args:
            topic_data: Topic information including scores and mastery
            
        Returns:
            Difficulty level for next question
        """
        current_difficulty = topic_data.get('difficulty_level', 'basic')
        mastery_level = topic_data.get('mastery_level', 'introduced')
        times_reviewed = topic_data.get('times_reviewed', 1)
        scores = topic_data.get('performance_scores', [])
        
        # Get recent performance (last 2 scores)
        recent_avg = sum(scores[-2:]) / len(scores[-2:]) if len(scores) >= 2 else scores[-1]
        
        # Progression logic
        difficulty_progression = {
            'basic': 'intermediate',
            'intermediate': 'advanced',
            'advanced': 'expert',
            'expert': 'expert'  # Max difficulty
        }
        
        # Advance difficulty if doing well
        if recent_avg >= 0.75 and times_reviewed >= 2:
            if mastery_level in ['proficient', 'mastered']:
                return difficulty_progression.get(current_difficulty, 'intermediate')
        
        # Stay at current difficulty if struggling
        if recent_avg < 0.6:
            return current_difficulty
        
        # Default progression based on times reviewed
        if times_reviewed >= 5:
            return 'advanced'
        elif times_reviewed >= 3:
            return 'intermediate'
        else:
            return 'basic'
    
    def _detect_learning_pace(self, scores: List[float]) -> str:
        """
        Detect student's learning pace based on score progression
        
        Args:
            scores: List of performance scores
            
        Returns:
            Learning pace: 'fast_learner', 'steady_learner', or 'needs_support'
        """
        if len(scores) < 2:
            return 'unknown'
        
        # Calculate improvement rate
        first_score = scores[0]
        recent_avg = sum(scores[-2:]) / len(scores[-2:])
        improvement = recent_avg - first_score
        
        # Fast learner: high scores consistently or rapid improvement
        if first_score >= 0.8 or (improvement >= 0.3 and recent_avg >= 0.75):
            return 'fast_learner'
        
        # Needs support: low scores or declining
        elif recent_avg < 0.5 or improvement < -0.1:
            return 'needs_support'
        
        # Steady learner: consistent moderate improvement
        else:
            return 'steady_learner'
    
    async def get_knowledge_gaps(self, session_id: str) -> Dict[str, Any]:
        """
        Identify knowledge gaps based on learning history
        
        Finds:
        - Prerequisites not yet studied
        - Topics started but not mastered
        - Areas with low performance scores
        
        Args:
            session_id: Session/student identifier
            
        Returns:
            dict with identified gaps and recommendations
        """
        profile = await self.get_profile(session_id)
        topics_studied = profile.get('topics_studied', {})
        
        gaps = {
            'not_mastered': [],
            'needs_review': [],
            'struggling_with': []
        }
        
        for topic, data in topics_studied.items():
            mastery_level = data.get('mastery_level', 'introduced')
            
            # Topics not yet mastered
            if mastery_level in ['introduced', 'learning']:
                gaps['not_mastered'].append(topic)
            
            # Topics that need review (not reviewed recently)
            last_reviewed = datetime.fromisoformat(data.get('last_reviewed', datetime.now().isoformat()))
            days_since = (datetime.now() - last_reviewed).days
            
            if days_since >= 14 and mastery_level != 'mastered':
                gaps['needs_review'].append(topic)
            
            # Topics with low performance
            if 'performance_scores' in data:
                avg_score = sum(data['performance_scores']) / len(data['performance_scores'])
                if avg_score < 0.6:
                    gaps['struggling_with'].append(topic)
        
        return gaps
    
    async def build_knowledge_graph(self, session_id: str) -> Dict[str, Any]:
        """
        Build a knowledge graph showing relationships between topics
        
        This helps visualize what the student knows and how concepts connect
        
        Args:
            session_id: Session/student identifier
            
        Returns:
            dict representing knowledge graph
        """
        profile = await self.get_profile(session_id)
        topics_studied = profile.get('topics_studied', {})
        
        # Simple graph structure: topic -> related topics
        knowledge_graph = {}
        
        for topic in topics_studied.keys():
            # In a real implementation, this would use NLP/embedding similarity
            # to find related topics. For now, we'll keep it simple.
            knowledge_graph[topic] = {
                'mastery': topics_studied[topic].get('mastery_level'),
                'times_reviewed': topics_studied[topic].get('times_reviewed'),
                'related_topics': []  # Would be populated with semantic similarity
            }
        
        profile['knowledge_graph'] = knowledge_graph
        await self.save_profile(session_id, profile)
        
        return knowledge_graph
    
    async def export_profile(self, session_id: str) -> Optional[str]:
        """
        Export profile as JSON string for backup or transfer
        
        Args:
            session_id: Session/student identifier
            
        Returns:
            JSON string or None if profile doesn't exist
        """
        profile = await self.get_profile(session_id)
        
        if not profile:
            return None
        
        try:
            return json.dumps(profile, indent=2)
        except Exception as e:
            logger.error(f"[MemoryBank] Error exporting profile: {str(e)}")
            return None
    
    def list_all_profiles(self) -> list:
        """
        List all stored profiles
        
        Returns:
            List of session IDs that have profiles
        """
        profiles = []
        
        for file_path in self.storage_dir.glob("profile_*.json"):
            # Extract session_id from filename
            session_id = file_path.stem.replace('profile_', '')
            profiles.append(session_id)
        
        return profiles
    
    async def clear_profile(self, session_id: str) -> bool:
        """
        Delete a profile (use with caution!)
        
        Args:
            session_id: Session/student identifier
            
        Returns:
            bool indicating success
        """
        try:
            # Remove from cache
            if session_id in self._cache:
                del self._cache[session_id]
            
            # Remove from disk
            profile_path = self._get_profile_path(session_id)
            if profile_path.exists():
                profile_path.unlink()
            
            logger.info(f"[MemoryBank] Profile cleared: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"[MemoryBank] Error clearing profile: {str(e)}")
            return False