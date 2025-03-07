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

## Notion Setup
1. Create a Notion account if you don't have one
2. Duplicate our template board: [Notion Template](https://veiled-basin-65e.notion.site/1969ba40539780f3bb43d57f257d3152?v=1969ba405397819fad37000c36773c94&pvs=4)
   - Click "Duplicate" in the top right corner
   - Select a workspace to copy to

3. Create a Notion integration:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Name it "Voice-to-Notion"
   - Copy the API key

4. Connect your board to the integration:
   - Open your duplicated board
   - Click "..." in the top right
   - Select "Add connections"
   - Choose your "Voice-to-Notion" integration

5. Get your database ID:
   - In your duplicated board, click "Share" in top right
   - Copy the link
   - The database ID is the string of characters between the last "/" and "?"
   - Example: from "workspace/1234abcd..." the ID would be "1234abcd"

## Environment Setup
1. Create a `.env` file in the root directory:
```bash
touch .env
```

2. Add your API keys to the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
```

## Testing Your Setup
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
