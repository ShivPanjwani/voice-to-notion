from openai import OpenAI
import json
import re
import os
from datetime import datetime
from api.trello_handler import fetch_cards, fetch_board_members, format_board_state, fetch_labels, create_checklist, find_card_by_name

def extract_tasks_trello(transcription, is_streaming=False):
    """Extract tasks and operations from transcription for Trello"""
    if not transcription:
        print("❌ No transcription provided.")
        return []
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Fetch current board state from Trello
        cards = fetch_cards()
        board_state = format_board_state(cards)
        
        # Fetch existing labels (epics)
        labels = fetch_labels()
        label_list = ", ".join([f'"{label}"' for label in labels]) if labels else "No labels found"
        
        # Fetch board members
        members = fetch_board_members()
        member_names = [member.get('fullName', member.get('username', '')) for member in members]
        member_list = ", ".join([f'"{member}"' for member in member_names]) if member_names else "No members found"
        
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
        - "To Do"
        - "In Progress"
        - "Done"
        
        Available Labels (Epics):
        {label_list}
        
        Available Members:
        {member_list}
        
        {streaming_context}
        
        SPOKEN INPUT TO PROCESS:
        "{transcription}"

        You are a project management AI. Your role is to extract task operations from spoken input and/or user provided transcription from user's meetings. Additionally, your role also includes extracting retrospective items of what's going well, what's not going well in relation to each task, and what changes or ideas to make based on the lessons learned from what's not going well or any new ideas discussed by the user.
        
        1. Create new tasks
        2. Update existing tasks
        3. Delete tasks when requested
        4. Rename existing tasks        
        5. Add comments to tasks
        6. Create or assign labels to tasks (Labels are broad-level categories that group tasks together, similar to epics)
        7. Assign members to tasks
        8. Remove members from tasks
        9. Create checklists in tasks (checklists are sub-tasks or items within a task)
        10. Update checklists status in tasks
        11. Delete checklists in tasks
        12. Add positive aspects related to the tasks to the "What's going well?" column
        13. Add challenges and lessons learned related to the tasksto the "What's not going well?" column
        14. Add improvement ideas to the "What changes/ideas to make?" column based on lessons learned or new ideas. The improvement ideas should be based on the lessons learned or new ideas discussed by the user. They may arise from exisiting tasks or may be new ideas that the user wants to implement.
        
        IMPORTANT: When a user talks about marking checklist items as done or complete, do NOT change the status of the parent task/card unless explicitly requested. Changing the status of checklist items should not affect the overall task status.
        
        IMPORTANT FOR NAMES: Users may make small typos in checklist or item names. The system can handle minor typos, but try to be as accurate as possible when extracting names. If the user mentions "Fun Checklist" but it's actually "Fun CheckList", be flexible with the name extraction.
        
        Pay special attention to rename operations which may use phrases like:
        - "update task name X to Y"
        - "rename task X to Y"
        - "change name of task X to Y"
        - "update the name of X to Y"
        
        For member assignments, listen for phrases like:
        - "assign X to task Y"
        - "make X responsible for Y"
        - "X should work on Y"
        - "put X on task Y"
        
        For member removal, listen for phrases like:
        - "remove X from task Y"
        - "X is no longer working on Y"
        - "take X off task Y"

        For checklist creation, listen for phrases like:
        - "add Y as an item in the Z checklist for task X"
        - "add a new checklist for task X"
        - "create a checklist named Y for task X"
        - "create a checklist for task X"
        - "create a checklist for task X with items Y and Z"
        - "add items to the checklist of task X"
        - "add Y and Z to the checklist in task X"
        - "add new items Y and Z to task X's checklist"
        - "add Y as a new item in task X"

        IMPORTANT: When users mention adding items to a checklist for a task, try to add them to an existing checklist first rather than creating a new checklist every time. If the task already has a checklist, add the new items to that checklist instead of creating a new one.
        
        HOWEVER, if the user explicitly asks to create a "new checklist", you should create a new checklist rather than adding to an existing one. Pay attention to phrases like "create a new checklist" which indicate the user wants a fresh checklist.
        
        For checklist update, listen for phrases like:
        - "the item Y in the Z checklist for task X is done"
        - "delete the item Y in the Z checklist for task X"
        - "we don't need Y in the Z checklist for task X anymore"
        - "remove Y from the Z checklist for task X"
        - "mark Y in the Z checklist for task X as done"
        - "mark Y in the Z checklist for task X as not done"
        - "Y in the Z checklist for task X is done"
        - "Y in the Z checklist for task X is not done"
        - "set the third item of the first checklist to done"
        - "mark the second item in the first checklist as complete"
        - "update the fourth item in the third checklist to done"

        IMPORTANT: The system can handle positional references to checklists and items. For example:
        - "first checklist" refers to the first checklist in the card
        - "second checklist" refers to the second checklist in the card
        - "third item" refers to the third item in a checklist
        - "set the third item of the first checklist to done" will mark the third item in the first checklist as complete
        - "update the second item in checklist 1 to done" will mark the second item in the first checklist as complete
        
        IMPORTANT FOR NEW ITEMS: When a user asks to add a new item to a checklist AND set its state (e.g., "add a new item called X to the checklist and set it to done"), interpret this as an "update_checklist_item" operation. The system will create the item if it doesn't exist and then update its state.

        IMPORTANT: For checklist item deletion, listen carefully for phrases like:
        - "delete the item Y in the Z checklist for task X"
        - "remove Y from the Z checklist for task X"
        - "delete Y from the Z checklist"
        - "remove the item Y from the checklist in task X"
        These should be processed as "delete_checklist_item" operations, NOT as "update_checklist_item" operations.
        
        IMPORTANT: When handling checklist item status updates (e.g., marking an item as done), do NOT change the overall task status unless explicitly requested. Checklist item status and task status are separate concepts.
        
        For checklist deletion, listen for phrases like:
        - "delete the Z checklist for task X"
        - "delete the checklist for task X"

        For updating a checklist item status, you MUST include:
        - "operation": "update_checklist_item"
        - "card": "exact card name"
        - "checklist": "exact checklist name"
        - "item": "exact item name"
        - "state": "complete" or "incomplete"
        
        For deleting a checklist item, you MUST include:
        - "operation": "delete_checklist_item"
        - "card": "exact card name"
        - "checklist": "exact checklist name"
        - "item": "exact item name"

        For retrospective reflections, listen for patterns like:
        - "what's going well with [task name]"
        - "what went well for [task name]"
        - "the good things about [task name] are"
        - "we're making progress on [task name] with"
        - "what's not going well with [task name]"
        - "what didn't go well for [task name]"
        - "we're having issues with [task name]"
        - "lessons learned from [task name]"
        - "for next time we should"
        - "changes we need to make for [task name]"
        - "ideas for improving [task name]"
        
        IMPORTANT: Every cardin the "What's going well?" and "What's not going well?" columns must match exactly with an existing task name from the "Not started", "In Progress", or "Done" columns.
        The idea is that every card in the "What's going well?" and "What's not going well?" columns should be a reflection (associated with) of a task in the "Not started", "In Progress", or "Done" columns.
        
        IMPORTANT: For "What's going well?" cards, always include positive aspects as a numbered list in the description field. 
       
        IMPORTANT: For "What's not going well?" cards, always include challenges as a numbered list in the desicription field and the associated lessons learned as numbered list in the comments field. 
        Note that for every challenge listed in the description field, there should be a corresponding lesson learned in the comments field.
        
        IMPORTANT: For "What changes/ideas to make?" cards, create a new descriptive task name and add checklist items based on lessons learned from "What's not going well?" or new ideas mentioned.
        Note that for every lesson learned listed in the comments field of the "What's not going well?" card, there should be a corresponding checklist item in the "What changes/ideas to make?" card.

        Return ONLY a JSON array containing task operations. Each operation should have:
        - "operation": "create", "update", "delete", "comment", "rename", "create_epic", "assign_epic", "assign_member", "remove_member", "create_checklist", "update_checklist_item", or "delete_checklist_item"
        - Appropriate fields for that operation type

        For rename operations, you MUST include:
        - "operation": "rename"
        - "old_name": "exact existing task name"
        - "new_name": "new task name"

        For creating a new label, you MUST include:
        - "operation": "create_epic"
        - "epic": "Label Name In Title Case"

        For assigning a label to a task, you MUST include:
        - "operation": "assign_epic"
        - "task": "exact task name"
        - "epic": "Label Name In Title Case"
        
        For assigning a member to a task, you MUST include:
        - "operation": "assign_member"
        - "task": "exact task name"
        - "member": "member name"
        
        For removing a member from a task, you MUST include:
        - "operation": "remove_member"
        - "task": "exact task name"
        - "member": "member name"

        For adding positive reflections (what's going well), you MUST include:
        - "operation": "add_reflection_positive"
        - "task": "exact task name"
        - "items": ["item 1", "item 2", ...] - List of things going well

        For adding negative reflections (what's not going well), you MUST include:
        - "operation": "add_reflection_negative"
        - "task": "exact task name"
        - "issues": ["issue 1", "issue 2", ...] - List of things not going well
        - "lessons_learned": ["lesson 1", "lesson 2", ...] - List of lessons learned from issues

        For creating improvement tasks, you MUST include:
        - "operation": "create_improvement_task"
        - "task_name": "descriptive name for the improvement task"
        - "description": "descriptive synthesis of the lessons learned from the associated what's not going well card"
        -"checklist_items": ["item 1", "item 2", ...] - List of action items derived from lessons learned

        Example rename operation:
        {{
            "operation": "rename",
            "old_name": "Complete Team Competency Evaluation And Gap Analysis",
            "new_name": "Team Competency Analysis"
        }}

        Example label operations:
        {{
"operation": "create_epic",
            "epic": "ShopTalk"
        }}
        {{
            "operation": "assign_epic",
            "task": "Prepare for ShopTalk",
            "epic": "Agilow Product"
        }}
        
        Example member operations:
        {{
            "operation": "assign_member",
            "task": "Design new landing page",
            "member": "John Smith"
        }}
        {{
            "operation": "remove_member",
            "task": "Update documentation",
            "member": "Jane Doe"
        }}

        Example checklist operation:
        {{
            "operation": "create_checklist",
            "card": "Design new landing page",
            "checklist": "To-Do List",
            "items": ["Research competitors", "Create wireframes", "Review with team"]
        }}

        Example for explicitly creating a new checklist (even if one exists):
        {{
            "operation": "create_checklist",
            "card": "Design new landing page",
            "checklist": "New Checklist Name",
            "items": ["First item", "Second item"],
            "force_new": true
        }}

        Example checklist item status update:
        {{
            "operation": "update_checklist_item",
            "card": "Design new landing page",
            "checklist": "To-Do List",
            "item": "Research competitors",
            "state": "complete"
        }}

        Example checklist item deletion:
        {{
            "operation": "delete_checklist_item",
            "card": "Design new landing page",
            "checklist": "To-Do List",
            "item": "Research competitors"
        }}

        Example scenarios for creating and immediately setting an item's state:
        - "Add a new item called 'Review PR' to the first checklist and mark it as done"
        - "In the Development checklist, create a new item 'Setup CI/CD' and set it to complete"
        - "Add 'Test Coverage' to the second checklist and mark it as done"
        
        All of these should generate an "update_checklist_item" operation, and the system will handle creating the item first.

        Other operation examples:
        [
            {{
                "operation": "create",
                "task": "Write documentation",
                "status": "To Do",
                "deadline": "2023-12-01",
                "member": "John"
            }},
            {{
                "operation": "update",
                "task": "Fix login bug",
                "status": "Done"
            }}
        ]

        Example retrospective operations:
        {{
            "operation": "add_reflection_positive",
            "task": "Prepare Investor Deck",
            "items": ["The design layout was well executed", "Team collaboration was excellent"]
        }}
        {{
            "operation": "add_reflection_negative",
            "task": "Prepare Investor Deck",
            "issues": ["ChatGPT did a poor job with image creation for the flyer", "We could have improved our pitch for the investor"],
            "lessons_learned": ["Use Gamma for presentations instead of ChatGPT image creator", "Make sure to practice the pitch and review with a friend before Pitch Day"]
        }}
        {{
            "operation": "create_improvement_task",
            "task_name": "Improve Presentation Process",
            "checklist_items": ["Use Gamma for presentations instead of ChatGPT image creator", "Practice pitch with friend before Pitch Day", "Create template library for future presentations"],
            "description": "The presentation could have been better. We should have practiced the ending segment of the pitch with a strong call to action. Practcing with a friend would have helped us improve our delivery."
        }}

        Do not include any explanations or text outside the JSON array.
        Ensure exact task names are used when referencing existing tasks.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a project management AI. Extract tasks from spoken input. When adding checklist items, prefer adding to existing checklists rather than creating new ones UNLESS the user explicitly requests a 'new checklist'. In that case, use force_new:true. IMPORTANT: When the user asks to delete or remove an item from a checklist, use the delete_checklist_item operation, NOT update_checklist_item. IMPORTANT: The system can handle positional references like 'first checklist' and 'third item', so interpret these correctly when extracting operations. IMPORTANT: When a user asks to add a new item to a checklist AND set its state, use update_checklist_item operation - the system will create the item if needed. Return ONLY valid JSON."},
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
                            print(f"  {i}. Create Label: {op.get('epic', 'unknown')}")
                        elif op_type == "assign_epic":
                            print(f"  {i}. Assign Label: {op.get('task', 'unknown')} to {op.get('epic', 'unknown')}")
                        elif op_type == "assign_member":
                            print(f"  {i}. Assign Member: {op.get('member', 'unknown')} to {op.get('task', 'unknown')}")
                        elif op_type == "remove_member":
                            print(f"  {i}. Remove Member: {op.get('member', 'unknown')} from {op.get('task', 'unknown')}")
                        elif op_type == "create_checklist":  # New checklist operation
                            card_name = op.get("card", "unknown")
                            checklist_name = op.get("checklist", "Checklist")
                            items = op.get("items", [])
                            print(f"  {i}. Create checklist: '{checklist_name}' in '{card_name}' with items: {items}")
                        elif op_type == "delete_checklist_item":
                            card_name = op.get("card", "unknown")
                            checklist_name = op.get("checklist", "Checklist")
                            item_name = op.get("item", "unknown")
                            print(f"  {i}. Delete checklist item: '{item_name}' from '{checklist_name}' in '{card_name}'")
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
