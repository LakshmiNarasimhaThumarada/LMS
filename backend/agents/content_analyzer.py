import json
from typing import Dict, List
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from backend.agents.base_agent import BaseAgent, AgentState
from backend.utils.pdf_utils import extract_pdf_text, detect_page_count

class ContentAnalyzerState(AgentState):
    """State for content analyzer workflow"""
    pdf_path: str
    pdf_text: str
    page_count: int
    chapters: List[Dict]
    total_topics: int
    estimated_hours: Dict
    difficulty: str

class ContentAnalyzerAgent(BaseAgent):
    """
    LangGraph agent that analyzes PDF content structure.
    
    Workflow:
    1. Extract text from PDF
    2. Detect structure (chapters, sections)
    3. Estimate study hours per chapter
    4. Classify difficulty
    """
    
    def __init__(self):
        super().__init__(model_name="llama-3.1-70b-versatile")
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        """Creates the LangGraph workflow"""
        
        workflow = StateGraph(ContentAnalyzerState)
        
        # Add nodes
        workflow.add_node("extract_text", self.extract_text_node)
        workflow.add_node("detect_structure", self.detect_structure_node)
        workflow.add_node("estimate_hours", self.estimate_hours_node)
        workflow.add_node("classify_difficulty", self.classify_difficulty_node)
        
        # Define edges
        workflow.set_entry_point("extract_text")
        workflow.add_edge("extract_text", "detect_structure")
        workflow.add_edge("detect_structure", "estimate_hours")
        workflow.add_edge("estimate_hours", "classify_difficulty")
        workflow.add_edge("classify_difficulty", END)
        
        return workflow.compile()
    
    def extract_text_node(self, state: ContentAnalyzerState) -> ContentAnalyzerState:
        """Node 1: Extract text from PDF"""
        
        try:
            # Extract full text
            pdf_text = extract_pdf_text(state['pdf_path'])
            page_count = detect_page_count(state['pdf_path'])
            
            state['pdf_text'] = pdf_text
            state['page_count'] = page_count
            state['current_step'] = "extract_text"
            
            return state
            
        except Exception as e:
            state['error'] = f"PDF extraction failed: {str(e)}"
            return state
    
    def detect_structure_node(self, state: ContentAnalyzerState) -> ContentAnalyzerState:
        """Node 2: Detect chapters and topics using LLM"""
        
        try:
            # Take first 15,000 characters for analysis (to fit in context)
            text_sample = state['pdf_text'][:15000]
            
            prompt = f"""You are an educational content analyzer. Analyze this textbook/study material and extract its structure.

INPUT TEXT (first part of document):
{text_sample}

TASK:
1. Identify all chapter numbers and titles
2. List 3-5 main topics per chapter
3. Classify overall difficulty level (Beginner/Intermediate/Advanced)

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON, no markdown formatting, no code blocks
- Do NOT include ```json or ``` in your response
- Start directly with the opening brace {{

OUTPUT FORMAT (JSON only):
{{
  "chapters": [
    {{
      "number": 1,
      "name": "Introduction to Calculus",
      "topics": ["Limits", "Continuity", "Derivatives", "Applications"]
    }},
    {{
      "number": 2,
      "name": "Integrals",
      "topics": ["Definite Integrals", "Indefinite Integrals", "Integration Techniques"]
    }}
  ],
  "difficulty": "Intermediate"
}}

ANALYZE NOW:"""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse response
            response_text = response.content.strip()
            
            # Remove markdown code blocks if present (despite instructions)
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            analysis = json.loads(response_text)
            
            state['chapters'] = analysis['chapters']
            state['total_topics'] = sum(len(ch['topics']) for ch in analysis['chapters'])
            state['difficulty'] = analysis['difficulty']
            state['current_step'] = "detect_structure"
            
            return state
            
        except json.JSONDecodeError as e:
            state['error'] = f"Failed to parse LLM response as JSON: {str(e)}. Response: {response_text[:200]}"
            return state
        except Exception as e:
            state['error'] = f"Structure detection failed: {str(e)}"
            return state
    
    def estimate_hours_node(self, state: ContentAnalyzerState) -> ContentAnalyzerState:
        """Node 3: Estimate study hours based on content"""
        
        try:
            # Base estimation: hours per chapter based on difficulty
            base_hours = {
                'Beginner': 2.0,
                'Intermediate': 3.0,
                'Advanced': 4.5
            }
            
            difficulty = state['difficulty']
            hours_per_chapter = base_hours.get(difficulty, 3.0)
            
            # Adjust based on page count
            pages_per_chapter = state['page_count'] / len(state['chapters'])
            
            if pages_per_chapter > 30:
                hours_per_chapter *= 1.3
            elif pages_per_chapter > 50:
                hours_per_chapter *= 1.6
            
            total_hours = hours_per_chapter * len(state['chapters'])
            
            # Add practice time (30% of study time)
            practice_hours = total_hours * 0.3
            
            # Add review time (20% of study time)
            review_hours = total_hours * 0.2
            
            state['estimated_hours'] = {
                'study': round(total_hours, 1),
                'practice': round(practice_hours, 1),
                'review': round(review_hours, 1),
                'total': round(total_hours + practice_hours + review_hours, 1),
                'per_chapter': round(hours_per_chapter, 1)
            }
            
            state['current_step'] = "estimate_hours"
            return state
            
        except Exception as e:
            state['error'] = f"Hours estimation failed: {str(e)}"
            return state
    
    def classify_difficulty_node(self, state: ContentAnalyzerState) -> ContentAnalyzerState:
        """Node 4: Final difficulty classification (already done in step 2)"""
        
        state['current_step'] = "completed"
        state['result'] = {
            'chapters': state['chapters'],
            'total_topics': state['total_topics'],
            'estimated_hours': state['estimated_hours'],
            'difficulty': state['difficulty'],
            'page_count': state['page_count']
        }
        
        return state
    
    def analyze(self, pdf_path: str) -> Dict:
        """
        Main entry point to analyze a PDF.
        """
        
        # Initialize state
        initial_state = {
            'pdf_path': pdf_path,
            'pdf_text': '',
            'page_count': 0,
            'chapters': [],
            'total_topics': 0,
            'estimated_hours': {},
            'difficulty': '',
            'messages': [],
            'current_step': 'init',
            'result': {},
            'error': None
        }
        
        # Run graph
        final_state = self.graph.invoke(initial_state)
        
        # Check for errors
        if final_state.get('error'):
            raise Exception(final_state['error'])
        
        return final_state['result']
