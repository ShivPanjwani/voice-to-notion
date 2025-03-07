"""
Audio Recorder Module for Voice-to-Notion
--------------------------------------------
This module handles the recording of audio input from the microphone.
"""

import speech_recognition as sr
import io

def record_audio():
    """
    Records audio using speech_recognition and returns audio buffer for transcription
    """
    recognizer = sr.Recognizer()
    
    # Audio recording settings
    recognizer.energy_threshold = 100
    recognizer.pause_threshold = 2.0    # 2 seconds of silence to stop
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("\n🎤 Recording... (Will stop after 2s of silence)")
            
            # Skip ambient noise message
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            audio = recognizer.listen(
                source,
                timeout=15,            # 15 seconds to start speaking
                phrase_time_limit=600   # 600 seconds of speech allowed
            )
            print("✅ Recording complete")
            
            # Prepare audio data for Whisper
            wav_data = audio.get_wav_data()
            audio_buffer = io.BytesIO(wav_data)
            audio_buffer.name = 'audio.wav'
            return audio_buffer
            
    except sr.WaitTimeoutError:
        print("⏹️ No speech detected within timeout period.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    return None
