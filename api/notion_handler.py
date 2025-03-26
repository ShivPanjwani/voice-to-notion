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

def handle_task_operations(operations):
    """Process a list of task operations"""
    results = []
    
    # Reorder operations: create_epic first, then create tasks, then other operations
    reordered_operations = []
    
    # First, add all create_epic operations
    for op in operations:
        if op.get("operation") == "create_epic":
            reordered_operations.append(op)
    
    # Then, add all create operations
    for op in operations:
        if op.get("operation") == "create":
            reordered_operations.append(op)
    
    # Finally, add all other operations
    for op in operations:
        if op.get("operation") not in ["create_epic", "create"]:
            reordered_operations.append(op)
    
    for op in reordered_operations:
        operation_type = op.get('operation')
        result = {"operation": operation_type, "success": False}
        
        try:
            if operation_type == 'create':
                result['success'] = create_task(op)
                result['task'] = op.get('task')
            
            elif operation_type == 'update':
                result['success'] = update_task(op)
                result['task'] = op.get('task')
            
            elif operation_type == 'delete':
                result['success'] = delete_task(op)
                result['task'] = op.get('task')
            
            elif operation_type == 'rename':
                result['success'] = rename_task(op)
                result['old_name'] = op.get('old_name')
                result['new_name'] = op.get('new_name')
            
            elif operation_type == 'comment':
                result['success'] = add_comment(op)
                result['task'] = op.get('task')
            
            elif operation_type == 'create_epic':
                result['success'] = create_epic(op)
                result['epic'] = op.get('epic')
            
            elif operation_type == 'assign_epic':
                result['success'] = assign_epic_to_task(op.get('task'), op.get('epic'))
                result['task'] = op.get('task')
                result['epic'] = op.get('epic')
            
            else:
                print(f"❌ Unknown operation type: {operation_type}")
        
        except Exception as e:
            print(f"❌ Error processing operation {operation_type}: {str(e)}")
        
        results.append(result)
    
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

# Add this new function to check if an epic already exists (case-insensitive)
def epic_exists(epic_name):
    """Check if an epic already exists (case-insensitive)"""
    epics = fetch_epics()
    
    # Make the search case-insensitive
    search_name = epic_name.lower().strip()
    
    for epic in epics:
        if epic.lower().strip() == search_name:
            return True, epic  # Return True and the existing epic with correct capitalization
    
    return False, None

# Update the create_epic function
def create_epic(epic_data):
    """Create a new epic in Notion"""
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Get the epic name
    epic_name = epic_data.get('epic')
    if not epic_name:
        print(f"❌ No epic name provided")
        return False
    
    # Standardize epic name to Title Case
    epic_name = ' '.join(word.capitalize() for word in epic_name.split())
    
    # Check if the epic already exists (case-insensitive)
    exists, existing_epic = epic_exists(epic_name)
    if exists:
        print(f"ℹ️ Epic already exists: {existing_epic}")
        return True
    
    # Get database schema to update select options
    url = f"https://api.notion.com/v1/databases/{notion_database_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get database schema: {response.text}")
        return False
    
    database = response.json()
    
    # Find the Select property in the database schema
    select_property_id = None
    select_options = []
    
    for prop_id, prop_data in database.get("properties", {}).items():
        if prop_data.get("type") == "select":
            select_property_id = prop_id
            select_options = prop_data.get("select", {}).get("options", [])
            break
    
    if not select_property_id:
        print("❌ No select property found in database schema")
        return False
    
    # Add the new epic to the select options
    select_options.append({
        "name": epic_name,
        "color": "blue"  # Default color
    })
    
    # Update the database schema with the new select option
    update_url = f"https://api.notion.com/v1/databases/{notion_database_id}"
    update_data = {
        "properties": {
            select_property_id: {
                "select": {
                    "options": select_options
                }
            }
        }
    }
    
    update_response = requests.patch(update_url, headers=headers, json=update_data)
    
    if update_response.status_code >= 200 and update_response.status_code < 300:
        print(f"✅ Created epic: {epic_name}")
        return True
    else:
        print(f"❌ Failed to create epic: {update_response.text}")
        return False