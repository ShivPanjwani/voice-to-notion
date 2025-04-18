"""
Transcription module for converting audio to text
"""
from openai import OpenAI
import os
from datetime import datetime

def transcribe_audio(audio_file):
    """
    Transcribes audio using OpenAI's Whisper API.
    Returns: Transcribed text or None.
    """
    if not audio_file:
        return None

    try:
        print("⏳ Transcribing audio...")
        
        # Initialize OpenAI client with API key from environment
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Check if audio_file is a string (file path) or file-like object
        if isinstance(audio_file, str):
            # Open the file if it's a path
            with open(audio_file, 'rb') as file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file
                )
        else:
            # Reset buffer position to start if it's a file-like object
            audio_file.seek(0)
            
            # Send the audio buffer to Whisper
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        # Print the transcription for debugging
        print("\n📝 Transcribed Text:")
        print("-" * 50)
        print(transcript.text)
        print("-" * 50 + "\n")

        # Save transcription to file
        try:
            with open("/Users/shivpanjwani/Downloads/V2N_TEXT_TEST.txt", "a") as file:
                file.write(f"\n\n--- Transcription: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                file.write(transcript.text)
                file.write("\n" + "-"*50)
            print("✅ Transcription saved to file")
        except Exception as e:
            print(f"❌ Error saving transcription to file: {str(e)}")

        return transcript.text

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        return None
