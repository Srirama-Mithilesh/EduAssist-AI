"""
Tutor Agent - Provides adaptive educational explanations

This agent is responsible for:
1. Breaking down complex concepts into understandable parts
2. Adapting explanations to student's education level
3. Providing examples, analogies, and visual descriptions
4. Asking clarifying questions when needed
5. Identifying and addressing misconceptions
6. Creating step-by-step learning paths

This demonstrates: Adaptive AI, pedagogical intelligence, personalization
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TutorAgent:
    """
    Specialized agent for educational explanations and tutoring
    Adapts teaching style based on student level and learning context
    """
    
    def __init__(self, client):
        """
        Initialize the Tutor Agent
        
        Args:
            client: Gemini client for LLM calls
        """
        self.client = client
        self.model_name = "gemini-2.5-flash"
        
        # Define teaching strategies for different levels
        self.level_strategies = {
            'elementary': {
                'vocabulary': 'simple, everyday words',
                'sentence_length': 'short sentences',
                'examples': 'concrete, relatable examples from daily life',
                'analogies': 'simple comparisons to familiar things',
                'depth': 'surface-level understanding'
            },
            'middle_school': {
                'vocabulary': 'age-appropriate with some technical terms explained',
                'sentence_length': 'moderate length',
                'examples': 'mix of concrete and abstract examples',
                'analogies': 'creative analogies and metaphors',
                'depth': 'fundamental concepts with some detail'
            },
            'high_school': {
                'vocabulary': 'technical terms with clear definitions',
                'sentence_length': 'varied length for engagement',
                'examples': 'real-world applications and scenarios',
                'analogies': 'sophisticated analogies when helpful',
                'depth': 'comprehensive understanding with connections'
            },
            'college': {
                'vocabulary': 'academic terminology expected',
                'sentence_length': 'complex sentences when needed',
                'examples': 'advanced applications and case studies',
                'analogies': 'used sparingly for complex concepts',
                'depth': 'deep understanding with theoretical framework'
            },
            'graduate': {
                'vocabulary': 'specialized academic language',
                'sentence_length': 'sophisticated academic style',
                'examples': 'research-level examples and current debates',
                'analogies': 'rare, only for extremely abstract concepts',
                'depth': 'expert-level depth with nuance and limitations'
            }
        }
        
        logger.info("✓ TutorAgent initialized")
    
    async def explain(self,
                     query: str,
                     student_level: str,
                     research_info: str = '',
                     context: Dict[str, Any] = None,
                     complexity: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate an adaptive educational explanation
        
        Args:
            query: Student's question
            student_level: Education level (elementary, middle_school, high_school, college, graduate)
            research_info: Verified information from research agent
            context: Previous conversation context
            complexity: Complexity of the topic (basic, intermediate, advanced)
            
        Returns:
            dict containing:
                - explanation: The educational explanation
                - teaching_strategy: Strategy used
                - follow_up_questions: Suggested questions to deepen understanding
        """
        logger.info(f"[Tutor Agent] Creating explanation for {student_level} level...")
        
        try:
            # Get teaching strategy for this level
            strategy = self.level_strategies.get(student_level, self.level_strategies['high_school'])
            
            # Build context-aware explanation prompt
            explanation_prompt = self._build_explanation_prompt(
                query=query,
                student_level=student_level,
                strategy=strategy,
                research_info=research_info,
                context=context,
                complexity=complexity
            )
            
            # Generate explanation using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=explanation_prompt
            )
            
            explanation_text = response.text.strip()
            
            # Generate follow-up questions to encourage deeper learning
            follow_up_questions = await self._generate_follow_up_questions(
                query=query,
                explanation=explanation_text,
                student_level=student_level
            )
            
            result = {
                'explanation': explanation_text,
                'teaching_strategy': strategy,
                'follow_up_questions': follow_up_questions,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("[Tutor Agent] ✓ Explanation generated")
            
            return result
            
        except Exception as e:
            logger.error(f"[Tutor Agent] Error: {str(e)}", exc_info=True)
            return {
                'explanation': 'I encountered an issue creating an explanation. Could you rephrase your question?',
                'teaching_strategy': {},
                'follow_up_questions': [],
                'error': str(e)
            }
    
    def _build_explanation_prompt(self,
                                 query: str,
                                 student_level: str,
                                 strategy: Dict[str, str],
                                 research_info: str,
                                 context: Optional[Dict[str, Any]],
                                 complexity: str) -> str:
        """
        Build a comprehensive prompt for generating adaptive explanations
        
        The prompt includes:
        - Student level and appropriate teaching strategy
        - Verified information to ensure accuracy
        - Context from previous conversations
        - Specific pedagogical guidelines
        """
        # Build context section
        context_section = ""
        if context and context.get('relevant_items'):
            context_section = f"""
Previous Context:
The student has previously discussed: {', '.join([item.get('topic', '') for item in context.get('relevant_items', [])])}
"""
        
        # Build research info section
        research_section = ""
        if research_info:
            research_section = f"""
Verified Information to Use:
{research_info}
"""
        
        # Create comprehensive prompt
        prompt = f"""You are an expert tutor helping a {student_level.replace('_', ' ')} student understand a concept.

Student's Question: "{query}"

{context_section}
{research_section}

Teaching Guidelines for {student_level.replace('_', ' ')} level:
- Vocabulary: Use {strategy['vocabulary']}
- Sentence Style: {strategy['sentence_length']}
- Examples: Provide {strategy['examples']}
- Analogies: Use {strategy['analogies']}
- Depth: Aim for {strategy['depth']}
- Topic Complexity: {complexity}

Your Task:
Create a clear, engaging explanation that:

1. **Directly answers the question** at the appropriate level
2. **Breaks down complex ideas** into understandable parts
3. **Uses concrete examples** that resonate with this age group
4. **Includes an analogy** if it helps understanding (especially for abstract concepts)
5. **Checks for understanding** by explaining potential misconceptions
6. **Builds on previous knowledge** if context suggests the student has background
7. **Ends with encouragement** and a hint about related topics to explore

Formatting Guidelines:
- Start with a clear, direct answer to the question
- Use short paragraphs (2-4 sentences each)
- Include ONE helpful analogy or example in a separate paragraph
- End with an encouraging note

Keep the explanation focused and not overly long (aim for 3-5 paragraphs unless the topic genuinely requires more detail).

Generate the explanation:"""

        return prompt
    
    async def _generate_follow_up_questions(self,
                                           query: str,
                                           explanation: str,
                                           student_level: str) -> List[str]:
        """
        Generate thoughtful follow-up questions to encourage deeper learning
        
        Good follow-up questions:
        - Build on what was just explained
        - Encourage application of concepts
        - Connect to related topics
        - Prompt critical thinking
        """
        follow_up_prompt = f"""Based on this explanation about "{query}":

{explanation}

Generate 3 thoughtful follow-up questions that would help a {student_level.replace('_', ' ')} student:
1. Deepen their understanding
2. Apply the concept to new situations
3. Make connections to related topics

Format as a simple numbered list. Keep questions engaging and appropriate for the level."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=follow_up_prompt
            )
            
            # Parse questions from response
            questions_text = response.text.strip()
            
            # Extract numbered questions
            import re
            questions = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|\Z)', questions_text, re.DOTALL)
            questions = [q.strip() for q in questions if q.strip()]
            
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            logger.warning(f"[Tutor Agent] Could not generate follow-up questions: {str(e)}")
            return []
    
    async def identify_misconceptions(self,
                                     student_response: str,
                                     topic: str) -> Dict[str, Any]:
        """
        Analyze a student's response to identify potential misconceptions
        
        This is useful for interactive tutoring where the student provides answers
        
        Args:
            student_response: What the student said/wrote
            topic: The topic being discussed
            
        Returns:
            dict with identified misconceptions and corrections
        """
        logger.info(f"[Tutor Agent] Analyzing student response for misconceptions...")
        
        misconception_prompt = f"""You are analyzing a student's understanding of: {topic}

Student's Response:
"{student_response}"

Task:
1. Identify any misconceptions or incorrect understandings
2. Note correct parts of their understanding
3. Suggest gentle corrections that build on what they got right

Respond in this format:

CORRECT UNDERSTANDING:
[What the student understood correctly]

MISCONCEPTIONS:
[Any incorrect understandings]

GENTLE CORRECTION:
[How to address the misconception positively]

CONFIDENCE: [high/medium/low]"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=misconception_prompt
            )
            
            analysis = response.text.strip()
            
            return {
                'analysis': analysis,
                'has_misconceptions': 'MISCONCEPTIONS:' in analysis and len(analysis.split('MISCONCEPTIONS:')[1].strip()) > 10,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Tutor Agent] Misconception analysis failed: {str(e)}")
            return {
                'analysis': '',
                'has_misconceptions': False,
                'error': str(e)
            }
    
    async def create_learning_path(self,
                                   goal_topic: str,
                                   current_knowledge: List[str],
                                   student_level: str) -> Dict[str, Any]:
        """
        Create a personalized learning path for a complex topic
        
        Useful for students who want to learn something comprehensive
        
        Args:
            goal_topic: What the student wants to learn
            current_knowledge: Topics they already know
            student_level: Their education level
            
        Returns:
            dict with step-by-step learning path
        """
        logger.info(f"[Tutor Agent] Creating learning path for: {goal_topic}")
        
        known_topics = ', '.join(current_knowledge) if current_knowledge else 'no prior knowledge indicated'
        
        learning_path_prompt = f"""Create a personalized learning path for a {student_level.replace('_', ' ')} student.

Goal: Master understanding of "{goal_topic}"
Current Knowledge: {known_topics}

Create a step-by-step learning path with:
1. Prerequisites they need (if any)
2. Core concepts to learn in order
3. Practice/application opportunities
4. Advanced topics to explore after mastery

Format as a clear, numbered learning sequence with brief descriptions of what they'll learn at each step."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=learning_path_prompt
            )
            
            learning_path = response.text.strip()
            
            return {
                'learning_path': learning_path,
                'goal_topic': goal_topic,
                'estimated_steps': learning_path.count('\n') // 3,  # Rough estimate
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Tutor Agent] Learning path creation failed: {str(e)}")
            return {
                'learning_path': '',
                'goal_topic': goal_topic,
                'error': str(e)
            }
    
    async def generate_practice_question(self,
                                        topic: str,
                                        difficulty_level: str,
                                        student_level: str,
                                        mastery_level: str = 'learning') -> Dict[str, Any]:
        """
        Generate a practice question for a specific topic
        
        This creates questions adapted to the student's current understanding
        and progressively increases difficulty as they improve.
        
        Args:
            topic: The topic to create a question about
            difficulty_level: Question difficulty (basic, intermediate, advanced, expert)
            student_level: Student's education level
            mastery_level: Their current mastery of the topic
            
        Returns:
            dict with question, difficulty, and grading criteria
        """
        logger.info(f"[Tutor Agent] Generating {difficulty_level} question on {topic}")
        
        difficulty_guidance = {
            'basic': 'recall and basic understanding - definitions, simple explanations',
            'intermediate': 'application and analysis - explain how/why, give examples',
            'advanced': 'synthesis and evaluation - compare, analyze relationships, solve complex problems',
            'expert': 'creation and expert analysis - design experiments, critique theories, novel applications'
        }
        
        question_prompt = f"""You are creating a practice question for a {student_level.replace('_', ' ')} student.

