import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .rag import get_relevant_context
from .prompts import QUIZ_GEN_PROMPT, QUIZ_EVAL_PROMPT
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    temperature=0.1, # Lower temperature for better structure
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

def quiz_gen_node(state):
    """
    Quiz Generation Node: Generates 5 questions from context.
    State needs: 'pdf_id'
    """
    pdf_id = state.get("pdf_id")
    if not pdf_id:
        return {"agent_response": "Please select a document first to generate a quiz."}
        
    # Get general context to generate broad questions
    context = get_relevant_context("Overview and key concepts", pdf_id, k=5)
    
    formatted_prompt = QUIZ_GEN_PROMPT.format(context=context)
    
    response = llm.invoke([HumanMessage(content=formatted_prompt)])
    
    # Try to parse JSON output
    try:
        # Simple cleanup in case of extra markdown
        content = response.content.replace("```json", "").replace("```", "").strip()
        quiz_data = json.loads(content)
        return {"active_quiz_data": quiz_data, "agent_response": "Quiz generated! Good luck."}
    except Exception as e:
        return {"agent_response": f"Error parsing quiz: {str(e)}", "raw_llm_output": response.content}

def quiz_eval_node(state):
    """
    Quiz Evaluation Node: Grades short answers using LLM-as-Judge.
    State needs: 'active_quiz_data', 'student_answers'
    """
    quiz = state.get("active_quiz_data")
    answers = state.get("student_answers")
    
    if not quiz or not answers:
        return {"agent_response": "No active quiz or answers found."}
        
    results = []
    score = 0
    
    for i, q in enumerate(quiz['questions']):
        user_ans = str(answers[i])
        correct_ans = str(q['correct_answer'])
        
        if q['type'] == 'mcq':
            is_correct = user_ans.strip().lower() == correct_ans.strip().lower()
            results.append({
                "question": q['question'],
                "user_answer": user_ans,
                "correct_answer": correct_ans,
                "is_correct": is_correct,
                "explanation": "Correct!" if is_correct else f"The correct answer was {correct_ans}."
            })
            if is_correct: score += 1
        else:
            # Short Answer - LLM-as-Judge
            eval_prompt = QUIZ_EVAL_PROMPT.format(
                question=q['question'],
                correct_answer=correct_ans,
                student_answer=user_ans
            )
            eval_res = llm.invoke([HumanMessage(content=eval_prompt)])
            
            try:
                eval_data = json.loads(eval_res.content.replace("```json", "").replace("```", "").strip())
                is_correct = eval_data.get("is_correct", False)
                results.append({
                    "question": q['question'],
                    "user_answer": user_ans,
                    "correct_answer": correct_ans,
                    "is_correct": is_correct,
                    "explanation": eval_data.get("explanation", "Grade processed.")
                })
                if is_correct: score += 1
            except:
                results.append({
                    "question": q['question'],
                    "user_answer": user_ans,
                    "correct_answer": correct_ans,
                    "is_correct": False,
                    "explanation": "Evaluation failed. Manual review recommended."
                })

    return {
        "quiz_results": {
            "score": score,
            "percentage": (score / len(quiz['questions'])) * 100,
            "results": results
        },
        "agent_response": f"Quiz evaluated. You scored {score}/{len(quiz['questions'])}."
    }
