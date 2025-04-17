# Save this as app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Voice-to-Task Management System",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: white;
        background: linear-gradient(to right, #4880EC, #019CAD);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 1.8rem;
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 7px;
        margin: 2rem 0 1rem 0;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 5px solid #4880EC;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        font-style: italic;
        border-top: 1px solid #ddd;
    }
    .highlight {
        background-color: #f0f7fb;
        border-left: 5px solid #4880EC;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown('<div class="main-header">🎤 Voice-to-Task Management System<br><span style="font-size: 1.2rem">Transform spoken words into organized action</span></div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
pages = [
    "Overview",
    "System Architecture",
    "Process Flow",
    "Supported Operations",
    "Retrospective Feature",
    "Example Workflow",
    "Challenges & Solutions",
    "Future Enhancements"
]
selection = st.sidebar.radio("Go to", pages)

# Overview page
if selection == "Overview":
    st.markdown("## System Overview")
    
    st.markdown("""
    <div class="info-box">
    The Voice-to-Task Management System is a cutting-edge solution that transforms spoken commands into organized tasks in project management tools. 
    By leveraging advanced speech recognition and natural language processing, it enables users to manage projects hands-free.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Key Features")
        st.markdown("""
        - **Speech-to-Text Conversion** using OpenAI Whisper
        - **Intelligent Task Extraction** powered by GPT-4
        - **Multi-platform Integration** with Trello and Notion
        - **Retrospective Analysis** for continuous improvement
        - **Natural Language Interface** for intuitive interaction
        """)
    
    with col2:
        st.markdown("### Benefits")
        st.markdown("""
        - **Increased Productivity** through hands-free task management
        - **Improved Accessibility** for users with different needs
        - **Enhanced Collaboration** with seamless integration
        - **Reduced Context Switching** between tools
        - **Continuous Improvement** through retrospective features
        """)
    
    st.markdown("### How It Works")
    st.image("https://via.placeholder.com/800x400?text=Voice+to+Task+Workflow", caption="Voice-to-Task Workflow Overview")

# System Architecture page
elif selection == "System Architecture":
    st.markdown('<div class="section-header">System Architecture</div>', unsafe_allow_html=True)
    
    # Function to create system architecture diagram using matplotlib
    def create_system_architecture():
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#f8f9fa')
        
        # Define node positions
        nodes = {
            'audio': (0.1, 0.5),
            'transcriber': (0.3, 0.5),
            'task_extractor': (0.5, 0.5),
            'trello_handler': (0.7, 0.7),
            'notion_handler': (0.7, 0.3),
            'trello': (0.9, 0.7),
            'notion': (0.9, 0.3)
        }
        
        # Define node labels
        labels = {
            'audio': 'Audio Input',
            'transcriber': 'Speech Transcriber\n(OpenAI Whisper)',
            'task_extractor': 'Task Extractor Agent\n(GPT-4)',
            'trello_handler': 'Trello API Handler',
            'notion_handler': 'Notion API Handler',
            'trello': 'Trello Board',
            'notion': 'Notion Database'
        }
        
        # Define node colors
        colors = {
            'audio': '#6ab7ff',
            'transcriber': '#56c2e6',
            'task_extractor': '#4dd4ac',
            'trello_handler': '#7986cb',
            'notion_handler': '#64b5f6',
            'trello': '#9575cd',
            'notion': '#4fc3f7'
        }
        
        # Draw nodes
        for node, pos in nodes.items():
            rect = patches.FancyBboxPatch(
                (pos[0]-0.08, pos[1]-0.05), 0.16, 0.1,
                linewidth=1, edgecolor='black', facecolor=colors[node], alpha=0.8,
                boxstyle=patches.BoxStyle("Round", pad=0.03), clip_on=False
            )
            ax.add_patch(rect)
            ax.text(pos[0], pos[1], labels[node], ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Draw edges
        # Audio to transcriber
        ax.annotate("", 
                    xy=(nodes['transcriber'][0]-0.08, nodes['transcriber'][1]), 
                    xytext=(nodes['audio'][0]+0.08, nodes['audio'][1]),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['audio'][0]+nodes['transcriber'][0])/2, 
                nodes['audio'][1]+0.03, 'Audio file/stream', 
                ha='center', va='center', fontsize=8)
        
        # Transcriber to task_extractor
        ax.annotate("", 
                    xy=(nodes['task_extractor'][0]-0.08, nodes['task_extractor'][1]), 
                    xytext=(nodes['transcriber'][0]+0.08, nodes['transcriber'][1]),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['transcriber'][0]+nodes['task_extractor'][0])/2, 
                nodes['transcriber'][1]+0.03, 'Text transcription', 
                ha='center', va='center', fontsize=8)
        
        # Task extractor to trello_handler
        ax.annotate("", 
                    xy=(nodes['trello_handler'][0]-0.08, nodes['trello_handler'][1]), 
                    xytext=(nodes['task_extractor'][0]+0.08, nodes['task_extractor'][1]),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['task_extractor'][0]+nodes['trello_handler'][0])/2, 
                (nodes['task_extractor'][1]+nodes['trello_handler'][1])/2+0.03, 
                'Task operations (JSON)', ha='center', va='center', fontsize=8)
        
        # Task extractor to notion_handler
        ax.annotate("", 
                    xy=(nodes['notion_handler'][0]-0.08, nodes['notion_handler'][1]), 
                    xytext=(nodes['task_extractor'][0]+0.08, nodes['task_extractor'][1]),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['task_extractor'][0]+nodes['notion_handler'][0])/2, 
                (nodes['task_extractor'][1]+nodes['notion_handler'][1])/2-0.03, 
                'Task operations (JSON)', ha='center', va='center', fontsize=8)
        
        # Draw remaining edges
        for start, end in [('trello_handler', 'trello'), ('notion_handler', 'notion')]:
            ax.annotate("", 
                        xy=(nodes[end][0]-0.08, nodes[end][1]), 
                        xytext=(nodes[start][0]+0.08, nodes[start][1]),
                        arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
            ax.text((nodes[start][0]+nodes[end][0])/2, 
                    nodes[start][1]+0.03, 'API requests', 
                    ha='center', va='center', fontsize=8)
        
        for start, end in [('trello', 'trello_handler'), ('notion', 'notion_handler')]:
            ax.annotate("", 
                        xy=(nodes[end][0]+0.08, nodes[end][1]-0.02), 
                        xytext=(nodes[start][0]-0.08, nodes[start][1]-0.02),
                        arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
            ax.text((nodes[start][0]+nodes[end][0])/2, 
                    nodes[start][1]-0.03, 'Board state', 
                    ha='center', va='center', fontsize=8)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    # Display the architecture diagram
    st.pyplot(create_system_architecture())
    
    st.markdown("""
    <div class="highlight">
    <strong>System Components:</strong>
    <ul>
        <li><strong>Audio Input:</strong> Captures user's voice commands</li>
        <li><strong>Speech Transcriber:</strong> Converts speech to text using OpenAI Whisper</li>
        <li><strong>Task Extractor Agent:</strong> Analyzes text to extract task operations using GPT-4</li>
        <li><strong>API Handlers:</strong> Convert operations to API-specific calls</li>
        <li><strong>Task Management Platforms:</strong> Trello and Notion where tasks are created and managed</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Process Flow page
elif selection == "Process Flow":
    st.markdown('<div class="section-header">Process Flow</div>', unsafe_allow_html=True)
    
    # Function to create data flow diagram
    def create_data_flow():
        fig, ax = plt.subplots(figsize=(8, 12), facecolor='#f8f9fa')
        
        # Define node positions (vertical flow)
        nodes = {
            'input': (0.5, 0.95),
            'whisper': (0.5, 0.85),
            'text': (0.5, 0.75),
            'gpt4': (0.5, 0.65),
            'json': (0.5, 0.55),
            'api_handler': (0.5, 0.45),
            'api_calls': (0.5, 0.35),
            'board': (0.5, 0.25),
            'feedback': (0.5, 0.15)
        }
        
        # Define node labels
        labels = {
            'input': 'User Voice Input\n"Create a task to update documentation"',
            'whisper': 'Whisper Transcription\nConverts speech to text',
            'text': 'Text Transcription\n"Create a task to update documentation"',
            'gpt4': 'GPT-4 Task Extraction\nParses intent and extracts operations',
            'json': 'JSON Operations\n{"operation": "create", "task": "Update documentation", "status": "To Do"}',
            'api_handler': 'API Handler\nConverts operations to API calls',
            'api_calls': 'API Requests\nPOST /cards with name, status, etc.',
            'board': 'Task Board\nUpdated with new task',
            'feedback': 'User Feedback\n"✅ Created: Update documentation"'
        }
        
        # Define node colors
        colors = {
            'input': '#bbdefb',
            'whisper': '#90caf9',
            'text': '#64b5f6',
            'gpt4': '#42a5f5',
            'json': '#2196f3',
            'api_handler': '#1e88e5',
            'api_calls': '#1976d2',
            'board': '#1565c0',
            'feedback': '#0d47a1'
        }
        
        # Draw nodes
        for node, pos in nodes.items():
            rect = patches.FancyBboxPatch(
                (pos[0]-0.2, pos[1]-0.04), 0.4, 0.08,
                linewidth=1, edgecolor='black', facecolor=colors[node], alpha=0.7,
                boxstyle=patches.BoxStyle("Round", pad=0.03), clip_on=False
            )
            ax.add_patch(rect)
            ax.text(pos[0], pos[1], labels[node], ha='center', va='center', fontsize=9, color='black')
        
        # Draw edges
        for i in range(len(nodes)-1):
            start_node = list(nodes.keys())[i]
            end_node = list(nodes.keys())[i+1]
            ax.annotate("", 
                        xy=(nodes[end_node][0], nodes[end_node][1]+0.04), 
                        xytext=(nodes[start_node][0], nodes[start_node][1]-0.04),
                        arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0.1, 1)
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    # Display the data flow diagram
    st.pyplot(create_data_flow())
    
    st.markdown("""
    <div class="highlight">
    <strong>Process Steps:</strong>
    <ol>
        <li>User speaks a command into the system</li>
        <li>Speech is transcribed to text using OpenAI Whisper</li>
        <li>Text is analyzed by GPT-4 to extract task operations</li>
        <li>Operations are converted to JSON format</li>
        <li>API handlers translate operations to platform-specific API calls</li>
        <li>API requests are sent to task management platforms</li>
        <li>Task boards are updated with new information</li>
        <li>User receives confirmation feedback</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

# Supported Operations page
elif selection == "Supported Operations":
    st.markdown('<div class="section-header">Supported Operations</div>', unsafe_allow_html=True)
    
    # Create a table of operation types
    operations = [
        ["create", "Create a new task", "Create a task to update documentation"],
        ["update", "Update task status", "Mark the documentation task as done"],
        ["delete", "Delete a task", "Delete the documentation task"],
        ["rename", "Rename a task", "Rename 'Update docs' to 'Update API documentation'"],
        ["comment", "Add a comment", "Add a comment to the documentation task"],
        ["create_epic", "Create a label/epic", "Create a new label called 'Documentation'"],
        ["assign_epic", "Assign label to task", "Add the Documentation label to the API task"],
        ["assign_member", "Assign member", "Assign John to the documentation task"],
        ["remove_member", "Remove member", "Remove John from the documentation task"],
        ["create_checklist", "Create checklist", "Add a checklist to the documentation task"],
        ["update_checklist_item", "Update checklist item", "Mark 'Update README' as complete"],
        ["delete_checklist_item", "Delete checklist item", "Remove 'Update README' from the checklist"],
        ["add_reflection_positive", "Add positive reflection", "What went well with the documentation task"],
        ["add_reflection_negative", "Add negative reflection", "What didn't go well with the documentation task"],
        ["create_improvement_task", "Create improvement task", "Create tasks based on lessons learned"]
    ]
    
    df = pd.DataFrame(operations, columns=['Operation', 'Description', 'Example'])
    st.dataframe(df, use_container_width=True, height=500)
    
    # Example JSON operations
    st.markdown("### Example JSON Operations")
    
    with st.expander("Create Task Example"):
        st.code("""
{
    "operation": "create",
    "task": "Write documentation",
    "status": "To Do",
    "deadline": "2023-12-01",
    "member": "John"
}
        """, language="json")
    
    with st.expander("Update Task Example"):
        st.code("""
{
    "operation": "update",
    "task": "Fix login bug",
    "status": "Done"
}
        """, language="json")
    
    with st.expander("Create Checklist Example"):
        st.code("""
{
    "operation": "create_checklist",
    "card": "Design new landing page",
    "checklist": "To-Do List",
    "items": ["Research competitors", "Create wireframes", "Review with team"]
}
        """, language="json")

# Retrospective Feature page
elif selection == "Retrospective Feature":
    st.markdown('<div class="section-header">Retrospective Feature</div>', unsafe_allow_html=True)
    
    st.markdown("""
    The retrospective feature allows teams to reflect on their work, identify what went well, what didn't go well,
    and create actionable improvement tasks based on lessons learned.
    """)
    
    # Function to create retrospective flow diagram
    def create_retrospective_flow():
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#f8f9fa')
        
        # Define node positions
        nodes = {
            'task': (0.5, 0.8),
            'positive': (0.2, 0.6),
            'negative': (0.8, 0.6),
            'lessons': (0.8, 0.4),
            'improvement': (0.5, 0.2)
        }
        
        # Define node labels
        labels = {
            'task': 'Original Task',
            'positive': 'What\'s Going Well?',
            'negative': 'What\'s Not Going Well?',
            'lessons': 'Lessons Learned',
            'improvement': 'Improvement Tasks'
        }
        
        # Define node colors
        colors = {
            'task': '#bbdefb',
            'positive': '#a5d6a7',
            'negative': '#ffcc80',
            'lessons': '#fff59d',
            'improvement': '#ef9a9a'
        }
        
        # Draw nodes
        for node, pos in nodes.items():
            rect = patches.FancyBboxPatch(
                (pos[0]-0.15, pos[1]-0.05), 0.3, 0.1,
                linewidth=1, edgecolor='black', facecolor=colors[node], alpha=0.7,
                boxstyle=patches.BoxStyle("Round", pad=0.03), clip_on=False
            )
            ax.add_patch(rect)
            ax.text(pos[0], pos[1], labels[node], ha='center', va='center', fontsize=10)
        
        # Draw edges
        ax.annotate("", 
                    xy=(nodes['positive'][0]+0.15, nodes['positive'][1]), 
                    xytext=(nodes['task'][0]-0.05, nodes['task'][1]-0.05),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['task'][0]+nodes['positive'][0])/2-0.05, 
                (nodes['task'][1]+nodes['positive'][1])/2, 
                'Positive reflections', ha='center', va='center', fontsize=8)
        
        ax.annotate("", 
                    xy=(nodes['negative'][0]-0.15, nodes['negative'][1]), 
                    xytext=(nodes['task'][0]+0.05, nodes['task'][1]-0.05),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['task'][0]+nodes['negative'][0])/2+0.05, 
                (nodes['task'][1]+nodes['negative'][1])/2, 
                'Challenges', ha='center', va='center', fontsize=8)
        
        ax.annotate("", 
                    xy=(nodes['lessons'][0], nodes['lessons'][1]+0.05), 
                    xytext=(nodes['negative'][0], nodes['negative'][1]-0.05),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text(nodes['negative'][0], 
                (nodes['negative'][1]+nodes['lessons'][1])/2, 
                'Extract lessons', ha='center', va='center', fontsize=8)
        
        ax.annotate("", 
                    xy=(nodes['improvement'][0]+0.15, nodes['improvement'][1]), 
                    xytext=(nodes['lessons'][0]-0.05, nodes['lessons'][1]-0.05),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
        ax.text((nodes['lessons'][0]+nodes['improvement'][0])/2, 
                (nodes['lessons'][1]+nodes['improvement'][1])/2, 
                'Create actionable tasks', ha='center', va='center', fontsize=8)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0.1, 0.9)
        ax.axis('off')
        plt.tight_layout()
        
        return fig
    
    # Display the retrospective flow diagram
    st.pyplot(create_retrospective_flow())
    
    st.markdown("""
    <div class="highlight">
    <strong>Retrospective Process:</strong>
    <ol>
        <li>Start with a completed or in-progress task</li>
        <li>Identify positive aspects that went well</li>
        <li>Identify challenges and issues that didn't go well</li>
        <li>Extract lessons learned from the challenges</li>
        <li>Create actionable improvement tasks based on lessons learned</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Example retrospective operations
    st.markdown("### Example Retrospective Operations")
    
    with st.expander("Positive Reflection Example"):
        st.code("""
{
    "operation": "add_reflection_positive",
    "task": "Prepare Investor Deck",
    "items": [
        "The design layout was well executed", 
        "Team collaboration was excellent"
    ]
}
        """, language="json")
    
    with st.expander("Negative Reflection Example"):
        st.code("""
{
    "operation": "add_reflection_negative",
    "task": "Prepare Investor Deck",
    "issues": [
        "ChatGPT did a poor job with image creation for the flyer", 
        "We could have improved our pitch for the investor"
    ],
    "lessons_learned": [
        "Use Gamma for presentations instead of ChatGPT image creator", 
        "Make sure to practice the pitch and review with a friend before Pitch Day"
    ]
}
        """, language="json")
    
    with st.expander("Improvement Task Example"):
        st.code("""
{
    "operation": "create_improvement_task",
    "task_name": "Improve Presentation Process",
    "checklist_items": [
        "Use Gamma for presentations instead of ChatGPT image creator", 
        "Practice pitch with friend before Pitch Day", 
        "Create template library for future presentations"
    ],
    "description": "The presentation could have been better. We should have practiced the ending segment of the pitch with a strong call to action. Practicing with a friend would have helped us improve our delivery."
}
        """, language="json")

# Example Workflow page
elif selection == "Example Workflow":
    st.markdown('<div class="section-header">Example Workflow</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Below is an example workflow showing how a user might interact with the system to create a task with a checklist.
    """)
    
    # Create a sequence diagram using mermaid
    mermaid_code = """
    sequenceDiagram
        participant User
        participant App as Main Application
        participant Whisper as Speech Transcriber
        participant GPT4 as Task Extractor
        participant Trello as Trello Handler
        participant API as Trello API
        
        User->>App: "Create a task for updating documentation with a checklist for README and API docs"
        App->>Whisper: Send audio
        Whisper->>App: Return transcription
        App->>GPT4: Send transcription
        GPT4->>Trello: Request current board state
        Trello->>API: Fetch cards
        API->>Trello: Return cards
        Trello->>GPT4: Return formatted board state
        GPT4->>App: Return JSON operations
        App->>Trello: Send operations
        Trello->>API: Create card "Update documentation"
        API->>Trello: Return card ID
        Trello->>API: Create checklist "Documentation Tasks"
        API->>Trello: Return checklist ID
        Trello->>API: Add items "Update README" and "Update API docs"
        API->>Trello: Confirm items added
        Trello->>App: Return operation results
        App->>User: "✅ Created: Update documentation\\n✅ Created checklist: Documentation Tasks"
    """
    
    st.markdown(f"""
    ```mermaid
    {mermaid_code}
    ```
    """)
    
    # Example retrospective workflow
    st.markdown("### Retrospective Workflow Example")
    
    retro_mermaid_code = """
    sequenceDiagram
        participant User
        participant App as Main Application
        participant Whisper as Speech Transcriber
        participant GPT4 as Task Extractor
        participant Trello as Trello Handler
        participant API as Trello API
        
        User->>App: "For the documentation task, what went well was the team collaboration and clear requirements. What didn't go well was the tight deadline and lack of examples. We learned we should start earlier and create templates."
        App->>Whisper: Send audio
        Whisper->>App: Return transcription
        App->>GPT4: Send transcription
        GPT4->>Trello: Request current board state
        Trello->>API: Fetch cards
        API->>Trello: Return cards
        Trello->>GPT4: Return formatted board state
        GPT4->>App: Return JSON operations
        App->>Trello: Send operations
        Trello->>API: Create card in "What's going well?" list
        API->>Trello: Return card ID
        Trello->>API: Add positive items to description
        Trello->>API: Create card in "What's not going well?" list
        API->>Trello: Return card ID
        Trello->>API: Add issues to description
        Trello->>API: Add lessons learned to comments
        Trello->>API: Create card in "What changes/ideas to make?" list
        API->>Trello: Return card ID
        Trello->>API: Add description synthesis
        Trello->>API: Create checklist with improvement items
        API->>Trello: Confirm items added
        Trello->>App: Return operation results
        App->>User: "✅ Added positive reflections\\n✅ Added negative reflections\\n✅ Created improvement task"
    """
    
    st.markdown(f"""
    ```mermaid
    {retro_mermaid_code}
    ```
    """)

# Challenges & Solutions page
elif selection == "Challenges & Solutions":
    st.markdown('<div class="section-header">Challenges & Solutions</div>', unsafe_allow_html=True)
    
    # Create challenges and solutions table
    challenges = [
        ["Ambiguous User Commands", "Users might express the same intent in many different ways", "Enhanced prompt engineering with examples of various phrasings; implemented fuzzy matching for task names"],
        ["Checklist Item Identification", "Difficulty in correctly identifying which checklist an item belongs to", "Implemented fuzzy matching for checklist names; added fallback to use the first checklist if ambiguous"],
        ["Streaming Audio Processing", "Processing incomplete sentences in streaming mode", "Added special handling for streaming mode with partial sentence detection"],
        ["Error Handling", "Graceful recovery from API failures", "Implemented comprehensive error handling and user-friendly error messages"],
        ["Context Management", "Maintaining context across multiple commands", "Enhanced board state formatting to provide complete context to the AI"]
    ]
    
    df = pd.DataFrame(challenges, columns=['Challenge', 'Description', 'Solution'])
    st.dataframe(df, use_container_width=True, height=300)
    
    # Technical implementation details
    st.markdown("### Technical Implementation Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Speech Recognition")
        st.markdown("""
        - **Model**: OpenAI Whisper
        - **Accuracy**: 95%+ for clear speech
         - **Model**: OpenAI Whisper
        - **Latency**: ~1-2 seconds for processing
        - **Languages**: Supports 100+ languages
        """)
    
    with col2:
        st.markdown("#### Natural Language Processing")
        st.markdown("""
        - **Model**: GPT-4
        - **Context Window**: 8K tokens
        - **Prompt Engineering**: Specialized for task extraction
        - **Error Handling**: Robust fallback mechanisms
        """)
    
    st.markdown("### Implementation Challenges")
    
    st.info("""
    One of the biggest challenges was handling ambiguous references to checklist items. 
    We implemented a fuzzy matching algorithm that can identify the correct checklist 
    even when users refer to it with slight variations in naming.
    """)

# Future Enhancements page
elif selection == "Future Enhancements":
    st.markdown('<div class="section-header">Future Enhancements</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Our roadmap includes several exciting enhancements to make the system even more powerful and user-friendly.
    The chart below shows our prioritization based on business value and implementation complexity.
    """)
    
    # Create future enhancements visualization
    enhancements = [
        "Multi-user support with voice recognition",
        "Integration with more project management tools",
        "Enhanced natural language understanding",
        "Mobile application development",
        "Real-time collaboration features",
        "Advanced analytics and reporting",
        "Custom voice commands and shortcuts"
    ]
    
    priorities = [9, 8, 10, 7, 6, 8, 7]
    complexity = [8, 7, 9, 6, 8, 7, 5]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=complexity,
        y=priorities,
        mode='markers+text',
        marker=dict(
            size=20,
            color=complexity,
            colorscale='Viridis',
            showscale=True,
            line=dict(width=2, color='white')
        ),
        text=enhancements,
        textposition="top center"
    ))
    
    fig.update_layout(
        title="Future Enhancements: Priority vs. Complexity",
        xaxis_title="Implementation Complexity (1-10)",
        yaxis_title="Business Priority (1-10)",
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(240,240,240,0.8)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed enhancement descriptions
    st.markdown("### Enhancement Details")
    
    enhancements_details = {
        "Multi-user support": "Implement voice recognition to identify different users and maintain separate contexts for each user.",
        "Integration with more tools": "Expand beyond Trello and Notion to include Jira, Asana, Monday.com, and other popular project management platforms.",
        "Enhanced NLU": "Improve natural language understanding to handle more complex commands and contextual references.",
        "Mobile application": "Develop native mobile apps for iOS and Android with offline capabilities.",
        "Real-time collaboration": "Enable multiple users to collaborate on tasks simultaneously with real-time updates.",
        "Advanced analytics": "Provide insights on productivity, task completion rates, and team performance.",
        "Custom voice commands": "Allow users to define custom shortcuts and command phrases for frequent operations."
    }
    
    for title, description in enhancements_details.items():
        with st.expander(title):
            st.write(description)

# Add a footer to all pages
st.markdown("""
<div class="footer">
    <p>Voice-to-Task Management System | Developed with ❤️ using Streamlit</p>
    <p style="font-size: 40px;">🎤 → 📋 → ✅</p>
</div>
""", unsafe_allow_html=True)

# Helper functions for visualizations
def create_system_architecture():
    # Create a matplotlib figure for the system architecture
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#f8f9fa')
    
    # Define node positions
    nodes = {
        'audio': (0.1, 0.5),
        'transcriber': (0.3, 0.5),
        'task_extractor': (0.5, 0.5),
        'trello_handler': (0.7, 0.7),
        'notion_handler': (0.7, 0.3),
        'trello': (0.9, 0.7),
        'notion': (0.9, 0.3)
    }
    
    # Define node labels
    labels = {
        'audio': 'Audio Input',
        'transcriber': 'Speech Transcriber\n(OpenAI Whisper)',
        'task_extractor': 'Task Extractor Agent\n(GPT-4)',
        'trello_handler': 'Trello API Handler',
        'notion_handler': 'Notion API Handler',
        'trello': 'Trello Board',
        'notion': 'Notion Database'
    }
    
    # Define node colors
    colors = {
        'audio': '#6ab7ff',
        'transcriber': '#56c2e6',
        'task_extractor': '#4dd4ac',
        'trello_handler': '#7986cb',
        'notion_handler': '#64b5f6',
        'trello': '#9575cd',
        'notion': '#4fc3f7'
    }
    
    # Draw nodes
    for node, pos in nodes.items():
        rect = patches.Rectangle(
            (pos[0]-0.08, pos[1]-0.05), 0.16, 0.1,
            linewidth=1, edgecolor='black', facecolor=colors[node], alpha=0.7,
            zorder=2
        )
        ax.add_patch(rect)
        ax.text(pos[0], pos[1], labels[node], ha='center', va='center', fontsize=9, fontweight='bold', zorder=3)
    
    # Draw edges
    ax.arrow(nodes['audio'][0]+0.08, nodes['audio'][1], nodes['transcriber'][0]-nodes['audio'][0]-0.16, 0, 
             head_width=0.02, head_length=0.01, fc='black', ec='black', zorder=1)
    ax.text((nodes['audio'][0]+nodes['transcriber'][0])/2, nodes['audio'][1]+0.03, 'Audio file/stream', 
            ha='center', va='center', fontsize=8)
    
    ax.arrow(nodes['transcriber'][0]+0.08, nodes['transcriber'][1], nodes['task_extractor'][0]-nodes['transcriber'][0]-0.16, 0, 
             head_width=0.02, head_length=0.01, fc='black', ec='black', zorder=1)
    ax.text((nodes['transcriber'][0]+nodes['task_extractor'][0])/2, nodes['transcriber'][1]+0.03, 'Text transcription', 
            ha='center', va='center', fontsize=8)
    
    # Draw edge from task_extractor to trello_handler
    ax.arrow(nodes['task_extractor'][0]+0.08, nodes['task_extractor'][1], 
             nodes['trello_handler'][0]-nodes['task_extractor'][0]-0.16, 
             nodes['trello_handler'][1]-nodes['task_extractor'][1], 
             head_width=0.02, head_length=0.01, fc='black', ec='black', zorder=1)
    ax.text((nodes['task_extractor'][0]+nodes['trello_handler'][0])/2, 
            (nodes['task_extractor'][1]+nodes['trello_handler'][1])/2+0.03, 
            'Task operations (JSON)', ha='center', va='center', fontsize=8)
    
    # Draw edge from task_extractor to notion_handler
    ax.arrow(nodes['task_extractor'][0]+0.08, nodes['task_extractor'][1], 
             nodes['notion_handler'][0]-nodes['task_extractor'][0]-0.16, 
             nodes['notion_handler'][1]-nodes['task_extractor'][1], 
             head_width=0.02, head_length=0.01, fc='black', ec='black', zorder=1)
    ax.text((nodes['task_extractor'][0]+nodes['notion_handler'][0])/2, 
            (nodes['task_extractor'][1]+nodes['notion_handler'][1])/2-0.03, 
            'Task operations (JSON)', ha='center', va='center', fontsize=8)
    
    # Draw remaining edges
    for start, end in [('trello_handler', 'trello'), ('notion_handler', 'notion')]:
        ax.arrow(nodes[start][0]+0.08, nodes[start][1], nodes[end][0]-nodes[start][0]-0.16, 0, 
                 head_width=0.02, head_length=0.01, fc='black', ec='black', zorder=1)
        ax.text((nodes[start][0]+nodes[end][0])/2, nodes[start][1]+0.03, 'API requests', 
                ha='center', va='center', fontsize=8)
    
    for start, end in [('trello', 'trello_handler'), ('notion', 'notion_handler')]:
        ax.arrow(nodes[start][0]-0.08, nodes[start][1]+0.02, nodes[end][0]-nodes[start][0]+0.16, 0, 
                 head_width=0.02, head_length=0.01, fc='black', ec='black', zorder=1)
        ax.text((nodes[start][0]+nodes[end][0])/2, nodes[start][1]-0.03, 'Board state', 
                ha='center', va='center', fontsize=8)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    
    # Convert plot to image
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

def create_retrospective_flow():
    # Create a matplotlib figure for the retrospective flow
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#f8f9fa')
    
    # Define node positions
    nodes = {
        'task': (0.5, 0.8),
        'positive': (0.2, 0.6),
        'negative': (0.8, 0.6),
        'lessons': (0.8, 0.4),
        'improvement': (0.5, 0.2)
    }
    
    # Define node labels
    labels = {
        'task': 'Task',
        'positive': 'What went well?',
        'negative': 'What didn\'t go well?',
        'lessons': 'Lessons Learned',
        'improvement': 'Improvement Tasks'
    }
    
    # Define node colors
    colors = {
        'task': '#4fc3f7',
        'positive': '#66bb6a',
        'negative': '#ef5350',
        'lessons': '#ffca28',
        'improvement': '#7986cb'
    }
    
    # Draw nodes
    for node, pos in nodes.items():
        rect = patches.Rectangle(
            (pos[0]-0.1, pos[1]-0.05), 0.2, 0.1,
            linewidth=1, edgecolor='black', facecolor=colors[node], alpha=0.7,
            zorder=2
        )
        ax.add_patch(rect)
        ax.text(pos[0], pos[1], labels[node], ha='center', va='center', fontsize=10, fontweight='bold', zorder=3)
    
    # Draw edges
    ax.annotate("", 
                xy=(nodes['positive'][0], nodes['positive'][1]), 
                xytext=(nodes['task'][0]-0.05, nodes['task'][1]-0.05),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
    ax.text((nodes['task'][0]+nodes['positive'][0])/2-0.05, 
            (nodes['task'][1]+nodes['positive'][1])/2, 
            'Reflect on positives', ha='center', va='center', fontsize=8)
    
    ax.annotate("", 
                xy=(nodes['negative'][0], nodes['negative'][1]), 
                xytext=(nodes['task'][0]+0.05, nodes['task'][1]-0.05),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
    ax.text((nodes['task'][0]+nodes['negative'][0])/2+0.05, 
            (nodes['task'][1]+nodes['negative'][1])/2, 
            'Identify challenges', ha='center', va='center', fontsize=8)
    
    ax.annotate("", 
                xy=(nodes['lessons'][0], nodes['lessons'][1]), 
                xytext=(nodes['negative'][0], nodes['negative'][1]-0.05),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
    ax.text(nodes['negative'][0], 
            (nodes['negative'][1]+nodes['lessons'][1])/2, 
            'Extract lessons', ha='center', va='center', fontsize=8)
    
    ax.annotate("", 
                xy=(nodes['improvement'][0]+0.15, nodes['improvement'][1]), 
                xytext=(nodes['lessons'][0]-0.05, nodes['lessons'][1]-0.05),
                arrowprops=dict(arrowstyle="->", lw=1.5, color='#555555'))
    ax.text((nodes['lessons'][0]+nodes['improvement'][0])/2, 
            (nodes['lessons'][1]+nodes['improvement'][1])/2, 
            'Create actionable tasks', ha='center', va='center', fontsize=8)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0.1, 0.9)
    ax.axis('off')
    plt.tight_layout()
    
    # Convert plot to image
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf