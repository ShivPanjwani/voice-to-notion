import os
import sys

def run_setup_wizard():
    """
    Runs a setup wizard to help users configure their environment
    """
    print("\n" + "=" * 50)
    print("Voice-to-Notion Setup Wizard")
    print("=" * 50 + "\n")
    
    print("This wizard will help you set up your Voice-to-Notion environment.")
    print("You'll need to provide your Notion API key, Notion database ID, and OpenAI API key.\n")
    
    notion_api_key = input("Enter your Notion API key: ")
    notion_database_id = input("Enter your Notion database ID: ")
    openai_api_key = input("Enter your OpenAI API key: ")
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"# Notion API credentials\n")
        f.write(f"NOTION_API_KEY={notion_api_key}\n")
        f.write(f"NOTION_DATABASE_ID={notion_database_id}\n\n")
        f.write(f"# OpenAI API credentials\n")
        f.write(f"OPENAI_API_KEY={openai_api_key}\n")
    
    print("\n✅ Setup complete! Your environment has been configured.")
