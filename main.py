#!/usr/bin/env python3
"""
Voice-to-Notion Task Manager
----------------------------
A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion.
"""

import os
import sys
from utils.config_manager import ConfigManager
from utils.setup_wizard import run_setup_wizard
from agents.audio_recorder import record_audio
from agents.transcription import transcribe_audio
from agents.task_extractor import extract_tasks
from api.notion_handler import handle_task_operations

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("Voice-to-Notion Task Manager")
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
    
    # Ask user if they want to process a transcript or record a meeting
    while True:
        choice = input("\nDo you want to [1] process a transcript or [2] record a meeting? (1/2): ")
        if choice == "1":
            process_transcript()
            break
        elif choice == "2":
            record_meeting()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

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
    task_operations = extract_tasks(transcript)
    
    if task_operations:
        # Process task operations
        results = handle_task_operations(task_operations)
        
        # Print formatted summary
        print(format_operation_summary(results))
    else:
        print("\nNo task operations found in the transcript.")

def record_meeting():
    """Record and process a meeting"""
    print("\n" + "=" * 50)
    print("Record Meeting")
    print("=" * 50)
    
    # Record audio
    audio_buffer = record_audio()
    
    if audio_buffer:
        print("\nTranscribing audio...")
        transcript = transcribe_audio(audio_buffer)
        
        if transcript:
            print("\n🎯 Processing Tasks from Transcript...")
            
            # Extract tasks from transcript
            print("\nExtracting tasks...")
            task_operations = extract_tasks(transcript)
            
            if task_operations:
                # Process task operations
                results = handle_task_operations(task_operations)
                
                # Print formatted summary
                print(format_operation_summary(results))
            else:
                print("\nNo task operations found in the transcript.")
        else:
            print("\nTranscription failed.")
    else:
        print("\nNo audio recorded. Exiting.")

if __name__ == "__main__":
    main()
