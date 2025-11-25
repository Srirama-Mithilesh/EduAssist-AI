"""
Context Manager - Context engineering and compaction

This handles:
1. Context window management to stay within token limits
2. Context compaction (summarizing old conversations)
3. Relevant context retrieval
4. Smart context prioritization

This demonstrates: Context engineering (context compaction)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages context for agent interactions to optimize token usage
    
    Key responsibilities:
    - Keep context within model token limits
    - Prioritize recent and relevant information
    - Compact older context through summarization
    - Maintain conversation coherence
    """
    
    def __init__(self, max_context_tokens: int = 8000):
        """
        Initialize context manager
        
        Args:
            max_context_tokens: Maximum tokens to use for context
                               (leaves room for prompt and response)
        """
        self.max_context_tokens = max_context_tokens
        
        # Rough estimation: 1 token ≈ 4 characters for English text
        self.chars_per_token = 4
        self.max_context_chars = max_context_tokens * self.chars_per_token
        
        logger.info(f"✓ ContextManager initialized (max tokens: {max_context_tokens})")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        This is a rough approximation. For production, use:
        - tiktoken library for accurate counting
        - Model-specific tokenizers
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        return len(text) // self.chars_per_token
    
    def summarize_context(self, session_context: Dict[str, Any]) -> str:
        """
        Create a compact summary of session context
        
        This is used when we need to provide context to agents
        but want to minimize token usage
        
        Args:
            session_context: Full session context
            
        Returns:
            Concise summary string
        """
        summary_parts = []
        
        # Student level
        level = session_context.get('knowledge_level', 'unknown')
        summary_parts.append(f"Student level: {level}")
        
        # Topics discussed
        topics = session_context.get('recent_topics', [])
        if topics:
            summary_parts.append(f"Recent topics: {', '.join(topics[-5:])}")
        
        # Learning preferences
        preferences = session_context.get('learning_preferences', {})
        if preferences:
            pref_str = ', '.join([f"{k}: {v}" for k, v in preferences.items()])
            summary_parts.append(f"Preferences: {pref_str}")
        
        # Recent interactions count
        interactions = session_context.get('previous_interactions', [])
        if interactions:
            summary_parts.append(f"Previous questions: {len(interactions)}")
        
        summary = " | ".join(summary_parts)
        
        logger.debug(f"[ContextManager] Context summary: {summary[:100]}...")
        
        return summary
    
    def compact_interactions(self, 
                           interactions: List[Dict[str, Any]], 
                           target_count: int = 3) -> List[Dict[str, Any]]:
        """
        Compact interaction history to most recent and relevant items
        
        Strategy:
        - Always keep most recent interactions
        - Summarize older interactions
        - Remove middle interactions if needed
        
        Args:
            interactions: List of interaction dicts
            target_count: Target number of interactions to keep
            
        Returns:
            Compacted list of interactions
        """
        if len(interactions) <= target_count:
            return interactions
        
        # Keep most recent ones
        recent = interactions[-target_count:]
        
        # Summarize older ones if there are many
        if len(interactions) > target_count + 3:
            older_topics = set()
            for interaction in interactions[:-target_count]:
                if 'topics' in interaction:
                    older_topics.update(interaction.get('topics', []))
            
            # Add summary as a pseudo-interaction
            summary_interaction = {
                'timestamp': interactions[0].get('timestamp', ''),
                'query': f"[Summary: Discussed {len(older_topics)} topics including {', '.join(list(older_topics)[:3])}]",
                'response': '[Previous conversation context]',
                'is_summary': True
            }
            
            return [summary_interaction] + recent
        
        return recent
    
    def build_context_for_agent(self,
                                current_query: str,
                                session_context: Dict[str, Any],
                                include_interactions: bool = True,
                                max_tokens: Optional[int] = None) -> str:
        """
        Build optimized context string for agent consumption
        
        This creates a context string that:
        - Stays within token limits
        - Prioritizes relevant information
        - Is formatted for agent understanding
        
        Args:
            current_query: The current student query
            session_context: Full session context
            include_interactions: Whether to include past interactions
            max_tokens: Override max tokens for this context
            
        Returns:
            Formatted context string ready for agent
        """
        max_tokens = max_tokens or self.max_context_tokens
        max_chars = max_tokens * self.chars_per_token
        
        context_parts = []
        
        # Current query (always included)
        context_parts.append(f"Current Query: {current_query}")
        
        # Student level and preferences
        level = session_context.get('knowledge_level', 'high_school')
        context_parts.append(f"Student Level: {level}")
        
        preferences = session_context.get('learning_preferences', {})
        if preferences:
            context_parts.append(f"Learning Preferences: {preferences}")
        
        # Recent topics
        topics = session_context.get('recent_topics', [])
        if topics:
            context_parts.append(f"Recent Topics: {', '.join(topics[-5:])}")
        
        # Previous interactions (if requested and space allows)
        if include_interactions:
            interactions = session_context.get('previous_interactions', [])
            if interactions:
                # Estimate space remaining
                current_size = sum(len(part) for part in context_parts)
                space_remaining = max_chars - current_size
                
                # Determine how many interactions we can fit
                interactions_to_include = self._fit_interactions_in_space(
                    interactions, 
                    space_remaining
                )
                
                if interactions_to_include:
                    context_parts.append("\nPrevious Interactions:")
                    for interaction in interactions_to_include:
                        query = interaction.get('query', '')
                        response = interaction.get('response', '')
                        
                        # Truncate long responses
                        if len(response) > 200:
                            response = response[:200] + "..."
                        
                        context_parts.append(f"Q: {query}")
                        context_parts.append(f"A: {response}")
        
        # Combine all parts
        full_context = "\n".join(context_parts)
        
        # Final check: truncate if still too long
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "\n[Context truncated]"
        
        logger.debug(f"[ContextManager] Built context: {self.estimate_tokens(full_context)} tokens")
        
        return full_context
    
    def _fit_interactions_in_space(self,
                                   interactions: List[Dict[str, Any]],
                                   space_chars: int) -> List[Dict[str, Any]]:
        """
        Fit as many interactions as possible in the available space
        
        Prioritizes most recent interactions
        
        Args:
            interactions: List of interactions
            space_chars: Available character space
            
        Returns:
            List of interactions that fit
        """
        fitted = []
        current_size = 0
        
        # Start from most recent
        for interaction in reversed(interactions):
            query = interaction.get('query', '')
            response = interaction.get('response', '')[:200]  # Limit response length
            
            interaction_size = len(query) + len(response) + 10  # +10 for formatting
            
            if current_size + interaction_size > space_chars:
                break
            
            fitted.insert(0, interaction)  # Insert at beginning to maintain order
            current_size += interaction_size
        
        return fitted
    
    def prioritize_context_items(self,
                                items: List[Dict[str, Any]],
                                current_query: str,
                                max_items: int = 5) -> List[Dict[str, Any]]:
        """
        Prioritize context items based on relevance to current query
        
        Uses simple keyword matching. In production, would use:
        - Embeddings and semantic similarity
        - Vector databases for efficient retrieval
        
        Args:
            items: List of context items (interactions, topics, etc.)
            current_query: Current query to match against
            max_items: Maximum items to return
            
        Returns:
            Prioritized list of items
        """
        # Extract keywords from current query
        query_words = set(current_query.lower().split())
        
        # Score each item by keyword overlap
        scored_items = []
        for item in items:
            # Get text from item (handle different formats)
            item_text = ""
            if isinstance(item, dict):
                item_text = str(item.get('query', '')) + " " + str(item.get('response', ''))
            else:
                item_text = str(item)
            
            item_words = set(item_text.lower().split())
            
            # Calculate overlap score
            overlap = len(query_words & item_words)
            scored_items.append((overlap, item))
        
        # Sort by score (descending) and return top items
        scored_items.sort(reverse=True, key=lambda x: x[0])
        
        prioritized = [item for score, item in scored_items[:max_items]]
        
        logger.debug(f"[ContextManager] Prioritized {len(prioritized)}/{len(items)} items")
        
        return prioritized
    
    def create_context_snapshot(self, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a compact snapshot of context for logging or analysis
        
        Args:
            session_context: Full session context
            
        Returns:
            Compact snapshot dict
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'student_level': session_context.get('knowledge_level'),
            'topics_count': len(session_context.get('recent_topics', [])),
            'interactions_count': len(session_context.get('previous_interactions', [])),
            'estimated_tokens': self.estimate_tokens(str(session_context))
        }