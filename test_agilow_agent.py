#!/usr/bin/env python3
"""
Test script for the Agilow Agent
"""

import os
import sys
import json
from utils.config_manager import ConfigManager
from agents.agilow_agent import AgilowAgent

def main():
    """Main test function"""
    print("\n" + "=" * 50)
    print("Agilow Agent Test")
    print("=" * 50 + "\n")
    
    # Initialize config manager
    try:
        config = ConfigManager()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please check your .env file.")
        sys.exit(1)
    
    # Initialize the Agilow agent
    agent = AgilowAgent()
    
    # Print the greeting
    greeting = agent.generate_greeting()
    print(f"🤖 Agilow: {greeting}\n")
    
    # Test conversation loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nExiting test script. Goodbye!")
            break
        
        # Process the input
        response = agent.process_input(user_input)
        
        # Print the response
        print(f"\n🤖 Agilow: {response['message']}\n")
        
        # Print actions if any
        if response["actions"]:
            print("Actions taken:")
            for action in response["actions"]:
                action_type = action["type"]
                
                if action_type == "task":
                    operation = action.get("operation", "")
                    data = action.get("data", {})
                    
                    if operation == "create":
                        name = data.get("name", "Unnamed Task")
                        status = data.get("status", "Unknown Status")
                        deadline = data.get("deadline", "No deadline")
                        assignee = data.get("assignee", "Unassigned")
                        print(f"  ✅ Created task: '{name}'")
                        print(f"     Status: {status}")
                        if deadline != "No deadline":
                            print(f"     Deadline: {deadline}")
                        if assignee != "Unassigned":
                            print(f"     Assigned to: {assignee}")
                    
                    elif operation == "update":
                        task = data.get("task", "Unknown Task")
                        status = data.get("status", None)
                        deadline = data.get("deadline", None)
                        assignee = data.get("assignee", None)
                        print(f"  ✅ Updated task: '{task}'")
                        if status:
                            print(f"     New status: {status}")
                        if deadline:
                            print(f"     New deadline: {deadline}")
                        if assignee:
                            print(f"     New assignee: {assignee}")
                    
                    elif operation == "delete":
                        task = data.get("task", "Unknown Task")
                        print(f"  ✅ Deleted task: '{task}'")
                    
                    elif operation == "rename":
                        old_name = data.get("old_name", "Unknown Task")
                        new_name = data.get("new_name", "Unknown Task")
                        print(f"  ✅ Renamed task: '{old_name}' → '{new_name}'")
                    
                    elif operation == "comment":
                        task = data.get("task", "Unknown Task")
                        comment = data.get("comment", "No comment")
                        print(f"  ✅ Added comment to '{task}':")
                        print(f"     \"{comment}\"")
                    
                    elif operation in ["create_epic", "assign_epic"]:
                        task = data.get("task", "Unknown Task")
                        epic = data.get("epic", "Unknown Epic")
                        if operation == "create_epic":
                            print(f"  ✅ Created new epic '{epic}' for task '{task}'")
                        else:
                            print(f"  ✅ Assigned epic '{epic}' to task '{task}'")
                
                elif action_type == "retrolog":
                    data = action.get("data", {})
                    team_member = data.get("team_member", "Unknown")
                    went_well = data.get("went_well", "")[:50] + "..." if len(data.get("went_well", "")) > 50 else data.get("went_well", "")
                    didnt_go_well = data.get("didnt_go_well", "")[:50] + "..." if len(data.get("didnt_go_well", "")) > 50 else data.get("didnt_go_well", "")
                    print(f"  ✅ Created retrolog entry for {team_member}:")
                    print(f"     Went well: {went_well}")
                    print(f"     Didn't go well: {didnt_go_well}")
                
                elif action_type == "weekly_summary":
                    data = action.get("data", {})
                    date_range = data.get("date_range", "Unknown date range")
                    completed = data.get("completed_tasks", "")[:50] + "..." if len(data.get("completed_tasks", "")) > 50 else data.get("completed_tasks", "")
                    print(f"  ✅ Created weekly summary for {date_range}:")
                    print(f"     Completed tasks: {completed}")
                
                elif action_type == "execution_insight":
                    data = action.get("data", {})
                    observations = data.get("observations", "")[:50] + "..." if len(data.get("observations", "")) > 50 else data.get("observations", "")
                    recommendations = data.get("recommendations", "")[:50] + "..." if len(data.get("recommendations", "")) > 50 else data.get("recommendations", "")
                    print(f"  ✅ Created execution insight:")
                    print(f"     Observations: {observations}")
                    print(f"     Recommendations: {recommendations}")
            print()
        
        # Check if we should exit
        if response["should_exit"]:
            print("\nAgilow has indicated the conversation should end. Goodbye!")
            break

if __name__ == "__main__":
    main() 