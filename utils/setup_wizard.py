import os
import sys

def run_setup_wizard():
    """Interactive setup wizard for first-time users"""
    print("\n" + "=" * 50)
    print("Voice-to-Notion Setup Wizard")
    print("=" * 50 + "\n")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("Configuration file (.env) already exists.")
        return
    
    print("This wizard will help you set up your API keys.")
    print("You'll need:")
    print("1. An OpenAI API key")
    print("2. A Notion API key")
    print("3. A Notion database ID\n")
    
    # Get API keys from user
    openai_api_key = input("Enter your OpenAI API key: ")
    notion_api_key = input("Enter your Notion API key: ")
    notion_database_id = input("Enter your Notion database ID: ")
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"OPENAI_API_KEY={openai_api_key}\n")
        f.write(f"NOTION_API_KEY={notion_api_key}\n")
        f.write(f"NOTION_DATABASE_ID={notion_database_id}\n")
    
    print("\nConfiguration saved to .env file.")
    print("You're all set to use Voice-to-Notion!")
