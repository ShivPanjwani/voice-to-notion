#!/usr/bin/env python3
"""
Voice-to-Notion Task Manager with Scrum Master
---------------------------------------------
A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion.
"""

import os
import sys
from utils.config_manager import ConfigManager
from utils.setup_wizard import run_setup_wizard
from agents.audio_recorder import record_audio
from agents.transcription import transcribe_audio
from agents.scrum_master import process_input
from api.notion_handler import handle_task_operations

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("Voice-to-Notion Task Manager with Scrum Master")
    print("=" * 50 + "\n")
    
    # Run setup wizard if .env doesn't exist
    if not os.path.exists(".env"):
        run_setup_wizard()
    
    # Initialize config manager
    try:
        config = ConfigManager()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please run the setup wizard again to configure your environment.")
        sys.exit(1)
    
    # Main menu loop
    conversation_history = None
    while True:
        print("\n" + "=" * 50)
        print("Main Menu")
        print("=" * 50)
        choice = input("\nWould you like to:\n[1] Talk to your Scrum Master\n[2] Enter a meeting\n[3] Process a transcript\n[4] Exit\n\nChoice: ")
        
        if choice == "1":
            conversation_history = talk_to_scrum_master(conversation_history)
        elif choice == "2":
            enter_meeting()
        elif choice == "3":
            process_transcript()
        elif choice == "4":
            print("\nThank you for using Voice-to-Notion Task Manager with Scrum Master. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def talk_to_scrum_master(conversation_history=None):
    """Interactive conversation with the Scrum Master"""
    print("\n" + "=" * 50)
    print("Talk to Your Scrum Master")
    print("=" * 50)
    
    if conversation_history is None:
        print("\n🤖 Scrum Master: Hello! I'm your Scrum Master. How can I help you today?")
        conversation_history = []
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'back']:
            break
        
        # Process the user input
        task_operations, conversation_history = process_input(user_input, conversation_history=conversation_history)
        
        if task_operations:
            print("🤖 Scrum Master: I've made the changes to your board. Would you like to verify and make any additional changes, or are we done for now?")
            verify_or_finalize = input("\nYou: ")
            
            if any(word in verify_or_finalize.lower() for word in ['no', 'done', 'finalize', 'finish', 'complete', 'exit', 'that\'s all', 'goodbye']):
                print("\n🤖 Scrum Master: Great! Your board is updated. Come back anytime you need assistance!")
                break
            else:
                print("\n🤖 Scrum Master: Let's continue. What additional changes would you like to make?")
    
    return conversation_history

def enter_meeting():
    """Enter a specific meeting type"""
    print("\n" + "=" * 50)
    print("Enter a Meeting")
    print("=" * 50)
    
    while True:
        meeting_type = input("\nWhat type of meeting would you like to have?\n[1] Stand-up Meeting\n[2] Planning Meeting\n[3] Back to Main Menu\n\nChoice: ")
        
        if meeting_type == "1":
            conduct_standup_meeting()
            break
        elif meeting_type == "2":
            conduct_planning_meeting()
            break
        elif meeting_type == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def conduct_standup_meeting():
    """Conduct a stand-up meeting"""
    print("\n" + "=" * 50)
    print("Stand-up Meeting")
    print("=" * 50)
    
    print("\n🤖 Scrum Master: Let's have our stand-up meeting. Please tell me:")
    print("1. What did you accomplish since the last meeting?")
    print("2. What are you planning to do today?")
    print("3. Are there any blockers in your way?")
    
    # Record audio
    print("\nPress spacebar to start recording, and press it again to stop.")
    audio_buffer = record_audio()
    
    if audio_buffer:
        print("\nTranscribing audio...")
        transcript = transcribe_audio(audio_buffer)
        
        if transcript:
            print("\nTranscription:")
            print(f"\"{transcript}\"\n")
            
            # Process with the Scrum Master
            task_operations, conversation_history = process_input(transcript, meeting_type="standup")
            
            if task_operations:
                # Process task operations
                results = handle_task_operations(task_operations)
                
                # Print formatted summary
                print(format_operation_summary(results))
                
                # Ask if user wants to verify or finalize
                print("\n🤖 Scrum Master: I've updated your board based on our stand-up. Is there anything else you'd like to discuss or should we wrap up?")
                verify_or_finalize = input("\nYou: ")
                
                # Check if user wants to finalize
                if any(word in verify_or_finalize.lower() for word in ['wrap up', 'done', 'finalize', 'finish', 'complete', 'exit', 'that\'s all', 'goodbye']):
                    print("\n🤖 Scrum Master: Great stand-up! I've updated your tasks. Have a productive day, and I'll see you at the next stand-up!")
            else:
                print("\nNo task operations found in the stand-up.")
        else:
            print("\nTranscription failed.")
    else:
        print("\nNo audio recorded. Exiting.")

