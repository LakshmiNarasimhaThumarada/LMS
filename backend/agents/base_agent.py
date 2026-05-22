from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Optional, Union
from langchain_core.messages import HumanMessage
from backend.config import settings

class AgentState(TypedDict):
    """Base state for all agents"""
    messages: List[HumanMessage]
    current_step: str
    result: dict
    error: Optional[str]

class BaseAgent:
    """Base class for all LangGraph agents"""
    
    def __init__(self, model_name: str = "llama-3.1-70b-versatile"):
        self.llm = ChatGroq(
            model=model_name,
            api_key=settings.GROQ_API_KEY,
            temperature=0.0,  # Deterministic for analysis
            max_tokens=8000
        )
    
    def create_graph(self) -> StateGraph:
        """Override this in child classes"""
        raise NotImplementedError
