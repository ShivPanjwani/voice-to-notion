# api/trello_handler.py
import os
import requests
import json
from datetime import datetime

# Trello API configuration
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD_ID = os.getenv("TRELLO_BOARD_ID")

# Cache for list IDs to avoid repeated API calls
list_id_cache = {}
label_cache = {}
member_cache = {}

def get_auth_params():
    """Return the authentication parameters for Trello API calls"""
    return {
        'key': TRELLO_API_KEY,
        'token': TRELLO_TOKEN
    }

def get_list_id(status):
    """Get the Trello list ID for a given status"""
    # Check cache first
    if status in list_id_cache:
        return list_id_cache[status]
    
    # Map status to expected list names
    status_map = {
        "Not started": "Not started",
        "In Progress": "In Progress",
        "Done": "Done"
    }
    
    list_name = status_map.get(status, status)
    
    # Get all lists on the board
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    response = requests.get(url, params=get_auth_params())
    
    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            # Cache all lists while we're here
            list_id_cache[lst['name']] = lst['id']
            
            if lst['name'] == list_name:
                return lst['id']
    
    print(f"❌ List not found for status: {status}")
    return None

def get_label_id(epic_name):
    """Get or create a label for the given epic name"""
    if epic_name in label_cache:
        return label_cache[epic_name]
    
    # Get all labels on the board
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/labels"
    response = requests.get(url, params=get_auth_params())
    
    if response.status_code == 200:
        labels = response.json()
        for label in labels:
            label_cache[label['name']] = label['id']
            if label['name'] == epic_name:
                return label['id']
        
        # Label doesn't exist, create it
        create_url = "https://api.trello.com/1/labels"
        params = get_auth_params()
        params.update({
            'name': epic_name,
            'color': 'blue',  # Default color
            'idBoard': TRELLO_BOARD_ID
        })
        
        create_response = requests.post(create_url, params=params)
        if create_response.status_code == 200:
            label_id = create_response.json()['id']
            label_cache[epic_name] = label_id
            return label_id
    
    print(f"❌ Failed to get or create label for epic: {epic_name}")
    return None

def get_member_id(username):
    """Get the Trello member ID for a given username"""
    if username in member_cache:
        return member_cache[username]
    
    # Get all members on the board
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/members"
    response = requests.get(url, params=get_auth_params())
    
    if response.status_code == 200:
        members = response.json()
        for member in members:
            # Cache all members
            member_cache[member['username']] = member['id']
            member_cache[member['fullName']] = member['id']
            
            # Check if username matches either username or full name
            if username.lower() == member['username'].lower() or username.lower() == member['fullName'].lower():
                return member['id']
    
    print(f"❌ Member not found: {username}")
    return None

def fetch_tasks():
    """Fetch all cards from the Trello board"""
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    params = get_auth_params()
    params['members'] = 'true'
    params['member_fields'] = 'fullName,username'
    params['labels'] = 'true'
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        cards = response.json()
        tasks = []
        
        # Also fetch lists to get status mapping
        lists_url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
        lists_response = requests.get(lists_url, params=get_auth_params())
        
        list_map = {}
        if lists_response.status_code == 200:
            for lst in lists_response.json():
                list_map[lst['id']] = lst['name']
                list_id_cache[lst['name']] = lst['id']
        
        for card in cards:
            task = {
                "id": card['id'],
                "name": card['name'],
                "status": list_map.get(card['idList'], "Unknown"),
                "url": card['url']
            }
            
            # Add due date if present
            if card.get('due'):
                task['deadline'] = card['due'].split('T')[0]  # Just get the date part
            
            # Add assignee if present
            if card.get('members') and len(card['members']) > 0:
                task['assignee'] = card['members'][0]['fullName']
            
            # Add epic/label if present
            if card.get('labels') and len(card['labels']) > 0:
                task['epic'] = card['labels'][0]['name']
            
            tasks.append(task)
        
        return tasks
    else:
        print(f"❌ Failed to fetch tasks: {response.text}")
        return []

def format_board_state(tasks):
    """Format the board state for display"""
    if not tasks:
        return "No tasks found"
    
    # Group tasks by status
    tasks_by_status = {}
    for task in tasks:
        status = task.get('status', 'Unknown')
        if status not in tasks_by_status:
            tasks_by_status[status] = []
        tasks_by_status[status].append(task)
    
    # Format the output
    output = []
    for status, task_list in tasks_by_status.items():
        output.append(f"{status} ({len(task_list)}):")
        for task in task_list:
            task_info = f"  - {task['name']}"
            
            if task.get('assignee'):
                task_info += f" (Assigned to: {task['assignee']})"
            
            if task.get('deadline'):
                task_info += f" (Due: {task['deadline']})"
            
            if task.get('epic'):
                task_info += f" (Epic: {task['epic']})"
            
            output.append(task_info)
    
    return "\n".join(output)

