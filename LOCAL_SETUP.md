# Emoticon - Local Installation Guide

## Overview
This guide helps you install and run Emoticon locally on your computer for full camera and screen recording capabilities.

## Prerequisites
- Python 3.8 or higher
- Webcam/camera access
- Windows, macOS, or Linux

## Installation Steps

### 1. Download Project Files
1. Download all project files from this Replit
2. Extract to a folder on your computer (e.g., `C:\emoticon` or `~/emoticon`)

### 2. Install Python
- Download Python 3.8+ from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### 3. Install Required Packages
Open terminal/command prompt in the project folder and run:
```bash
pip install streamlit opencv-python mediapipe openai psycopg2-binary sqlalchemy pillow mss numpy
```

### 4. Set Up Environment Variables
Create a `.env` file in the project folder:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application

#### Main Application
```bash
streamlit run app.py --server.port 5000
```

#### Screen Recorder Mode
```bash
streamlit run screen_recorder_standalone.py --server.port 5001
```

## Screen Recorder Features

### What It Does
- Records your screen during video calls
- Analyzes facial expressions in real-time
- Shows popup notifications for significant expression changes
- Works with Zoom, Teams, Google Meet, and other video platforms

### How to Use
1. Start the screen recorder: `streamlit run screen_recorder_standalone.py`
2. Open your video call application
3. Position the recorder window where you can see it
4. Click "Start Recording" in the recorder interface
5. Get live analysis during your call

### Configuration Options
- **Sensitivity**: Adjust how sensitive the analysis is to changes
- **Cooldown**: Set minimum time between analyses
- **Analysis History**: View past analyses from your session

## Troubleshooting

### Camera Not Working
- Check camera permissions in your operating system
- Ensure no other applications are using the camera
- Try restarting the application

### Installation Issues
- Make sure Python is properly installed and in PATH
- Try upgrading pip: `pip install --upgrade pip`
- Install packages one by one if bulk installation fails

### Performance Issues
- Close unnecessary applications
- Ensure good lighting for better face detection
- Lower the sensitivity if getting too many analyses

## Database Setup (Optional)
For persistent data storage, you can set up a local PostgreSQL database:
```bash
# Install PostgreSQL locally
# Set DATABASE_URL environment variable
DATABASE_URL=postgresql://username:password@localhost:5432/emoticon
```

## Security Notes
- Keep your OpenAI API key secure
- Don't share your `.env` file
- The application processes video locally for privacy

## Support
If you encounter issues:
1. Check the console output for error messages
2. Ensure all dependencies are installed
3. Verify your OpenAI API key is valid
4. Check camera permissions