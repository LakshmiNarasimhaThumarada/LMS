import os
import requests
# Using direct DB access for analysis
from db import users_collection, db
from .prompts import SUPERVISOR_PROMPT
from bson import ObjectId

def progress_node(state):
    """
    Progress Tracker Agent Node: Analyzes scores and gives advice.
    State needs: 'user_id'
    """
    user_id = state.get("user_id")
    if not user_id:
        return {"agent_response": "I couldn't identify your user profile. Please login again."}
        
    try:
        # Fetch quiz history from MongoDB
        quizzes = list(db.quizzes.find({"userId": ObjectId(user_id)}))
        
        if not quizzes:
            return {"agent_response": "You haven't taken any quizzes yet! Take your first quiz to see your progress analytics."}
            
        # Analyze weak areas
        topic_scores = {}
        for q in quizzes:
            topic = q.get('topic', 'General')
            score = q.get('score', 0) / 5.0 # Normalize to 0-1
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(score)
            
        weak_topics = []
        for topic, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            if avg < 0.7:
                weak_topics.append({"topic": topic, "score": f"{avg*100:.0f}%"})
                
        if not weak_topics:
            return {"agent_response": "Fantastic! You are mastering all topics so far (all scores > 70%). Keep up the momentum!"}
            
        weak_list = ", ".join([f"{t['topic']} ({t['score']})" for t in weak_topics])
        recommendation = f"Based on your performance, I recommend reviewing: {weak_list}. We should spend more time on these topics in the chat."
        
        return {
            "weak_areas_summary": weak_topics,
            "agent_response": recommendation
        }
        
    except Exception as e:
        return {"agent_response": f"Error tracking progress: {str(e)}"}
