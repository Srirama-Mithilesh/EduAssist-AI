"""
Coordinator Agent - The orchestrator of EduAssist AI

This agent is responsible for:
1. Analyzing student queries to understand intent
2. Routing queries to appropriate specialized agents
3. Managing sequential and parallel agent execution
4. Synthesizing responses from multiple agents
5. Ensuring coherent final answers to students

This demonstrates: Multi-agent orchestration, decision-making logic
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Main orchestrator that coordinates all specialized agents
    to provide comprehensive educational assistance
    """
    
    def __init__(self, client, memory_agent, research_agent, tutor_agent, context_manager):
        """
        Initialize the Coordinator Agent
        
        Args:
            client: Gemini client for LLM calls
            memory_agent: Agent handling memory and context
            research_agent: Agent handling web search and verification
            tutor_agent: Agent handling explanations and tutoring
            context_manager: Manages context window and token limits
        """
        self.client = client
        self.memory_agent = memory_agent
        self.research_agent = research_agent
        self.tutor_agent = tutor_agent
        self.context_manager = context_manager
        
        # Model configuration - using Gemini 2.0 Flash for speed
        self.model_name = "gemini-2.5-flash"
        
        logger.info(f"✓ CoordinatorAgent initialized with model: {self.model_name}")
    
    async def process(self, 
                     query: str,
                     session_id: str,
                     session_context: Dict[str, Any],
                     student_level: str) -> Dict[str, Any]:
        """
        Main processing pipeline for student queries
        
        This method orchestrates the entire multi-agent workflow:
        1. Analyze query intent
        2. Determine which agents to invoke
        3. Execute agents (sequential or parallel as needed)
        4. Synthesize final response
        
        Args:
            query: Student's question
            session_id: Session identifier
            session_context: Previous conversation context from memory
            student_level: Student's education level
            
        Returns:
            dict with answer, sources, agent_trace, topics_covered
        """
        logger.info(f"[Coordinator] Processing query for session: {session_id}")
        
        # Initialize agent trace for observability
        agent_trace = []
        start_time = datetime.now()
        
        try:
            # STEP 1: Analyze the query to determine intent and required actions
            query_analysis = await self._analyze_query(
                query=query,
                session_context=session_context,
                student_level=student_level
            )
            
            agent_trace.append({
                'agent': 'coordinator',
                'action': 'query_analysis',
                'result': query_analysis,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"[Coordinator] Query analysis: {query_analysis['intent']}")
            
            # STEP 2: Determine which agents to invoke based on analysis
            agents_needed = query_analysis['agents_needed']
            
            # STEP 3: Execute agents based on strategy
            agent_results = await self._execute_agents(
                query=query,
                query_analysis=query_analysis,
                agents_needed=agents_needed,
                session_context=session_context,
                student_level=student_level,
                agent_trace=agent_trace
            )
            
            # STEP 4: Synthesize final response from all agent outputs
            final_response = await self._synthesize_response(
                query=query,
                query_analysis=query_analysis,
                agent_results=agent_results,
                student_level=student_level
            )
            
            agent_trace.append({
                'agent': 'coordinator',
                'action': 'synthesis_complete',
                'timestamp': datetime.now().isoformat()
            })
            
            # STEP 5: Prepare final output
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'answer': final_response['answer'],
                'sources': final_response.get('sources', []),
                'topics_covered': query_analysis.get('topics', []),
                'agent_trace': agent_trace,
                'quality_score': final_response.get('quality_score', 0.8),
                'processing_time': processing_time
            }
            
            logger.info(f"[Coordinator] ✓ Processing complete in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"[Coordinator] Error: {str(e)}", exc_info=True)
            agent_trace.append({
                'agent': 'coordinator',
                'action': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'answer': "I encountered an issue processing your question. Could you rephrase it?",
                'sources': [],
                'topics_covered': [],
                'agent_trace': agent_trace,
                'error': str(e)
            }
    
    async def _analyze_query(self, 
                            query: str, 
                            session_context: Dict[str, Any],
                            student_level: str) -> Dict[str, Any]:
        """
        Analyze the student's query to determine:
        - Intent (factual question, explanation needed, clarification, etc.)
        - Topics involved
        - Which agents should be invoked
        - Whether real-time information is needed
        
        This uses Gemini to understand the query in context
        """
        # Build analysis prompt with context
        context_summary = self.context_manager.summarize_context(session_context)
        
        analysis_prompt = f"""You are analyzing a student's query to determine how to best help them learn.

Student Level: {student_level}
Previous Context: {context_summary}

Current Query: "{query}"

Analyze this query and respond with a JSON object containing:
1. "intent": The primary intent (factual_question, concept_explanation, clarification, comparison, application, etc.)
2. "topics": List of topics/concepts involved
3. "requires_current_info": Boolean - ONLY TRUE if this needs very recent/up-to-date information (news, current events, recent discoveries)
4. "requires_research": Boolean - ONLY TRUE if verification or multiple sources needed (set FALSE for basic math, well-known facts, simple definitions)
5. "complexity": Level (basic, intermediate, advanced)
6. "agents_needed": List of agents to invoke - choose from: ["memory", "research", "tutor"]
   - Use "memory" if query references previous conversation
   - Use "research" ONLY if current information or verification needed (NOT for simple/well-known facts)
   - Use "tutor" for explanations and concept breakdowns
7. "execution_strategy": "sequential" or "parallel"

IMPORTANT GUIDELINES FOR "requires_research":
- Set FALSE for: basic math (2+2), simple definitions, well-known historical facts, fundamental concepts
- Set FALSE for: questions answerable with general knowledge (photosynthesis basics, capitals, etc.)
- Set TRUE for: current events, recent discoveries, specific statistics, disputed facts, complex technical details
- When in doubt, prefer FALSE to save time and cost

Example response:
{{
  "intent": "concept_explanation",
  "topics": ["quantum mechanics", "entanglement"],
  "requires_current_info": false,
  "requires_research": false,
  "complexity": "intermediate",
  "agents_needed": ["tutor"],
  "execution_strategy": "sequential"
}}

Provide only the JSON response, no other text."""

        try:
            # Call Gemini for analysis
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=analysis_prompt
            )
            
            # Parse the JSON response
            import json
            analysis_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if analysis_text.startswith('```'):
                # Remove opening ```
                parts = analysis_text.split('```')
                if len(parts) >= 2:
                    analysis_text = parts[1]
                    if analysis_text.startswith('json'):
                        analysis_text = analysis_text[4:]
                    # Remove any trailing ```
                    if '```' in analysis_text:
                        analysis_text = analysis_text.split('```')[0]
                analysis_text = analysis_text.strip()
            
            # Parse JSON with error handling
            try:
                analysis = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                logger.warning(f"[Coordinator] JSON parse failed: {str(e)}, trying to extract JSON from text")
                # Try to find JSON object in the text
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    raise ValueError("Could not find valid JSON in response")
            
            # Validate required fields
            required_fields = ['intent', 'topics', 'requires_current_info', 'requires_research', 
                             'complexity', 'agents_needed', 'execution_strategy']
            
            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"[Coordinator] Missing field '{field}' in analysis, using default")
                    # Add default values for missing fields
                    if field == 'intent':
                        analysis[field] = 'general_question'
                    elif field == 'topics':
                        analysis[field] = ['general']
                    elif field in ['requires_current_info', 'requires_research']:
                        analysis[field] = False
                    elif field == 'complexity':
                        analysis[field] = 'intermediate'
                    elif field == 'agents_needed':
                        analysis[field] = ['tutor']
                    elif field == 'execution_strategy':
                        analysis[field] = 'sequential'
            
            return analysis
            
        except Exception as e:
            logger.error(f"[Coordinator] Analysis failed: {str(e)}, using safe defaults")
            # Fallback to safe defaults if analysis completely fails
            return {
                'intent': 'general_question',
                'topics': ['unknown'],
                'requires_current_info': False,
                'requires_research': False,
                'complexity': 'intermediate',
                'agents_needed': ['tutor'],
                'execution_strategy': 'sequential'
            }
    
    async def _execute_agents(self,
                             query: str,
                             query_analysis: Dict[str, Any],
                             agents_needed: List[str],
                             session_context: Dict[str, Any],
                             student_level: str,
                             agent_trace: List[Dict]) -> Dict[str, Any]:
        """
        Execute the required agents based on analysis
        
        Supports both sequential and parallel execution strategies:
        - Sequential: Memory -> Research -> Tutor (when each depends on previous)
        - Parallel: Research multiple sources simultaneously
        """
        results = {}
        strategy = query_analysis.get('execution_strategy', 'sequential')
        
        logger.info(f"[Coordinator] Executing agents: {agents_needed} ({strategy})")
        
        if strategy == 'parallel' and 'research' in agents_needed:
            # Parallel execution for research (can search multiple things at once)
            results['research'] = await self._execute_research_parallel(
                query=query,
                query_analysis=query_analysis,
                agent_trace=agent_trace
            )
        else:
            # Sequential execution (default and safest)
            # This ensures each agent can use the output of previous agents
            
            # 1. Memory Agent (if needed)
            if 'memory' in agents_needed:
                results['memory'] = await self._execute_memory_agent(
                    query=query,
                    session_context=session_context,
                    agent_trace=agent_trace
                )
            
            # 2. Research Agent (if needed)
            if 'research' in agents_needed:
                results['research'] = await self._execute_research_agent(
                    query=query,
                    query_analysis=query_analysis,
                    agent_trace=agent_trace
                )
            
            # 3. Tutor Agent (almost always needed)
            if 'tutor' in agents_needed:
                results['tutor'] = await self._execute_tutor_agent(
                    query=query,
                    query_analysis=query_analysis,
                    research_results=results.get('research'),
                    memory_results=results.get('memory'),
                    student_level=student_level,
                    agent_trace=agent_trace
                )
        
        return results
    
    async def _execute_memory_agent(self,
                                    query: str,
                                    session_context: Dict[str, Any],
                                    agent_trace: List[Dict]) -> Dict[str, Any]:
        """Execute memory agent to retrieve relevant past context"""
        logger.info("[Coordinator] → Invoking Memory Agent")
        
        try:
            result = await self.memory_agent.retrieve_relevant_context(
                query=query,
                session_context=session_context
            )
            
            agent_trace.append({
                'agent': 'memory',
                'action': 'context_retrieval',
                'result_summary': f"Retrieved {len(result.get('relevant_items', []))} items",
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"[Memory Agent] Error: {str(e)}")
            return {'relevant_items': [], 'error': str(e)}
    
    async def _execute_research_agent(self,
                                      query: str,
                                      query_analysis: Dict[str, Any],
                                      agent_trace: List[Dict]) -> Dict[str, Any]:
        """Execute research agent for web search and verification"""
        logger.info("[Coordinator] → Invoking Research Agent")
        
        try:
            result = await self.research_agent.research(
                query=query,
                topics=query_analysis.get('topics', []),
                requires_verification=query_analysis.get('requires_research', True)
            )
            
            agent_trace.append({
                'agent': 'research',
                'action': 'web_research',
                'result_summary': f"Found {len(result.get('sources', []))} sources",
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"[Research Agent] Error: {str(e)}")
            return {'sources': [], 'information': '', 'error': str(e)}
    
    async def _execute_research_parallel(self,
                                        query: str,
                                        query_analysis: Dict[str, Any],
                                        agent_trace: List[Dict]) -> Dict[str, Any]:
        """Execute multiple research queries in parallel for faster results"""
        logger.info("[Coordinator] → Invoking Research Agent (parallel mode)")
        
        topics = query_analysis.get('topics', [query])
        
        # Create parallel research tasks
        tasks = [
            self.research_agent.research(
                query=f"{topic} {query}",
                topics=[topic],
                requires_verification=True
            )
            for topic in topics[:3]  # Limit to 3 parallel searches
        ]
        
        try:
            # Execute all research tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            combined_sources = []
            combined_info = []
            
            for result in results:
                if isinstance(result, dict) and not isinstance(result, Exception):
                    combined_sources.extend(result.get('sources', []))
                    combined_info.append(result.get('information', ''))
            
            agent_trace.append({
                'agent': 'research',
                'action': 'parallel_web_research',
                'result_summary': f"Found {len(combined_sources)} sources across {len(tasks)} searches",
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'sources': combined_sources,
                'information': '\n\n'.join(combined_info)
            }
            
        except Exception as e:
            logger.error(f"[Research Agent Parallel] Error: {str(e)}")
            return {'sources': [], 'information': '', 'error': str(e)}
    
    async def _execute_tutor_agent(self,
                                   query: str,
                                   query_analysis: Dict[str, Any],
                                   research_results: Optional[Dict[str, Any]],
                                   memory_results: Optional[Dict[str, Any]],
                                   student_level: str,
                                   agent_trace: List[Dict]) -> Dict[str, Any]:
        """Execute tutor agent to create educational explanation"""
        logger.info("[Coordinator] → Invoking Tutor Agent")
        
        try:
            result = await self.tutor_agent.explain(
                query=query,
                student_level=student_level,
                research_info=research_results.get('information', '') if research_results else '',
                context=memory_results if memory_results else {},
                complexity=query_analysis.get('complexity', 'intermediate')
            )
            
            agent_trace.append({
                'agent': 'tutor',
                'action': 'explanation_generation',
                'result_summary': 'Explanation generated',
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"[Tutor Agent] Error: {str(e)}")
            return {'explanation': '', 'error': str(e)}
    
    async def _synthesize_response(self,
                                   query: str,
                                   query_analysis: Dict[str, Any],
                                   agent_results: Dict[str, Any],
                                   student_level: str) -> Dict[str, Any]:
        """
        Synthesize final response from all agent outputs
        
        This is where we combine:
        - Research findings (with citations)
        - Tutor explanations (adapted to level)
        - Memory context (for continuity)
        
        Into one coherent, helpful answer
        """
        logger.info("[Coordinator] Synthesizing final response...")
        
        # Extract information from agent results
        research_info = agent_results.get('research', {}).get('information', '')
        research_sources = agent_results.get('research', {}).get('sources', [])
        tutor_explanation = agent_results.get('tutor', {}).get('explanation', '')
        
        # Build synthesis prompt
        synthesis_prompt = f"""You are synthesizing a final response for a student.

Student Level: {student_level}
Query: "{query}"

Available Information:
{research_info}

Tutor's Explanation:
{tutor_explanation}

Create a comprehensive, clear answer that:
1. Directly answers the student's question
2. Uses appropriate complexity for their level
3. Cites sources when using specific facts
4. Is engaging and educational
5. Ends with a related question or encouragement

Keep the response focused and not too long (2-4 paragraphs unless more detail needed)."""

        try:
            # Generate final synthesis
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=synthesis_prompt
            )
            
            final_answer = response.text.strip()
            
            return {
                'answer': final_answer,
                'sources': research_sources,
                'quality_score': 0.85  # Could implement actual quality scoring
            }
            
        except Exception as e:
            logger.error(f"[Coordinator] Synthesis failed: {str(e)}")
            
            # Fallback: use tutor explanation if synthesis fails
            return {
                'answer': tutor_explanation or "I'm having trouble formulating a complete answer right now. Could you rephrase your question?",
                'sources': research_sources,
                'quality_score': 0.6
            }