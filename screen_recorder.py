import cv2
import mediapipe as mp
import numpy as np
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import os
from PIL import Image, ImageTk
from openai_analyzer import analyze_expression
from video_analyzer import VideoEmotionAnalyzer
import mss
import uuid
from database import save_emotion_analysis
from datetime import datetime

class ScreenRecorderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Emoticon - Screen Recorder")
        self.root.geometry("400x300")
        self.root.configure(bg='#2c3e50')
        
        # Initialize components
        self.analyzer = VideoEmotionAnalyzer(significance_threshold=0.2)
        self.session_id = str(uuid.uuid4())
        self.is_recording = False
        self.is_analyzing = False
        self.analysis_queue = queue.Queue()
        self.popup_window = None
        self.last_analysis_time = 0
        self.analysis_cooldown = 10  # seconds between analyses
        
        # Screen capture
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[0]  # Primary monitor
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="Screen Recorder Mode", 
            font=("Arial", 16, "bold"),
            bg='#2c3e50', 
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Record your screen and get live emotion analysis\nfor video calls (Zoom, Teams, etc.)",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            justify='center'
        )
        instructions.pack(pady=5)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready to record",
            font=("Arial", 12),
            bg='#2c3e50',
            fg='#3498db'
        )
        self.status_label.pack(pady=10)
        
        # Record button
        self.record_button = tk.Button(
            self.root,
            text="Start Recording",
            command=self.toggle_recording,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10
        )
        self.record_button.pack(pady=10)
        
        # Analysis toggle
        self.analysis_var = tk.BooleanVar(value=True)
        analysis_check = tk.Checkbutton(
            self.root,
            text="Live Analysis (shows popups for major changes)",
            variable=self.analysis_var,
            font=("Arial", 10),
            bg='#2c3e50',
            fg='white',
            selectcolor='#34495e'
        )
        analysis_check.pack(pady=5)
        
        # Sensitivity slider
        tk.Label(
            self.root,
            text="Analysis Sensitivity:",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=(20, 5))
        
        self.sensitivity_var = tk.DoubleVar(value=0.2)
        sensitivity_slider = tk.Scale(
            self.root,
            from_=0.1,
            to=0.5,
            resolution=0.05,
            variable=self.sensitivity_var,
            orient='horizontal',
            bg='#34495e',
            fg='white',
            highlightbackground='#2c3e50',
            command=self.update_sensitivity
        )
        sensitivity_slider.pack(pady=5)
        
        # Exit button
        exit_button = tk.Button(
            self.root,
            text="Exit",
            command=self.exit_app,
            font=("Arial", 10),
            bg='#e74c3c',
            fg='white',
            padx=15,
            pady=5
        )
        exit_button.pack(pady=10)
        
        # Keep window on top
        self.root.attributes('-topmost', True)
        
    def update_sensitivity(self, value):
        self.analyzer.significance_threshold = float(value)
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="Stop Recording", bg='#e74c3c')
        self.status_label.config(text="Recording... Analyzing expressions", fg='#e74c3c')
        
        # Start recording thread
        self.recording_thread = threading.Thread(target=self.record_screen)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording", bg='#27ae60')
        self.status_label.config(text="Recording stopped", fg='#3498db')
        
    def record_screen(self):
        while self.is_recording:
            try:
                # Capture screen
                screenshot = self.sct.grab(self.monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                
                # Analyze if enabled and enough time has passed
                if (self.analysis_var.get() and 
                    time.time() - self.last_analysis_time > self.analysis_cooldown):
                    
                    current_time = time.time()
                    result = self.analyzer.analyze_video_frame(frame, current_time)
                    
                    if result:
                        self.last_analysis_time = current_time
                        self.show_analysis_popup(result)
                        
                        # Save to database
                        save_emotion_analysis(
                            self.session_id,
                            result.get('expressions', []),
                            result.get('ai_analysis', 'No analysis available'),
                            'screen_recording',
                            result.get('significance_score', 0.0)
                        )
                
                time.sleep(0.1)  # Limit processing rate
                
            except Exception as e:
                print(f"Recording error: {e}")
                time.sleep(1)
                
    def show_analysis_popup(self, analysis_result):
        # Close existing popup
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
            
        # Create new popup
        self.popup_window = tk.Toplevel(self.root)
        self.popup_window.title("Live Analysis")
        self.popup_window.geometry("350x200")
        self.popup_window.configure(bg='#34495e')
        self.popup_window.attributes('-topmost', True)
        
        # Position in top-right corner
        self.popup_window.geometry("+{}+{}".format(
            self.root.winfo_screenwidth() - 370,
            50
        ))
        
        # Content
        expressions = analysis_result.get('expressions', [])
        ai_analysis = analysis_result.get('ai_analysis', 'No analysis available')
        significance = analysis_result.get('significance_score', 0.0)
        
        # Title
        title_label = tk.Label(
            self.popup_window,
            text="🎭 Live Expression Analysis",
            font=("Arial", 12, "bold"),
            bg='#34495e',
            fg='white'
        )
        title_label.pack(pady=5)
        
        # Expressions
        if expressions:
            expr_text = ", ".join(expressions[:3])  # Show first 3 expressions
            expr_label = tk.Label(
                self.popup_window,
                text=f"Detected: {expr_text}",
                font=("Arial", 10),
                bg='#34495e',
                fg='#3498db',
                wraplength=300
            )
            expr_label.pack(pady=5)
        
        # AI Analysis
        analysis_label = tk.Label(
            self.popup_window,
            text=ai_analysis[:100] + "..." if len(ai_analysis) > 100 else ai_analysis,
            font=("Arial", 9),
            bg='#34495e',
            fg='#ecf0f1',
            wraplength=300,
            justify='left'
        )
        analysis_label.pack(pady=5, padx=10)
        
        # Significance
        sig_label = tk.Label(
            self.popup_window,
            text=f"Significance: {significance:.2f}",
            font=("Arial", 8),
            bg='#34495e',
            fg='#95a5a6'
        )
        sig_label.pack(pady=5)
        
        # Close button
        close_button = tk.Button(
            self.popup_window,
            text="Close",
            command=self.popup_window.destroy,
            font=("Arial", 8),
            bg='#e74c3c',
            fg='white'
        )
        close_button.pack(pady=5)
        
        # Auto-close after 8 seconds
        self.popup_window.after(8000, lambda: self.popup_window.destroy() if self.popup_window.winfo_exists() else None)
        
    def exit_app(self):
        self.is_recording = False
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ScreenRecorderApp()
        app.run()
    except Exception as e:
        print(f"Error starting screen recorder: {e}")
        messagebox.showerror("Error", f"Failed to start screen recorder: {e}")