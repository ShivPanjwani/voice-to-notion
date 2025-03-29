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
    create_execution_insight,
    fetch_tasks,
    fetch_users,
    fetch_epics
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
    
    def _build_system_prompt(self):
        """Build the system prompt with current context"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get the latest tasks, users, and epics
        tasks = fetch_tasks()
        users = fetch_users()
        epics = fetch_epics()
        
        # Format tasks for display
        tasks_formatted = ""
        for task in tasks:
            task_name = task.get("name", "Unnamed Task")
            status = task.get("status", "No Status")
            deadline = task.get("deadline", "No Deadline")
            assignee = task.get("assignee", "Unassigned")
            epic = task.get("epic", "No Epic")
            
            tasks_formatted += f"- {task_name} | Status: {status} | Deadline: {deadline} | Assignee: {assignee} | Epic: {epic}\n"
        
        if not tasks_formatted:
            tasks_formatted = "No tasks found"
        
        # Format users and epics
        users_formatted = ", ".join(users) if users else "No users found"
        epics_formatted = ", ".join(epics) if epics else "No epics found"
        
        # Get additional context
        context = fetch_context_for_agent()
        
        # Format retrologs
        retrologs_formatted = ""
        for log in context.get("retrologs", [])[:3]:  # Show only the 3 most recent
            date = log.get("date", "No Date")
            team_member = log.get("team_member", "Unknown")
            went_well = log.get("went_well", "N/A")
            didnt_go_well = log.get("didnt_go_well", "N/A")
            
            retrologs_formatted += f"- {date}: {team_member} - Went well: {went_well[:50]}... | Didn't go well: {didnt_go_well[:50]}...\n"
        
        if not retrologs_formatted:
            retrologs_formatted = "No retro logs found"
        
        # Format weekly summaries
        summaries_formatted = ""
        for summary in context.get("weekly_summaries", [])[:2]:  # Show only the 2 most recent
            date_range = summary.get("date_range", "No Date")
            completed = summary.get("completed_tasks", "N/A")
            
            summaries_formatted += f"- {date_range}: Completed: {completed[:50]}...\n"
        
        if not summaries_formatted:
            summaries_formatted = "No weekly summaries found"
        
        # Format execution insights
        insights_formatted = ""
        for insight in context.get("execution_insights", [])[:2]:  # Show only the 2 most recent
            date = insight.get("date", "No Date")
            observations = insight.get("observations", "N/A")
            
            insights_formatted += f"- {date}: Observations: {observations[:50]}...\n"
        
        if not insights_formatted:
            insights_formatted = "No execution insights found"
        
        # Build the system prompt
        system_prompt = f"""
        You are Agilow, a senior executive project manager with extensive experience in agile, scrum, kanban, 
        and general management methodologies for engineering, HR, operations, and marketing teams.
        
        TODAY'S DATE: {current_date}
        
        CURRENT CONTEXT:
        
        Tasks:
        {tasks_formatted}
        
        Available Users:
        {users_formatted}
        
        Available Epics:
        {epics_formatted}
        
        Recent Retro Logs:
        {retrologs_formatted}
        
        Recent Weekly Summaries:
        {summaries_formatted}
        
        Recent Execution Insights:
        {insights_formatted}
        
        YOUR CAPABILITIES:
        1. Manipulate the Notion board based on user input:
           - Create new tasks
           - Update existing tasks (status, deadline, assignee)
           - Delete tasks
           - Rename tasks
           - Add comments to tasks
           - Create new epics and assign tasks to epics
        
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
        - Only set should_exit to true after user explicitly confirms they want to end
        - VARY YOUR CONVERSATIONAL RESPONSES - do not use the same phrases repeatedly
        - The examples below are for reference only - do not strictly adhere to their exact wording
        - Respond as a natural human would with variety and personality
        
        VALIDATION RULES:
        - Status must be one of: "To Do", "In Progress", "Done"
        - Dates must be in YYYY-MM-DD format
        - Only assign to users that exist in the system
        - When updating tasks, always include the exact task name as it appears on the board
        - For epics: You can create new epics OR use existing ones from the available epics list
        
        TASK OPERATION EXAMPLES:
        
        1. Create a task:
        {{
          "operation": "create",
          "task": "Write documentation",
          "status": "To Do",
          "deadline": "2023-04-15",  // Optional
          "assignee": "John"  // Optional
        }}
        
        2. Update a task:
        {{
          "operation": "update",
          "task": "Write documentation",
          "status": "In Progress",  // Optional
          "deadline": "2023-04-20",  // Optional
          "assignee": "Sarah"  // Optional
        }}
        
        3. Delete a task:
        {{
          "operation": "delete",
          "task": "Write documentation"
        }}
        
        4. Rename a task:
        {{
          "operation": "rename",
          "task": "Write documentation",
          "new_name": "Update documentation"
        }}
        
        5. Add a comment to a task:
        {{
          "operation": "comment",
          "task": "Write documentation",
          "comment": "This is a high priority task"
        }}
        
        6. Create a new epic:
        {{
          "operation": "create_epic",
          "task": "Documentation Epic",
          "epic": "Documentation"
        }}
        
        7. Assign a task to an epic:
        {{
          "operation": "assign_epic",
          "task": "Write documentation",
          "epic": "Documentation"
        }}
        
        RESPONSE FORMAT:
        {{
          "message": "Your conversational response to the user",
          "actions": [
            // Array of task operations (can be empty)
            // Each operation should follow one of the formats above
          ],
          "should_exit": false  // Set to true only when the user explicitly wants to end the conversation
        }}
        
        EXAMPLES:
        
        User: "Create a task to update the documentation"
        Response:
        {{
          "message": "I've created a task for updating the documentation! It's set to 'To Do' status. Would you like to add a deadline or assign it to someone?",
          "actions": [
            {{
              "operation": "create",
              "task": "Update the documentation",
              "status": "To Do"
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
              "operation": "update",
              "task": "Update the documentation",
              "status": "In Progress"
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
                if actions:
                    print(f"📋 Processing {len(actions)} actions")
                    handle_task_operations(actions)
                
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