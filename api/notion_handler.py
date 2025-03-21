# api/notion_handler.py
import requests
import json
import os
from datetime import datetime

def fetch_tasks():
    """Fetch all tasks from Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"❌ Error fetching tasks: {response.text}")
        return []

def fetch_users():
    """Fetch all users from Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = "https://api.notion.com/v1/users"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        users = {}
        for user in response.json().get("results", []):
            users[user["name"]] = user["id"]
        return users
    else:
        print(f"❌ Error fetching users: {response.text}")
        return {}

def format_board_state(tasks):
    """Format current board state for GPT"""
    # First, get all users
    users = fetch_users()
    
    board_state = "Current Board State:\n\n"
    
    # Add available assignees section
    board_state += "Available Team Members:\n"
    for user_name in users.keys():
        board_state += f"- {user_name}\n"
    
    board_state += "\nCurrent Tasks:\n"
    statuses = {"Not started": [], "In Progress": [], "Done": []}
    
    # Group tasks by status
    for task in tasks:
        status = task["properties"]["Status"]["status"]["name"]
        name = task["properties"]["Name"]["title"][0]["text"]["content"]
        
        # Get assignee
        assignee = None
        if "Assign" in task["properties"] and task["properties"]["Assign"]["people"]:
            assignee = task["properties"]["Assign"]["people"][0]["name"]
        
        # Get deadline
        deadline = "No deadline"
        if "Deadline" in task["properties"] and task["properties"]["Deadline"] is not None:
            date_obj = task["properties"]["Deadline"].get("date")
            if date_obj:
                deadline = date_obj.get("start", "No deadline")
            
        statuses[status].append((name, assignee, deadline))
    
    # Format tasks by status
    for status, tasks in statuses.items():
        board_state += f"\n{status}:\n"
        for name, assignee, deadline in tasks:
            assignee_text = f", Assigned to: {assignee}" if assignee else ""
            board_state += f"- {name}{assignee_text} (Due: {deadline})\n"
    
    return board_state

def fetch_epics():
    """Fetch all existing epics from Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code >= 200 and response.status_code < 300:
        results = response.json().get("results", [])
        epics = set()
        
        for page in results:
            if "Select" in page["properties"] and page["properties"]["Select"].get("select"):
                epic = page["properties"]["Select"]["select"].get("name")
                if epic:
                    epics.add(epic)
        
        return list(epics)
    
    return []

def get_epic_colors():
    """Get all colors used by existing epics"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code >= 200 and response.status_code < 300:
        results = response.json().get("results", [])
        used_colors = set()
        
        for page in results:
            if "Select" in page["properties"] and page["properties"]["Select"].get("select"):
                color = page["properties"]["Select"]["select"].get("color")
                if color:
                    used_colors.add(color)
        
        return list(used_colors)
    
    return []

def get_unique_color(used_colors):
    """Get a unique color not used by existing epics"""
    all_colors = [
        "default", "gray", "brown", "orange", "yellow", 
        "green", "blue", "purple", "pink", "red"
    ]
    
    available_colors = [color for color in all_colors if color not in used_colors]
    
    if available_colors:
        return available_colors[0]  # Return the first available color
    else:
        return "default"  # If all colors are used, default to "default"

