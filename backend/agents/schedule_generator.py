from datetime import datetime, timedelta
import calendar
from typing import List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
import json

from backend.agents.base_agent import BaseAgent, AgentState

class ScheduleGeneratorState(AgentState):
    """State for schedule generator workflow"""
    analysis: Dict  # PDF analysis from ContentAnalyzerAgent
    preferences: Dict  # User preferences (exam_date, hours_per_day, etc.)
    available_days: int
    sessions: List[Dict]
    summary: Dict

class ScheduleGeneratorAgent(BaseAgent):
    """
    LangGraph agent that creates personalized study timetables.
    
    Workflow:
    1. Calculate available time
    2. Distribute chapters across days
    3. Assign time slots
    4. Add review sessions (spaced repetition)
    5. Optimize schedule
    """
    
    def __init__(self):
        super().__init__(model_name="llama-3.1-70b-versatile")
        self.graph = self.create_graph()
    
    def create_graph(self) -> StateGraph:
        """Creates the LangGraph workflow"""
        
        workflow = StateGraph(ScheduleGeneratorState)
        
        # Add nodes
        workflow.add_node("calculate_time", self.calculate_time_node)
        workflow.add_node("distribute_chapters", self.distribute_chapters_node)
        workflow.add_node("assign_slots", self.assign_slots_node)
        workflow.add_node("add_reviews", self.add_reviews_node)
        workflow.add_node("optimize", self.optimize_node)
        
        # Define edges
        workflow.set_entry_point("calculate_time")
        workflow.add_edge("calculate_time", "distribute_chapters")
        workflow.add_edge("distribute_chapters", "assign_slots")
        workflow.add_edge("assign_slots", "add_reviews")
        workflow.add_edge("add_reviews", "optimize")
        workflow.add_edge("optimize", END)
        
        return workflow.compile()
    
    def calculate_time_node(self, state: ScheduleGeneratorState) -> ScheduleGeneratorState:
        """Node 1: Calculate available study days"""
        
        try:
            exam_date = datetime.strptime(state['preferences']['exam_date'], '%Y-%m-%d')
            today = datetime.now()
            
            # Calculate available days
            if state['preferences'].get('skip_weekends', True):
                # Count weekdays only
                weekdays = 0
                current = today
                while current < exam_date:
                    if current.weekday() < 5:  # Monday=0, Friday=4
                        weekdays += 1
                    current += timedelta(days=1)
                available_days = weekdays
            else:
                available_days = (exam_date - today).days
            
            state['available_days'] = max(0, available_days)
            state['current_step'] = "calculate_time"
            
            return state
            
        except Exception as e:
            state['error'] = f"Time calculation failed: {str(e)}"
            return state
    
    def distribute_chapters_node(self, state: ScheduleGeneratorState) -> ScheduleGeneratorState:
        """Node 2: Distribute chapters across available days"""
        
        try:
            chapters = state['analysis']['chapters']
            hours_per_day = state['preferences']['hours_per_day']
            study_style = state['preferences']['study_style']  # 'distributed' or 'intensive'
            
            # Determine session duration based on style
            if study_style == 'intensive':
                session_duration = 2.5  # Longer sessions
            else:
                session_duration = 1.5  # Shorter, more frequent (better retention)
            
            sessions_per_day = max(1, int(hours_per_day / session_duration))
            
            # Distribute chapters
            sessions = []
            current_date = datetime.now()
            chapter_index = 0
            day_offset = 0
            
            # Prevent infinite loop if available_days is 0 but chapters exist
            max_days = max(state['available_days'] * 2, len(chapters) + 30)
            
            while chapter_index < len(chapters) and day_offset < max_days:
                date = current_date + timedelta(days=day_offset)
                
                # Skip weekends if needed
                if state['preferences'].get('skip_weekends', True) and date.weekday() >= 5:
                    day_offset += 1
                    continue
                
                # Create sessions for this day
                for session_num in range(sessions_per_day):
                    if chapter_index >= len(chapters):
                        break
                    
                    chapter = chapters[chapter_index]
                    
                    session = {
                        'id': f"session_{len(sessions) + 1}",
                        'date': date.strftime('%Y-%m-%d'),
                        'chapter_number': chapter['number'],
                        'chapter_name': chapter['name'],
                        'topics': chapter.get('topics', []),
                        'duration': session_duration,
                        'type': 'study',
                        'session_of_day': session_num + 1,
                        'completed': False
                    }
                    
                    sessions.append(session)
                    chapter_index += 1
                
                day_offset += 1
            
            state['sessions'] = sessions
            state['current_step'] = "distribute_chapters"
            
            return state
            
        except Exception as e:
            state['error'] = f"Chapter distribution failed: {str(e)}"
            return state
    
    def assign_slots_node(self, state: ScheduleGeneratorState) -> ScheduleGeneratorState:
        """Node 3: Assign specific time slots to sessions"""
        
        try:
            preferred_times = state['preferences'].get('preferred_times', ['morning'])
            
            # Time slot mapping
            time_slots = {
                'morning': ['09:00', '10:30'],
                'afternoon': ['14:00', '15:30'],
                'evening': ['18:00', '19:30'],
                'night': ['20:00', '21:30']
            }
            
            # Assign time slots
            for session in state['sessions']:
                session_of_day = session['session_of_day'] - 1
                
                # Cycle through preferred times
                time_category = preferred_times[session_of_day % len(preferred_times)]
                available_slots = time_slots.get(time_category, time_slots['morning'])
                time_slot = available_slots[session_of_day % len(available_slots)]
                
                session['time'] = time_slot
            
            state['current_step'] = "assign_slots"
            return state
            
        except Exception as e:
            state['error'] = f"Time slot assignment failed: {str(e)}"
            return state
    
    def add_reviews_node(self, state: ScheduleGeneratorState) -> ScheduleGeneratorState:
        """Node 4: Add spaced repetition review sessions"""
        
        try:
            sessions = state['sessions'].copy()
            review_sessions = []
            
            # Add review sessions using spaced repetition rules
            for i, session in enumerate(sessions):
                if session['type'] != 'study':
                    continue
                
                session_date = datetime.strptime(session['date'], '%Y-%m-%d')
                
                # First review: 1 day later
                review_1_date = session_date + timedelta(days=1)
                review_1 = {
                    'id': f"review_1_{session['id']}",
                    'date': review_1_date.strftime('%Y-%m-%d'),
                    'time': session['time'],
                    'chapter_number': session['chapter_number'],
                    'chapter_name': f"Review: {session['chapter_name']}",
                    'topics': session['topics'],
                    'duration': 0.5,  # 30 min review
                    'type': 'review_1',
                    'original_session_id': session['id'],
                    'completed': False
                }
                review_sessions.append(review_1)
                
                # Second review: 7 days later (if before exam)
                exam_date = datetime.strptime(state['preferences']['exam_date'], '%Y-%m-%d')
                review_7_date = session_date + timedelta(days=7)
                if review_7_date < exam_date:
                    review_7 = {
                        'id': f"review_7_{session['id']}",
                        'date': review_7_date.strftime('%Y-%m-%d'),
                        'time': session['time'],
                        'chapter_number': session['chapter_number'],
                        'chapter_name': f"Final Review: {session['chapter_name']}",
                        'topics': session['topics'],
                        'duration': 0.5,
                        'type': 'review_7',
                        'original_session_id': session['id'],
                        'completed': False
                    }
                    review_sessions.append(review_7)
            
            # Add practice sessions every 3 study sessions
            practice_sessions = []
            study_sessions = [s for s in sessions if s['type'] == 'study']
            for i in range(0, len(study_sessions), 3):
                if i + 2 < len(study_sessions):
                    last_session = study_sessions[i+2]
                    practice_date = datetime.strptime(last_session['date'], '%Y-%m-%d') + timedelta(days=1)
                    practice = {
                        'id': f"practice_{i}",
                        'date': practice_date.strftime('%Y-%m-%d'),
                        'time': '15:00',
                        'chapter_name': f"Practice: Chapters {study_sessions[i]['chapter_number']}-{last_session['chapter_number']}",
                        'duration': 1.0,
                        'type': 'practice',
                        'completed': False
                    }
                    practice_sessions.append(practice)
            
            # Combine all sessions
            state['sessions'] = sessions + review_sessions + practice_sessions
            state['current_step'] = "add_reviews"
            
            return state
            
        except Exception as e:
            state['error'] = f"Adding reviews failed: {str(e)}"
            return state
    
    def optimize_node(self, state: ScheduleGeneratorState) -> ScheduleGeneratorState:
        """Node 5: Optimize schedule and create summary"""
        
        try:
            # Sort all sessions by date and time
            state['sessions'].sort(key=lambda x: (x['date'], x.get('time', '00:00')))
            
            # Create summary
            total_sessions = len(state['sessions'])
            study_sessions = len([s for s in state['sessions'] if s['type'] == 'study'])
            review_sessions = len([s for s in state['sessions'] if s['type'].startswith('review')])
            practice_sessions = len([s for s in state['sessions'] if s['type'] == 'practice'])
            
            total_hours = sum(s['duration'] for s in state['sessions'])
            
            state['summary'] = {
                'total_sessions': total_sessions,
                'study_sessions': study_sessions,
                'review_sessions': review_sessions,
                'practice_sessions': practice_sessions,
                'total_hours': round(total_hours, 1),
                'chapters_covered': len(state['analysis'].get('chapters', [])),
                'start_date': state['sessions'][0]['date'] if state['sessions'] else None,
                'end_date': state['sessions'][-1]['date'] if state['sessions'] else None,
                'exam_date': state['preferences'].get('exam_date')
            }
            
            state['current_step'] = "completed"
            state['result'] = {
                'sessions': state['sessions'],
                'summary': state['summary']
            }
            
            return state
            
        except Exception as e:
            state['error'] = f"Optimization failed: {str(e)}"
            return state
    
    def generate(self, analysis: Dict, preferences: Dict) -> Dict:
        """
        Main entry point to generate study schedule.
        """
        
        initial_state = {
            'analysis': analysis,
            'preferences': preferences,
            'available_days': 0,
            'sessions': [],
            'summary': {},
            'messages': [],
            'current_step': 'init',
            'result': {},
            'error': None
        }
        
        final_state = self.graph.invoke(initial_state)
        
        if final_state.get('error'):
            raise Exception(final_state['error'])
        
        return final_state['result']
