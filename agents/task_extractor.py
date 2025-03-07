# agents/task_extractor.py
from openai import OpenAI
import json
import re
import os
from datetime import datetime
from api.notion_handler import fetch_tasks, fetch_users, format_board_state

def extract_tasks(transcription):
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
        
        prompt = f"""
        Today's date is {current_date}.

        {board_state}

        Available Status Options:
        - "Not started"
        - "In Progress"
        - "Done"
        
        SPOKEN INPUT TO PROCESS:
        "{transcription}"

        You are a project management AI. Your role is to extract task operations from spoken input and/or user provided transcription from user's meeetings. 
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

        Return ONLY a JSON array containing task operations. Each operation should have:
        - "operation": "create", "update", "delete", "comment", or "rename"
        - Appropriate fields for that operation type

        For rename operations, you MUST include:
        - "operation": "rename"
        - "old_name": "exact existing task name"
        - "new_name": "new task name"

        Example rename operation:
        {{
            "operation": "rename",
            "old_name": "Complete Team Competency Evaluation And Gap Analysis",
            "new_name": "Team Competency Analysis"
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
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a task extraction AI. Extract tasks from spoken input."},
                {"role": "user", "content": prompt}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean up the response - remove markdown code blocks
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            tasks = json.loads(result)
            if isinstance(tasks, list):
                # Simplified output - no need to print number of tasks
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