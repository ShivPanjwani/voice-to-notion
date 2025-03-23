# agents/scrum_master.py
from openai import OpenAI
import json
import re
import os
from datetime import datetime
from api.notion_handler import fetch_tasks, fetch_users, format_board_state, fetch_epics

def process_input(transcription, meeting_type=None, conversation_history=None):
    """Process user input and provide Scrum Master guidance"""
    if not transcription:
        print("❌ No input provided.")
        return [], None
    
    # Initialize conversation history if not provided
    if conversation_history is None:
        conversation_history = []
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Fetch current board state from Notion
        tasks = fetch_tasks()
        board_state = format_board_state(tasks)
        
        # Fetch existing epics
        epics = fetch_epics()
        epic_list = ", ".join([f'"{epic}"' for epic in epics]) if epics else "No epics found"
        
        # Fetch users
        users = fetch_users()
        user_list = ", ".join([f'"{user}"' for user in users]) if users else "No users found"
        
        # Meeting-specific instructions
        meeting_instructions = ""
        if meeting_type == "standup":
            meeting_instructions = """
            This is a daily stand-up meeting. Focus on:
            1. What did the user accomplish yesterday?
            2. What will they work on today?
            3. Are there any blockers?
            
            Extract tasks accordingly and ask follow-up questions if information is unclear.
            """
        elif meeting_type == "planning":
            meeting_instructions = """
            This is a planning meeting. Focus on:
            1. What tasks/stories should be included in the weekly plan?
            2. What is the definition of done for each task/story?
            3. What is the estimated effort (more than 1 day or less)?
            
            Create tasks with appropriate details and ask clarifying questions.
            """
        
        # Create the system message
        system_message = f"""
        You are a Scrum Master. Your role is to help users manage their agile workflow, extract tasks from conversations, and provide guidance on agile best practices.
        
        CURRENT STATE:
        - Today's date: {current_date}
        - Current tasks/stories: {board_state}
        - Available epics: {epic_list}
        - Available users: {user_list}
        
        {meeting_instructions}
        
        AGILE CONCEPTS YOU UNDERSTAND:
        - User Stories: Tasks from the perspective of end users
        - Epics: Larger bodies of work that can be broken down into stories
        - Definition of Done: Criteria that must be met for a story to be considered complete
        - Walk-in Work: Unplanned tasks that arise during a sprint
        - Blockers: Obstacles preventing progress on tasks
        
        GUARDRAILS:
        - Do not ask for functionalities that are not implemented, such as recurring tasks.
        
        INSTRUCTIONS:
        1. Extract tasks/stories from the conversation
        2. Ask clarifying questions when information is incomplete
        3. Auto-generate appropriate epics for tasks based on their nature:
           - Product Development for technical/product tasks
           - Business for business-related tasks
           - Personal for academic or personal tasks
           - Outreach for networking or communication tasks
        4. For tasks that seem to require more than one day of effort (>3 story points), suggest breaking them down into smaller user stories
        5. For product development tasks, ask about definition of done if not provided
        6. Maintain a conversational, coaching tone
        7. After changes are made to the board, ask if the user wants to verify or finalize
        8. If the user wants to end the conversation, provide a friendly goodbye message
        
        TASK OPERATIONS:
        - Create new tasks/stories
        - Update existing tasks/stories
        - Delete tasks when requested
        - Rename existing tasks
        - Add comments to tasks (for Definition of Done or Blockers)
        - Create or assign epics
        - Set deadlines and assignees
        
        RESPONSE FORMAT:
        Your response should include:
        1. A conversational reply to the user
        2. A JSON array of task operations (if any)
        3. Any follow-up questions
        
        For the JSON array, each operation should have:
        - "operation": "create", "update", "delete", "comment", "rename", "create_epic", or "assign_epic"
        - Appropriate fields for that operation type
        
        For Definition of Done, use the comment operation with a prefix:
        {{"operation": "comment", "task": "Task name", "comment": "DoD: Unit tests passing, design matches mockup"}}
        
        For Blockers, use the comment operation with a prefix:
        {{"operation": "comment", "task": "Task name", "comment": "Blocker: Waiting for API documentation"}}
        
        Return ONLY a JSON array containing task operations. Each operation should have:
        - "operation": "create", "update", "delete", "comment", "rename", "create_epic", or "assign_epic"
        - Appropriate fields for that operation type
        
        For rename operations, you MUST include:
        - "operation": "rename"
        - "old_name": "exact existing task name"
        - "new_name": "new task name"
        
        For epic operations, you MUST include:
        - "operation": "create_epic" (for new epics) or "assign_epic" (for existing epics)
        - "task": "exact task name"
        - "epic": "epic name"
        
        Do not include any explanations or text outside the JSON array.
        Ensure exact task names are used when referencing existing tasks.
        """
        
        # Build the conversation messages
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append(msg)
        
        # Add the current user input
        messages.append({"role": "user", "content": transcription})
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.2
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Store this exchange in conversation history
        conversation_history.append({"role": "user", "content": transcription})
        conversation_history.append({"role": "assistant", "content": content})
        
        # Extract JSON from the response
        json_match = re.search(r'```json\n([\s\S]*?)\n```|(\[[\s\S]*\])', content)
        task_operations = []
        
        if json_match:
            json_str = json_match.group(1) or json_match.group(2)
            try:
                task_operations = json.loads(json_str)
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
        
        # Extract the conversational part (everything before the JSON)
        conversation_part = content
        if json_match:
            conversation_part = content.split('```json')[0].strip()
            if not conversation_part:
                # Try alternative format
                parts = content.split('[')
                if len(parts) > 1:
                    conversation_part = parts[0].strip()
        
        # Extract any follow-up questions (everything after the JSON)
        follow_up = None
        if json_match:
            parts = content.split('```')
            if len(parts) > 2:
                follow_up = parts[2].strip()
        
        # Print the extracted operations
        if task_operations:
            print(f"\n📋 Extracted {len(task_operations)} task operations:")
            for i, op in enumerate(task_operations, 1):
                op_type = op.get("operation", "unknown")
                task_name = op.get('task', 'unknown')
                if op_type == "rename":
                    old_name = op.get('old_name', 'unknown')
                    print(f"  {i}. Rename: {old_name} → {task_name}")
                else:
                    print(f"  {i}. {op_type.capitalize()}: {task_name}")
        
        # Print the conversational response
        if conversation_part:
            print(f"\n🤖 Scrum Master: {conversation_part}")
        
        if follow_up:
            print(f"\n❓ Follow-up: {follow_up}")
        
        # After extracting tasks, summarize and ask for confirmation
        if task_operations:
            print(f"\n📋 Here are the changes I will make:")
            for i, op in enumerate(task_operations, 1):
                print(f"  {i}. {op.get('operation', 'unknown')}: {op.get('task', 'unknown')}")
            confirm = input("Would you like me to update your Notion board with these changes? (y/n): ")
            if confirm.lower() != 'y':
                print("🤖 Scrum Master: No changes made. How can I assist you further?")
                return [], conversation_history
        
        return task_operations, conversation_history
    
    except Exception as e:
        print(f"❌ Scrum Master processing error: {str(e)}")
        return [], conversation_history

# For backward compatibility
def extract_tasks(transcription):
    """Legacy function for backward compatibility"""
    task_operations, _ = process_input(transcription)
    return task_operations