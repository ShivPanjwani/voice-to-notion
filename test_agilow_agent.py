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
                # Get the operation type
                operation = action.get("operation", "unknown")
                
                # Handle different operation types
                if operation == "create":
                    task = action.get("task", "Unnamed Task")
                    status = action.get("status", "Unknown Status")
                    deadline = action.get("deadline", "No deadline")
                    assignee = action.get("assignee", "Unassigned")
                    print(f"  ✅ Created task: '{task}'")
                    print(f"     Status: {status}")
                    if deadline and deadline != "No deadline":
                        print(f"     Deadline: {deadline}")
                    if assignee and assignee != "Unassigned":
                        print(f"     Assigned to: {assignee}")
                
                elif operation == "update":
                    task = action.get("task", "Unknown Task")
                    status = action.get("status", None)
                    deadline = action.get("deadline", None)
                    assignee = action.get("assignee", None)
                    print(f"  ✅ Updated task: '{task}'")
                    if status:
                        print(f"     New status: {status}")
                    if deadline:
                        print(f"     New deadline: {deadline}")
                    if assignee:
                        print(f"     New assignee: {assignee}")
                
                elif operation == "delete":
                    task = action.get("task", "Unknown Task")
                    print(f"  ✅ Deleted task: '{task}'")
                
                elif operation == "rename":
                    old_name = action.get("old_name", "Unknown Task")
                    new_name = action.get("new_name", "Unknown Task")
                    print(f"  ✅ Renamed task: '{old_name}' → '{new_name}'")
                
                elif operation == "comment":
                    task = action.get("task", "Unknown Task")
                    comment = action.get("comment", "No comment")
                    print(f"  ✅ Added comment to '{task}':")
                    print(f"     \"{comment}\"")
                
                elif operation in ["create_epic", "assign_epic"]:
                    task = action.get("task", "Unknown Task")
                    epic = action.get("epic", "Unknown Epic")
                    if operation == "create_epic":
                        print(f"  ✅ Created new epic '{epic}' for task '{task}'")
                    else:
                        print(f"  ✅ Assigned epic '{epic}' to task '{task}'")
                
                elif operation == "create_retrolog":
                    team_member = action.get("team_member", "Unknown")
                    went_well = action.get("went_well", "")[:50] + "..." if len(action.get("went_well", "")) > 50 else action.get("went_well", "")
                    didnt_go_well = action.get("didnt_go_well", "")[:50] + "..." if len(action.get("didnt_go_well", "")) > 50 else action.get("didnt_go_well", "")
                    print(f"  ✅ Created retrolog entry for {team_member}:")
                    print(f"     Went well: {went_well}")
                    print(f"     Didn't go well: {didnt_go_well}")
                
                elif operation == "create_weekly_summary":
                    date_range = action.get("date_range", "Unknown date range")
                    completed = action.get("completed_tasks", "")[:50] + "..." if len(action.get("completed_tasks", "")) > 50 else action.get("completed_tasks", "")
                    print(f"  ✅ Created weekly summary for {date_range}:")
                    print(f"     Completed tasks: {completed}")
                
                elif operation == "create_execution_insight":
                    observations = action.get("observations", "")[:50] + "..." if len(action.get("observations", "")) > 50 else action.get("observations", "")
                    recommendations = action.get("recommendations", "")[:50] + "..." if len(action.get("recommendations", "")) > 50 else action.get("recommendations", "")
                    print(f"  ✅ Created execution insight:")
                    print(f"     Observations: {observations}")
                    print(f"     Recommendations: {recommendations}")
                
                else:
                    print(f"  ❓ Unknown operation: {operation}")
            print()
        
        # Check if we should exit
        if response["should_exit"]:
            print("\nAgilow has indicated the conversation should end. Goodbye!")
            break

if __name__ == "__main__":
    main() 