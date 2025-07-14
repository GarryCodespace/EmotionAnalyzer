import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple
import math

class BodyLanguageAnalyzer:
    def __init__(self):
        """Initialize body language analyzer with MediaPipe Pose and Hands"""
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize pose detection
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize hand detection
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Body language patterns with confidence calculations
        self.body_patterns = {
            "crossed_arms": self._detect_crossed_arms,
            "hands_on_hips": self._detect_hands_on_hips,
            "arms_open": self._detect_open_arms,
            "defensive_posture": self._detect_defensive_posture,
            "confident_stance": self._detect_confident_stance,
            "leaning_forward": self._detect_leaning_forward,
            "leaning_back": self._detect_leaning_back,
            "crossed_legs": self._detect_crossed_legs,
            "wide_stance": self._detect_wide_stance,
            "closed_stance": self._detect_closed_stance,
            "hand_to_face": self._detect_hand_to_face,
            "hand_to_neck": self._detect_hand_to_neck,
            "hand_to_chest": self._detect_hand_to_chest,
            "covering_mouth": self._detect_covering_mouth,
            "covering_eyes": self._detect_covering_eyes,
            "fidgeting": self._detect_fidgeting,
            "pointing": self._detect_pointing,
            "open_palms": self._detect_open_palms,
            "clenched_fists": self._detect_clenched_fists,
            "self_soothing": self._detect_self_soothing,
            "territorial_stance": self._detect_territorial_stance,
            "submissive_posture": self._detect_submissive_posture,
            "power_pose": self._detect_power_pose,
            "anxiety_indicators": self._detect_anxiety_indicators,
            "engagement_signals": self._detect_engagement_signals
        }
        
        self.previous_landmarks = None
        self.gesture_history = []
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        try:
            a = np.array([point1.x, point1.y])
            b = np.array([point2.x, point2.y])
            c = np.array([point3.x, point3.y])
            
            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)
            
            if angle > 180.0:
                angle = 360 - angle
                
            return angle
        except:
            return 0
    
    def calculate_distance(self, point1, point2):
        """Calculate normalized distance between two points"""
        try:
            return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
        except:
            return 0
    
    def _detect_crossed_arms(self, pose_landmarks, hand_landmarks) -> float:
        """Detect crossed arms posture"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_elbow = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ELBOW]
            right_elbow = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
            
            # Check if wrists are crossed over body midline
            wrist_cross = abs(left_wrist.x - right_wrist.x) < 0.3
            
            # Check if elbows are positioned defensively
            elbow_height = abs(left_elbow.y - right_elbow.y) < 0.1
            
            # Calculate arm angles
            left_arm_angle = self.calculate_angle(
                pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER],
                left_elbow,
                left_wrist
            )
            right_arm_angle = self.calculate_angle(
                pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER],
                right_elbow,
                right_wrist
            )
            
            # Crossed arms typically have specific angle ranges
            arm_angles_crossed = (70 < left_arm_angle < 110) and (70 < right_arm_angle < 110)
            
            confidence = 0.0
            if wrist_cross:
                confidence += 0.4
            if elbow_height:
                confidence += 0.3
            if arm_angles_crossed:
                confidence += 0.3
                
            return min(confidence, 1.0)
        except:
            return 0.0
    
    def _detect_hands_on_hips(self, pose_landmarks, hand_landmarks) -> float:
        """Detect hands on hips posture"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            # Check if wrists are near hip level
            left_hip_distance = self.calculate_distance(left_wrist, left_hip)
            right_hip_distance = self.calculate_distance(right_wrist, right_hip)
            
            # Hands on hips typically have wrists close to hip area
            left_on_hip = left_hip_distance < 0.15
            right_on_hip = right_hip_distance < 0.15
            
            confidence = 0.0
            if left_on_hip:
                confidence += 0.5
            if right_on_hip:
                confidence += 0.5
                
            return confidence
        except:
            return 0.0
    
    def _detect_open_arms(self, pose_landmarks, hand_landmarks) -> float:
        """Detect open, welcoming arm posture"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            # Check if arms are spread wide
            arm_width = abs(left_wrist.x - right_wrist.x)
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            
            # Open arms should be wider than shoulders
            arms_open = arm_width > shoulder_width * 1.5
            
            # Check if arms are at comfortable height (not too high or low)
            arm_height_good = (abs(left_wrist.y - left_shoulder.y) < 0.3 and 
                             abs(right_wrist.y - right_shoulder.y) < 0.3)
            
            confidence = 0.0
            if arms_open:
                confidence += 0.6
            if arm_height_good:
                confidence += 0.4
                
            return confidence
        except:
            return 0.0
    
    def _detect_defensive_posture(self, pose_landmarks, hand_landmarks) -> float:
        """Detect defensive body language"""
        if not pose_landmarks:
            return 0.0
            
        confidence = 0.0
        
        # Check for crossed arms component
        crossed_arms_conf = self._detect_crossed_arms(pose_landmarks, hand_landmarks)
        confidence += crossed_arms_conf * 0.4
        
        # Check for hunched shoulders
        try:
            left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            
            # Hunched shoulders are higher relative to nose
            shoulder_height = (left_shoulder.y + right_shoulder.y) / 2
            hunched = shoulder_height < nose.y - 0.1
            
            if hunched:
                confidence += 0.3
        except:
            pass
        
        # Check for closed leg stance
        try:
            left_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            
            ankle_distance = abs(left_ankle.x - right_ankle.x)
            if ankle_distance < 0.1:  # Very close together
                confidence += 0.3
        except:
            pass
            
        return min(confidence, 1.0)
    
    def _detect_confident_stance(self, pose_landmarks, hand_landmarks) -> float:
        """Detect confident body language"""
        if not pose_landmarks:
            return 0.0
            
        confidence = 0.0
        
        # Check for upright posture
        try:
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            left_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            hip_center = ((left_hip.x + right_hip.x) / 2, (left_hip.y + right_hip.y) / 2)
            
            # Upright posture: nose should be roughly above hip center
            posture_alignment = abs(nose.x - hip_center[0]) < 0.1
            
            if posture_alignment:
                confidence += 0.4
        except:
            pass
        
        # Check for hands on hips (confidence gesture)
        hands_on_hips_conf = self._detect_hands_on_hips(pose_landmarks, hand_landmarks)
        confidence += hands_on_hips_conf * 0.3
        
        # Check for wide stance
        wide_stance_conf = self._detect_wide_stance(pose_landmarks, hand_landmarks)
        confidence += wide_stance_conf * 0.3
        
        return min(confidence, 1.0)
    
    def _detect_leaning_forward(self, pose_landmarks, hand_landmarks) -> float:
        """Detect forward leaning posture (engagement/aggression)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            left_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            hip_center_x = (left_hip.x + right_hip.x) / 2
            
            # Forward lean: nose is significantly forward of hip center
            forward_lean = nose.x > hip_center_x + 0.1
            
            return 0.8 if forward_lean else 0.0
        except:
            return 0.0
    
    def _detect_leaning_back(self, pose_landmarks, hand_landmarks) -> float:
        """Detect backward leaning posture (disengagement/relaxation)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            left_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            hip_center_x = (left_hip.x + right_hip.x) / 2
            
            # Backward lean: nose is significantly behind hip center
            backward_lean = nose.x < hip_center_x - 0.1
            
            return 0.8 if backward_lean else 0.0
        except:
            return 0.0
    
    def _detect_crossed_legs(self, pose_landmarks, hand_landmarks) -> float:
        """Detect crossed legs posture"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_knee = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE]
            right_knee = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_KNEE]
            left_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            
            # Check if legs are crossed by looking at knee-ankle alignment
            left_leg_angle = abs(left_knee.x - left_ankle.x)
            right_leg_angle = abs(right_knee.x - right_ankle.x)
            
            # Crossed legs typically have different angles
            legs_crossed = abs(left_leg_angle - right_leg_angle) > 0.1
            
            # Also check if ankles are close together
            ankle_distance = abs(left_ankle.x - right_ankle.x)
            ankles_close = ankle_distance < 0.15
            
            confidence = 0.0
            if legs_crossed:
                confidence += 0.5
            if ankles_close:
                confidence += 0.5
                
            return confidence
        except:
            return 0.0
    
    def _detect_wide_stance(self, pose_landmarks, hand_landmarks) -> float:
        """Detect wide leg stance (confidence/dominance)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            ankle_width = abs(left_ankle.x - right_ankle.x)
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            
            # Wide stance: ankle width is significantly larger than shoulder width
            wide_stance = ankle_width > shoulder_width * 1.3
            
            return 0.8 if wide_stance else 0.0
        except:
            return 0.0
    
    def _detect_closed_stance(self, pose_landmarks, hand_landmarks) -> float:
        """Detect closed/narrow leg stance"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            
            ankle_distance = abs(left_ankle.x - right_ankle.x)
            
            # Closed stance: ankles are very close together
            closed_stance = ankle_distance < 0.08
            
            return 0.8 if closed_stance else 0.0
        except:
            return 0.0
    
    def _detect_hand_to_face(self, pose_landmarks, hand_landmarks) -> float:
        """Detect hand touching face (thinking/stress/deception)"""
        if not pose_landmarks or not hand_landmarks:
            return 0.0
            
        try:
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            # Check if either wrist is near the face
            left_face_distance = self.calculate_distance(left_wrist, nose)
            right_face_distance = self.calculate_distance(right_wrist, nose)
            
            near_face = left_face_distance < 0.2 or right_face_distance < 0.2
            
            return 0.7 if near_face else 0.0
        except:
            return 0.0
    
    def _detect_hand_to_neck(self, pose_landmarks, hand_landmarks) -> float:
        """Detect hand touching neck (stress/discomfort)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            # Use shoulder as neck approximation
            left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            neck_area = ((left_shoulder.x + right_shoulder.x) / 2, 
                        (left_shoulder.y + right_shoulder.y) / 2 - 0.1)
            
            # Check if either wrist is near neck area
            left_neck_distance = math.sqrt((left_wrist.x - neck_area[0])**2 + 
                                         (left_wrist.y - neck_area[1])**2)
            right_neck_distance = math.sqrt((right_wrist.x - neck_area[0])**2 + 
                                          (right_wrist.y - neck_area[1])**2)
            
            near_neck = left_neck_distance < 0.15 or right_neck_distance < 0.15
            
            return 0.7 if near_neck else 0.0
        except:
            return 0.0
    
    def _detect_hand_to_chest(self, pose_landmarks, hand_landmarks) -> float:
        """Detect hand on chest (sincerity/protection)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            chest_area = ((left_shoulder.x + right_shoulder.x) / 2, 
                         (left_shoulder.y + right_shoulder.y) / 2 + 0.1)
            
            # Check if either wrist is near chest area
            left_chest_distance = math.sqrt((left_wrist.x - chest_area[0])**2 + 
                                          (left_wrist.y - chest_area[1])**2)
            right_chest_distance = math.sqrt((right_wrist.x - chest_area[0])**2 + 
                                           (right_wrist.y - chest_area[1])**2)
            
            near_chest = left_chest_distance < 0.15 or right_chest_distance < 0.15
            
            return 0.7 if near_chest else 0.0
        except:
            return 0.0
    
    def _detect_covering_mouth(self, pose_landmarks, hand_landmarks) -> float:
        """Detect hand covering mouth (deception/surprise)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            # Approximate mouth position relative to nose
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            mouth_area = (nose.x, nose.y + 0.05)
            
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            # Check if either wrist is near mouth area
            left_mouth_distance = math.sqrt((left_wrist.x - mouth_area[0])**2 + 
                                          (left_wrist.y - mouth_area[1])**2)
            right_mouth_distance = math.sqrt((right_wrist.x - mouth_area[0])**2 + 
                                           (right_wrist.y - mouth_area[1])**2)
            
            covering_mouth = left_mouth_distance < 0.1 or right_mouth_distance < 0.1
            
            return 0.8 if covering_mouth else 0.0
        except:
            return 0.0
    
    def _detect_covering_eyes(self, pose_landmarks, hand_landmarks) -> float:
        """Detect hand covering eyes (shame/embarrassment)"""
        if not pose_landmarks:
            return 0.0
            
        try:
            # Approximate eye area relative to nose
            nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
            eye_area = (nose.x, nose.y - 0.03)
            
            left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            # Check if either wrist is near eye area
            left_eye_distance = math.sqrt((left_wrist.x - eye_area[0])**2 + 
                                        (left_wrist.y - eye_area[1])**2)
            right_eye_distance = math.sqrt((right_wrist.x - eye_area[0])**2 + 
                                         (right_wrist.y - eye_area[1])**2)
            
            covering_eyes = left_eye_distance < 0.1 or right_eye_distance < 0.1
            
            return 0.8 if covering_eyes else 0.0
        except:
            return 0.0
    
    def _detect_fidgeting(self, pose_landmarks, hand_landmarks) -> float:
        """Detect fidgeting movements (anxiety/nervousness)"""
        if not pose_landmarks or not self.previous_landmarks:
            return 0.0
            
        try:
            # Compare current hand positions with previous
            current_left_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            current_right_wrist = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            prev_left_wrist = self.previous_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
            prev_right_wrist = self.previous_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
            
            # Calculate movement
            left_movement = self.calculate_distance(current_left_wrist, prev_left_wrist)
            right_movement = self.calculate_distance(current_right_wrist, prev_right_wrist)
            
            # Fidgeting involves small but frequent movements
            total_movement = left_movement + right_movement
            
            # Store movement history for pattern detection
            self.gesture_history.append(total_movement)
            if len(self.gesture_history) > 10:
                self.gesture_history.pop(0)
            
            # Check for consistent small movements
            if len(self.gesture_history) >= 5:
                avg_movement = sum(self.gesture_history[-5:]) / 5
                if 0.02 < avg_movement < 0.1:  # Small but consistent movement
                    return 0.6
            
            return 0.0
        except:
            return 0.0
    
    def _detect_pointing(self, pose_landmarks, hand_landmarks) -> float:
        """Detect pointing gesture (direction/emphasis)"""
        if not hand_landmarks:
            return 0.0
            
        try:
            confidence = 0.0
            
            for hand_landmark in hand_landmarks:
                # Check if index finger is extended
                landmarks = hand_landmark.landmark
                
                # Index finger tip and joints
                index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                index_pip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP]
                index_mcp = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_MCP]
                
                # Check if index finger is extended (roughly straight)
                finger_length = self.calculate_distance(index_tip, index_mcp)
                joint_distance = self.calculate_distance(index_tip, index_pip)
                
                # Pointing typically has extended index finger
                if finger_length > 0.15 and joint_distance > 0.08:
                    confidence += 0.5
            
            return min(confidence, 1.0)
        except:
            return 0.0
    
    def _detect_open_palms(self, pose_landmarks, hand_landmarks) -> float:
        """Detect open palms (honesty/openness)"""
        if not hand_landmarks:
            return 0.0
            
        try:
            confidence = 0.0
            
            for hand_landmark in hand_landmarks:
                # For open palms, fingers should be spread and extended
                landmarks = hand_landmark.landmark
                
                # Check finger spread
                thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
                pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
                
                finger_spread = self.calculate_distance(thumb_tip, pinky_tip)
                
                # Open palms typically have good finger spread
                if finger_spread > 0.2:
                    confidence += 0.5
            
            return min(confidence, 1.0)
        except:
            return 0.0
    
    def _detect_clenched_fists(self, pose_landmarks, hand_landmarks) -> float:
        """Detect clenched fists (anger/tension)"""
        if not hand_landmarks:
            return 0.0
            
        try:
            confidence = 0.0
            
            for hand_landmark in hand_landmarks:
                landmarks = hand_landmark.landmark
                
                # Check if fingers are curled inward
                thumb_tip = landmarks[self.mp_hands.HandLandmark.THUMB_TIP]
                index_tip = landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = landmarks[self.mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = landmarks[self.mp_hands.HandLandmark.PINKY_TIP]
                
                wrist = landmarks[self.mp_hands.HandLandmark.WRIST]
                
                # In clenched fist, fingertips are close to wrist
                distances = [
                    self.calculate_distance(tip, wrist) for tip in 
                    [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
                ]
                
                avg_distance = sum(distances) / len(distances)
                
                # Clenched fist has fingertips close to wrist
                if avg_distance < 0.15:
                    confidence += 0.5
            
            return min(confidence, 1.0)
        except:
            return 0.0
    
    def _detect_self_soothing(self, pose_landmarks, hand_landmarks) -> float:
        """Detect self-soothing gestures (stress management)"""
        confidence = 0.0
        
        # Hand to neck/face/chest are all self-soothing
        confidence += self._detect_hand_to_neck(pose_landmarks, hand_landmarks) * 0.4
        confidence += self._detect_hand_to_face(pose_landmarks, hand_landmarks) * 0.3
        confidence += self._detect_hand_to_chest(pose_landmarks, hand_landmarks) * 0.3
        
        return min(confidence, 1.0)
    
    def _detect_territorial_stance(self, pose_landmarks, hand_landmarks) -> float:
        """Detect territorial/dominant stance"""
        confidence = 0.0
        
        # Wide stance + hands on hips = territorial
        confidence += self._detect_wide_stance(pose_landmarks, hand_landmarks) * 0.5
        confidence += self._detect_hands_on_hips(pose_landmarks, hand_landmarks) * 0.5
        
        return min(confidence, 1.0)
    
    def _detect_submissive_posture(self, pose_landmarks, hand_landmarks) -> float:
        """Detect submissive body language"""
        confidence = 0.0
        
        # Combination of defensive postures
        confidence += self._detect_defensive_posture(pose_landmarks, hand_landmarks) * 0.4
        confidence += self._detect_closed_stance(pose_landmarks, hand_landmarks) * 0.3
        confidence += self._detect_self_soothing(pose_landmarks, hand_landmarks) * 0.3
        
        return min(confidence, 1.0)
    
    def _detect_power_pose(self, pose_landmarks, hand_landmarks) -> float:
        """Detect power pose (confidence/dominance)"""
        confidence = 0.0
        
        # Combination of confident gestures
        confidence += self._detect_confident_stance(pose_landmarks, hand_landmarks) * 0.5
        confidence += self._detect_open_arms(pose_landmarks, hand_landmarks) * 0.3
        confidence += self._detect_wide_stance(pose_landmarks, hand_landmarks) * 0.2
        
        return min(confidence, 1.0)
    
    def _detect_anxiety_indicators(self, pose_landmarks, hand_landmarks) -> float:
        """Detect anxiety-related body language"""
        confidence = 0.0
        
        # Multiple anxiety indicators
        confidence += self._detect_fidgeting(pose_landmarks, hand_landmarks) * 0.4
        confidence += self._detect_self_soothing(pose_landmarks, hand_landmarks) * 0.3
        confidence += self._detect_defensive_posture(pose_landmarks, hand_landmarks) * 0.3
        
        return min(confidence, 1.0)
    
    def _detect_engagement_signals(self, pose_landmarks, hand_landmarks) -> float:
        """Detect engagement/interest signals"""
        confidence = 0.0
        
        # Forward lean indicates engagement
        confidence += self._detect_leaning_forward(pose_landmarks, hand_landmarks) * 0.5
        confidence += self._detect_open_arms(pose_landmarks, hand_landmarks) * 0.3
        confidence += self._detect_open_palms(pose_landmarks, hand_landmarks) * 0.2
        
        return min(confidence, 1.0)
    
    def analyze_body_language(self, frame) -> Dict:
        """Analyze body language from video frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose and hands
        pose_results = self.pose.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        
        body_language_data = {
            "detected_patterns": [],
            "confidence_scores": {},
            "frame_analysis": {
                "pose_detected": pose_results.pose_landmarks is not None,
                "hands_detected": hand_results.multi_hand_landmarks is not None,
                "num_hands": len(hand_results.multi_hand_landmarks) if hand_results.multi_hand_landmarks else 0
            }
        }
        
        if pose_results.pose_landmarks:
            # Analyze each body language pattern
            for pattern_name, detector_func in self.body_patterns.items():
                try:
                    confidence = detector_func(
                        pose_results.pose_landmarks,
                        hand_results.multi_hand_landmarks
                    )
                    
                    body_language_data["confidence_scores"][pattern_name] = confidence
                    
                    # Add to detected patterns if confidence is high enough
                    if confidence > 0.4:
                        body_language_data["detected_patterns"].append({
                            "pattern": pattern_name,
                            "confidence": confidence
                        })
                        
                except Exception as e:
                    continue
            
            # Store current landmarks for fidgeting detection
            self.previous_landmarks = pose_results.pose_landmarks
        
        # Sort detected patterns by confidence
        body_language_data["detected_patterns"].sort(
            key=lambda x: x["confidence"], 
            reverse=True
        )
        
        return body_language_data
    
    def get_body_language_interpretation(self, patterns: List[Dict]) -> str:
        """Get interpretation of body language patterns"""
        if not patterns:
            return "No significant body language patterns detected."
        
        interpretations = {
            "crossed_arms": "Defensive or closed-off stance, possibly feeling uncomfortable or disagreeable",
            "hands_on_hips": "Confident, assertive, or potentially confrontational posture",
            "arms_open": "Open, welcoming, and receptive to interaction",
            "defensive_posture": "Feeling threatened, uncomfortable, or resistant to the situation",
            "confident_stance": "Self-assured, comfortable, and in control",
            "leaning_forward": "Engaged, interested, or showing assertiveness",
            "leaning_back": "Relaxed, disengaged, or maintaining distance",
            "crossed_legs": "Formal, reserved, or slightly defensive posture",
            "wide_stance": "Confident, dominant, or claiming territory",
            "closed_stance": "Insecure, submissive, or feeling vulnerable",
            "hand_to_face": "Thinking, processing, or possibly being deceptive",
            "hand_to_neck": "Feeling stressed, uncomfortable, or anxious",
            "hand_to_chest": "Showing sincerity, emphasis, or protective instincts",
            "covering_mouth": "Surprised, shocked, or potentially hiding something",
            "covering_eyes": "Embarrassed, ashamed, or overwhelmed",
            "fidgeting": "Nervous, anxious, or restless",
            "pointing": "Directing attention, making emphasis, or showing authority",
            "open_palms": "Honest, open, and trustworthy demeanor",
            "clenched_fists": "Angry, tense, or feeling aggressive",
            "self_soothing": "Managing stress or anxiety through comfort gestures",
            "territorial_stance": "Asserting dominance or claiming space",
            "submissive_posture": "Feeling inferior, insecure, or deferential",
            "power_pose": "Displaying confidence, authority, and control",
            "anxiety_indicators": "Showing signs of nervousness, stress, or discomfort",
            "engagement_signals": "Actively interested, focused, and involved"
        }
        
        # Get top 3 patterns
        top_patterns = patterns[:3]
        
        result = "Body Language Analysis:\n\n"
        
        for i, pattern_data in enumerate(top_patterns, 1):
            pattern_name = pattern_data["pattern"]
            confidence = pattern_data["confidence"]
            
            interpretation = interpretations.get(pattern_name, "Unknown pattern")
            
            result += f"{i}. {pattern_name.replace('_', ' ').title()} ({confidence:.1%})\n"
            result += f"   {interpretation}\n\n"
        
        return result.strip()
    
    def reset(self):
        """Reset analyzer state"""
        self.previous_landmarks = None
        self.gesture_history = []