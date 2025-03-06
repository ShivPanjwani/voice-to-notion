import os
from dotenv import load_dotenv

class ConfigManager:
    """Manages configuration and API keys for the application"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Check for required environment variables
        self._check_required_vars()
    
    def _check_required_vars(self):
        """Check if all required environment variables are set"""
        required_vars = [
            "OPENAI_API_KEY",
            "NOTION_API_KEY",
            "NOTION_DATABASE_ID"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print("\nError: Missing required environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\nPlease create a .env file based on .env.example and add your API keys.")
            print("See README.md for more information.")
            exit(1)
    
    def get_openai_api_key(self):
        """Get the OpenAI API key"""
        return os.getenv("OPENAI_API_KEY")
    
    def get_notion_api_key(self):
        """Get the Notion API key"""
        return os.getenv("NOTION_API_KEY")
    
    def get_notion_database_id(self):
        """Get the Notion database ID"""
        return os.getenv("NOTION_DATABASE_ID")