def conduct_planning_meeting():
    """Conduct a planning meeting"""
    print("\n" + "=" * 50)
    print("Planning Meeting")
    print("=" * 50)
    
    print("\n🤖 Scrum Master: Let's plan our work. Please tell me about the tasks you want to work on in the coming week.")
    
    # Record audio
    print("\nPress spacebar to start recording, and press it again to stop.")
    audio_buffer = record_audio()
    
    if audio_buffer:
        print("\nTranscribing audio...")
        transcript = transcribe_audio(audio_buffer)
        
        if transcript:
            print("\nTranscription:")
            print(f"\"{transcript}\"\n")
            
            # Process with the Scrum Master
            task_operations, conversation_history = process_input(transcript, meeting_type="planning")
            
            if task_operations:
                # Process task operations
                results = handle_task_operations(task_operations)
                
                # Print formatted summary
                print(format_operation_summary(results))
                
                # Ask if user wants to verify or finalize
                print("\n🤖 Scrum Master: I've updated your board with the planned tasks. Would you like to review the plan or are we good to go?")
                verify_or_finalize = input("\nYou: ")
                
                # Check if user wants to finalize
                if any(word in verify_or_finalize.lower() for word in ['good to go', 'done', 'finalize', 'finish', 'complete', 'exit', 'that\'s all', 'goodbye']):
                    print("\n🤖 Scrum Master: Great planning session! Your tasks are all set up. Let's have a productive week ahead!")
            else:
                print("\nNo task operations found in the planning meeting.")
        else:
            print("\nTranscription failed.")
    else:
        print("\nNo audio recorded. Exiting.")

def format_operation_summary(results):
    """Format operation results into a clean summary"""
    if not results:
        return "No operations performed."
    
    success_count = sum(1 for result in results if result.get("success", False))
    
    summary = f"\n✅ Successfully performed {success_count} of {len(results)} operations:\n"
    
    for result in results:
        task_name = result.get("task", "Unknown task")
        operation = result.get("operation", "unknown")
        success = result.get("success", False)
        
        # Format the operation description
        if operation == "create":
            description = "New task created"
        elif operation == "update":
            description = "Task updated"
        elif operation == "delete":
            description = "Task deleted"
        elif operation == "comment":
            description = "Comment added"
        elif operation == "rename":
            description = "Task renamed"
        elif operation == "create_epic":
            description = f"Epic created: {result.get('epic', 'Unknown')}"
        elif operation == "assign_epic":
            description = f"Assigned to epic: {result.get('epic', 'Unknown')}"
        else:
            description = f"Unknown operation: {operation}"
        
        # Add status indicator
        status = "✅" if success else "❌"
        
        summary += f"{status} {task_name} - {description}\n"
    
    return summary

def process_transcript():
    """Process an existing transcript"""
    print("\n" + "=" * 50)
    print("Process Transcript")
    print("=" * 50)
    
    # Ask user for input method
    while True:
        choice = input("\nDo you want to [1] provide a file path or [2] paste the transcript directly? (1/2): ")
        if choice == "1":
            # Get transcript from file
            transcript_path = input("\nEnter the path to your transcript file: ")
            try:
                with open(transcript_path, 'r') as f:
                    transcript = f.read()
                print("\nTranscript loaded successfully.")
            except FileNotFoundError:
                print(f"\nError: File '{transcript_path}' not found.")
                return
            except Exception as e:
                print(f"\nError: {str(e)}")
                return
            break
        elif choice == "2":
            # Get transcript from user input
            print("\nPaste your transcript below and press Enter twice when done:")
            lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            transcript = "\n".join(lines)
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    # Process the transcript
    print("\nExtracting tasks...")
    task_operations, conversation_history = process_input(transcript)
    
    if task_operations:
        # Process task operations
        results = handle_task_operations(task_operations)
        
        # Print formatted summary
        print(format_operation_summary(results))
        
        # Ask if user wants to verify or finalize
        print("\n🤖 Scrum Master: I've processed the transcript and updated your board. Is there anything else you'd like me to do with this information?")
        verify_or_finalize = input("\nYou: ")
        
        # Check if user wants to finalize
        if any(word in verify_or_finalize.lower() for word in ['no', 'done', 'finalize', 'finish', 'complete', 'exit', 'that\'s all', 'goodbye']):
            print("\n🤖 Scrum Master: Great! Your transcript has been processed and your board is updated. Come back anytime you need assistance!")
    else:
        print("\nNo task operations found in the transcript.")

if __name__ == "__main__":
    main()
