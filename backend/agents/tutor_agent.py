import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .rag import get_relevant_context
from .prompts import TUTOR_PROMPT
from dotenv import load_dotenv

load_dotenv()

from backend.config import settings

# Initialize LLM
llm = ChatGroq(
    temperature=0.3,
    model_name=settings.GROQ_MODEL,
    groq_api_key=settings.GROQ_API_KEY
)

def tutor_node(state):
    """
    Tutor Agent Node: Responsible for explaining concepts.
    State needs: 'message', 'pdf_id'
    """
    message = state["message"]
    pdf_id = state.get("pdf_id")
    
    context = ""
    if pdf_id:
        context = get_relevant_context(message, pdf_id)
        
    formatted_prompt = TUTOR_PROMPT.format(context=context, question=message)
    
    response = llm.invoke([HumanMessage(content=formatted_prompt)])
    
    return {"agent_response": response.content}
