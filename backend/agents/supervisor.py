import os
from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .prompts import SUPERVISOR_PROMPT
from .tutor_agent import tutor_node
from .quiz_agent import quiz_gen_node, quiz_eval_node
from .progress_agent import progress_node
from dotenv import load_dotenv

load_dotenv()

# Define State
class AgentState(TypedDict):
    message: str
    user_id: str
    pdf_id: str
    agent_response: str
    conversation_history: List[HumanMessage]
    active_quiz_data: dict
    student_answers: List[str]
    quiz_results: dict
    weak_areas_summary: List[dict]
    next_node: str

# Initialize Supervisor LLM
llm = ChatGroq(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def supervisor_node(state: AgentState):
    """Orchestrates routing based on user message."""
    message = state["message"]
    history = state.get("conversation_history", [])
    
    # Simple explicit routing or LLM routing
    # If the user is submitting answers, always route to quiz_eval
    if "student_answers" in state and state["student_answers"]:
        return {"next_node": "quiz_eval"}
        
    formatted_prompt = SUPERVISOR_PROMPT.format(message=message)
    response = llm.invoke([HumanMessage(content=formatted_prompt)])
    
    # Extract selection
    selection = response.content.lower().strip()
    
    if "tutor" in selection: return {"next_node": "tutor"}
    if "quiz" in selection: return {"next_node": "quiz_gen"}
    if "progress" in selection: return {"next_node": "progress"}
    
    return {"next_node": "tutor"} # Default

# Build Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("tutor", tutor_node)
workflow.add_node("quiz_gen", quiz_gen_node)
workflow.add_node("quiz_eval", quiz_eval_node)
workflow.add_node("progress", progress_node)

# Add Conditional Edges
workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda x: x["next_node"],
    {
        "tutor": "tutor",
        "quiz_gen": "quiz_gen",
        "quiz_eval": "quiz_eval",
        "progress": "progress"
    }
)

# Terminate from all nodes back to END
workflow.add_edge("tutor", END)
workflow.add_edge("quiz_gen", END)
workflow.add_edge("quiz_eval", END)
workflow.add_edge("progress", END)

# Compile
app_graph = workflow.compile()
