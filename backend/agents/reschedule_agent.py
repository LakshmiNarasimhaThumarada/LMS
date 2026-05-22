from langgraph.graph import StateGraph, END
from datetime import datetime, timedelta
from typing import Dict, List

from backend.agents.base_agent import BaseAgent, AgentState

class RescheduleState(AgentState):
    """State for rescheduling workflow"""
    plan_id: str
    user_id: str
    trigger_type: str  # 'difficulty', 'missed', 'request'
    affected_session: Dict
    current_sessions: List[Dict]
    new_sessions: List[Dict]

class RescheduleAgent(BaseAgent):
    """
    LangGraph agent that adapts study schedule based on progress.
    
    Workflows:
    1. Add review session if topic marked 'hard'
    2. Reschedule missed sessions
    3. Adjust remaining schedule based on pace
    """
    
    def __init__(self):
        super().__init__(model_name="llama-3.1-70b-versatile")
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        """Creates the LangGraph workflow"""
        
        workflow = StateGraph(RescheduleState)
        
        # Add nodes
        workflow.add_node("analyze_trigger", self.analyze_trigger_node)
        workflow.add_node("add_review", self.add_review_node)
        workflow.add_node("reschedule_missed", self.reschedule_missed_node)
        workflow.add_node("adjust_schedule", self.adjust_schedule_node)
        workflow.add_node("finalize", self.finalize_node)
        
        # Define conditional edges
        workflow.set_entry_point("analyze_trigger")
        
        def route_after_analyze(state):
            if state['trigger_type'] == 'difficulty':
                return "add_review"
            elif state['trigger_type'] == 'missed':
                return "reschedule_missed"
            else:
                return "adjust_schedule"
        
        workflow.add_conditional_edges(
            "analyze_trigger",
            route_after_analyze,
            {
                "add_review": "add_review",
                "reschedule_missed": "reschedule_missed",
                "adjust_schedule": "adjust_schedule"
            }
        )
        
        workflow.add_edge("add_review", "finalize")
        workflow.add_edge("reschedule_missed", "finalize")
        workflow.add_edge("adjust_schedule", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def analyze_trigger_node(self, state: RescheduleState) -> RescheduleState:
        """Node 1: Analyze why rescheduling is needed"""
        state['current_step'] = "analyze_trigger"
        return state
    
    def add_review_node(self, state: RescheduleState) -> RescheduleState:
        """Node 2: Add extra review session for difficult topic"""
        
        try:
            session = state['affected_session']
            
            # Create review session 3 days after original
            original_date = datetime.strptime(session['date'], '%Y-%m-%d')
            review_date = original_date + timedelta(days=3)
            
            review_session = {
                'id': f"adaptive_review_{session['id']}_{int(datetime.now().timestamp())}",
                'date': review_date.strftime('%Y-%m-%d'),
                'time': session['time'],
                'chapter_number': session.get('chapter_number'),
                'chapter_name': f"🔄 Extra Review: {session['chapter_name']}",
                'topics': session.get('topics', []),
                'duration': 1.0,
                'type': 'adaptive_review',
                'original_session_id': session['id'],
                'reason': 'Marked as difficult',
                'completed': False
            }
            
            state['new_sessions'] = [review_session]
            state['current_step'] = "add_review"
            
            return state
            
        except Exception as e:
            state['error'] = f"Add review failed: {str(e)}"
            return state
    
    def reschedule_missed_node(self, state: RescheduleState) -> RescheduleState:
        """Node 3: Reschedule a missed session"""
        
        try:
            session = state['affected_session']
            current_sessions = state['current_sessions']
            
            # Find next available slot (tomorrow or later)
            tomorrow = datetime.now() + timedelta(days=1)
            
            # Find a day with fewer than 2 sessions
            candidate_date = tomorrow
            for _ in range(30):  # Check next 30 days
                date_str = candidate_date.strftime('%Y-%m-%d')
                sessions_on_day = [
                    s for s in current_sessions
                    if s['date'] == date_str
                ]
                
                if len(sessions_on_day) < 2:
                    # Found a slot
                    rescheduled = session.copy()
                    rescheduled['id'] = f"{session['id']}_rescheduled_{int(datetime.now().timestamp())}"
                    rescheduled['date'] = date_str
                    rescheduled['rescheduled'] = True
                    rescheduled['original_date'] = session['date']
                    rescheduled['completed'] = False
                    
                    state['new_sessions'] = [rescheduled]
                    break
                
                candidate_date += timedelta(days=1)
            
            state['current_step'] = "reschedule_missed"
            return state
            
        except Exception as e:
            state['error'] = f"Reschedule failed: {str(e)}"
            return state
    
    def adjust_schedule_node(self, state: RescheduleState) -> RescheduleState:
        """Node 4: Adjust remaining schedule based on pace"""
        
        # Future: Use LLM to intelligently redistribute remaining sessions
        # For now, keep existing schedule
        state['new_sessions'] = []
        state['current_step'] = "adjust_schedule"
        return state
    
    def finalize_node(self, state: RescheduleState) -> RescheduleState:
        """Node 5: Finalize changes"""
        
        state['current_step'] = "completed"
        state['result'] = {
            'new_sessions': state['new_sessions'],
            'trigger_type': state['trigger_type']
        }
        
        return state
    
    def reschedule(
        self,
        plan_id: str,
        user_id: str,
        trigger_type: str,
        affected_session: Dict,
        current_sessions: List[Dict]
    ) -> Dict:
        """
        Main entry point for rescheduling.
        """
        
        initial_state = {
            'plan_id': plan_id,
            'user_id': user_id,
            'trigger_type': trigger_type,
            'affected_session': affected_session,
            'current_sessions': current_sessions,
            'new_sessions': [],
            'messages': [],
            'current_step': 'init',
            'result': {},
            'error': None
        }
        
        final_state = self.graph.invoke(initial_state)
        
        if final_state.get('error'):
            raise Exception(final_state['error'])
        
        return final_state['result']
