# agents/task_extractor.py
from openai import OpenAI
import json
import os
import re
from datetime import datetime

def extract_tasks(transcription, is_streaming=False):
    """Extract tasks and operations from transcription"""
    if not transcription:
        print("❌ No input provided.")
        return []
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Determine which task manager is being used
        task_manager = os.getenv("TASK_MANAGER", "notion").lower()
        platform_name = "Trello" if task_manager == "trello" else "Notion"
        
        # Create the prompt
        prompt = f"""
        Extract task operations from the following meeting transcript.
        
        Today's date: {datetime.now().strftime("%Y-%m-%d")}
        
        You are extracting tasks for {platform_name}.
        
        For each task operation, provide a JSON object with the following structure:
        
        For creating a new task:
        {{
            "operation": "create",
            "task": "task name",
            "status": "Not started", // Optional, defaults to "Not started"
            "deadline": "YYYY-MM-DD", // Optional
            "assignee": "person name", // Optional
            "epic": "epic name" // Optional
        }}
        
        For updating an existing task:
        {{
            "operation": "update",
            "task": "exact task name",
            "status": "In Progress", // Optional
            "deadline": "YYYY-MM-DD", // Optional
            "assignee": "person name", // Optional
            "epic": "epic name" // Optional
        }}
        
        For deleting a task:
        {{
            "operation": "delete",
            "task": "exact task name"
        }}
        
        For renaming a task:
        {{
            "operation": "rename",
            "old_name": "exact existing task name",
            "new_name": "new task name"
        }}
        
        For adding a comment to a task:
        {{
            "operation": "comment",
            "task": "exact task name",
            "comment": "comment text"
        }}
        
        For creating a new epic:
        {{
            "operation": "create_epic",
            "epic": "epic name"
        }}
        
        For assigning an epic to a task:
        {{
            "operation": "assign_epic",
            "task": "exact task name",
            "epic": "epic name"
        }}
        
        Return ONLY a JSON array of these operations, with no additional text or explanation.
        
        Transcript:
        {transcription}
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a project management AI. Extract tasks from spoken input. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean up the response - remove markdown code blocks and any explanatory text
        result = re.sub(r'```json|```', '', result).strip()
        
        # Find the first [ and last ] to extract just the JSON array
        start_idx = result.find('[')
        end_idx = result.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            result = result[start_idx:end_idx]
        
        try:
            tasks = json.loads(result)
            if isinstance(tasks, list):
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
                print(f"❌ Invalid response format. Expected a list but got: {type(tasks)}")
                return []
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Raw response: {result}")
            return []
    
    except Exception as e:
        print(f"❌ Task extraction error: {str(e)}")
        return []