def assign_epic_to_task(task_name, epic_name):
    """Assign an existing epic to a task"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Find the task by name
    page_id = find_task_by_name(task_name)
    
    if not page_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    data = {
        "properties": {
            "Select": {
                "select": {
                    "name": epic_name
                }
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Assigned epic '{epic_name}' to task: {task_name}")
        return True
    else:
        print(f"❌ Failed to assign epic: {response.text}")
        return False

def create_epic_for_task(task_name, epic_name):
    """Create a new epic and assign it to a task"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Find the task by name
    page_id = find_task_by_name(task_name)
    
    if not page_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    # Get used colors to avoid duplicates
    used_colors = get_epic_colors()
    unique_color = get_unique_color(used_colors)
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    data = {
        "properties": {
            "Select": {
                "select": {
                    "name": epic_name,
                    "color": unique_color
                }
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Created new epic '{epic_name}' with color '{unique_color}' and assigned to task: {task_name}")
        return True
    else:
        print(f"❌ Failed to create epic: {response.text}")
        return False

def handle_task_operations(task_operations):
    """Process task operations in Notion"""
    results = []
    
    for operation in task_operations:
        op_type = operation.get('operation', '').lower()
        
        try:
            if op_type == 'create':
                success = create_task(operation)
                results.append({
                    "operation": "create",
                    "task": operation.get('task', 'Unknown'),
                    "success": success,
                    "details": "Task created successfully" if success else "Failed to create task"
                })
            
            elif op_type == 'update':
                success = update_task(operation)
                results.append({
                    "operation": "update",
                    "task": operation.get('task', 'Unknown'),
                    "success": success,
                    "details": "Task updated successfully" if success else "Failed to update task"
                })
            
            elif op_type == 'delete':
                success = delete_task(operation)
                results.append({
                    "operation": "delete",
                    "task": operation.get('task', 'Unknown'),
                    "success": success,
                    "details": "Task deleted successfully" if success else "Failed to delete task"
                })
            
            elif op_type == 'comment':
                success = add_comment(operation)
                results.append({
                    "operation": "comment",
                    "task": operation.get('task', 'Unknown'),
                    "success": success,
                    "details": "Comment added successfully" if success else "Failed to add comment"
                })
            
            elif op_type == 'rename':
                success = rename_task(operation)
                results.append({
                    "operation": "rename",
                    "task": operation.get('old_name', 'Unknown'),
                    "success": success,
                    "details": "Task renamed successfully" if success else "Failed to rename task"
                })
            
            elif op_type == 'create_epic':
                success = create_epic_for_task(operation.get('task'), operation.get('epic'))
                results.append({
                    "operation": "create_epic",
                    "task": operation.get('task', 'Unknown'),
                    "epic": operation.get('epic', 'Unknown'),
                    "success": success,
                    "details": "Epic created and assigned successfully" if success else "Failed to create epic"
                })
            
            elif op_type == 'assign_epic':
                success = assign_epic_to_task(operation.get('task'), operation.get('epic'))
                results.append({
                    "operation": "assign_epic",
                    "task": operation.get('task', 'Unknown'),
                    "epic": operation.get('epic', 'Unknown'),
                    "success": success,
                    "details": "Epic assigned successfully" if success else "Failed to assign epic"
                })
            
            else:
                print(f"❌ Unknown operation type: {op_type}")
                results.append({
                    "operation": op_type,
                    "task": operation.get('task', 'Unknown'),
                    "success": False,
                    "details": "Unknown operation type"
                })
            
        except Exception as e:
            print(f"❌ Error processing operation {op_type}: {str(e)}")
            results.append({
                "operation": op_type,
                "task": operation.get('task', operation.get('old_name', 'Unknown')),
                "success": False,
                "error": str(e),
                "details": "Operation failed"
            })
    
    return results

def create_task(task_data):
    """Create a new task in Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = "https://api.notion.com/v1/pages"
    
    # Prepare the request data
    data = {
        "parent": {"database_id": notion_database_id},
        "properties": {
            "Name": {
                "title": [{"text": {"content": task_data.get('task', 'Untitled Task')}}]
            },
            "Status": {
                "status": {"name": task_data.get('status', 'Not started')}
            }
        }
    }
    
    # Add deadline if provided
    if 'deadline' in task_data and task_data['deadline']:
        data["properties"]["Deadline"] = {
            "date": {"start": task_data['deadline']}
        }
    
    # Add assignee if provided and user exists
    if 'assignee' in task_data and task_data['assignee']:
        users = fetch_users()
        user_id = users.get(task_data['assignee'])
        if user_id:
            data["properties"]["Assign"] = {
                "people": [{"id": user_id}]
            }
        else:
            print(f"⚠️ User not found: {task_data['assignee']}")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Created task: {task_data.get('task')}")
        return True
    else:
        print(f"❌ Failed to create task: {response.text}")
        return False

def update_task(task_data):
    """Update an existing task in Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # First, find the task by name
    task_name = task_data.get('task')
    page_id = find_task_by_name(task_name)
    
    if not page_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # Prepare properties to update
    properties = {}
    
    if 'status' in task_data:
        properties["Status"] = {"status": {"name": task_data['status']}}
    
    if 'deadline' in task_data and task_data['deadline']:
        properties["Deadline"] = {"date": {"start": task_data['deadline']}}
    
    if 'assignee' in task_data and task_data['assignee']:
        users = fetch_users()
        user_id = users.get(task_data['assignee'])
        if user_id:
            properties["Assign"] = {"people": [{"id": user_id}]}
            print(f"✅ Updating assignee to: {task_data['assignee']}")
        else:
            print(f"⚠️ Could not find user ID for {task_data['assignee']}")
    
    data = {"properties": properties}
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Updated task: {task_name}")
        return True
    else:
        print(f"❌ Failed to update task: {response.text}")
        return False

def delete_task(task_data):
    """Delete (archive) a task from Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Find the task by name
    task_name = task_data.get('task')
    page_id = find_task_by_name(task_name)
    
    if not page_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # Archive the page
    data = {"archived": True}
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Archived task: {task_name}")
        return True
    else:
        print(f"❌ Failed to archive task: {response.text}")
        return False

def add_comment(task_data):
    """Add a comment to a task in Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Find the task by name
    task_name = task_data.get('task')
    page_id = find_task_by_name(task_name)
    
    if not page_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    url = "https://api.notion.com/v1/comments"
    
    data = {
        "parent": {"page_id": page_id},
        "rich_text": [
            {
                "type": "text",
                "text": {"content": task_data.get('comment', '')}
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Added comment to task: {task_name}")
        return True
    else:
        print(f"❌ Failed to add comment: {response.text}")
        return False

def rename_task(task_data):
    """Rename a task in Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Find the task by old name
    old_name = task_data.get('old_name')
    if not old_name:
        print(f"❌ No old name provided for rename operation")
        return False
        
    page_id = find_task_by_name(old_name)
    
    if not page_id:
        print(f"❌ Task not found: {old_name}")
        return False
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # Update the task name
    data = {
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": task_data.get('new_name', 'Untitled Task')
                        }
                    }
                ]
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"✅ Renamed task: {old_name} → {task_data.get('new_name')}")
        return True
    else:
        print(f"❌ Failed to rename task: {response.text}")
        return False

def find_task_by_name(task_name):
    """Find a task by name and return its page ID"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    
    # Query for the task by name
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code >= 200 and response.status_code < 300:
        results = response.json().get("results", [])
        
        # Make the search case-insensitive
        search_name = task_name.lower().strip()
        
        for page in results:
            title_property = page["properties"]["Name"]["title"]
            if title_property:
                current_name = title_property[0]["text"]["content"].lower().strip()
                if current_name == search_name:
                    return page["id"]
                # Add fuzzy matching for better results
                elif search_name in current_name or current_name in search_name:
                    return page["id"]
    
    return None