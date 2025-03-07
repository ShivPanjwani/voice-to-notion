# Setup Guide

## Prerequisites Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/voice-to-notion.git
cd voice-to-notion

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## API Configuration

1. Create a `.env` file in the root directory:
```bash
touch .env
```

2. Add your API keys to the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=1969ba40539780f3bb43d57f257d3152
```

To obtain API keys:
- OpenAI API Key: Visit https://platform.openai.com/api-keys
- Notion API Key: Visit https://www.notion.so/my-integrations

## Testing Base Installation

```bash
# Run the application
python main.py

# Test with sample prompt
# When prompted, choose option 2 (paste transcript) and use:
"Create a new task called Test Setup with due date tomorrow"
```

## Development Guidelines

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Test thoroughly
4. Create pull request
