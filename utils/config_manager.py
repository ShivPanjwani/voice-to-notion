import os
from dotenv import load_dotenv

class ConfigManager:
    """Manages configuration and environment variables"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Get required environment variables
        self.notion_api_key = os.getenv("NOTION_API_KEY")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        self.notion_retrolog_database_id = os.getenv("NOTION_RETROLOG_DATABASE_ID")
        self.notion_weekly_history_database_id = os.getenv("NOTION_WEEKLY_HISTORY_DATABASE_ID")
        self.notion_execution_insights_database_id = os.getenv("NOTION_EXECUTION_INSIGHTS_DATABASE_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate required environment variables
        self._validate_config()
        
        # Set OpenAI API key for use in other modules
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
    
    def _validate_config(self):
        """Validates that all required configuration values are present"""
        missing_vars = []
        
        if not self.notion_api_key:
            missing_vars.append("NOTION_API_KEY")
        if not self.notion_database_id:
            missing_vars.append("NOTION_DATABASE_ID")
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")
        
        # These are optional for backward compatibility
        # but we'll warn if they're missing
        optional_vars = []
        if not self.notion_retrolog_database_id:
            optional_vars.append("NOTION_RETROLOG_DATABASE_ID")
        if not self.notion_weekly_history_database_id:
            optional_vars.append("NOTION_WEEKLY_HISTORY_DATABASE_ID")
        if not self.notion_execution_insights_database_id:
            optional_vars.append("NOTION_EXECUTION_INSIGHTS_DATABASE_ID")
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file.")
        
        if optional_vars:
            print(f"Warning: Missing optional environment variables: {', '.join(optional_vars)}. Some features may be limited.")
    
    def get_openai_api_key(self):
        """Get the OpenAI API key"""
        return self.openai_api_key
    
    def get_notion_api_key(self):
        """Get the Notion API key"""
        return self.notion_api_key
    
    def get_notion_database_id(self):
        """Get the Notion database ID"""
        return self.notion_database_id
    
    def get_notion_retrolog_database_id(self):
        """Get the Notion retrolog database ID"""
        return self.notion_retrolog_database_id
    
    def get_notion_weekly_history_database_id(self):
        """Get the Notion weekly history database ID"""
        return self.notion_weekly_history_database_id
    
    def get_notion_execution_insights_database_id(self):
        """Get the Notion execution insights database ID"""
        return self.notion_execution_insights_database_id
