#!/usr/bin/env python3
"""
Voice-to-Notion Task Manager
----------------------------
A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    print("\n" + "=" * 50)
    print("Voice-to-Notion Task Manager")
    print("=" * 50 + "\n")
    
    print("Setting up application...")
    print("This is a placeholder. The full implementation will be added step by step.")
    
    # Check for required environment variables
    required_vars = ["NOTION_API_KEY", "NOTION_DATABASE_ID", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\nError: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in a .env file or in your environment.")
        sys.exit(1)
    
    print("\nAll required environment variables are set.")
    print("Application is ready to be implemented!")

if __name__ == "__main__":
    main()
