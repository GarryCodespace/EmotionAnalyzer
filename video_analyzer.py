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
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.significance_threshold = significance_threshold
        self.previous_landmarks = None
        self.previous_expressions = set()
        self.frame_count = 0
        self.analysis_history = []
        
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
    
    def detect_expressions(self, landmarks) -> List[str]:
        """Detect facial expressions from landmarks"""
        expressions = []
        
        # Define gesture detection functions (subset of main gestures for video)
        gesture_functions = {
            "smile": lambda lm: abs(lm[61].x - lm[291].x) > 0.05,
            "frown": lambda lm: abs(lm[61].x - lm[291].x) < 0.035,
            "raised_eyebrows": lambda lm: (lm[159].y - lm[65].y) > 0.04,
            "squint": lambda lm: abs(lm[159].y - lm[145].y) < 0.01,
            "mouth_open": lambda lm: abs(lm[13].y - lm[14].y) > 0.04,
            "brow_furrow": lambda lm: abs(lm[65].x - lm[295].x) < 0.03,
            "surprise": lambda lm: (lm[159].y - lm[65].y) > 0.06 and abs(lm[13].y - lm[14].y) > 0.05,
            "concentration": lambda lm: abs(lm[65].x - lm[295].x) < 0.035 and abs(lm[159].y - lm[145].y) < 0.012,
            "confusion": lambda lm: (lm[159].y - lm[65].y) > 0.03 and abs(lm[61].x - lm[291].x) < 0.025,
            "contempt": lambda lm: abs(lm[61].y - lm[291].y) > 0.015,
            "disgust": lambda lm: lm[12].y < lm[15].y - 0.015 and abs(lm[6].y - lm[168].y) < 0.02,
            "fear": lambda lm: abs(lm[159].y - lm[145].y) > 0.025 and (lm[159].y - lm[65].y) > 0.04,
            "anger": lambda lm: abs(lm[65].x - lm[295].x) < 0.025 and abs(lm[61].x - lm[291].x) < 0.03,
            "sadness": lambda lm: lm[61].y > lm[13].y + 0.015 and lm[291].y > lm[13].y + 0.015,
            "joy": lambda lm: abs(lm[61].x - lm[291].x) > 0.07 and abs(lm[159].y - lm[145].y) > 0.02,
            "neutral": lambda lm: abs(lm[159].y - lm[145].y) > 0.015 and abs(lm[13].y - lm[14].y) > 0.01,
            "thinking": lambda lm: abs(lm[65].x - lm[295].x) < 0.04 and lm[13].y > lm[14].y + 0.015,
            "skeptical": lambda lm: (lm[159].y - lm[65].y) > 0.04 and abs(lm[61].x - lm[291].x) < 0.025,
            "amused": lambda lm: abs(lm[61].x - lm[291].x) > 0.06 and abs(lm[159].y - lm[145].y) < 0.015,
            "interested": lambda lm: (lm[159].y - lm[65].y) > 0.035 and lm[10].y < lm[152].y - 0.05
        }
        
        for expression, detector in gesture_functions.items():
            try:
                if detector(landmarks):
                    expressions.append(expression)
            except (IndexError, AttributeError):
                continue
        
        return expressions
    
    def is_significant_change(self, current_landmarks, current_expressions) -> bool:
        """Determine if there's a significant change in expression"""
        if self.previous_landmarks is None:
            return True
        
        # Calculate geometric distance between landmark sets
        landmark_distance = self.calculate_landmark_distance(
            self.previous_landmarks, current_landmarks
        )
        
        # Check for expression changes
        current_expr_set = set(current_expressions)
        previous_expr_set = self.previous_expressions
        
        # Significant change if:
        # 1. Large geometric change in facial landmarks
        # 2. New expressions appeared or disappeared
        # 3. Major expression category change
        
        geometric_change = landmark_distance > self.significance_threshold
        expression_change = len(current_expr_set.symmetric_difference(previous_expr_set)) > 0
        
        return geometric_change or expression_change
    
    def analyze_video_frame(self, frame, timestamp: float) -> Optional[Dict]:
        """
        Analyze a single video frame
        
        Args:
            frame: OpenCV frame
            timestamp: Frame timestamp in seconds
            
        Returns:
            Analysis result if significant change detected, None otherwise
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0].landmark
        current_expressions = self.detect_expressions(landmarks)
        
        # Check if this is a significant change
        if self.is_significant_change(landmarks, current_expressions):
            # Generate AI analysis
            if current_expressions:
                ai_analysis = analyze_expression(", ".join(current_expressions))
                
                analysis_result = {
                    'timestamp': timestamp,
                    'expressions': current_expressions,
                    'ai_analysis': ai_analysis,
                    'frame_number': self.frame_count,
                    'significance_score': self.calculate_landmark_distance(
                        self.previous_landmarks, landmarks
                    ) if self.previous_landmarks else 1.0
                }
                
                self.analysis_history.append(analysis_result)
                
                # Update previous state
                self.previous_landmarks = landmarks
                self.previous_expressions = set(current_expressions)
                
                return analysis_result
        
        self.frame_count += 1
        return None
    
    def process_video(self, video_path: str, max_analyses: int = 20) -> List[Dict]:
        """
        Process entire video and return significant moments
        
        Args:
            video_path: Path to video file
            max_analyses: Maximum number of analyses to perform
            
        Returns:
            List of analysis results for significant moments
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        analyses = []
        frame_count = 0
        
        # Process every nth frame to optimize performance
        frame_skip = max(1, total_frames // (max_analyses * 3))
        
        while cap.isOpened() and len(analyses) < max_analyses:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames for performance
            if frame_count % frame_skip == 0:
                timestamp = frame_count / fps
                
                analysis = self.analyze_video_frame(frame, timestamp)
                if analysis:
                    analyses.append(analysis)
            
            frame_count += 1
        
        cap.release()
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