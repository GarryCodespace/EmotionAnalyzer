# Facial Expression Analysis System

## Overview

This application is a real-time facial expression analysis system that combines computer vision with AI-powered emotional interpretation. It uses MediaPipe for facial landmark detection and OpenAI's GPT-4o model to provide psychological insights about detected expressions and gestures.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web-based user interface
- **Real-time Processing**: OpenCV for video capture and frame processing
- **User Interaction**: Simple web interface for live camera feed and analysis results

### Backend Architecture
- **Computer Vision**: MediaPipe Face Mesh for facial landmark detection
- **Expression Detection**: Custom gesture recognition system using 100+ predefined facial expressions
- **AI Analysis**: OpenAI GPT-4o integration for emotional interpretation
- **Database**: PostgreSQL for storing analysis results, user sessions, and statistics
- **Processing Pipeline**: Real-time video frame analysis with gesture detection and AI interpretation

## Key Components

### 1. Facial Landmark Detection
- **Technology**: MediaPipe Face Mesh
- **Purpose**: Detect 468 facial landmarks in real-time
- **Configuration**: Single face detection with refined landmarks
- **Output**: 3D coordinates (x, y, z) for each facial point

### 2. Gesture Recognition System
- **Implementation**: 100+ predefined gestures using lambda functions
- **Detection Method**: Geometric analysis of facial landmark positions
- **Gesture Types**: 
  - Basic expressions (smile, frown, blink)
  - Complex combinations (brow furrow + frown)
  - Micro-expressions (subtle smile, lip bite)
  - Head movements (tilts, turns)
- **Sensitivity**: Adjustable thresholds for different gesture types

### 3. AI Expression Analysis
- **Model**: OpenAI GPT-4o
- **Purpose**: Provide psychological insights and emotional interpretation
- **Input**: Comma-separated list of detected gestures
- **Output**: Emotional analysis including mood, underlying feelings, and social context
- **Response Limit**: 150 words maximum for concise insights

### 4. Real-time Processing Pipeline
- **Video Capture**: OpenCV camera integration
- **Frame Processing**: Real-time landmark detection and gesture analysis
- **Analysis Trigger**: Gesture detection triggers AI analysis
- **Display**: Live video feed with overlaid analysis results

### 5. Video Analysis System
- **Smart Detection**: Analyzes only significant expression changes to reduce noise
- **Significance Threshold**: Configurable threshold for determining meaningful changes
- **Temporal Analysis**: Compares consecutive frames for landmark movement patterns
- **Batch Processing**: Processes uploaded videos efficiently with frame skipping
- **Timeline Generation**: Creates expression timeline with significant moments

### 6. Screen Recorder Mode
- **External Application Recording**: Captures entire screen for video calls (Zoom, Teams, etc.)
- **Live Analysis Popups**: Shows real-time emotion analysis in overlay windows
- **Major Change Detection**: Only triggers popups for significant expression changes
- **Configurable Sensitivity**: Adjustable threshold for analysis triggering
- **Independent Operation**: Runs separately from main Streamlit app
- **Cooldown System**: 10-second intervals between analyses to prevent spam
- **Desktop Integration**: Tkinter-based GUI with always-on-top positioning

## Data Flow

### Live Processing
1. **Video Input**: Camera captures live video frames
2. **Face Detection**: MediaPipe processes frames to extract facial landmarks
3. **Gesture Analysis**: Custom algorithms evaluate landmark positions against gesture definitions
4. **AI Processing**: Detected gestures are sent to OpenAI for emotional analysis
5. **Database Storage**: Analysis results are stored in PostgreSQL with session tracking
6. **Result Display**: Analysis results are shown in the Streamlit interface alongside live video

### Video Upload Processing
1. **Video Upload**: User uploads video file (MP4, AVI, MOV, MKV)
2. **Temporary Storage**: Video saved to temporary file for processing
3. **Frame Analysis**: Process frames with intelligent skipping for performance
4. **Significance Detection**: Compare consecutive frames for meaningful expression changes
5. **Selective Analysis**: Only analyze frames with significant changes (configurable threshold)
6. **Timeline Generation**: Create expression timeline with timestamps and significance scores
7. **Database Storage**: Save significant moments with video analysis type
8. **Summary Display**: Show dominant emotions, timeline, and detailed analysis

## External Dependencies

### Required Libraries
- **streamlit**: Web application framework
- **opencv-python (cv2)**: Computer vision and video processing
- **mediapipe**: Google's ML framework for face detection
- **openai**: Official OpenAI API client
- **psycopg2-binary**: PostgreSQL adapter for Python
- **sqlalchemy**: Database ORM for Python
- **mss**: Multi-platform screen capture library
- **pillow**: Image processing library
- **tkinter**: GUI framework (built-in with Python)
- **time**: Built-in Python module for timing operations

### API Dependencies
- **OpenAI API**: Requires valid API key stored in environment variable `OPENAI_API_KEY`
- **Model**: Specifically uses GPT-4o model (latest as of May 2024)
- **PostgreSQL Database**: Requires DATABASE_URL environment variable for data persistence

### Hardware Requirements
- **Camera**: Webcam or built-in camera for video input
- **Processing**: Real-time video processing capabilities

## Deployment Strategy

### Environment Setup
- **API Key Configuration**: OpenAI API key must be set as environment variable
- **Dependencies**: All required Python packages must be installed
- **Camera Access**: Application requires camera permissions

### Running the Application
- **Command**: `streamlit run app.py`
- **Access**: Web browser interface on local host
- **Real-time Operation**: Continuous video processing and analysis

### Error Handling
- **API Key Validation**: Application checks for OpenAI API key on startup
- **Graceful Degradation**: System handles missing dependencies or camera access issues
- **Rate Limiting**: OpenAI API calls are managed to prevent quota exceeded errors

### Performance Considerations
- **Real-time Processing**: Optimized for live video analysis
- **Memory Management**: Efficient handling of video frames and landmark data
- **API Usage**: Balanced between real-time responsiveness and API cost management