import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

pdf_id = "6a88109f6bb0e0ae337b5fd6"  # The latest Narasimha_cog.pdf ID

print("Step 1: Checking Chroma DB for PDF ID:", pdf_id)
from backend.agents.rag import get_relevant_context
try:
    context = get_relevant_context("Overview and key concepts", pdf_id, k=5)
    print(f"Retrieved context length: {len(context)}")
    print("Preview of context:", repr(context[:200]) if context else "NONE")
except Exception as e:
    print("Error calling get_relevant_context:", e)
    context = ""

print("\nStep 2: Running quiz_gen_node...")
from backend.agents.quiz_agent import quiz_gen_node
try:
    res = quiz_gen_node({"pdf_id": pdf_id})
    print("\nResult Keys:", list(res.keys()))
    print("\nAgent Response:", res.get("agent_response"))
    if "raw_llm_output" in res:
        print("\n--- RAW LLM OUTPUT ---")
        print(res["raw_llm_output"])
        print("----------------------")
    else:
        print("\nActive Quiz Data:", res.get("active_quiz_data"))
except Exception as e:
    print("Error running quiz_gen_node:", e)
