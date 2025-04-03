#!/usr/bin/env python3
"""
Voice Task Manager
-----------------
A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion or Trello.
"""

import os
import sys
from utils.config_manager import ConfigManager
from utils.setup_wizard import run_setup_wizard
from agents.audio_recorder import record_audio
from agents.transcription import transcribe_audio
from agents.streaming_processor import StreamingMeetingProcessor
from agents.meeting_processor import process_meeting

def select_tool():
    """Ask the user which tool they want to use"""
    print("\n🔧 Task Management Tool Selection")
    print("--------------------------------")
    print("1. Notion")
    print("2. Trello")
    
    while True:
        choice = input("\nSelect a tool (1-2): ").strip()
        if choice == "1":
            return "notion"
        elif choice == "2":
            return "trello"
        else:
            print("❌ Invalid choice. Please select 1 for Notion or 2 for Trello.")

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("Voice Task Manager")
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
    
    # Ask user which tool they want to use
    selected_tool = select_tool()
    
    # Import the appropriate modules based on the selected tool
    if selected_tool == "notion":
        from agents.task_extractor import extract_tasks
        from api.notion_handler import handle_task_operations, format_operation_summary
        print("\n✅ Using Notion for task management")
    else:  # trello
        from agents.task_extractor_trello import extract_tasks_trello as extract_tasks
        from api.trello_handler import handle_task_operations_trello as handle_task_operations
        from api.trello_handler import format_operation_summary_trello as format_operation_summary
        print("\n✅ Using Trello for task management")
    
    # Ask user if they want to process a transcript or record a meeting
    while True:
        print("\nChoose an option:")
        print("1. Process a transcript")
        print("2. Record a meeting (batch processing)")
        print("3. Live streaming meeting (real-time updates)")
        
        choice = input("\nEnter your choice (1/2/3): ")
        
        if choice == "1":
            process_transcript(extract_tasks, handle_task_operations, format_operation_summary)
            break
        elif choice == "2":
            record_meeting(extract_tasks, handle_task_operations, format_operation_summary)
            break
        elif choice == "3":
            stream_meeting(selected_tool)
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def process_transcript(extract_tasks_fn, handle_operations_fn, format_summary_fn):
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
    
    task_operations = extract_tasks_fn(transcript)
    if task_operations:
        # Process task operations
        results = handle_operations_fn(task_operations)
        # Print formatted summary
        print(format_summary_fn(results))
    else:
        print("\nNo task operations found in the transcript.")


def record_meeting(extract_tasks_fn, handle_operations_fn, format_summary_fn):
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
            
            task_operations = extract_tasks_fn(transcript)
            if task_operations:
                # Process task operations
                results = handle_operations_fn(task_operations)
                # Print formatted summary
                print(format_summary_fn(results))
            else:
                print("\nNo task operations found in the transcript.")
        else:
            print("\nTranscription failed.")
    else:
        print("\nNo audio recorded. Exiting.")


def stream_meeting(selected_tool):
    """Stream and process a meeting in real-time"""
    print("\n" + "=" * 50)
    print("Live Streaming Meeting")
    print("=" * 50)
    
    # Initialize the streaming processor with the selected tool
    processor = StreamingMeetingProcessor(tool=selected_tool)
    
    # Start streaming
    processor.start_streaming()


if __name__ == "__main__":
    main()
