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

## Data Flow

1. **Video Input**: Camera captures live video frames
2. **Face Detection**: MediaPipe processes frames to extract facial landmarks
3. **Gesture Analysis**: Custom algorithms evaluate landmark positions against gesture definitions
4. **AI Processing**: Detected gestures are sent to OpenAI for emotional analysis
5. **Result Display**: Analysis results are shown in the Streamlit interface alongside live video

## External Dependencies

### Required Libraries
- **streamlit**: Web application framework
- **opencv-python (cv2)**: Computer vision and video processing
- **mediapipe**: Google's ML framework for face detection
- **openai**: Official OpenAI API client
- **time**: Built-in Python module for timing operations

### API Dependencies
- **OpenAI API**: Requires valid API key stored in environment variable `OPENAI_API_KEY`
- **Model**: Specifically uses GPT-4o model (latest as of May 2024)

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