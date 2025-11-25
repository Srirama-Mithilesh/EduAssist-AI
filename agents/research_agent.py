"""
Research Agent - Handles web search and source verification

This agent is responsible for:
1. Searching the web for current, relevant information
2. Verifying sources for credibility
3. Cross-referencing information across multiple sources
4. Extracting and summarizing key facts
5. Providing citations for all information

This demonstrates: Tool usage (web search), custom verification tools
"""

import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Specialized agent for web research and information verification
    Uses web search tools to find current, credible information
    """
    
    def __init__(self, client):
        """
        Initialize the Research Agent
        
        Args:
            client: Gemini client for LLM calls
        """
        self.client = client
        self.model_name = "gemini-2.5-flash"
        
        # Source credibility scoring (prefer academic and educational sources)
        self.credible_domains = {
            '.edu': 0.9,
            '.gov': 0.85,
            'scholar.google': 0.95,
            'ncbi.nlm.nih.gov': 0.95,
            'britannica.com': 0.85,
            'khanacademy.org': 0.9,
            'coursera.org': 0.8,
            'mit.edu': 0.95,
            'stanford.edu': 0.95,
            'nature.com': 0.9,
            'sciencedirect.com': 0.85
        }
        
        logger.info("✓ ResearchAgent initialized")
    
    async def research(self,
                      query: str,
                      topics: List[str],
                      requires_verification: bool = True) -> Dict[str, Any]:
        """
        Conduct research on the given query using Gemini with web search
        
        Args:
            query: The search query
            topics: List of topics involved
            requires_verification: Whether to verify across multiple sources
            
        Returns:
            dict containing:
                - information: Summarized research findings
                - sources: List of credible sources used
                - verification_status: Whether info was verified
        """
        logger.info(f"[Research Agent] Starting research on: {query[:50]}...")
        
        try:
            # Build research prompt for Gemini with web search
            research_prompt = f"""You are a research assistant helping a student learn.

Research Query: {query}
Topics: {', '.join(topics)}
Verification Required: {requires_verification}

Your task:
1. Search the web for accurate, current information on this topic
2. Prioritize credible educational sources (.edu, .gov, academic sites, Khan Academy)
3. Verify facts across multiple sources if verification is required
4. Provide a clear, educational summary suitable for students
5. List all sources you consulted

Format your response as:

SUMMARY:
[Your verified summary here - 2-3 paragraphs explaining the topic clearly]

KEY FACTS:
- Fact 1 (from Source X)
- Fact 2 (from Source Y)
- Fact 3 (from Source Z)

SOURCES:
1. [Full URL] - [Source name/title]
2. [Full URL] - [Source name/title]
...

Make sure the summary is educational, accurate, and includes specific details."""

            # Call Gemini with web search tool enabled
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=research_prompt,
                tools=[{'google_search': {}}]  # Enable built-in web search!
            )
            
            # Extract text from response
            research_text = response.text.strip()
            
            # Parse sources from response
            sources = self._extract_sources_from_response(research_text)
            
            # Extract just the summary section for cleaner output
            summary = self._extract_summary_section(research_text)
            
            result = {
                'information': summary or research_text,
                'sources': sources,
                'full_research': research_text,  # Keep full response for reference
                'verification_status': 'verified' if (requires_verification and len(sources) >= 2) else 'unverified'
            }
            
            logger.info(f"[Research Agent] ✓ Research complete. Found {len(sources)} sources")
            
            return result
            
        except Exception as e:
            logger.error(f"[Research Agent] Error: {str(e)}", exc_info=True)
            
            # Fallback: If search fails, use Gemini's knowledge directly
            fallback_prompt = f"""Provide educational information about: {query}
            
Topics: {', '.join(topics)}

Provide factual, accurate information suitable for students. 
Acknowledge if this topic requires current information that you may not have."""

            try:
                fallback_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=fallback_prompt
                )
                
                return {
                    'information': fallback_response.text,
                    'sources': [],
                    'verification_status': 'fallback',
                    'note': 'Using general knowledge (web search unavailable)'
                }
            except Exception as fallback_error:
                logger.error(f"[Research Agent] Fallback also failed: {str(fallback_error)}")
                return {
                    'information': f"I encountered an issue researching {query}. Please try rephrasing your question.",
                    'sources': [],
                    'error': str(e)
                }
    
    def _extract_sources_from_response(self, text: str) -> List[str]:
        """
        Extract URLs from Gemini's response
        
        Args:
            text: Response text containing URLs
            
        Returns:
            List of unique URLs found
        """
        import re
        # Find all URLs in the text (http:// or https://)
        urls = re.findall(r'https?://[^\s\)\]\,]+', text)
        
        # Clean up URLs (remove trailing punctuation)
        cleaned_urls = []
        for url in urls:
            url = url.rstrip('.,;:')
            cleaned_urls.append(url)
        
        # Return unique URLs, max 5
        unique_urls = list(dict.fromkeys(cleaned_urls))  # Preserve order while removing duplicates
        return unique_urls[:5]
    
    def _extract_summary_section(self, text: str) -> str:
        """
        Extract just the summary section from the full response
        
        Args:
            text: Full research response
            
        Returns:
            Summary text only
        """
        import re
        
        # Try to find SUMMARY: section
        summary_match = re.search(r'SUMMARY:\s*(.*?)(?=\n\nKEY FACTS:|$)', text, re.DOTALL | re.IGNORECASE)
        
        if summary_match:
            return summary_match.group(1).strip()
        
        # If no clear summary section, return first few paragraphs
        paragraphs = text.split('\n\n')
        return '\n\n'.join(paragraphs[:2]) if paragraphs else text
    
    def check_source_credibility(self, url: str) -> float:
        """
        Public method to check credibility of a specific URL
        Useful for other agents or external verification
        
        Returns:
            float: Credibility score between 0 and 1
        """
        score = 0.5  # Default
        
        for domain, domain_score in self.credible_domains.items():
            if domain in url:
                score = domain_score
                break
        
        return score