"""
Transcription module for converting audio to text
"""
from openai import OpenAI
import os

def transcribe_audio(audio_buffer):
    """
    Transcribes audio using OpenAI's Whisper API.
    Returns: Transcribed text or None.
    """
    if not audio_buffer:
        return None

    try:
        print("⏳ Transcribing audio...")
        
        # Initialize OpenAI client with API key from environment
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Reset buffer position to start
        audio_buffer.seek(0)
        
        # Send the audio buffer to Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_buffer
        )

        # Print the transcription for debugging
        print("\n📝 Transcribed Text:")
        print("-" * 50)
        print(transcript.text)
        print("-" * 50 + "\n")

        return transcript.text

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        return None
