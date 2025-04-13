import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import os
from gtts import gTTS
import tempfile
import threading
import time as time_module
import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy import signal
import io
import random
import librosa

class TextToSpeechReader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text to Speech Reader")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.is_reading = False
        self.current_audio_file = None
        self.playback_speed = 1.0  # Default speed
        self.playback_thread = None
        self.should_stop = False
        self.audio_data = None
        self.sample_rate = None
        self.stream = None
        self.current_position = 0
        self.total_frames = 0
        self.status_var = tk.StringVar(value="Ready")
        self.start_time = None
        self.audio_duration = 0
        
        # Debug mode
        self.debug_mode = True
        
        # Print available audio devices
        self.print_audio_devices()
        
        # Fun facts
        self.fun_facts = [
            "The average person spends about six months of their lifetime waiting for red lights to turn green.",
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
            "The shortest war in history was between Britain and Zanzibar in 1896. It lasted only 38 minutes.",
            "A day on Venus is longer than its year. Venus takes 243 Earth days to rotate on its axis but only 225 Earth days to orbit the Sun.",
            "The human brain can process images in as little as 13 milliseconds.",
            "The average person walks the equivalent of three times around the world in a lifetime.",
            "Bananas are berries, but strawberries aren't.",
            "The first oranges weren't orange. The original oranges from Southeast Asia were actually green.",
            "The world's oldest known living tree is a Great Basin bristlecone pine named Methuselah, which is over 4,800 years old.",
            "The human body sheds about 600,000 particles of skin every hour.",
            "The average person spends about six months of their lifetime waiting for red lights to turn green.",
            "The shortest war in history was between Britain and Zanzibar in 1896. It lasted only 38 minutes.",
            "A day on Venus is longer than its year. Venus takes 243 Earth days to rotate on its axis but only 225 Earth days to orbit the Sun.",
            "The human brain can process images in as little as 13 milliseconds.",
            "The average person walks the equivalent of three times around the world in a lifetime."
        ]
        
        # Create GUI elements
        self.create_widgets()
        
    def print_audio_devices(self):
        """Print available audio devices for debugging"""
        try:
            devices = sd.query_devices()
            print("\n=== AVAILABLE AUDIO DEVICES ===")
            for i, device in enumerate(devices):
                print(f"Device {i}: {device['name']}")
                print(f"  Input channels: {device['max_input_channels']}")
                print(f"  Output channels: {device['max_output_channels']}")
                print(f"  Default sample rate: {device['default_samplerate']}")
                print(f"  Host API: {device['hostapi']}")
                print()
            
            # Get default devices
            default_input = sd.query_devices(kind='input')
            default_output = sd.query_devices(kind='output')
            print(f"Default input device: {default_input['name']}")
            print(f"Default output device: {default_output['name']}")
            print("================================\n")
        except Exception as e:
            print(f"Error querying audio devices: {e}")
        
    def create_widgets(self):
        # Text area
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=20)
        self.text_area.pack(padx=10, pady=10, expand=True, fill='both')
        
        # Status label
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, anchor="w")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.root, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Speed control frame
        speed_frame = tk.Frame(self.root)
        speed_frame.pack(pady=5)
        
        # Speed label
        self.speed_label = tk.Label(speed_frame, text=f"Speed: {self.playback_speed}x")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        # Speed control buttons
        self.speed_down_button = tk.Button(speed_frame, text="Slower", command=self.decrease_speed)
        self.speed_down_button.pack(side=tk.LEFT, padx=5)
        
        self.speed_up_button = tk.Button(speed_frame, text="Faster", command=self.increase_speed)
        self.speed_up_button.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        # Open file button
        self.open_button = tk.Button(button_frame, text="Open File", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        # Read button
        self.read_button = tk.Button(button_frame, text="Read Text", command=self.start_reading)
        self.read_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_reading)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Clear text button
        self.clear_button = tk.Button(button_frame, text="Clear Text", command=self.clear_text)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Save audio button
        self.save_button = tk.Button(button_frame, text="Save Audio", command=self.save_audio)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Fun Facts button
        self.fun_facts_button = tk.Button(button_frame, text="Fun Fact", command=self.insert_fun_fact)
        self.fun_facts_button.pack(side=tk.LEFT, padx=5)
        
        # Test Audio button
        self.test_button = tk.Button(button_frame, text="Test Audio", command=self.test_audio)
        self.test_button.pack(side=tk.LEFT, padx=5)
        
    def test_audio(self):
        """Test audio playback with a simple beep"""
        try:
            self.update_status("Testing audio with a beep...")
            
            # Generate a simple beep sound
            sample_rate = 44100
            duration = 0.5  # seconds
            frequency = 440  # Hz (A4 note)
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            beep = 0.5 * np.sin(2 * np.pi * frequency * t)
            
            # Ensure the beep is 2D (stereo)
            if len(beep.shape) == 1:
                beep = beep.reshape(-1, 1)
            
            # Play the beep
            sd.play(beep, sample_rate)
            sd.wait()  # Wait until the beep is finished
            
            self.update_status("Audio test completed")
        except Exception as e:
            error_msg = f"Error testing audio: {str(e)}"
            print(error_msg)
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
        
    def insert_fun_fact(self):
        """Insert a random fun fact into the text area"""
        # Select a random fun fact
        fun_fact = random.choice(self.fun_facts)
        
        # Insert into text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, fun_fact)
        
        self.update_status("Inserted a fun fact")
        
    def update_status(self, message):
        """Update the status message and ensure it's visible"""
        self.status_var.set(message)
        self.root.update_idletasks()
        if self.debug_mode:
            print(f"Status: {message}")
        
    def update_progress(self, value):
        """Update the progress bar value"""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def clear_text(self):
        """Clear all text from the text area"""
        self.text_area.delete(1.0, tk.END)
        self.update_status("Text area cleared")
        
    def increase_speed(self):
        if self.playback_speed < 2.0:  # Maximum speed limit
            self.playback_speed += 0.25
            self.speed_label.config(text=f"Speed: {self.playback_speed}x")
            self.update_status(f"Speed increased to {self.playback_speed}x")
    
    def decrease_speed(self):
        if self.playback_speed > 0.5:  # Minimum speed limit
            self.playback_speed -= 0.25
            self.speed_label.config(text=f"Speed: {self.playback_speed}x")
            self.update_status(f"Speed decreased to {self.playback_speed}x")
    
    def save_audio(self):
        """Save the current audio to a file"""
        if not self.current_audio_file:
            messagebox.showwarning("Warning", "No audio to save! Generate audio first.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Copy the current audio file to the selected path
                import shutil
                shutil.copy2(self.current_audio_file, file_path)
                messagebox.showinfo("Success", f"Audio saved to {file_path}")
                self.update_status(f"Audio saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving audio: {str(e)}")
                self.update_status(f"Error saving audio: {e}")
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                self.update_status(f"File opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {str(e)}")
                self.update_status(f"Error opening file: {e}")
    
    def time_stretch(self, audio_data, speed_factor):
        """Time stretch audio while preserving pitch using librosa"""
        if speed_factor == 1.0:
            return audio_data
            
        # Process each channel separately
        stretched_channels = []
        for channel in range(audio_data.shape[1]):
            # Get the channel data
            channel_data = audio_data[:, channel]
            
            # Use librosa's time_stretch function
            stretched_channel = librosa.effects.time_stretch(
                channel_data,
                rate=speed_factor
            )
            
            # Ensure the stretched audio has the same length as the original
            if len(stretched_channel) > len(channel_data):
                stretched_channel = stretched_channel[:len(channel_data)]
            elif len(stretched_channel) < len(channel_data):
                # Pad with zeros if necessary
                padding = np.zeros(len(channel_data) - len(stretched_channel))
                stretched_channel = np.concatenate([stretched_channel, padding])
            
            stretched_channels.append(stretched_channel)
        
        # Combine channels back together
        return np.column_stack(stretched_channels)
    
    def start_reading(self):
        if self.is_reading:
            return
            
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to read!")
            return
            
        self.is_reading = True
        self.should_stop = False
        self.read_button.config(state='disabled')
        self.update_status("Starting text-to-speech conversion...")
        self.update_progress(0)
        
        # Start reading in a separate thread
        self.playback_thread = threading.Thread(target=self.read_text, args=(text,), daemon=True)
        self.playback_thread.start()
    
    def read_text(self, text):
        try:
            self.update_status("Starting text-to-speech conversion...")
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                self.current_audio_file = temp_file.name
                self.update_status("Created temporary audio file")
            
            # Generate speech
            self.update_status("Generating speech...")
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(self.current_audio_file)
            self.update_status("Speech generated successfully")
            
            # Try a simpler approach to play the audio
            self.update_status("Playing audio...")
            try:
                # Load the audio file
                self.audio_data, self.sample_rate = sf.read(self.current_audio_file)
                self.total_frames = len(self.audio_data)
                self.audio_duration = self.total_frames / self.sample_rate
                self.update_status(f"Audio loaded: {self.total_frames} frames at {self.sample_rate}Hz")
                
                # Convert to float32 if needed
                if self.audio_data.dtype != np.float32:
                    self.audio_data = self.audio_data.astype(np.float32)
                
                # Ensure audio is 2D (stereo)
                if len(self.audio_data.shape) == 1:
                    self.audio_data = self.audio_data.reshape(-1, 1)
                
                # Apply time stretching while preserving pitch
                if self.playback_speed != 1.0:
                    self.audio_data = self.time_stretch(self.audio_data, self.playback_speed)
                
                # Play the audio directly
                self.start_time = time_module.time()
                sd.play(self.audio_data, self.sample_rate)
                
                # Update progress while playing
                while sd.get_stream().active and not self.should_stop:
                    elapsed_time = time_module.time() - self.start_time
                    progress = min(100, (elapsed_time / self.audio_duration) * 100)
                    self.update_progress(progress)
                    self.update_status(f"Playing: {progress:.1f}% complete")
                    time_module.sleep(0.1)
                
                # Wait for playback to complete
                sd.wait()
                
                if not self.should_stop:
                    self.update_status("Playback completed")
                    self.update_progress(100)
            except Exception as e:
                error_msg = f"Error during audio playback: {str(e)}"
                print(error_msg)
                self.update_status(error_msg)
                messagebox.showerror("Error", error_msg)
            
        except Exception as e:
            error_msg = f"Error during text-to-speech: {str(e)}"
            print(error_msg)
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
        finally:
            self.update_status("Cleaning up...")
            self.is_reading = False
            self.read_button.config(state='normal')
            if self.current_audio_file and os.path.exists(self.current_audio_file):
                os.unlink(self.current_audio_file)
                self.update_status("Temporary file deleted")
    
    def stop_reading(self):
        if self.is_reading:
            self.update_status("Stopping playback...")
            self.should_stop = True
            sd.stop()
            self.read_button.config(state='normal')
            self.update_status("Playback stopped")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextToSpeechReader()
    app.run() 