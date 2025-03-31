import os
import sys
from pathlib import Path
from dotenv import load_dotenv

class ConfigManager:
    """Manages configuration and environment variables"""
    
    def __init__(self, env_file=".env"):
        """Initialize the config manager with improved configuration handling"""
        # Load base configuration
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        
        # Store configuration values
        self.notion_api_key = os.getenv("NOTION_API_KEY")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validates that all required configuration values are present"""
        missing_vars = []
        
        if not self.notion_api_key:
            missing_vars.append("NOTION_API_KEY")
        if not self.notion_database_id:
            missing_vars.append("NOTION_DATABASE_ID")
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")
        
        if missing_vars:
            raise ValueError(f"Missing required configuration values: {', '.join(missing_vars)}")
    
    def get_openai_api_key(self):
        """Get the OpenAI API key"""
        return self.openai_api_key
    
    def get_notion_api_key(self):
        """Get the Notion API key"""
        return self.notion_api_key
    
    def get_notion_database_id(self):
        """Get the Notion database ID"""
        return self.notion_database_id
    
    def override(self, **kwargs):
        """Override configuration values at runtime"""
        for key, value in kwargs.items():
            if key == "NOTION_DATABASE_ID":
                self.notion_database_id = value
                os.environ["NOTION_DATABASE_ID"] = value
            elif key == "NOTION_API_KEY":
                self.notion_api_key = value
                os.environ["NOTION_API_KEY"] = value
            elif key == "OPENAI_API_KEY":
                self.openai_api_key = value
                os.environ["OPENAI_API_KEY"] = value

# Add this to make the file runnable for testing
if __name__ == "__main__":
    try:
        config = ConfigManager()
        
        # Test override
        test_db_id = "1c29ba40539780b9bd22d3efa4e7390d"
        config.override(NOTION_DATABASE_ID=test_db_id)
        
        print("✅ ConfigManager test successful")
    except ValueError as e:
        print(f"❌ ConfigManager test failed: {str(e)}")
        print("You can fix this by uncommenting a NOTION_DATABASE_ID in your .env file")
        print("Or by running the following code:")
        print("config = ConfigManager()")
        print("config.override(NOTION_DATABASE_ID=\"your_database_id_here\")")
