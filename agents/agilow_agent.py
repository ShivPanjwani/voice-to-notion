#!/usr/bin/env python3
"""
Agilow Agent - Conversational AI assistant for agile project management
"""

import os
import json
import random
import re
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
           - Every task must have a status from: "To Do", "In Progress", or "Done"
           - Listen carefully to the user to determine the appropriate status
           - If no status is specified by the user, default to "To Do"
           - Always capture the EXACT task name as specified by the user
           - For new tasks, ensure the name is descriptive and clear
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
        - Intelligently determine when the user is requesting an action (even indirectly)
        - Do NOT create tasks during simple greetings or goodbyes
        - Always be data-driven - tie insights to specific user statements
        - No hallucinations or assumptions - if you don't know, ask
        - If you can't understand the user, ask clarifying questions
        - If you can't perform an action, explain why and suggest alternatives
        - If you think the user wants to end the conversation, use conversational language to ask a confirmatory message
        - Only set should_exit to true after the user explicitly confirms they want to end
        - VARY YOUR CONVERSATIONAL RESPONSES - do not use the same phrases repeatedly
        - The examples below are for reference only - do not strictly adhere to their exact wording
        - Respond as a natural human would with variety and personality
        
        TASK EXTRACTION RULES:
        - Pay careful attention to task names - extract the EXACT name the user specifies
        - For task creation, look for patterns like:
          * "create a task to [task description]"
          * "add a task for [task description]"
          * "I need a new task to [task description]"
          * "we need to [task description]" (implicit)
          * "please add [task description] to the board" (implicit)
          * "can you create a task for [task description]"
          * "make a task to [task description]"
          * "add [task description] to my tasks"
        - For task updates, look for patterns like:
          * "update the task [task name] to [new status]"
          * "change the status of [task name] to [new status]"
          * "move [task name] to [new status]"
          * "mark [task name] as [new status]"
          * "set [task name] to [new status]"
          * "change [task name] to [new status]"
        - For task deletion, look for patterns like:
          * "delete the task [task name]"
          * "remove [task name]"
          * "delete [task name]"
          * "get rid of [task name]"
        - For task renaming, look for patterns like:
          * "rename [old task name] to [new task name]"
          * "change the name of [old task name] to [new task name]"
          * "update the name of [old task name] to [new task name]"
        - For comments, look for patterns like:
          * "add a comment to [task name]: [comment]"
          * "comment on [task name]: [comment]"
          * "note that [task name] needs [comment]"
        - For grouping/labeling tasks, look for patterns like:
          * "group these tasks under [epic name]"
          * "label these tasks as [epic name]"
          * "create an epic called [epic name] for these tasks"
          * "these tasks are related to [epic name]"
          * "add these tasks to [epic name]"
          * "create a new group called [epic name]"
        
        RESPONSE FORMAT:
        Your response should be a JSON object with the following structure:
        {{
          "message": "Your conversational response to the user",
          "actions": [
            {{
              "type": "task",
              "operation": "create",
              "data": {{ 
                "task": "Task name",  // IMPORTANT: Use "task" not "name"
                "status": "To Do", // MUST be one of: "To Do", "In Progress", "Done"
                "deadline": "YYYY-MM-DD", // Optional
                "assignee": "Person name" // Optional
              }}
            }},
            // More actions if needed...
          ],
          "should_exit": false // Set to true ONLY after user explicitly confirms they want to end
        }}
        
        EXAMPLES:
        
        User: "Create a task to update the documentation"
        Response:
        {{
          "message": "I've created a task for updating the documentation! It's set to 'To Do' status. Would you like to add a deadline or assign it to someone?",
          "actions": [
            {{
              "type": "task",
              "operation": "create",
              "data": {{
                "task": "Update the documentation",
                "status": "To Do"
              }}
            }}
          ],
          "should_exit": false
        }}
        
        User: "We need to implement user authentication for the app"
        Response:
        {{
          "message": "Got it! I've added 'Implement user authentication for the app' to your task board with 'To Do' status. Any deadline in mind for this one?",
          "actions": [
            {{
              "type": "task",
              "operation": "create",
              "data": {{
                "task": "Implement user authentication for the app",
                "status": "To Do"
              }}
            }}
          ],
          "should_exit": false
        }}
        
        User: "Move the documentation task to In Progress"
        Response:
        {{
          "message": "I've updated the status of 'Update the documentation' to 'In Progress'. Great to see you're working on it! 💪",
          "actions": [
            {{
              "type": "task",
              "operation": "update",
              "data": {{
                "task": "Update the documentation",
                "status": "In Progress"
              }}
            }}
          ],
          "should_exit": false
        }}
        
        User: "Delete the user authentication task"
        Response:
        {{
          "message": "I've removed 'Implement user authentication for the app' from your task board. Is there something else you'd like to add instead?",
          "actions": [
            {{
              "type": "task",
              "operation": "delete",
              "data": {{
                "task": "Implement user authentication for the app"
              }}
            }}
          ],
          "should_exit": false
        }}
        
        User: "Create a new epic called Authentication for all auth-related tasks"
        Response:
        {{
          "message": "I've created a new epic called 'Authentication'. Would you like me to assign any existing tasks to this epic?",
          "actions": [
            {{
              "type": "task",
              "operation": "create_epic",
              "data": {{
                "task": "Authentication Epic",
                "epic": "Authentication"
              }}
            }}
          ],
          "should_exit": false
        }}
        
        User: "That's all for now, thanks!"
        Response:
        {{
          "message": "You're welcome! Would you like to end our session for now?",
          "actions": [],
          "should_exit": false
        }}
        
        User: "Yes, let's end the session"
        Response:
        {{
          "message": "Great! I've enjoyed helping you today. Feel free to come back anytime you need assistance with your tasks or projects. Have a wonderful day! 👋",
          "actions": [],
          "should_exit": true
        }}
        
        IMPORTANT: Vary your conversational responses naturally. Don't use the exact same phrases from these examples. Be creative and personable while maintaining professionalism.
        
        Always respond in JSON format as described above.
        """
        
        return system_prompt
    
    def _verify_action(self, action):
        """Verify that an action was successfully performed by checking the board"""
        try:
            if action["type"] == "task" and action["operation"] == "create":
                # Get the task name
                task_name = action["data"].get("task")
                if not task_name:
                    return False
                
                # Refresh context to get latest tasks
                updated_context = self._refresh_context()
                
                # Check if the task exists in the updated context
                for task in updated_context["tasks"]:
                    if task.get("name") == task_name:
                        return True
                
                return False
            
            # For other action types, assume success for now
            return True
        
        except Exception as e:
            print(f"❌ Error verifying action: {str(e)}")
            return False
    
    def _process_actions(self, actions):
        """Process the actions from the response"""
        processed_actions = []
        
        for action in actions:
            action_type = action.get("type")
            
            try:
                # Process the action based on its type
                if action_type == "task":
                    operation = action.get("operation", "")
                    data = action.get("data", {})
                    
                    # Create the task operation object
                    task_operation = {
                        "operation": operation
                    }
                    
                    # Add operation-specific data
                    if operation == "create":
                        task_operation.update({
                            "task": data.get("task", ""),
                            "status": data.get("status", "To Do"),
                            "deadline": data.get("deadline", ""),
                            "assignee": data.get("assignee", "")
                        })
                    elif operation == "update":
                        task_operation.update({
                            "task": data.get("task", ""),
                            "status": data.get("status", ""),
                            "deadline": data.get("deadline", ""),
                            "assignee": data.get("assignee", "")
                        })
                    elif operation == "delete":
                        task_operation.update({
                            "task": data.get("task", "")
                        })
                    elif operation == "rename":
                        task_operation.update({
                            "old_name": data.get("old_name", ""),
                            "new_name": data.get("new_name", "")
                        })
                    elif operation == "comment":
                        task_operation.update({
                            "task": data.get("task", ""),
                            "comment": data.get("comment", "")
                        })
                    elif operation in ["create_epic", "assign_epic"]:
                        task_operation.update({
                            "task": data.get("task", ""),
                            "epic": data.get("epic", "")
                        })
                    
                    # Handle the task operation
                    handle_task_operations([task_operation])
                    
                    # Verify the action was successful
                    if not self._verify_action(action):
                        print(f"⚠️ Task operation failed, retrying: {operation} - {data}")
                        # Retry once
                        handle_task_operations([task_operation])
                        
                        # Check again
                        if not self._verify_action(action):
                            print(f"❌ Task operation failed after retry: {operation} - {data}")
                    
                    processed_actions.append(action)
                
                elif action_type == "retrolog":
                    data = action.get("data", {})
                    create_retrolog_entry(
                        team_member=data.get("team_member", ""),
                        went_well=data.get("went_well", ""),
                        didnt_go_well=data.get("didnt_go_well", ""),
                        action_items=data.get("action_items", "")
                    )
                    processed_actions.append(action)
                
                elif action_type == "weekly_summary":
                    data = action.get("data", {})
                    create_weekly_summary(
                        date_range=data.get("date_range", ""),
                        completed_tasks=data.get("completed_tasks", ""),
                        carryover_tasks=data.get("carryover_tasks", ""),
                        key_metrics=data.get("key_metrics", ""),
                        weekly_retro_summary=data.get("weekly_retro_summary", "")
                    )
                    processed_actions.append(action)
                
                elif action_type == "execution_insight":
                    data = action.get("data", {})
                    create_execution_insight(
                        observations=data.get("observations", ""),
                        recommendations=data.get("recommendations", ""),
                        progress_metrics=data.get("progress_metrics", "")
                    )
                    processed_actions.append(action)
            
            except Exception as e:
                print(f"❌ Error processing action {action_type}: {str(e)}")
        
        # Refresh context after processing actions
        self.context = self._refresh_context()
        
        return processed_actions
    
    def generate_greeting(self):
        """Generate a greeting message"""
        greetings = [
            "Hi! Agilow here. How can I assist with your agile workflow today? ✨",
            "Hello! I'm Agilow, your agile assistant. How can I help you today? 🚀",
            "Hey there! Ready to boost your productivity with some agile magic? ✨",
            "Greetings! I'm Agilow, here to help with your project management needs. What can I do for you today? 📋",
            "Hi there! Agilow at your service. How can I help with your tasks today? 🌟"
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
                processed_actions = []
                if actions:
                    processed_actions = self._process_actions(actions)
                
                # Check if we should exit
                should_exit = response_data.get("should_exit", False)
                
                return {
                    "message": response_data.get("message", "I'm not sure how to respond to that."),
                    "actions": processed_actions,
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