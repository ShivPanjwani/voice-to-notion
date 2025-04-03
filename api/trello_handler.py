# api/trello_handler.py
import requests
import json
import os
from datetime import datetime, timedelta
import random

def fetch_cards():
    """Fetch all cards from Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    
    url = f"https://api.trello.com/1/boards/{trello_board_id}/cards"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch cards: {response.text}")
        return []

def fetch_lists():
    """Fetch all lists from Trello board"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    
    url = f"https://api.trello.com/1/boards/{trello_board_id}/lists"
    
    query = {
        'key': trello_api_key,
        'token': trello_token,
        'fields': 'name,id'
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error fetching lists: {response.text}")
        return []

def fetch_board_members():
    """Fetch all members of the Trello board"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    
    url = f"https://api.trello.com/1/boards/{trello_board_id}/members"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch board members: {response.text}")
        return []

def fetch_labels():
    """Fetch all labels from the Trello board"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    
    url = f"https://api.trello.com/1/boards/{trello_board_id}/labels"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        labels = response.json()
        return [label.get('name') for label in labels if label.get('name')]
    else:
        print(f"❌ Failed to fetch labels: {response.text}")
        return []

def format_board_state(cards):
    """Format the current board state for the AI prompt"""
    if not cards:
        return "No cards found on the board."
    
    formatted_cards = []
    for card in cards:
        card_info = {
            "name": card.get("name", "Unnamed Card"),
            "description": card.get("desc", "No description"),
            "status": get_list_name_by_id(card.get("idList", "")),
            "due_date": card.get("due", "No due date"),
            "labels": [label.get("name", "Unnamed Label") for label in card.get("labels", [])]
        }
        formatted_cards.append(card_info)
    
    return json.dumps(formatted_cards, indent=2)

def get_list_name_by_id(list_id):
    """Get the name of a list by its ID"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    url = f"https://api.trello.com/1/lists/{list_id}"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        return response.json().get("name", "Unknown List")
    else:
        return "Unknown List"

def get_list_id_by_name(list_name):
    """Get the ID of a list by its name"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    
    url = f"https://api.trello.com/1/boards/{trello_board_id}/lists"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            if lst.get("name", "").lower() == list_name.lower():
                return lst.get("id")
        
        # If no exact match, try partial match
        for lst in lists:
            if list_name.lower() in lst.get("name", "").lower():
                return lst.get("id")
        
        return None
    else:
        print(f"❌ Failed to fetch lists: {response.text}")
        return None

def find_card_by_name(card_name):
    """Find a card by its name"""
    cards = fetch_cards()
    
    for card in cards:
        if card.get("name", "").lower() == card_name.lower():
            return card.get("id")
    
    # If no exact match, try partial match
    for card in cards:
        if card_name.lower() in card.get("name", "").lower():
            return card.get("id")
    
    return None

def get_full_board_id():
    """Get the full board ID from the short ID in the URL"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    short_board_id = os.getenv("TRELLO_BOARD_ID")
    
    # Try to get the full board ID from the short ID
    url = f"https://api.trello.com/1/boards/{short_board_id}"
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    try:
        response = requests.get(url, params=query)
        if response.status_code == 200:
            board_data = response.json()
            full_id = board_data.get('id')
            print(f"✅ Retrieved full board ID: {full_id}")
            return full_id
        else:
            print(f"❌ Failed to get full board ID: {response.text}")
            return short_board_id  # Fall back to short ID if we can't get the full ID
    except Exception as e:
        print(f"❌ Exception getting full board ID: {str(e)}")
        return short_board_id  # Fall back to short ID if we can't get the full ID

def find_label_by_name(label_name):
    """Find a label by its name"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    
    url = f"https://api.trello.com/1/boards/{trello_board_id}/labels"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.get(url, params=query)
    
    if response.status_code == 200:
        labels = response.json()
        
        for label in labels:
            if label.get("name", "").lower() == label_name.lower():
                return label.get("id")
        
        # If no exact match, try partial match
        for label in labels:
            if label_name.lower() in label.get("name", "").lower():
                return label.get("id")
        
        return None
    else:
        print(f"❌ Failed to fetch labels: {response.text}")
        return None

def create_label(label_data):
    """Create a new label in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Extract the label name from the data
    label_name = label_data.get('epic')
    if not label_name:
        print("❌ No label name provided")
        return False
    
    # Get the full board ID
    full_board_id = get_full_board_id()
    if not full_board_id:
        print("❌ Could not get full board ID")
        return False
    
    # Select a random color
    color = random.choice(['yellow', 'purple', 'blue', 'red', 'green', 'orange', 'black', 'sky', 'pink', 'lime'])
    
    # Create a label on the board
    url = "https://api.trello.com/1/labels"
    
    query = {
        'name': label_name,
        'color': color,
        'idBoard': full_board_id,
        'key': trello_api_key,
        'token': trello_token
    }
    
    try:
        response = requests.request("POST", url, params=query)
        
        if response.status_code == 200:
            print(f"✅ Created label: {label_name}")
            return True
        else:
            print(f"❌ Failed to create label: {response.text}")
            print(f"❌ Response status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception creating label: {str(e)}")
        return False

def add_label_to_card(card_id, label_id):
    """Add a label to a card"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    url = f"https://api.trello.com/1/cards/{card_id}/idLabels"
    
    query = {
        'key': trello_api_key,
        'token': trello_token,
        'value': label_id
    }
    
    response = requests.request("POST", url, params=query)
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to add label to card: {response.text}")
        return False

def remove_label_from_card(card_id, label_id):
    """Remove a label from a card"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    url = f"https://api.trello.com/1/cards/{card_id}/idLabels/{label_id}"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.delete(url, params=query)
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to remove label from card: {response.text}")
        return False

def assign_label_to_card(task_data):
    """Assign a label to a card in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Find the card by name
    card_id = find_card_by_name(task_data.get('task', ''))
    
    if not card_id:
        print(f"❌ Card not found: {task_data.get('task')}")
        return False
    
    # Find the label by name
    label_name = task_data.get('epic', '')
    label_id = find_label_by_name(label_name)
    
    if not label_id:
        # Create the label if it doesn't exist
        create_label_result = create_label({'epic': label_name})
        if create_label_result:
            # Try to find the newly created label
            label_id = find_label_by_name(label_name)
            if not label_id:
                print(f"❌ Could not find or create label: {label_name}")
                return False
        else:
            print(f"❌ Could not create label: {label_name}")
            return False
    
    # Add the label to the card
    add_label_to_card(card_id, label_id)
    return True

def create_card(task_data):
    """Create a new card in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Get the list ID for the status
    status = task_data.get('status', 'Not started')
    list_id = get_list_id_by_name(status)
    
    if not list_id:
        print(f"❌ List not found for status: {status}")
        # Try with alternative names as fallbacks
        fallback_names = ['To Do', 'Not Started', 'Backlog', 'Todo']
        for fallback in fallback_names:
            list_id = get_list_id_by_name(fallback)
            if list_id:
                print(f"✅ Using '{fallback}' list instead")
                break
        
        if not list_id:
            return False
    
    # Create the card
    url = "https://api.trello.com/1/cards"
    
    query = {
        'key': trello_api_key,
        'token': trello_token,
        'idList': list_id,
        'name': task_data.get('task', 'Unnamed Task'),
        'desc': task_data.get('description', '')
    }
    
    # Add due date if provided
    if 'due_date' in task_data:
        # Check if the date is already in ISO format
        if 'T' in task_data['due_date'] and 'Z' in task_data['due_date']:
            # Already in ISO format, adjust timezone
            query['due'] = adjust_timezone_for_trello(task_data['due_date'])
        else:
            try:
                # Parse the due date
                due_date = datetime.strptime(task_data['due_date'], "%Y-%m-%d")
                # Format for Trello API
                query['due'] = due_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            except ValueError:
                print(f"❌ Invalid due date format: {task_data['due_date']}")
    elif 'deadline' in task_data:
        # Check if the date is already in ISO format
        if 'T' in task_data['deadline'] and 'Z' in task_data['deadline']:
            # Already in ISO format, adjust timezone
            query['due'] = adjust_timezone_for_trello(task_data['deadline'])
        else:
            try:
                # Parse the deadline
                due_date = datetime.strptime(task_data['deadline'], "%Y-%m-%d")
                # Format for Trello API
                query['due'] = due_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            except ValueError:
                print(f"❌ Invalid deadline format: {task_data['deadline']}")
    
    response = requests.post(url, params=query)
    
    if response.status_code == 200:
        card_id = response.json().get('id')
        
        # Assign label if provided
        if 'epic' in task_data and task_data['epic']:
            assign_label_to_card({
                'task': task_data.get('task', 'Unnamed Task'),
                'epic': task_data['epic']
            })
        
        # Add comment if provided
        if 'comment' in task_data and task_data['comment']:
            add_comment_to_card({
                'task': task_data.get('task', 'Unnamed Task'),
                'comment': task_data['comment']
            })
        
        return True
    else:
        print(f"❌ Failed to create card: {response.text}")
        return False

def update_card(task_data):
    """Update a card in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Find the card by name
    card_id = find_card_by_name(task_data.get('task', ''))
    
    if not card_id:
        print(f"❌ Card not found: {task_data.get('task')}")
        return False
    
    # Update the card
    url = f"https://api.trello.com/1/cards/{card_id}"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    # Add fields to update
    if 'description' in task_data:
        query['desc'] = task_data['description']
    
    if 'status' in task_data:
        list_id = get_list_id_by_name(task_data['status'])
        if list_id:
            query['idList'] = list_id
        else:
            print(f"❌ List not found for status: {task_data['status']}")
    
    # Check for due_date (from task extractor) or deadline (alternative name)
    if 'due_date' in task_data:
        # Check if the date is already in ISO format
        if 'T' in task_data['due_date'] and 'Z' in task_data['due_date']:
            # Already in ISO format, adjust timezone
            query['due'] = adjust_timezone_for_trello(task_data['due_date'])
        else:
            try:
                # Parse the due date
                due_date = datetime.strptime(task_data['due_date'], "%Y-%m-%d")
                # Format for Trello API
                query['due'] = due_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            except ValueError:
                print(f"❌ Invalid due date format: {task_data['due_date']}")
    elif 'deadline' in task_data:
        # Check if the date is already in ISO format
        if 'T' in task_data['deadline'] and 'Z' in task_data['deadline']:
            # Already in ISO format, adjust timezone
            query['due'] = adjust_timezone_for_trello(task_data['deadline'])
        else:
            try:
                # Parse the deadline
                due_date = datetime.strptime(task_data['deadline'], "%Y-%m-%d")
                # Format for Trello API
                query['due'] = due_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            except ValueError:
                print(f"❌ Invalid deadline format: {task_data['deadline']}")
    
    response = requests.put(url, params=query)
    
    if response.status_code == 200:
        # Assign label if provided
        if 'epic' in task_data and task_data['epic']:
            assign_label_to_card({
                'task': task_data.get('task', ''),
                'epic': task_data['epic']
            })
        
        # Add comment if provided
        if 'comment' in task_data and task_data['comment']:
            add_comment_to_card({
                'task': task_data.get('task', ''),
                'comment': task_data['comment']
            })
        
        return True
    else:
        print(f"❌ Failed to update card: {response.text}")
        return False

def add_comment_to_card(task_data):
    """Add a comment to a card in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Find the card by name
    card_id = find_card_by_name(task_data.get('task', ''))
    
    if not card_id:
        print(f"❌ Card not found: {task_data.get('task')}")
        return False
    
    # Add comment to the card
    url = f"https://api.trello.com/1/cards/{card_id}/actions/comments"
    
    query = {
        'key': trello_api_key,
        'token': trello_token,
        'text': task_data.get('comment', '')
    }
    
    response = requests.post(url, params=query)
    
    if response.status_code == 200:
        print(f"✅ Added comment to card: {task_data.get('task')}")
        return True
    else:
        print(f"❌ Failed to add comment: {response.text}")
        return False

def delete_card(task_data):
    """Delete a card in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Find the card by name
    card_id = find_card_by_name(task_data.get('task', ''))
    
    if not card_id:
        print(f"❌ Card not found: {task_data.get('task')}")
        return False
    
    # Delete the card
    url = f"https://api.trello.com/1/cards/{card_id}"
    
    query = {
        'key': trello_api_key,
        'token': trello_token
    }
    
    response = requests.delete(url, params=query)
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to delete card: {response.text}")
        return False

def rename_card(task_data):
    """Rename a card in Trello"""
    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    
    # Find the card by name
    card_id = find_card_by_name(task_data.get('old_name', ''))
    
    if not card_id:
        print(f"❌ Card not found: {task_data.get('old_name')}")
        return False
    
    # Rename the card
    url = f"https://api.trello.com/1/cards/{card_id}"
    
    query = {
        'key': trello_api_key,
        'token': trello_token,
        'name': task_data.get('new_name', '')
    }
    
    response = requests.put(url, params=query)
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to rename card: {response.text}")
        return False

def handle_task_operations_trello(task_operations):
    """Handle task operations for Trello"""
    results = []
    
    for operation in task_operations:
        op_type = operation.get('operation')
        
        if op_type == 'create':
            success = create_card(operation)
            results.append({
                'operation': 'create',
                'task': operation.get('task'),
                'success': success
            })
        elif op_type == 'update':
            success = update_card(operation)
            results.append({
                'operation': 'update',
                'task': operation.get('task'),
                'success': success
            })
        elif op_type == 'delete':
            success = delete_card(operation)
            results.append({
                'operation': 'delete',
                'task': operation.get('task'),
                'success': success
            })
        elif op_type == 'rename':
            success = rename_card(operation)
            results.append({
                'operation': 'rename',
                'old_name': operation.get('old_name'),
                'new_name': operation.get('new_name'),
                'success': success
            })
        elif op_type == 'create_epic':
            success = create_label(operation)
            results.append({
                'operation': 'create_epic',
                'epic': operation.get('epic'),
                'success': success
            })
        elif op_type == 'assign_epic':
            success = assign_label_to_card(operation)
            results.append({
                'operation': 'assign_epic',
                'task': operation.get('task'),
                'epic': operation.get('epic'),
                'success': success
            })
        elif op_type == 'comment':
            success = add_comment_to_card(operation)
            results.append({
                'operation': 'comment',
                'task': operation.get('task'),
                'success': success
            })
        else:
            print(f"⚠️ Unknown operation type: {op_type}")
            results.append({
                'operation': op_type,
                'success': False,
                'error': 'Unknown operation type'
            })
    
    return results

def format_operation_summary_trello(results):
    """Format a summary of the operations performed"""
    if not results:
        return "No operations performed."
    
    success_count = sum(1 for result in results if result.get('success', False))
    
    summary = f"\n✅ Successfully processed {success_count} of {len(results)} operations.\n"
    
    for result in results:
        operation = result.get('operation', '')
        success = result.get('success', False)
        
        if operation == 'create':
            status = "✅" if success else "❌"
            summary += f"\n{status} Created task: '{result.get('task', '')}'"
        elif operation == 'update':
            status = "✅" if success else "❌"
            summary += f"\n{status} Updated task: '{result.get('task', '')}'"
        elif operation == 'delete':
            status = "✅" if success else "❌"
            summary += f"\n{status} Deleted task: '{result.get('task', '')}'"
        elif operation == 'rename':
            status = "✅" if success else "❌"
            summary += f"\n{status} Renamed task: '{result.get('old_name', '')}' to '{result.get('new_name', '')}'"
        elif operation == 'create_epic':
            status = "✅" if success else "❌"
            summary += f"\n{status} Created label: '{result.get('epic', '')}'"
        elif operation == 'assign_epic':
            status = "✅" if success else "❌"
            summary += f"\n{status} Assigned label '{result.get('epic', '')}' to task: '{result.get('task', '')}'"
        elif operation == 'comment':
            status = "✅" if success else "❌"
            summary += f"\n{status} Added comment to task: '{result.get('task', '')}'"
    
    return summary

def fetch_context_for_agent_trello():
    """Fetch context data from Trello for the Agilow agent"""
    try:
        # Fetch cards (tasks)
        cards = fetch_cards()
        
        # Get lists to map card status
        lists = fetch_lists()
        list_map = {list_item['id']: list_item['name'] for list_item in lists}
        
        # Map Trello lists to standardized statuses
        status_map = {}
        for list_item in lists:
            name = list_item['name'].lower()
            if 'done' in name or 'complete' in name:
                status_map[list_item['id']] = "Done"
            elif 'progress' in name or 'doing' in name or 'working' in name:
                status_map[list_item['id']] = "In Progress"
            else:
                status_map[list_item['id']] = "Not started"
        
        # Format cards as tasks
        tasks = []
        for card in cards:
            task = {
                "id": card['id'],
                "name": card['name'],
                "status": status_map.get(card['idList'], "To Do"),
                "list": list_map.get(card['idList'], "Unknown"),
                "due_date": card['due'].split('T')[0] if card['due'] else None,
                "url": card['url']
            }
            tasks.append(task)
        
        # For now, we'll return a simplified context
        # In a full implementation, you might want to add more data types
        return {
            "tasks": tasks,
            "retrologs": [],  # Not implemented for Trello
            "weekly_summaries": [],  # Not implemented for Trello
            "execution_insights": []  # Not implemented for Trello
        }
        
    except Exception as e:
        print(f"❌ Error fetching context for agent: {str(e)}")
        return {
            "tasks": [],
            "retrologs": [],
            "weekly_summaries": [],
            "execution_insights": []
        }

def adjust_timezone_for_trello(iso_date_string):
    """
    Adjust the timezone in an ISO date string for Trello.
    If the string contains 'T' and 'Z', it's already in ISO format.
    This function will adjust the time to account for timezone differences.
    """
    if 'T' in iso_date_string and 'Z' in iso_date_string:
        # Parse the ISO date string
        try:
            # Remove the Z and parse
            dt = datetime.strptime(iso_date_string.replace('Z', ''), "%Y-%m-%dT%H:%M:%S.000")
            
            # Add 4 hours to adjust for EDT timezone (UTC-4)
            # You may need to adjust this offset based on your timezone
            dt = dt + timedelta(hours=4)
            
            # Format back to ISO with Z
            return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except ValueError:
            print(f"⚠️ Could not parse ISO date: {iso_date_string}")
            return iso_date_string
    return iso_date_string