from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from backend.utils.auth import require_jwt
from backend.db import db
from backend.agents.quiz_agent import quiz_gen_node, quiz_eval_node

router = APIRouter()

class QuizGenerateRequest(BaseModel):
    pdf_id: str
    difficulty: str
    num_questions: int

class QuizEvaluateRequest(BaseModel):
    quiz_id: str
    answers: List[str]

class QuizSaveResultRequest(BaseModel):
    quiz_id: str
    score: str
    topic: Optional[str] = None

@router.post("/generate")
async def generate_quiz(
    request: QuizGenerateRequest,
    user = Depends(require_jwt)
):
    try:
        # Run real LangGraph AI Quiz Agent node
        res = quiz_gen_node({
            "pdf_id": request.pdf_id
        })
        
        # Check if quiz generation failed
        active_quiz_data = res.get("active_quiz_data")
        if not active_quiz_data:
            raise Exception(res.get("agent_response", "AI Quiz generation failed."))
            
        # Format questions for MongoDB
        db_questions = []
        for q in active_quiz_data.get("questions", []):
            db_q = {
                "_id": ObjectId(),
                "question": q.get("question"),
                "type": "mcq" if q.get("type") == "mcq" else "short",
                "correctAnswer": q.get("correct_answer"),
                "explanation": q.get("explanation") or "Standard explanation."
            }
            if q.get("type") == "mcq":
                db_q["options"] = q.get("options", [])
            db_questions.append(db_q)
            
        # Insert into MongoDB
        session = {
            "userId": ObjectId(user["id"]),
            "pdfId": ObjectId(request.pdf_id) if ObjectId.is_valid(request.pdf_id) else request.pdf_id,
            "questions": db_questions,
            "difficulty": request.difficulty,
            "createdAt": datetime.utcnow()
        }
        
        res_db = await db.quizsessions.insert_one(session)
        quiz_id = str(res_db.inserted_id)
        
        # Format response matching Node.js structure
        formatted_questions = []
        for q in db_questions:
            fq = {
                "id": str(q["_id"]),
                "question": q["question"],
                "type": q["type"]
            }
            if "options" in q:
                fq["options"] = q["options"]
            formatted_questions.append(fq)
            
        return {
            "quiz_id": quiz_id,
            "questions": formatted_questions
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quiz Generation failed: {str(e)}")

@router.post("/evaluate")
async def evaluate_quiz(
    request: QuizEvaluateRequest,
    user = Depends(require_jwt)
):
    try:
        # Retrieve quiz session from MongoDB
        session = await db.quizsessions.find_one({"_id": ObjectId(request.quiz_id)})
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
            
        # Prepare state for quiz_eval_node
        eval_questions = []
        for q in session["questions"]:
            eval_q = {
                "question": q["question"],
                "type": q["type"],
                "correct_answer": q["correctAnswer"],
                "explanation": q.get("explanation") or ""
            }
            eval_questions.append(eval_q)
            
        # Call LangGraph AI Evaluator node (LLM-as-Judge)
        res = quiz_eval_node({
            "active_quiz_data": {"questions": eval_questions},
            "student_answers": request.answers
        })
        
        quiz_results = res.get("quiz_results")
        if not quiz_results:
            raise Exception(res.get("agent_response", "AI Grading failed."))
            
        # Format results response matching Node.js
        formatted_score = f"{quiz_results['score']}/{len(eval_questions)}"
        return {
            "score": formatted_score,
            "percentage": quiz_results["percentage"],
            "results": quiz_results["results"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quiz Evaluation failed: {str(e)}")

@router.post("/save-result")
async def save_quiz_result(
    request: QuizSaveResultRequest,
    user = Depends(require_jwt)
):
    try:
        # Parse score (e.g. "3/5")
        numeric_score = int(request.score.split('/')[0]) if '/' in request.score else 0
        
        quiz_doc = {
            "userId": ObjectId(user["id"]),
            "topic": request.topic or "General Quiz",
            "score": numeric_score,
            "date": datetime.utcnow()
        }
        
        await db.quizzes.insert_one(quiz_doc)
        return {"message": "Result saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Saving result failed: {str(e)}")
