#!/usr/bin/env python3
"""
Voice-to-Notion Task Manager
----------------------------
A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion.
"""

import os
import sys
import openai
from utils.config_manager import ConfigManager
from utils.setup_wizard import run_setup_wizard
from agents.audio_recorder import record_audio

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("Voice-to-Notion Task Manager")
    print("=" * 50 + "\n")
    
    # Run setup wizard if .env doesn't exist
    if not os.path.exists(".env"):
        run_setup_wizard()
    
    # Initialize config manager
    config = ConfigManager()
    
    # Set up OpenAI API key
    openai.api_key = config.get_openai_api_key()
    
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

def process_transcript():
    """Process an existing transcript"""
    print("\n" + "=" * 50)
    print("Process Transcript")
    print("=" * 50)
    
    # Get transcript from user
    transcript_path = input("\nEnter the path to your transcript file: ")
    
    try:
        with open(transcript_path, 'r') as f:
            transcript = f.read()
        
        print("\nTranscript loaded successfully.")
        print("\nThis feature is not yet implemented.")
        # TODO: Implement transcript processing
        
    except FileNotFoundError:
        print(f"\nError: File '{transcript_path}' not found.")
    except Exception as e:
        print(f"\nError: {str(e)}")

def record_meeting():
    """Record and process a meeting"""
    print("\n" + "=" * 50)
    print("Record Meeting")
    print("=" * 50)
    
    # Record audio
    audio_buffer = record_audio()
    
    if audio_buffer:
        print("\nTranscribing audio...")
        # TODO: Implement audio transcription
        print("\nThis feature is not yet implemented.")
    else:
        print("\nNo audio recorded. Exiting.")

if __name__ == "__main__":
    main()
