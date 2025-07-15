"""
Stress and Anxiety Level Estimation System
Analyzes forehead wrinkling, lip tension, and fidgeting patterns
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional
import math
from datetime import datetime

class StressAnalyzer:
    def __init__(self):
        """Initialize stress analyzer with MediaPipe Face Mesh and Pose"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Stress indicators history for temporal analysis
        self.stress_history = []
        self.max_history_length = 30
        
        # Forehead wrinkle detection points
        self.forehead_points = [
            # Horizontal forehead lines
            [10, 151], [9, 10], [151, 337], [299, 333],
            # Vertical frown lines
            [55, 285], [8, 9], [151, 9]
        ]
        
        # Lip tension analysis points
        self.lip_points = [
            [61, 291], [39, 181], [0, 17], [269, 405],
            [375, 321], [308, 324], [78, 95]
        ]
        
        # Eye strain indicators
        self.eye_strain_points = [
            [33, 133], [160, 144], [159, 145], [362, 398]
        ]
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        v1 = np.array([point1.x - point2.x, point1.y - point2.y])
        v2 = np.array([point3.x - point2.x, point3.y - point2.y])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        return np.degrees(angle)
    
    def analyze_forehead_tension(self, face_landmarks) -> Dict:
        """Analyze forehead wrinkling and tension patterns"""
        if not face_landmarks:
            return {'tension_score': 0.0, 'wrinkle_intensity': 0.0, 'indicators': []}
        
        landmarks = face_landmarks.landmark
        indicators = []
        tension_scores = []
        
        # Horizontal forehead lines analysis
        forehead_top = landmarks[10]
        forehead_mid = landmarks[151]
        forehead_sides = [landmarks[109], landmarks[338]]
        
        # Measure vertical compression (wrinkle formation)
        vertical_compression = abs(forehead_top.y - forehead_mid.y)
        if vertical_compression < 0.02:
            tension_scores.append(0.8)
            indicators.append("horizontal_forehead_lines")
        
        # Frown line analysis (vertical lines between eyebrows)
        left_brow = landmarks[55]
        right_brow = landmarks[285]
        center_brow = landmarks[9]
        
        # Distance between inner eyebrows
        brow_distance = self.calculate_distance(left_brow, right_brow)
        if brow_distance < 0.045:
            tension_scores.append(0.9)
            indicators.append("frown_lines")
        
        # Eyebrow position analysis
        brow_height = (left_brow.y + right_brow.y) / 2
        eye_height = (landmarks[159].y + landmarks[386].y) / 2
        
        if brow_height < eye_height - 0.035:
            tension_scores.append(0.7)
            indicators.append("raised_eyebrows")
        elif brow_height > eye_height - 0.015:
            tension_scores.append(0.6)
            indicators.append("lowered_eyebrows")
        
        # Forehead muscle tension
        forehead_width = abs(landmarks[109].x - landmarks[338].x)
        if forehead_width < 0.12:
            tension_scores.append(0.5)
            indicators.append("forehead_compression")
        
        tension_score = np.mean(tension_scores) if tension_scores else 0.0
        wrinkle_intensity = min(len(indicators) * 0.25, 1.0)
        
        return {
            'tension_score': tension_score,
            'wrinkle_intensity': wrinkle_intensity,
            'indicators': indicators,
            'brow_distance': brow_distance,
            'vertical_compression': vertical_compression
        }
    
    def analyze_lip_tension(self, face_landmarks) -> Dict:
        """Analyze lip tension and mouth stress indicators"""
        if not face_landmarks:
            return {'tension_score': 0.0, 'compression': 0.0, 'indicators': []}
        
        landmarks = face_landmarks.landmark
        indicators = []
        tension_scores = []
        
        # Lip compression analysis
        upper_lip = landmarks[13]
        lower_lip = landmarks[14]
        lip_separation = abs(upper_lip.y - lower_lip.y)
        
        if lip_separation < 0.008:
            tension_scores.append(0.8)
            indicators.append("lip_compression")
        
        # Lip corner tension
        left_corner = landmarks[61]
        right_corner = landmarks[291]
        lip_width = abs(left_corner.x - right_corner.x)
        
        if lip_width < 0.045:
            tension_scores.append(0.7)
            indicators.append("lip_pursing")
        
        # Mouth asymmetry (stress indicator)
        mouth_center = landmarks[13]
        left_distance = abs(left_corner.x - mouth_center.x)
        right_distance = abs(right_corner.x - mouth_center.x)
        asymmetry = abs(left_distance - right_distance)
        
        if asymmetry > 0.015:
            tension_scores.append(0.6)
            indicators.append("mouth_asymmetry")
        
        # Jaw tension (affects lip area)
        jaw_left = landmarks[172]
        jaw_right = landmarks[397]
        jaw_width = abs(jaw_left.x - jaw_right.x)
        
        if jaw_width < 0.08:
            tension_scores.append(0.5)
            indicators.append("jaw_tension")
        
        # Lip color changes (pale lips from tension)
        # This would require color analysis in actual implementation
        
        tension_score = np.mean(tension_scores) if tension_scores else 0.0
        compression = 1.0 - (lip_separation / 0.02) if lip_separation < 0.02 else 0.0
        
        return {
            'tension_score': tension_score,
            'compression': compression,
            'indicators': indicators,
            'lip_separation': lip_separation,
            'lip_width': lip_width,
            'asymmetry': asymmetry
        }
    
    def analyze_fidgeting(self, pose_landmarks, hand_landmarks) -> Dict:
        """Analyze fidgeting and restless movement patterns"""
        indicators = []
        fidget_scores = []
        
        # Hand fidgeting analysis
        if hand_landmarks:
            for hand in hand_landmarks:
                # Rapid hand movements
                thumb_tip = hand.landmark[4]
                index_tip = hand.landmark[8]
                
                # Finger spacing (nervous finger movements)
                finger_spacing = self.calculate_distance(thumb_tip, index_tip)
                if finger_spacing < 0.05:
                    fidget_scores.append(0.7)
                    indicators.append("finger_tension")
        
        # Body fidgeting analysis
        if pose_landmarks:
            landmarks = pose_landmarks.landmark
            
            # Shoulder tension
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            shoulder_height_diff = abs(left_shoulder.y - right_shoulder.y)
            
            if shoulder_height_diff > 0.03:
                fidget_scores.append(0.6)
                indicators.append("shoulder_tension")
            
            # Neck tension
            nose = landmarks[0]
            neck = landmarks[1]
            neck_angle = abs(nose.y - neck.y)
            
            if neck_angle > 0.15:
                fidget_scores.append(0.5)
                indicators.append("neck_strain")
        
        # Add temporal analysis for movement patterns
        if len(self.stress_history) > 5:
            recent_scores = [h.get('fidget_score', 0) for h in self.stress_history[-5:]]
            if np.std(recent_scores) > 0.2:
                fidget_scores.append(0.8)
                indicators.append("restless_movement")
        
        fidget_score = np.mean(fidget_scores) if fidget_scores else 0.0
        
        return {
            'fidget_score': fidget_score,
            'indicators': indicators,
            'movement_patterns': len(indicators)
        }
    
    def analyze_eye_strain(self, face_landmarks) -> Dict:
        """Analyze eye strain indicators"""
        if not face_landmarks:
            return {'strain_score': 0.0, 'indicators': []}
        
        landmarks = face_landmarks.landmark
        indicators = []
        strain_scores = []
        
        # Eye opening analysis
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]
        
        left_eye_opening = abs(left_eye_top.y - left_eye_bottom.y)
        right_eye_opening = abs(right_eye_top.y - right_eye_bottom.y)
        
        # Squinting detection
        avg_eye_opening = (left_eye_opening + right_eye_opening) / 2
        if avg_eye_opening < 0.012:
            strain_scores.append(0.8)
            indicators.append("squinting")
        
        # Eye asymmetry
        eye_asymmetry = abs(left_eye_opening - right_eye_opening)
        if eye_asymmetry > 0.008:
            strain_scores.append(0.6)
            indicators.append("eye_asymmetry")
        
        # Eyelid tension
        left_eyelid = landmarks[33]
        right_eyelid = landmarks[362]
        eyelid_height = (left_eyelid.y + right_eyelid.y) / 2
        
        if eyelid_height < landmarks[10].y - 0.08:
            strain_scores.append(0.5)
            indicators.append("eyelid_tension")
        
        strain_score = np.mean(strain_scores) if strain_scores else 0.0
        
        return {
            'strain_score': strain_score,
            'indicators': indicators,
            'eye_opening': avg_eye_opening
        }
    
    def calculate_stress_level(self, forehead_analysis: Dict, lip_analysis: Dict, 
                             fidget_analysis: Dict, eye_analysis: Dict) -> Dict:
        """Calculate overall stress level from all indicators"""
        
        # Weighted scoring system
        weights = {
            'forehead': 0.35,  # Forehead tension is a strong stress indicator
            'lip': 0.25,       # Lip tension is moderate indicator
            'fidget': 0.25,    # Fidgeting is moderate indicator
            'eye': 0.15        # Eye strain is supporting indicator
        }
        
        # Calculate weighted stress score
        stress_components = {
            'forehead': forehead_analysis['tension_score'],
            'lip': lip_analysis['tension_score'],
            'fidget': fidget_analysis['fidget_score'],
            'eye': eye_analysis['strain_score']
        }
        
        weighted_score = sum(
            stress_components[component] * weights[component] 
            for component in stress_components
        )
        
        # Convert to percentage
        stress_percentage = min(int(weighted_score * 100), 100)
        
        # Determine stress level category
        if stress_percentage >= 80:
            stress_level = "Very High"
            stress_color = "#FF4444"
        elif stress_percentage >= 60:
            stress_level = "High"
            stress_color = "#FF8800"
        elif stress_percentage >= 40:
            stress_level = "Moderate"
            stress_color = "#FFCC00"
        elif stress_percentage >= 20:
            stress_level = "Low"
            stress_color = "#88CC00"
        else:
            stress_level = "Very Low"
            stress_color = "#44CC44"
        
        # Collect all indicators
        all_indicators = []
        all_indicators.extend(forehead_analysis['indicators'])
        all_indicators.extend(lip_analysis['indicators'])
        all_indicators.extend(fidget_analysis['indicators'])
        all_indicators.extend(eye_analysis['indicators'])
        
        # Generate recommendations
        recommendations = self.generate_stress_recommendations(stress_percentage, all_indicators)
        
        return {
            'stress_percentage': stress_percentage,
            'stress_level': stress_level,
            'stress_color': stress_color,
            'components': stress_components,
            'indicators': all_indicators,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def generate_stress_recommendations(self, stress_percentage: int, indicators: List[str]) -> List[str]:
        """Generate personalized stress reduction recommendations"""
        recommendations = []
        
        if stress_percentage >= 70:
            recommendations.append("Take deep breaths - try 4-7-8 breathing technique")
            recommendations.append("Consider a 5-minute break from current activity")
        
        if "frown_lines" in indicators or "forehead_compression" in indicators:
            recommendations.append("Consciously relax your forehead muscles")
            recommendations.append("Try gentle forehead massage")
        
        if "lip_compression" in indicators or "jaw_tension" in indicators:
            recommendations.append("Relax your jaw and lips")
            recommendations.append("Do gentle jaw stretches")
        
        if "fidget_score" in indicators or "restless_movement" in indicators:
            recommendations.append("Try progressive muscle relaxation")
            recommendations.append("Take a short walk if possible")
        
        if "squinting" in indicators or "eye_strain" in indicators:
            recommendations.append("Rest your eyes - look at something distant")
            recommendations.append("Adjust lighting or screen brightness")
        
        if stress_percentage >= 50:
            recommendations.append("Consider stress management techniques")
            recommendations.append("Stay hydrated and maintain good posture")
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def analyze_stress_level(self, frame) -> Dict:
        """Main function to analyze stress level from video frame"""
        if frame is None:
            return {'error': 'No frame provided'}
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        face_results = self.face_mesh.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        
        # Analyze different stress indicators
        forehead_analysis = self.analyze_forehead_tension(face_results.multi_face_landmarks[0] if face_results.multi_face_landmarks else None)
        lip_analysis = self.analyze_lip_tension(face_results.multi_face_landmarks[0] if face_results.multi_face_landmarks else None)
        fidget_analysis = self.analyze_fidgeting(pose_results.pose_landmarks, hand_results.multi_hand_landmarks)
        eye_analysis = self.analyze_eye_strain(face_results.multi_face_landmarks[0] if face_results.multi_face_landmarks else None)
        
        # Calculate overall stress level
        stress_analysis = self.calculate_stress_level(forehead_analysis, lip_analysis, fidget_analysis, eye_analysis)
        
        # Add detailed breakdown
        stress_analysis['detailed_analysis'] = {
            'forehead': forehead_analysis,
            'lip': lip_analysis,
            'fidget': fidget_analysis,
            'eye': eye_analysis
        }
        
        # Update history
        self.stress_history.append(stress_analysis)
        if len(self.stress_history) > self.max_history_length:
            self.stress_history.pop(0)
        
        return stress_analysis
    
    def get_stress_trend(self) -> Dict:
        """Get stress level trend over time"""
        if len(self.stress_history) < 2:
            return {'trend': 'insufficient_data', 'direction': 'stable'}
        
        recent_scores = [h['stress_percentage'] for h in self.stress_history[-5:]]
        older_scores = [h['stress_percentage'] for h in self.stress_history[-10:-5]] if len(self.stress_history) >= 10 else recent_scores
        
        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)
        
        if recent_avg > older_avg + 10:
            trend = 'increasing'
        elif recent_avg < older_avg - 10:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'recent_average': recent_avg,
            'change': recent_avg - older_avg,
            'direction': trend
        }
    
    def reset_history(self):
        """Reset stress analysis history"""
        self.stress_history = []