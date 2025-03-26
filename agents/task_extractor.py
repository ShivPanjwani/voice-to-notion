# agents/task_extractor.py
from openai import OpenAI
import json
import re
import os
from datetime import datetime
from api.notion_handler import fetch_tasks, fetch_users, format_board_state, fetch_epics

def extract_tasks(transcription, is_streaming=False):
    """Extract tasks and operations from transcription"""
    if not transcription:
        print("❌ No transcription provided.")
        return []
    
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
        
        # Additional context for streaming mode
        streaming_context = """
        IMPORTANT STREAMING INSTRUCTIONS:
        You are processing a live audio stream that may contain partial sentences or incomplete thoughts.
        - Only extract tasks when you are confident the speaker has finished expressing the complete task
        - If a sentence seems cut off or incomplete, DO NOT extract a task from it
        - Wait for more context in future chunks before making decisions on ambiguous statements
        - Prioritize precision over recall - it's better to miss a task than to create an incorrect one
        """ if is_streaming else ""
        
        prompt = f"""
        Today's date is {current_date}.

        {board_state}

        Available Status Options:
        - "Not started"
        - "In Progress"
        - "Done"
        
        Available Epics:
        {epic_list}
        
        {streaming_context}
        
        SPOKEN INPUT TO PROCESS:
        "{transcription}"

        You are a project management AI. Your role is to extract task operations from spoken input and/or user provided transcription from user's meetings. 
        1. Create new tasks
        2. Update existing tasks
        3. Delete tasks when requested
        4. Rename existing tasks        
        Pay special attention to rename operations which may use phrases like:
        - "update task name X to Y"
        - "rename task X to Y"
        - "change name of task X to Y"
        - "update the name of X to Y"
        5. Add comments to tasks
        6. Create or assign epics to tasks (Epics are broad-level categories that group tasks together)
           - Only create or assign epics when explicitly requested
           - Do not suggest epics unless asked
           - When creating a new epic, use the "create_epic" operation with ONLY the "epic" field
           - When assigning an existing epic to a task, use the "assign_epic" operation
           - Use Title Case for all epic names (capitalize first letter of each word)
           - Check if an epic with a similar name already exists (ignoring case differences)

        Common phrases that indicate epic creation:
        - "Create an epic called X"
        - "New epic named X"
        - "Add epic X"
        - "Under this epic..."
        - "This epic is going to be called X"
        - "Put these tasks under epic X"
        - "Group these under X"
        - "Label these as X"

        Return ONLY a JSON array containing task operations. Each operation should have:
        - "operation": "create", "update", "delete", "comment", "rename", "create_epic", or "assign_epic"
        - Appropriate fields for that operation type

        For rename operations, you MUST include:
        - "operation": "rename"
        - "old_name": "exact existing task name"
        - "new_name": "new task name"

        For creating a new epic, you MUST include:
        - "operation": "create_epic"
        - "epic": "Epic Name In Title Case"

        For assigning an epic to a task, you MUST include:
        - "operation": "assign_epic"
        - "task": "exact task name"
        - "epic": "Epic Name In Title Case"

        Example rename operation:
        {{
            "operation": "rename",
            "old_name": "Complete Team Competency Evaluation And Gap Analysis",
            "new_name": "Team Competency Analysis"
        }}

        Example epic operations:
        {{
            "operation": "create_epic",
            "epic": "ShopTalk"
        }}
        {{
            "operation": "assign_epic",
            "task": "Prepare for ShopTalk",
            "epic": "Agilow Product"
        }}

        Other operation examples:
        [
            {{
                "operation": "create",
                "task": "Write documentation",
                "status": "Not started",
                "deadline": "2023-12-01",
                "assignee": "John"
            }},
            {{
                "operation": "update",
                "task": "Fix login bug",
                "status": "Done"
            }}
        ]

        Do not include any explanations or text outside the JSON array.
        Ensure exact task names are used when referencing existing tasks.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a project management AI. Extract tasks from spoken input. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean up the response - remove markdown code blocks
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            tasks = json.loads(result)
            if isinstance(tasks, list):
                # Reorder operations: create_epic first, then create tasks, then other operations
                reordered_tasks = []
                # First, add all create_epic operations
                for op in tasks:
                    if op.get("operation") == "create_epic":
                        # Ensure epic names are in Title Case
                        if "epic" in op:
                            op["epic"] = ' '.join(word.capitalize() for word in op["epic"].split())
                        reordered_tasks.append(op)
                # Then, add all create operations
                for op in tasks:
                    if op.get("operation") == "create":
                        # Ensure epic names are in Title Case if present
                        if "epic" in op:
                            op["epic"] = ' '.join(word.capitalize() for word in op["epic"].split())
                        reordered_tasks.append(op)
                # Finally, add all other operations
                for op in tasks:
                    if op.get("operation") not in ["create_epic", "create"]:
                        # Ensure epic names are in Title Case if present
                        if "epic" in op:
                            op["epic"] = ' '.join(word.capitalize() for word in op["epic"].split())
                        reordered_tasks.append(op)
                
                tasks = reordered_tasks
                
                # Print the extracted operations
                if tasks:
                    print(f"\n📋 Extracted {len(tasks)} task operations:")
                    for i, op in enumerate(tasks, 1):
                        op_type = op.get("operation", "unknown")
                        if op_type == "create":
                            print(f"  {i}. Create: {op.get('task', 'unknown')}")
                        elif op_type == "delete":
                            print(f"  {i}. Delete: {op.get('task', 'unknown')}")
                        elif op_type == "update":
                            print(f"  {i}. Update: {op.get('task', 'unknown')} - {', '.join([f'{k}: {v}' for k, v in op.items() if k not in ['operation', 'task']])}")
                        elif op_type == "rename":
                            print(f"  {i}. Rename: {op.get('old_name', 'unknown')} → {op.get('new_name', 'unknown')}")
                        elif op_type == "create_epic":
                            print(f"  {i}. Create Epic: {op.get('epic', 'unknown')}")
                        elif op_type == "assign_epic":
                            print(f"  {i}. Assign Epic: {op.get('task', 'unknown')} to {op.get('epic', 'unknown')}")
                        else:
                            print(f"  {i}. {op_type.capitalize()}: {op}")
                else:
                    print("\n📋 No task operations extracted.")
                
                return tasks
            else:
                print("❌ Invalid response format: not a list")
                return []
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON response: {result}")
            return []
            
    except Exception as e:
        print(f"❌ Task extraction error: {str(e)}")
        return []