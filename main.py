#!/usr/bin/env python3
"""
Voice-to-Task Manager
---------------------------------------------
A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion or Trello.
"""

import os
import sys
from utils.config_manager import ConfigManager
from utils.setup_wizard import run_setup_wizard
from agents.audio_recorder import record_audio
from agents.transcription import transcribe_audio
from agents.task_extractor import extract_tasks
from dotenv import load_dotenv, set_key

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("Voice-to-Task Manager")
    print("=" * 50 + "\n")
    
    # Run setup wizard if .env doesn't exist
    if not os.path.exists(".env"):
        run_setup_wizard()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize config manager
    try:
        config = ConfigManager()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please run the setup wizard again to configure your environment.")
        sys.exit(1)
    
    # Ask user to select task manager
    print("\nSelect your task manager:")
    print("[1] Notion")
    print("[2] Trello")
    
    task_choice = input("\nChoice (default: 1): ").strip()
    
    if task_choice == "2":
        task_manager = "trello"
        # Update the environment variable
        set_key(".env", "TASK_MANAGER", "trello")
        # Reload environment variables
        load_dotenv()
        from api.trello_handler import handle_task_operations, fetch_tasks, format_board_state, fetch_users, fetch_epics
        print("\nUsing Trello as task manager")
    else:
        task_manager = "notion"
        # Update the environment variable
        set_key(".env", "TASK_MANAGER", "notion")
        # Reload environment variables
        load_dotenv()
        from api.notion_handler import handle_task_operations, fetch_tasks, format_board_state, fetch_users, fetch_epics
        print("\nUsing Notion as task manager")
    
    # Main menu
    while True:
        print("\n" + "=" * 50)
        print("Main Menu")
        print("=" * 50)
        choice = input("\nWould you like to:\n[1] Record a meeting (batch processing)\n[2] Enter a live meeting (real-time updates)\n[3] Process a transcript\n[4] Exit\n\nChoice: ")
        
        if choice == "1":
            record_meeting(handle_task_operations)
        elif choice == "2":
            enter_live_meeting()
        elif choice == "3":
            process_transcript(handle_task_operations)
        elif choice == "4":
            print("\nThank you for using Voice-to-Task Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def record_meeting(handle_task_operations):
    """Record a meeting and process it in batch"""
    print("\n" + "=" * 50)
    print("Record a Meeting (Batch Processing)")
    print("=" * 50)
    
    print("\nRecording... Press Ctrl+C to stop.")
    try:
        audio_buffer = record_audio()
        if not audio_buffer:
            print("❌ No audio recorded.")
            return
        
        print("\nTranscribing audio...")
        transcript = transcribe_audio(audio_buffer)
        if not transcript:
            print("❌ Transcription failed.")
            return
        
        print("\nTranscription:")
        print(f"\"{transcript}\"\n")
        
        print("\nExtracting tasks...")
        task_operations = extract_tasks(transcript)
        
        if task_operations:
            # Process task operations
            results = handle_task_operations(task_operations)
            
            # Print formatted summary
            success_count = sum(1 for result in results if result.get("success", False))
            print(f"\n✅ Successfully processed {success_count} of {len(results)} operations.")
        else:
            print("\nNo task operations found in the transcript.")
    
    except KeyboardInterrupt:
        print("\nRecording stopped.")
    except Exception as e:
        print(f"\nError: {str(e)}")

def enter_live_meeting():
    """Enter a live meeting with real-time updates"""
    print("\n" + "=" * 50)
    print("Live Meeting (Real-time Updates)")
    print("=" * 50)
    
    # Import meeting processor here to avoid circular imports
    from agents.meeting_processor import process_meeting
    process_meeting()

def process_transcript(handle_task_operations):
    """Process a transcript from user input"""
    print("\n" + "=" * 50)
    print("Process a Transcript")
    print("=" * 50)
    
    # Get transcript from user
    print("\nPaste your transcript below and press Enter twice when done:")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    transcript = "\n".join(lines)
    
    if not transcript:
        print("❌ No transcript provided.")
        return
    
    # Process the transcript
    print("\nExtracting tasks...")
    task_operations = extract_tasks(transcript)
    
    if task_operations:
        # Process task operations
        results = handle_task_operations(task_operations)
        
        # Print formatted summary
        success_count = sum(1 for result in results if result.get("success", False))
        print(f"\n✅ Successfully processed {success_count} of {len(results)} operations.")
    else:
        print("\nNo task operations found in the transcript.")

if __name__ == "__main__":
    main()