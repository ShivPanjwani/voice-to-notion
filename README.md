# Voice-to-Notion Task Manager

A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion.

## Features

- Process meeting transcripts to extract tasks
- Record and process live meetings
- Automatically create tasks in Notion
- Organize tasks by assignee, status, and tags

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `NOTION_API_KEY`: Your Notion API key
   - `NOTION_DATABASE_ID`: Your Notion database ID
   - `OPENAI_API_KEY`: Your OpenAI API key
4. Run the application: `python main.py`

## Usage

Follow the prompts in the terminal to either:
- Process a meeting transcript
- Record and process a live meeting