Topic: {topic}
Current Mastery: {mastery_level}
Difficulty Level: {difficulty_level}

Create a question that tests {difficulty_guidance.get(difficulty_level, 'understanding')}.

The question should:
1. Be appropriate for {student_level.replace('_', ' ')} level
2. Match {difficulty_level} difficulty
3. Be clear and unambiguous
4. Test genuine understanding (not just memorization)

Also provide:
- The correct/ideal answer
- Key points the answer should include
- Common misconceptions to watch for

Format your response as:

QUESTION:
[The practice question here]

IDEAL ANSWER:
[What a perfect answer would include]

KEY POINTS:
- Point 1
- Point 2
- Point 3

COMMON MISCONCEPTIONS:
- Misconception 1
- Misconception 2
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=question_prompt
            )
            
            response_text = response.text.strip()
            
            # Parse the response
            question = self._extract_section(response_text, 'QUESTION')
            ideal_answer = self._extract_section(response_text, 'IDEAL ANSWER')
            key_points = self._extract_section(response_text, 'KEY POINTS')
            misconceptions = self._extract_section(response_text, 'COMMON MISCONCEPTIONS')
            
            return {
                'question': question,
                'ideal_answer': ideal_answer,
                'key_points': key_points,
                'common_misconceptions': misconceptions,
                'difficulty_level': difficulty_level,
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Tutor Agent] Question generation failed: {str(e)}")
            return {
                'question': f"Explain {topic} at a {difficulty_level} level.",
                'ideal_answer': '',
                'error': str(e)
            }
    
    async def grade_answer(self,
                          question: str,
                          student_answer: str,
                          ideal_answer: str,
                          key_points: str,
                          student_level: str) -> Dict[str, Any]:
        """
        Grade a student's answer and provide constructive feedback
        
        This uses Gemini to:
        - Evaluate accuracy and completeness
        - Identify what the student understood well
        - Point out gaps or misconceptions
        - Provide encouraging, constructive feedback
        
        Args:
            question: The question that was asked
            student_answer: Student's response
            ideal_answer: The ideal/correct answer
            key_points: Key points that should be covered
            student_level: Student's education level
            
        Returns:
            dict with score (0-1), feedback, and areas for improvement
        """
        logger.info(f"[Tutor Agent] Grading answer for {student_level} student")
        
        grading_prompt = f"""You are grading a {student_level.replace('_', ' ')} student's answer.

QUESTION:
{question}

STUDENT'S ANSWER:
{student_answer}

IDEAL ANSWER:
{ideal_answer}

KEY POINTS TO CHECK:
{key_points}

Your task:
1. Evaluate the accuracy and completeness of the student's answer
2. Identify what they understood correctly
3. Note any misconceptions or gaps
4. Provide a score from 0.0 to 1.0:
   - 0.9-1.0: Excellent, comprehensive understanding
   - 0.7-0.89: Good understanding with minor gaps
   - 0.5-0.69: Partial understanding, some misconceptions
   - 0.3-0.49: Limited understanding, major gaps
   - 0.0-0.29: Minimal understanding

5. Give encouraging, constructive feedback appropriate for their level

Format your response as:

SCORE: [number from 0.0 to 1.0]

WHAT YOU GOT RIGHT:
[Positive feedback on correct points]

AREAS TO IMPROVE:
[Constructive feedback on gaps/errors]

NEXT STEPS:
[Specific suggestions for improvement]

OVERALL FEEDBACK:
[Encouraging summary and motivation]
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=grading_prompt
            )
            
            grading_text = response.text.strip()
            
            # Extract score
            score = self._extract_score(grading_text)
            
            # Extract feedback sections
            correct_points = self._extract_section(grading_text, 'WHAT YOU GOT RIGHT')
            improvements = self._extract_section(grading_text, 'AREAS TO IMPROVE')
            next_steps = self._extract_section(grading_text, 'NEXT STEPS')
            overall_feedback = self._extract_section(grading_text, 'OVERALL FEEDBACK')
            
            return {
                'score': score,
                'correct_points': correct_points,
                'areas_to_improve': improvements,
                'next_steps': next_steps,
                'overall_feedback': overall_feedback,
                'full_grading': grading_text,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Tutor Agent] Grading failed: {str(e)}")
            return {
                'score': 0.5,  # Default neutral score
                'correct_points': 'Unable to evaluate automatically.',
                'areas_to_improve': '',
                'next_steps': 'Please try explaining your answer in more detail.',
                'overall_feedback': 'Keep practicing!',
                'error': str(e)
            }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted text"""
        import re
        
        # Try to find the section
        pattern = rf"{section_name}:?\s*\n(.*?)(?=\n[A-Z][A-Z\s]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Fallback: return empty string
        return ""
    
    def _extract_score(self, text: str) -> float:
        """Extract numerical score from grading text"""
        import re
        
        # Look for "SCORE: 0.85" format
        score_match = re.search(r'SCORE:?\s*([0-9]*\.?[0-9]+)', text, re.IGNORECASE)
        
        if score_match:
            try:
                score = float(score_match.group(1))
                # Ensure score is between 0 and 1
                return max(0.0, min(1.0, score))
            except ValueError:
                pass
        
        # Fallback: return neutral score
        return 0.5