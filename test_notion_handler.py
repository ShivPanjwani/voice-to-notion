#!/usr/bin/env python3
"""
Test script for Notion handler functions
"""

import os
import sys
from utils.config_manager import ConfigManager
from api.notion_handler import (
    create_retrolog_entry,
    fetch_retrolog_entries,
    create_weekly_summary,
    fetch_weekly_summaries,
    create_execution_insight,
    fetch_execution_insights,
    fetch_context_for_agent
)

def test_retrolog_functions():
    """Test retrolog database functions"""
    print("\nTesting Retrolog Functions...")
    
    # Create a test entry - using empty string for team_member to avoid person/user issues
    result = create_retrolog_entry(
        team_member="",  # Empty string to avoid person/user issues
        went_well="Successfully implemented the new feature",
        didnt_go_well="Deployment took longer than expected",
        action_items="Improve deployment automation"
    )
    
    print(f"Create result: {result}")
    
    # Fetch entries
    entries = fetch_retrolog_entries(3)
    print(f"\nFetched {len(entries)} retrolog entries:")
    for entry in entries:
        print(f"- {entry['date']}: {entry['went_well'][:30]}...")

def test_weekly_summary_functions():
    """Test weekly summary database functions"""
    print("\nTesting Weekly Summary Functions...")
    
    # Create a test entry
    result = create_weekly_summary(
        date_range="2023-05-01",
        completed_tasks="Task 1, Task 2, Task 3",
        carryover_tasks="Task 4, Task 5",
        key_metrics="Velocity: 15 points, Bugs: 2",
        weekly_retro_summary="Team is making good progress but needs to focus on quality"
    )
    
    print(f"Create result: {result}")
    
    # Fetch entries
    summaries = fetch_weekly_summaries(3)
    print(f"\nFetched {len(summaries)} weekly summaries:")
    for summary in summaries:
        print(f"- {summary['date_range']}: {summary['completed_tasks'][:30]}...")

def test_execution_insight_functions():
    """Test execution insight database functions"""
    print("\nTesting Execution Insight Functions...")
    
    # Create a test entry
    result = create_execution_insight(
        observations="Team is spending too much time in meetings",
        recommendations="Limit meetings to mornings only",
        progress_metrics="Meeting time: 15 hours/week, Coding time: 20 hours/week"
    )
    
    print(f"Create result: {result}")
    
    # Fetch entries
    insights = fetch_execution_insights(3)
    print(f"\nFetched {len(insights)} execution insights:")
    for insight in insights:
        print(f"- {insight['date']}: {insight['observations'][:30]}...")

def test_context_fetch():
    """Test fetching comprehensive context"""
    print("\nTesting Context Fetch...")
    
    context = fetch_context_for_agent()
    print(f"Context contains:")
    print(f"- {len(context['tasks'])} tasks")
    print(f"- {len(context['retrologs'])} retrolog entries")
    print(f"- {len(context['weekly_summaries'])} weekly summaries")
    print(f"- {len(context['execution_insights'])} execution insights")

def main():
    """Main test function"""
    print("\n" + "=" * 50)
    print("Notion Handler Test Script")
    print("=" * 50 + "\n")
    
    # Initialize config manager
    try:
        config = ConfigManager()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please check your .env file.")
        sys.exit(1)
    
    # Run tests
    while True:
        print("\n" + "=" * 50)
        print("Test Menu")
        print("=" * 50)
        choice = input("\nWhat would you like to test:\n[1] Retrolog Functions\n[2] Weekly Summary Functions\n[3] Execution Insight Functions\n[4] Context Fetch\n[5] All Tests\n[6] Exit\n\nChoice: ")
        
        if choice == "1":
            test_retrolog_functions()
        elif choice == "2":
            test_weekly_summary_functions()
        elif choice == "3":
            test_execution_insight_functions()
        elif choice == "4":
            test_context_fetch()
        elif choice == "5":
            test_retrolog_functions()
            test_weekly_summary_functions()
            test_execution_insight_functions()
            test_context_fetch()
        elif choice == "6":
            print("\nExiting test script. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")

if __name__ == "__main__":
    main() 