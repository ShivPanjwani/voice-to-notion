"""
Streaming Meeting Processor Module
----------------------------------
Handles real-time processing of meeting audio with live Notion updates.
"""

import threading
import time
import queue
import os
from agents.audio_recorder import record_audio_chunk
from agents.transcription import transcribe_audio
from agents.task_extractor import extract_tasks
from api.notion_handler import handle_task_operations
from pynput import keyboard

class StreamingMeetingProcessor:
    """Processes meeting audio in real-time with continuous Notion updates."""
    
    def __init__(self, chunk_duration=5):
        """Initialize the streaming processor with specified chunk duration."""
        self.chunk_duration = chunk_duration  # seconds
        self.audio_queue = queue.Queue()
        self.transcript_buffer = ""
        self.processed_operations = {}  # Track operations by their unique signature
        self.is_recording = False
        self.recording_thread = None
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.listener = None
    
    def start(self):
        """Start the streaming meeting process."""
        self.is_recording = True
        self.stop_event.clear()
        
        # Set up keyboard listener
        def on_press(key):
            try:
                if key == keyboard.Key.space:
                    print("\n🛑 Stopping recording...")
                    self.stop()
                    return False
            except AttributeError:
                pass
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        print("\n🎙️ Live streaming started. Press spacebar to stop.")
        
        # Wait for recording thread to complete
        self.recording_thread.join()
        
        # Signal processing thread to finish remaining work
        self.audio_queue.put(None)  # Sentinel value
        
        # Wait for processing to complete with a timeout
        processing_timeout = 60  # seconds
        self.processing_thread.join(timeout=processing_timeout)
        
        if self.processing_thread.is_alive():
            print("\n⚠️ Processing is taking longer than expected. Continuing in background.")
        
        print("\n✅ Live streaming completed.")
        return True
    
    def stop(self):
        """Stop the streaming process."""
        self.is_recording = False
        self.stop_event.set()
    
    def _recording_worker(self):
        """Worker thread that records audio chunks."""
        chunk_num = 0
        
        while self.is_recording:
            print(f"\n📊 Recording chunk {chunk_num + 1}...")
            audio_file = record_audio_chunk(self.chunk_duration, self.stop_event)
            
            if self.stop_event.is_set():
                self.is_recording = False
                break
                
            if audio_file:
                self.audio_queue.put(audio_file)
                chunk_num += 1
        
        print("\n🛑 Recording stopped.")
    
    def _processing_worker(self):
        """Worker thread that processes audio chunks."""
        while True:
            try:
                # Get the next audio chunk with a timeout
                try:
                    audio_file = self.audio_queue.get(timeout=1.0)
                except queue.Empty:
                    # If we're not recording anymore and queue is empty, we're done
                    if not self.is_recording and self.audio_queue.empty():
                        break
                    continue
                
                # None is our sentinel value indicating we should stop
                if audio_file is None:
                    break
                
                # Transcribe the audio chunk
                print("\n🔄 Transcribing audio chunk...")
                transcript_chunk = transcribe_audio(audio_file)
                
                # Clean up the temporary audio file
                try:
                    os.unlink(audio_file)
                except:
                    pass
                
                if not transcript_chunk:
                    print("❌ Failed to transcribe chunk.")
                    self.audio_queue.task_done()
                    continue
                
                # Add to transcript buffer
                self.transcript_buffer += " " + transcript_chunk
                print(f"\n📝 Latest transcript: \"{transcript_chunk}\"")
                
                # Extract tasks from the updated transcript
                print("\n🔍 Extracting tasks...")
                task_operations = extract_tasks(self.transcript_buffer, is_streaming=True)
                
                if task_operations:
                    # Filter out operations we've already processed
                    new_operations = []
                    for op in task_operations:
                        # Create a unique signature for the operation
                        if op['operation'] == 'create':
                            op_sig = f"create:{op.get('task', '')}"
                        elif op['operation'] == 'update':
                            op_sig = f"update:{op.get('task', '')}:{','.join(sorted([k for k in op.keys() if k not in ['operation', 'task']]))}"
                        elif op['operation'] == 'rename':
                            op_sig = f"rename:{op.get('old_name', '')}:{op.get('new_name', '')}"
                        elif op['operation'] in ['create_epic', 'assign_epic']:
                            op_sig = f"{op['operation']}:{op.get('task', '')}:{op.get('epic', '')}"
                        else:
                            op_sig = f"{op['operation']}:{op.get('task', '')}"
                        
                        # Check if we've seen this exact operation before
                        if op_sig not in self.processed_operations:
                            new_operations.append(op)
                            self.processed_operations[op_sig] = True
                    
                    if new_operations:
                        print(f"\n📋 Processing {len(new_operations)} new task operations...")
                        try:
                            results = handle_task_operations(new_operations)
                            
                            # Print summary of operations
                            success_count = sum(1 for r in results if r.get("success", False))
                            print(f"✅ Successfully processed {success_count} of {len(results)} operations.")
                            
                            # Print details of each operation
                            for i, result in enumerate(results):
                                status = "✅" if result.get("success", False) else "❌"
                                op_type = result.get("operation", "unknown")
                                task = result.get("task", result.get("old_name", "unknown task"))
                                print(f"  {i+1}. {status} {op_type.capitalize()}: {task}")
                        except Exception as e:
                            print(f"❌ Error processing operations: {str(e)}")
                
                self.audio_queue.task_done()
            
            except Exception as e:
                print(f"❌ Processing error: {str(e)}")
                # Continue processing other chunks
                continue 