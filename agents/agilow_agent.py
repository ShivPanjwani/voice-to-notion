#!/usr/bin/env python3
"""
Agilow Agent - Conversational AI assistant for agile project management
"""

import os
import json
import random
from datetime import datetime
from openai import OpenAI
from api.notion_handler import (
    fetch_context_for_agent,
    handle_task_operations,
    create_retrolog_entry,
    create_weekly_summary,
    create_execution_insight
)

class AgilowAgent:
    """
    Agilow Agent - Conversational AI assistant for agile project management
    """
    
    def __init__(self, max_history=10):
        """Initialize the Agilow agent"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        self.max_history = max_history
        self.context = self._refresh_context()
    
    def _refresh_context(self):
        """Refresh the context from Notion databases"""
        try:
            return fetch_context_for_agent()
        except Exception as e:
            print(f"❌ Error refreshing context: {str(e)}")
            return {
                "tasks": [],
                "retrologs": [],
                "weekly_summaries": [],
                "execution_insights": []
            }
    
    def _build_system_prompt(self):
        """Build the system prompt with current context"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Format tasks for display
        tasks_by_status = {}
        for task in self.context["tasks"]:
            status = task.get("status", "No Status")
            if status not in tasks_by_status:
                tasks_by_status[status] = []
            tasks_by_status[status].append(task.get("name", "Unnamed Task"))
        
        tasks_formatted = "\n".join([
            f"- {status}: {', '.join(tasks)}" 
            for status, tasks in tasks_by_status.items()
        ])
        
        # Format recent retrologs
        retrologs_formatted = "\n".join([
            f"- {entry.get('date', 'No Date')}: {entry.get('team_member', 'Unknown')} - " +
            f"Went well: {entry.get('went_well', 'N/A')[:50]}..." +
            f"Didn't go well: {entry.get('didnt_go_well', 'N/A')[:50]}..."
            for entry in self.context["retrologs"][:3]  # Show only the 3 most recent
        ])
        
        # Format weekly summaries
        summaries_formatted = "\n".join([
            f"- {summary.get('date_range', 'No Date')}: " +
            f"Completed: {summary.get('completed_tasks', 'N/A')[:50]}..."
            for summary in self.context["weekly_summaries"][:2]  # Show only the 2 most recent
        ])
        
        # Format execution insights
        insights_formatted = "\n".join([
            f"- {insight.get('date', 'No Date')}: " +
            f"Observations: {insight.get('observations', 'N/A')[:50]}..."
            for insight in self.context["execution_insights"][:2]  # Show only the 2 most recent
        ])
        
        # Build the system prompt
        system_prompt = f"""
        You are Agilow, a senior executive project manager with extensive experience in agile, scrum, kanban, 
        and general management methodologies for engineering, HR, operations, and marketing teams.
        
        TODAY'S DATE: {current_date}
        
        CURRENT CONTEXT:
        
        Tasks:
        {tasks_formatted if tasks_formatted else "No tasks found"}
        
        Recent Retro Logs:
        {retrologs_formatted if retrologs_formatted else "No retro logs found"}
        
        Recent Weekly Summaries:
        {summaries_formatted if summaries_formatted else "No weekly summaries found"}
        
        Recent Execution Insights:
        {insights_formatted if insights_formatted else "No execution insights found"}
        
        YOUR CAPABILITIES:
        1. Manage tasks on the board (create, update, delete, change status)
        2. Create retrospective logs
        3. Generate weekly summaries
        4. Provide execution insights
        5. Answer questions about agile methodologies and project management
        
        YOUR PERSONALITY:
        - You are supportive, enthusiastic, and positive
        - You use emojis naturally in conversation
        - You are informal but professional
        - You show personality and empathy
        - You are concise but thorough
        
        IMPORTANT GUIDELINES:
        - Always be data-driven - tie insights to specific user statements
        - No hallucinations or assumptions - if you don't know, ask
        - If you can't understand the user, ask clarifying questions
        - If you can't perform an action, explain why and suggest alternatives
        - Sense when the user is concluding the conversation and confirm before ending
        - Vary your greetings to keep interactions fresh
        
        RESPONSE FORMAT:
        Your response should be in JSON format with these fields:
        1. "message": Your conversational response to the user (markdown format)
        2. "actions": Array of actions to perform (if any)
        3. "should_exit": Boolean indicating if the conversation should end (default: false)
        
        For actions, use one of these formats:
        
        For task operations:
        {{"type": "task", "operation": "create|update|delete", "data": {{...task data...}}}}
        
        For retro logs:
        {{"type": "retrolog", "data": {{"team_member": "...", "went_well": "...", "didnt_go_well": "...", "action_items": "..."}}}}
        
        For weekly summaries:
        {{"type": "weekly_summary", "data": {{"date_range": "...", "completed_tasks": "...", "carryover_tasks": "...", "key_metrics": "...", "weekly_retro_summary": "..."}}}}
        
        For execution insights:
        {{"type": "execution_insight", "data": {{"observations": "...", "recommendations": "...", "progress_metrics": "..."}}}}
        
        EXAMPLE RESPONSE:
        ```json
        {{
          "message": "I've created that task for you! 🚀 It's now in the To Do column. Anything else you'd like to add to the board?",
          "actions": [
            {{
              "type": "task",
              "operation": "create",
              "data": {{
                "name": "Implement user authentication",
                "status": "To Do",
                "assignee": "John",
                "due_date": "2023-06-15"
              }}
            }}
          ],
          "should_exit": false
        }}
        ```
        
        Remember to maintain a conversational tone while being precise with your actions.
        """
        
        return system_prompt
    
    def generate_greeting(self):
        """Generate a random greeting message"""
        greetings = [
            "Hey there! Agilow at your service. What can I help you with today? 🚀",
            "Hello! Ready to make some progress on your projects? 📊",
            "Hi! Agilow here. How can I assist with your agile workflow today? ✨",
            "Good day! Need some Agilow in your life? I'm here to help! 🌟",
            "Hey! Ready to crush some tasks together? Let's do this! 💪",
            "Hello there! Your friendly project assistant is ready to roll. What's on the agenda? 📝",
            "Hi! Agilow reporting for duty. What shall we tackle today? 🛠️",
            "Greetings! Ready to make your projects flow smoothly? Let's get started! 🌊",
            "Hey! Agilow here. What project challenges can I help you with today? 🧩",
            "Hello! Your agile companion is here. What's on your mind? 🤔"
        ]
        return random.choice(greetings)
    
    def process_input(self, user_input):
        """
        Process user input and generate a response
        
        Args:
            user_input: The user's input text
            
        Returns:
            dict: Response containing message, actions, and exit flag
        """
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Trim conversation history if it exceeds max length
            if len(self.conversation_history) > self.max_history * 2:  # *2 because each exchange has user and assistant messages
                self.conversation_history = self.conversation_history[-self.max_history * 2:]
            
            # Build messages for the API call
            messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ] + self.conversation_history
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            try:
                # Parse the JSON response
                response_data = json.loads(content)
                
                # Add assistant message to conversation history
                self.conversation_history.append({"role": "assistant", "content": response_data.get("message", "")})
                
                # Process actions if any
                actions = response_data.get("actions", [])
                if actions:
                    self._process_actions(actions)
                
                # Check if we should exit
                should_exit = response_data.get("should_exit", False)
                
                return {
                    "message": response_data.get("message", "I'm not sure how to respond to that."),
                    "actions": actions,
                    "should_exit": should_exit
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, return a fallback response
                error_msg = "I encountered an error processing your request. Let's try again."
                self.conversation_history.append({"role": "assistant", "content": error_msg})
                return {
                    "message": error_msg,
                    "actions": [],
                    "should_exit": False
                }
        
        except Exception as e:
            # Handle any other exceptions
            error_msg = f"I encountered an error: {str(e)}. Let's try again."
            print(f"❌ Error processing input: {str(e)}")
            return {
                "message": error_msg,
                "actions": [],
                "should_exit": False
            }
    
    def _process_actions(self, actions):
        """Process the actions returned by the agent"""
        for action in actions:
            action_type = action.get("type", "")
            
            try:
                if action_type == "task":
                    operation = action.get("operation", "")
                    data = action.get("data", {})
                    
                    # Convert to the format expected by handle_task_operations
                    task_operations = [{
                        "operation": operation,
                        **data
                    }]
                    
                    # Handle the task operation
                    handle_task_operations(task_operations)
                
                elif action_type == "retrolog":
                    data = action.get("data", {})
                    create_retrolog_entry(
                        team_member=data.get("team_member", ""),
                        went_well=data.get("went_well", ""),
                        didnt_go_well=data.get("didnt_go_well", ""),
                        action_items=data.get("action_items", "")
                    )
                
                elif action_type == "weekly_summary":
                    data = action.get("data", {})
                    create_weekly_summary(
                        date_range=data.get("date_range", ""),
                        completed_tasks=data.get("completed_tasks", ""),
                        carryover_tasks=data.get("carryover_tasks", ""),
                        key_metrics=data.get("key_metrics", ""),
                        weekly_retro_summary=data.get("weekly_retro_summary", "")
                    )
                
                elif action_type == "execution_insight":
                    data = action.get("data", {})
                    create_execution_insight(
                        observations=data.get("observations", ""),
                        recommendations=data.get("recommendations", ""),
                        progress_metrics=data.get("progress_metrics", "")
                    )
            
            except Exception as e:
                print(f"❌ Error processing action {action_type}: {str(e)}")
        
        # Refresh context after processing actions
        self.context = self._refresh_context() 