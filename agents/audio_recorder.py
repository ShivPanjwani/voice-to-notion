"""
Audio Recorder Module for Voice-to-Notion
--------------------------------------------
This module handles the recording of audio input from the microphone.
"""

import pyaudio
import wave
import tempfile
import os
import threading
from pynput import keyboard

def record_audio():
    """
    Records audio from the microphone until spacebar is pressed.
    Returns: Path to the recorded audio file or None.
    """
    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    # Create a temporary file to store the audio
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_filename = temp_file.name
    temp_file.close()
    
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open stream
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        print("🎤 Recording... Press spacebar to stop.")
        
        frames = []
        
        # Create a flag to stop recording
        stop_recording = threading.Event()
        
        # Define the key listener callback
        def on_press(key):
            try:
                if key == keyboard.Key.space:
                    stop_recording.set()
                    # Return False to stop listener
                    return False
            except AttributeError:
                pass
        
        # Start the keyboard listener in a separate thread
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        # Record until spacebar is pressed
        while not stop_recording.is_set():
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("✅ Recording stopped.")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the recorded audio to a WAV file
        if frames:
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            
            return temp_filename
        else:
            print("❌ No audio recorded.")
            os.unlink(temp_filename)
            return None
            
    except Exception as e:
        print(f"❌ Recording error: {str(e)}")
        try:
            os.unlink(temp_filename)
        except:
            pass
        return None