def fetch_users():
    """Fetch all members from the Trello board"""
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/members"
    response = requests.get(url, params=get_auth_params())
    
    if response.status_code == 200:
        members = response.json()
        users = []
        
        for member in members:
            # Cache member IDs
            member_cache[member['username']] = member['id']
            member_cache[member['fullName']] = member['id']
            
            users.append(member['fullName'])
        
        return users
    else:
        print(f"❌ Failed to fetch users: {response.text}")
        return []

def fetch_epics():
    """Fetch all labels from the Trello board as epics"""
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/labels"
    response = requests.get(url, params=get_auth_params())
    
    if response.status_code == 200:
        labels = response.json()
        epics = []
        
        for label in labels:
            if label['name']:  # Only include labels with names
                label_cache[label['name']] = label['id']
                epics.append(label['name'])
        
        return epics
    else:
        print(f"❌ Failed to fetch epics: {response.text}")
        return []

def create_task(task_data):
    """Create a new card in Trello"""
    url = "https://api.trello.com/1/cards"
    
    # Extract task properties
    task_name = task_data.get('task', 'Untitled Task')
    status = task_data.get('status', 'Not started')
    deadline = task_data.get('deadline')
    assignee = task_data.get('assignee')
    epic = task_data.get('epic')
    
    # Get the list ID for the status
    list_id = get_list_id(status)
    if not list_id:
        print(f"❌ Cannot create task: Invalid status '{status}'")
        return False
    
    # Build the request parameters
    params = get_auth_params()
    params.update({
        'name': task_name,
        'idList': list_id,
        'pos': 'top'  # Place at the top of the list
    })
    
    # Add due date if provided
    if deadline:
        params['due'] = f"{deadline}T12:00:00.000Z"
    
    # Add description if provided
    if task_data.get('description'):
        params['desc'] = task_data['description']
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        card_id = response.json()['id']
        print(f"✅ Created task: {task_name}")
        
        # Add assignee if provided
        if assignee:
            member_id = get_member_id(assignee)
            if member_id:
                member_url = f"https://api.trello.com/1/cards/{card_id}/idMembers"
                member_params = get_auth_params()
                member_params['value'] = member_id
                requests.post(member_url, params=member_params)
        
        # Add epic/label if provided
        if epic:
            label_id = get_label_id(epic)
            if label_id:
                label_url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
                label_params = get_auth_params()
                label_params['value'] = label_id
                requests.post(label_url, params=label_params)
        
        return True
    else:
        print(f"❌ Failed to create task: {response.text}")
        return False

def update_task(task_data):
    """Update a card in Trello"""
    # Find the task by name
    task_name = task_data.get('task')
    if not task_name:
        print(f"❌ No task name provided for update operation")
        return False
    
    # Fetch all cards to find the one with matching name
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    response = requests.get(url, params=get_auth_params())
    
    card_id = None
    if response.status_code == 200:
        cards = response.json()
        for card in cards:
            if card['name'].lower() == task_name.lower():
                card_id = card['id']
                break
    
    if not card_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    # Build the update parameters
    params = get_auth_params()
    update_data = {}
    
    # Update status if provided
    if task_data.get('status'):
        list_id = get_list_id(task_data['status'])
        if list_id:
            update_data['idList'] = list_id
    
    # Update deadline if provided
    if task_data.get('deadline'):
        update_data['due'] = f"{task_data['deadline']}T12:00:00.000Z"
    
    # Update description if provided
    if task_data.get('description'):
        update_data['desc'] = task_data['description']
    
    # Update name if provided (different from task identifier)
    if task_data.get('new_name'):
        update_data['name'] = task_data['new_name']
    
    # Make the update request if we have data to update
    if update_data:
        update_url = f"https://api.trello.com/1/cards/{card_id}"
        params.update(update_data)
        update_response = requests.put(update_url, params=params)
        
        if update_response.status_code != 200:
            print(f"❌ Failed to update task properties: {update_response.text}")
            return False
    
    # Update assignee if provided
    if task_data.get('assignee'):
        member_id = get_member_id(task_data['assignee'])
        if member_id:
            # First, remove existing members
            members_url = f"https://api.trello.com/1/cards/{card_id}/idMembers"
            members_response = requests.get(members_url, params=get_auth_params())
            
            if members_response.status_code == 200:
                current_members = members_response.json()
                for member_id in current_members:
                    remove_url = f"https://api.trello.com/1/cards/{card_id}/idMembers/{member_id}"
                    requests.delete(remove_url, params=get_auth_params())
            
            # Then add the new member
            add_member_url = f"https://api.trello.com/1/cards/{card_id}/idMembers"
            member_params = get_auth_params()
            member_params['value'] = member_id
            member_response = requests.post(add_member_url, params=member_params)
            
            if member_response.status_code != 200:
                print(f"❌ Failed to update assignee: {member_response.text}")
    
    # Update epic/label if provided
    if task_data.get('epic'):
        label_id = get_label_id(task_data['epic'])
        if label_id:
            # First, remove existing labels
            labels_url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
            labels_response = requests.get(labels_url, params=get_auth_params())
            
            if labels_response.status_code == 200:
                current_labels = labels_response.json()
                for label_id in current_labels:
                    remove_url = f"https://api.trello.com/1/cards/{card_id}/idLabels/{label_id}"
                    requests.delete(remove_url, params=get_auth_params())
            
            # Then add the new label
            add_label_url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
            label_params = get_auth_params()
            label_params['value'] = label_id
            label_response = requests.post(add_label_url, params=label_params)
            
            if label_response.status_code != 200:
                print(f"❌ Failed to update epic: {label_response.text}")
    
    print(f"✅ Updated task: {task_name}")
    return True

