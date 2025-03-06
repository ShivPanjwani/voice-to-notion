# Voice-to-Notion Task Manager

A tool that extracts tasks from meeting transcripts or live meetings and adds them to Notion.

## Features

- Record audio from meetings and transcribe in real-time
- Process existing meeting transcripts to extract tasks
- Automatically identify tasks, deadlines, and assignees
- Create and update tasks in Notion with proper organization
- Support for custom columns including "Outreach" tasks

## Setup for Contributors

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/voice-to-notion.git
   cd voice-to-notion
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file with your API keys
   nano .env  # or use any text editor
   ```

5. Run the application
   ```bash
   python main.py
   ```

## Required API Keys

You'll need the following API keys:

1. **OpenAI API Key**: For transcription and task extraction
   - Sign up at https://platform.openai.com/
   - Create an API key in your account settings

2. **Notion API Key**: For creating and updating tasks
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Grant it access to your task database

3. **Notion Database ID**: To identify your task database
   - Open your Notion database in a browser
   - The ID is in the URL: https://www.notion.so/workspace/[database-id]?v=...

## Usage

The application offers two main modes:

1. **Process Transcript**: Upload an existing meeting transcript to extract tasks
2. **Live Meeting**: Record a meeting in real-time and extract tasks as you go

Follow the prompts in the terminal interface to use either mode.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
