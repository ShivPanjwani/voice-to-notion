from agents.audio_recorder import record_audio
from agents.transcription import transcribe_audio
from agents.scrum_master import extract_tasks  # Using the compatibility function
from api.notion_handler import handle_task_operations

def process_meeting():
    """
    Process a live meeting:
    1. Record audio
    2. Transcribe audio
    3. Extract tasks
    4. Update Notion
    """
    print("\nStarting meeting processing...")
    
    # Record audio
    audio_buffer = record_audio()
    
    if not audio_buffer:
        print("❌ No audio recorded. Exiting.")
        return False
    
    # Transcribe audio
    transcript = transcribe_audio(audio_buffer)
    
    if not transcript:
        print("❌ Transcription failed. Exiting.")
        return False
    
    print("\nTranscription:")
    print(f"\"{transcript}\"\n")
    
    # Extract tasks
    task_operations = extract_tasks(transcript)
    
    if not task_operations:
        print("❌ No tasks extracted. Exiting.")
        return False
    
    # Process tasks in Notion
    results = handle_task_operations(task_operations)
    
    # Print summary
    success_count = sum(1 for result in results if result.get("success", False))
    print(f"\n✅ Successfully processed {success_count} of {len(results)} operations.")
    
    return True
