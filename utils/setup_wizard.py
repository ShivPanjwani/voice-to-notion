import os
import sys

def run_setup_wizard():
    """
    Runs a setup wizard to help users configure their environment
    """
    print("\n" + "=" * 50)
    print("Voice Task Manager Setup Wizard")
    print("=" * 50 + "\n")
    
    print("This wizard will help you set up your Voice Task Manager environment.")
    print("You'll need to provide API keys for the services you want to use.\n")
    
    # Ask which tools to configure
    print("Which task management tools would you like to configure?")
    print("1. Notion only")
    print("2. Trello only")
    print("3. Both Notion and Trello")
    
    while True:
        choice = input("\nEnter your choice (1/2/3): ")
        if choice in ["1", "2", "3"]:
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Always get OpenAI API key
    openai_api_key = input("\nEnter your OpenAI API key: ")
    
    # Initialize .env content
    env_content = [
        "# OpenAI API credentials",
        f"OPENAI_API_KEY={openai_api_key}",
        ""
    ]
    
    # Configure Notion if selected
    if choice in ["1", "3"]:
        print("\n--- Notion Configuration ---")
        notion_api_key = input("Enter your Notion API key: ")
        notion_database_id = input("Enter your Notion database ID: ")
        
        env_content.extend([
            "# Notion API credentials",
            f"NOTION_API_KEY={notion_api_key}",
            f"NOTION_DATABASE_ID={notion_database_id}",
            ""
        ])
    
    # Configure Trello if selected
    if choice in ["2", "3"]:
        print("\n--- Trello Configuration ---")
        trello_api_key = input("Enter your Trello API key: ")
        trello_token = input("Enter your Trello token: ")
        trello_board_id = input("Enter your Trello board ID: ")
        
        env_content.extend([
            "# Trello API credentials",
            f"TRELLO_API_KEY={trello_api_key}",
            f"TRELLO_TOKEN={trello_token}",
            f"TRELLO_BOARD_ID={trello_board_id}",
            ""
        ])
    
    # Create .env file
    with open(".env", "w") as f:
        f.write("\n".join(env_content))
    
    print("\n✅ Setup complete! Your environment has been configured.")
