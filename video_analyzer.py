import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os
from typing import List, Dict, Tuple, Optional
import json
from openai_analyzer import analyze_expression

class VideoEmotionAnalyzer:
    def __init__(self, significance_threshold: float = 0.15):
        """
        Initialize video emotion analyzer
        
        Args:
            significance_threshold: Minimum change threshold to trigger analysis
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=5,  # Support up to 5 faces
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.significance_threshold = significance_threshold
        self.previous_landmarks = None
        self.previous_expressions = set()
        self.frame_count = 0
        self.analysis_history = []
        self.last_analysis_time = 0
        self.min_time_between_analyses = 1.0  # Minimum 1 second between analyses
        
        # Define key facial landmarks for expression analysis
        self.key_landmarks = {
            'mouth_corners': [61, 291],
            'eyebrows': [65, 295],
            'eyes': [159, 386, 145, 374],
            'nose': [6, 168],
            'jaw': [152, 172, 397]
        }
    
    def calculate_landmark_distance(self, landmarks1, landmarks2) -> float:
        """Calculate normalized distance between two landmark sets"""
        if landmarks1 is None or landmarks2 is None:
            return float('inf')
        
        total_distance = 0
        key_points = 0
        
        for region, indices in self.key_landmarks.items():
            for idx in indices:
                if idx < len(landmarks1) and idx < len(landmarks2):
                    p1 = landmarks1[idx]
                    p2 = landmarks2[idx]
                    
                    # Calculate euclidean distance
                    dist = np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
                    total_distance += dist
                    key_points += 1
        
        return total_distance / key_points if key_points > 0 else 0
    
    def _calculate_smile_confidence(self, landmarks) -> float:
        """Calculate confidence score for smile detection"""
        mouth_width = abs(landmarks[61].x - landmarks[291].x)
        mouth_curve = (landmarks[13].y - landmarks[14].y) * 0.5
        confidence = min(1.0, max(0.0, (mouth_width - 0.04) * 10 + mouth_curve * 5))
        return confidence if confidence > 0.3 else 0.0
    
    def _calculate_frown_confidence(self, landmarks) -> float:
        """Calculate confidence score for frown detection"""
        mouth_width = abs(landmarks[61].x - landmarks[291].x)
        mouth_curve = (landmarks[14].y - landmarks[13].y) * 0.5
        confidence = min(1.0, max(0.0, (0.045 - mouth_width) * 10 + mouth_curve * 5))
        return confidence if confidence > 0.3 else 0.0
    
    def _calculate_raised_eyebrows_confidence(self, landmarks) -> float:
        """Calculate confidence score for raised eyebrows"""
        eyebrow_height = (landmarks[159].y - landmarks[65].y) + (landmarks[386].y - landmarks[295].y)
        confidence = min(1.0, max(0.0, (eyebrow_height - 0.03) * 15))
        return confidence if confidence > 0.3 else 0.0
    
    def _calculate_squint_confidence(self, landmarks) -> float:
        """Calculate confidence score for squinting"""
        eye_openness = abs(landmarks[159].y - landmarks[145].y) + abs(landmarks[386].y - landmarks[374].y)
        confidence = min(1.0, max(0.0, (0.015 - eye_openness) * 20))
        return confidence if confidence > 0.3 else 0.0
    
    def _calculate_mouth_open_confidence(self, landmarks) -> float:
        """Calculate confidence score for mouth open"""
        mouth_openness = abs(landmarks[13].y - landmarks[14].y)
        confidence = min(1.0, max(0.0, (mouth_openness - 0.02) * 20))
        return confidence if confidence > 0.3 else 0.0
    
    def _calculate_brow_furrow_confidence(self, landmarks) -> float:
        """Calculate confidence score for brow furrow"""
        brow_distance = abs(landmarks[65].x - landmarks[295].x)
        confidence = min(1.0, max(0.0, (0.035 - brow_distance) * 15))
        return confidence if confidence > 0.3 else 0.0
    
    def _calculate_surprise_confidence(self, landmarks) -> float:
        """Calculate confidence score for surprise expression"""
        eyebrow_height = (landmarks[159].y - landmarks[65].y) + (landmarks[386].y - landmarks[295].y)
        mouth_openness = abs(landmarks[13].y - landmarks[14].y)
        confidence = min(1.0, max(0.0, (eyebrow_height - 0.05) * 10 + (mouth_openness - 0.03) * 10))
        return confidence if confidence > 0.3 else 0.0
    
    def detect_expressions_with_confidence(self, landmarks) -> List[Dict[str, float]]:
        """Detect facial expressions from landmarks with confidence scores"""
        expressions = []
        
        # Define gesture detection functions with confidence calculation
        gesture_functions = {
            "smile": lambda lm: self._calculate_smile_confidence(lm),
            "frown": lambda lm: self._calculate_frown_confidence(lm),
            "raised_eyebrows": lambda lm: self._calculate_raised_eyebrows_confidence(lm),
            "squint": lambda lm: self._calculate_squint_confidence(lm),
            "mouth_open": lambda lm: self._calculate_mouth_open_confidence(lm),
            "brow_furrow": lambda lm: self._calculate_brow_furrow_confidence(lm),
            "surprise": lambda lm: self._calculate_surprise_confidence(lm),
        }
        
        # Detect expressions with confidence scores
        for gesture_name, confidence_func in gesture_functions.items():
            try:
                confidence = confidence_func(landmarks)
                if confidence > 0.0:
                    expressions.append({
                        "name": gesture_name,
                        "confidence": confidence
                    })
            except Exception as e:
                # Skip gestures that fail due to missing landmarks
                continue
        
        return expressions
    
    def detect_expressions(self, landmarks) -> List[str]:
        """Detect facial expressions from landmarks (legacy method)"""
        expressions_with_confidence = self.detect_expressions_with_confidence(landmarks)
        return [expr["name"] for expr in expressions_with_confidence if expr["confidence"] > 0.5]
    
    def is_significant_change(self, current_landmarks, current_expressions, timestamp) -> bool:
        """Determine if there's a significant change in expression"""
        # Check temporal constraint - prevent analyses too close together
        if timestamp - self.last_analysis_time < self.min_time_between_analyses:
            return False
        
        if self.previous_landmarks is None:
            # Only return True if there are actual expressions detected
            return len(current_expressions) > 0
        
        # Calculate geometric distance between landmark sets
        landmark_distance = self.calculate_landmark_distance(
            self.previous_landmarks, current_landmarks
        )
        
        # Check for expression changes
        current_expr_set = set(current_expressions)
        previous_expr_set = self.previous_expressions
        
        # Significant change if:
        # 1. Large geometric change in facial landmarks AND expressions exist
        # 2. New expressions appeared or disappeared AND they are meaningful
        # 3. Must have expressions to be considered significant
        # 4. Must have substantial differences, not just minor variations
        
        geometric_change = landmark_distance > self.significance_threshold
        expression_change = len(current_expr_set.symmetric_difference(previous_expr_set)) > 1  # Need more than 1 change
        has_expressions = len(current_expressions) > 0
        
        # Additional check: avoid similar expressions (e.g., just "smile" variations)
        substantial_change = geometric_change and expression_change
        
        return substantial_change and has_expressions
    
    def analyze_video_frame(self, frame, timestamp: float) -> Optional[Dict]:
        """
        Analyze a single video frame using AI vision analysis
        Detects expressions in every frame regardless of significance
        
        Args:
            frame: OpenCV frame
            timestamp: Frame timestamp in seconds
            
        Returns:
            Analysis result if face detected, None otherwise
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # Check temporal constraint - prevent analyses too close together
        if timestamp - self.last_analysis_time < self.min_time_between_analyses:
            self.frame_count += 1
            return None
        
        # Use AI vision analysis for accurate expression detection
        from ai_vision_analyzer import AIVisionAnalyzer
        ai_vision = AIVisionAnalyzer()
        
        # Analyze frame with AI vision
        ai_analysis = ai_vision.analyze_facial_expressions(rgb_frame)
        
        # Extract expressions and analysis from AI
        ai_expressions = ai_analysis.get('facial_expressions', [])
        analysis_text = ai_analysis.get('detailed_analysis', 'Neutral expression detected')
        emotional_state = ai_analysis.get('emotional_state', 'neutral')
        confidence_level = ai_analysis.get('confidence_level', 'low')
        
        # Calculate landmark change for reference
        landmark_change = self.calculate_landmark_distance(self.previous_landmarks, landmarks)
        
        # Create analysis result with proper emotional state
        final_expressions = ai_expressions if ai_expressions else [emotional_state]
        
        # Avoid defaulting to neutral - use emotional state if available
        if not final_expressions or (len(final_expressions) == 1 and final_expressions[0] == 'neutral'):
            final_expressions = [emotional_state if emotional_state != 'neutral' else 'calm']
        
        analysis_result = {
            'timestamp': timestamp,
            'expressions': final_expressions,
            'ai_analysis': analysis_text,
            'frame_number': self.frame_count,
            'emotional_state': emotional_state,
            'confidence_level': confidence_level,
            'significance_score': landmark_change if self.previous_landmarks else 1.0
        }
        
        self.analysis_history.append(analysis_result)
        
        # Update previous state and last analysis time
        self.last_analysis_time = timestamp
        self.previous_landmarks = landmarks
        self.previous_expressions = set(ai_expressions) if ai_expressions else set(['neutral'])
        
        self.frame_count += 1
        return analysis_result
    
    def process_video(self, video_path: str, max_analyses: int = 10, progress_callback=None) -> List[Dict]:
        """
        Process entire video and return significant moments using AI analysis
        
        Args:
            video_path: Path to video file
            max_analyses: Maximum number of analyses to perform
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of analysis results for significant moments
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        analyses = []
        frame_count = 0
        
        # For long videos, skip more frames to reduce processing time
        if duration > 300:  # 5 minutes
            frame_skip = max(1, int(fps * 5))  # Process every 5 seconds
        elif duration > 120:  # 2 minutes  
            frame_skip = max(1, int(fps * 3))  # Process every 3 seconds
        else:
            frame_skip = max(1, int(fps * 1.5))  # Process every 1.5 seconds
        
        # Jump to processing frames at intervals
        target_frames = list(range(0, total_frames, frame_skip))
        
        for i, target_frame in enumerate(target_frames):
            if len(analyses) >= max_analyses:
                break
                
            # Report progress
            if progress_callback:
                progress = min(100, int((i / len(target_frames)) * 100))
                progress_callback(progress)
                
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = cap.read()
            if not ret:
                continue
            
            timestamp = target_frame / fps
            
            # Only analyze if we have a face and sufficient time gap
            analysis = self.analyze_video_frame(frame, timestamp)
            if analysis:
                analyses.append(analysis)
        
        cap.release()
        
        # If no significant expressions were found, return empty list
        if not analyses:
            return []
        
        return analyses
    
    def get_video_summary(self) -> Dict:
        """Get summary of video analysis"""
        if not self.analysis_history:
            return {'total_analyses': 0, 'dominant_emotions': [], 'timeline': []}
        
        # Count expression frequencies
        expression_counts = {}
        for analysis in self.analysis_history:
            for expr in analysis['expressions']:
                expression_counts[expr] = expression_counts.get(expr, 0) + 1
        
        # Get dominant emotions
        dominant_emotions = sorted(
            expression_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            'total_analyses': len(self.analysis_history),
            'dominant_emotions': dominant_emotions,
            'timeline': [
                {
                    'timestamp': a['timestamp'],
                    'expressions': a['expressions'][:3],  # Top 3 expressions
                    'significance': a['significance_score']
                }
                for a in self.analysis_history
            ]
        }
    
    def reset(self):
        """Reset analyzer state for new video"""
        self.previous_landmarks = None
        self.previous_expressions = set()
        self.frame_count = 0
        self.analysis_history = []
        self.last_analysis_time = 0