def delete_task(task_data):
    """Delete a card in Trello"""
    # Find the task by name
    task_name = task_data.get('task')
    if not task_name:
        print(f"❌ No task name provided for delete operation")
        return False
    
    # Fetch all cards to find the one with matching name
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    response = requests.get(url, params=get_auth_params())
    
    card_id = None
    if response.status_code == 200:
        cards = response.json()
        for card in cards:
            if card['name'].lower() == task_name.lower():
                card_id = card['id']
                break
    
    if not card_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    # Delete the card
    delete_url = f"https://api.trello.com/1/cards/{card_id}"
    delete_response = requests.delete(delete_url, params=get_auth_params())
    
    if delete_response.status_code == 200:
        print(f"✅ Deleted task: {task_name}")
        return True
    else:
        print(f"❌ Failed to delete task: {delete_response.text}")
        return False

def rename_task(task_data):
    """Rename a card in Trello"""
    # This is just a special case of update_task
    old_name = task_data.get('old_name')
    new_name = task_data.get('new_name')
    
    if not old_name or not new_name:
        print(f"❌ Both old_name and new_name are required for rename operation")
        return False
    
    update_data = {
        'task': old_name,
        'new_name': new_name
    }
    
    result = update_task(update_data)
    if result:
        print(f"✅ Renamed task: {old_name} → {new_name}")
    
    return result

def add_comment(task_data):
    """Add a comment to a card in Trello"""
    # Find the task by name
    task_name = task_data.get('task')
    comment = task_data.get('comment')
    
    if not task_name or not comment:
        print(f"❌ Both task name and comment are required")
        return False
    
    # Fetch all cards to find the one with matching name
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    response = requests.get(url, params=get_auth_params())
    
    card_id = None
    if response.status_code == 200:
        cards = response.json()
        for card in cards:
            if card['name'].lower() == task_name.lower():
                card_id = card['id']
                break
    
    if not card_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    # Add the comment
    comment_url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    comment_params = get_auth_params()
    comment_params['text'] = comment
    
    comment_response = requests.post(comment_url, params=comment_params)
    
    if comment_response.status_code == 200:
        print(f"✅ Added comment to task: {task_name}")
        return True
    else:
        print(f"❌ Failed to add comment: {comment_response.text}")
        return False

def create_epic(task_data):
    """Create a new label in Trello"""
    epic_name = task_data.get('epic')
    if not epic_name:
        print(f"❌ No epic name provided")
        return False
    
    # Create the label
    url = "https://api.trello.com/1/labels"
    params = get_auth_params()
    params.update({
        'name': epic_name,
        'color': 'blue',  # Default color
        'idBoard': TRELLO_BOARD_ID
    })
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        label_id = response.json()['id']
        label_cache[epic_name] = label_id
        print(f"✅ Created epic: {epic_name}")
        return True
    else:
        print(f"❌ Failed to create epic: {response.text}")
        return False

def assign_epic(task_data):
    """Assign a label to a card in Trello"""
    task_name = task_data.get('task')
    epic_name = task_data.get('epic')
    
    if not task_name or not epic_name:
        print(f"❌ Both task name and epic name are required")
        return False
    
    # Find the task by name
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    response = requests.get(url, params=get_auth_params())
    
    card_id = None
    if response.status_code == 200:
        cards = response.json()
        for card in cards:
            if card['name'].lower() == task_name.lower():
                card_id = card['id']
                break
    
    if not card_id:
        print(f"❌ Task not found: {task_name}")
        return False
    
    # Get or create the label
    label_id = get_label_id(epic_name)
    if not label_id:
        print(f"❌ Failed to get or create label for epic: {epic_name}")
        return False
    
    # Assign the label to the card
    label_url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
    label_params = get_auth_params()
    label_params['value'] = label_id
    
    label_response = requests.post(label_url, params=label_params)
    
    if label_response.status_code == 200:
        print(f"✅ Assigned epic '{epic_name}' to task: {task_name}")
        return True
    else:
        print(f"❌ Failed to assign epic: {label_response.text}")
        return False

def handle_task_operations(operations):
    """Process a list of task operations"""
    results = []
    
    for op in operations:
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
                result['success'] = assign_epic(op)
                result['task'] = op.get('task')
                result['epic'] = op.get('epic')
            
            else:
                print(f"❌ Unknown operation type: {operation_type}")
        
        except Exception as e:
            print(f"❌ Error processing operation {operation_type}: {str(e)}")
        
        results.append(result)
    
    return results