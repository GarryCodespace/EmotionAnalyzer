import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import math
from openai_analyzer import analyze_expression
from openai import OpenAI
import os

class LieDetector:
    def __init__(self):
        """Initialize lie detector with deception analysis patterns"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Micro-expression patterns associated with deception
        self.deception_indicators = {
            "micro_expressions": [
                "brief_smile", "forced_smile", "asymmetrical_smile",
                "lip_compression", "lip_purse", "mouth_cover",
                "eye_contact_avoidance", "rapid_blinking", "eye_flutter",
                "nostril_flare", "nose_touch", "jaw_tension",
                "brow_flash", "eyebrow_raise", "forehead_wrinkle"
            ],
            "body_language": [
                "hand_to_face", "hand_to_neck", "covering_mouth",
                "covering_eyes", "fidgeting", "self_soothing",
                "defensive_posture", "crossed_arms", "closed_stance",
                "leaning_back", "barrier_creation", "touching_objects"
            ],
            "vocal_stress": [
                "voice_pitch_change", "speaking_rate_change",
                "vocal_hesitation", "throat_clearing"
            ]
        }
        
        # Weighted scoring for different indicators
        self.indicator_weights = {
            "micro_expressions": 0.4,
            "body_language": 0.3,
            "timing_patterns": 0.2,
            "consistency_analysis": 0.1
        }
        
        # Baseline patterns for comparison
        self.baseline_patterns = {}
        self.analysis_history = []
    
    def analyze_micro_expressions(self, facial_expressions: List[str]) -> Dict:
        """Analyze micro-expressions for deception indicators"""
        deception_score = 0.0
        detected_indicators = []
        
        # Check for deception-related micro-expressions
        for expression in facial_expressions:
            if any(indicator in expression.lower() for indicator in self.deception_indicators["micro_expressions"]):
                detected_indicators.append(expression)
                
                # Weight different expressions differently
                if "smile" in expression.lower() and ("brief" in expression or "forced" in expression or "asymmetrical" in expression):
                    deception_score += 0.15
                elif "eye" in expression.lower() and ("contact" in expression or "flutter" in expression or "blink" in expression):
                    deception_score += 0.12
                elif "mouth" in expression.lower() and ("cover" in expression or "compression" in expression):
                    deception_score += 0.18
                elif "nose" in expression.lower() or "nostril" in expression.lower():
                    deception_score += 0.10
                else:
                    deception_score += 0.08
        
        return {
            "score": min(deception_score, 1.0),
            "indicators": detected_indicators,
            "category": "micro_expressions"
        }
    
    def analyze_body_language_deception(self, body_patterns: List[Dict]) -> Dict:
        """Analyze body language for deception indicators"""
        deception_score = 0.0
        detected_indicators = []
        
        for pattern in body_patterns:
            pattern_name = pattern.get("pattern", "")
            confidence = pattern.get("confidence", 0.0)
            
            if pattern_name in self.deception_indicators["body_language"]:
                detected_indicators.append(pattern_name)
                
                # Weight different body language patterns
                if "hand_to_face" in pattern_name or "covering_mouth" in pattern_name:
                    deception_score += confidence * 0.20
                elif "fidgeting" in pattern_name or "self_soothing" in pattern_name:
                    deception_score += confidence * 0.15
                elif "defensive_posture" in pattern_name or "crossed_arms" in pattern_name:
                    deception_score += confidence * 0.12
                elif "leaning_back" in pattern_name or "closed_stance" in pattern_name:
                    deception_score += confidence * 0.10
                else:
                    deception_score += confidence * 0.08
        
        return {
            "score": min(deception_score, 1.0),
            "indicators": detected_indicators,
            "category": "body_language"
        }
    
    def analyze_timing_patterns(self, expression_sequence: List[str]) -> Dict:
        """Analyze timing and sequence patterns for deception"""
        deception_score = 0.0
        timing_indicators = []
        
        if len(expression_sequence) < 3:
            return {"score": 0.0, "indicators": [], "category": "timing_patterns"}
        
        # Check for rapid expression changes (possible concealment)
        rapid_changes = 0
        for i in range(1, len(expression_sequence)):
            if expression_sequence[i] != expression_sequence[i-1]:
                rapid_changes += 1
        
        if rapid_changes > len(expression_sequence) * 0.7:
            deception_score += 0.15
            timing_indicators.append("rapid_expression_changes")
        
        # Check for suppressed expressions (brief then neutral)
        suppressed_count = 0
        for i in range(len(expression_sequence) - 1):
            current = expression_sequence[i]
            next_expr = expression_sequence[i + 1]
            
            if ("smile" in current or "frown" in current) and "neutral" in next_expr:
                suppressed_count += 1
        
        if suppressed_count > 2:
            deception_score += 0.12
            timing_indicators.append("expression_suppression")
        
        return {
            "score": min(deception_score, 1.0),
            "indicators": timing_indicators,
            "category": "timing_patterns"
        }
    
    def analyze_consistency(self, facial_expressions: List[str], body_patterns: List[Dict]) -> Dict:
        """Analyze consistency between facial expressions and body language"""
        consistency_score = 0.0
        inconsistency_indicators = []
        
        # Extract emotion categories
        positive_facial = any(word in expr.lower() for expr in facial_expressions 
                            for word in ["smile", "joy", "happy", "content", "relaxed"])
        negative_facial = any(word in expr.lower() for expr in facial_expressions 
                            for word in ["frown", "angry", "sad", "fear", "disgust"])
        
        # Extract body language categories
        positive_body = any(pattern.get("pattern", "") in ["open_arms", "confident_stance", "engagement_signals"] 
                          for pattern in body_patterns)
        negative_body = any(pattern.get("pattern", "") in ["defensive_posture", "crossed_arms", "anxiety_indicators"] 
                          for pattern in body_patterns)
        
        # Check for inconsistencies
        if positive_facial and negative_body:
            consistency_score += 0.20
            inconsistency_indicators.append("positive_face_negative_body")
        elif negative_facial and positive_body:
            consistency_score += 0.15
            inconsistency_indicators.append("negative_face_positive_body")
        
        # Check for conflicting signals
        if positive_facial and negative_facial:
            consistency_score += 0.10
            inconsistency_indicators.append("conflicting_facial_signals")
        
        return {
            "score": min(consistency_score, 1.0),
            "indicators": inconsistency_indicators,
            "category": "consistency_analysis"
        }
    
    def calculate_deception_probability(self, analysis_results: Dict) -> float:
        """Calculate overall deception probability from all analysis components"""
        total_score = 0.0
        
        for category, weight in self.indicator_weights.items():
            if category in analysis_results:
                total_score += analysis_results[category]["score"] * weight
        
        # Apply additional factors
        indicator_count = sum(len(result.get("indicators", [])) for result in analysis_results.values())
        
        # More indicators increase probability
        if indicator_count > 5:
            total_score += 0.10
        elif indicator_count > 3:
            total_score += 0.05
        
        return min(total_score, 1.0)
    
    def analyze_deception(self, facial_expressions: List[str], body_patterns: List[Dict], 
                         expression_history: List[str] = None) -> Dict:
        """Comprehensive deception analysis"""
        
        # Individual analysis components
        micro_analysis = self.analyze_micro_expressions(facial_expressions)
        body_analysis = self.analyze_body_language_deception(body_patterns)
        
        # Timing analysis if history is available
        timing_analysis = {"score": 0.0, "indicators": [], "category": "timing_patterns"}
        if expression_history and len(expression_history) > 2:
            timing_analysis = self.analyze_timing_patterns(expression_history)
        
        # Consistency analysis
        consistency_analysis = self.analyze_consistency(facial_expressions, body_patterns)
        
        # Compile results
        analysis_results = {
            "micro_expressions": micro_analysis,
            "body_language": body_analysis,
            "timing_patterns": timing_analysis,
            "consistency_analysis": consistency_analysis
        }
        
        # Calculate overall probability
        deception_probability = self.calculate_deception_probability(analysis_results)
        
        # Store for history
        self.analysis_history.append({
            "probability": deception_probability,
            "facial_expressions": facial_expressions,
            "body_patterns": body_patterns
        })
        
        return {
            "deception_probability": deception_probability,
            "confidence_level": self.get_confidence_level(deception_probability),
            "analysis_breakdown": analysis_results,
            "key_indicators": self.get_key_indicators(analysis_results),
            "interpretation": self.get_interpretation(deception_probability, analysis_results)
        }
    
    def get_confidence_level(self, probability: float) -> str:
        """Get confidence level description"""
        if probability < 0.2:
            return "Low"
        elif probability < 0.4:
            return "Moderate"
        elif probability < 0.6:
            return "High"
        elif probability < 0.8:
            return "Very High"
        else:
            return "Extremely High"
    
    def get_key_indicators(self, analysis_results: Dict) -> List[str]:
        """Get top indicators across all categories"""
        all_indicators = []
        
        for category, results in analysis_results.items():
            if results["score"] > 0.1:  # Only include significant indicators
                all_indicators.extend(results["indicators"])
        
        return all_indicators[:5]  # Return top 5
    
    def get_interpretation(self, probability: float, analysis_results: Dict) -> str:
        """Get human-readable interpretation"""
        if probability < 0.2:
            return "Low likelihood of deception. Expressions and body language appear consistent and natural."
        elif probability < 0.4:
            return "Some indicators present, but could be due to nervousness or discomfort rather than deception."
        elif probability < 0.6:
            return "Moderate signs of potential deception. Multiple indicators detected across facial and body language."
        elif probability < 0.8:
            return "Strong indicators of possible deception. Significant inconsistencies and stress signals detected."
        else:
            return "High likelihood of deception. Multiple strong indicators across micro-expressions and body language."
    
    def get_ai_deception_analysis(self, facial_expressions: List[str], body_patterns: List[Dict], 
                                 deception_analysis: Dict) -> str:
        """Get AI-powered deception analysis"""
        try:
            # Prepare comprehensive input for AI analysis
            expressions_text = ", ".join(facial_expressions)
            body_patterns_text = ", ".join([p.get("pattern", "") for p in body_patterns])
            
            probability = deception_analysis["deception_probability"]
            key_indicators = ", ".join(deception_analysis["key_indicators"])
            
            prompt = f"""
            Analyze the following behavioral data for potential deception indicators:
            
            Facial Expressions: {expressions_text}
            Body Language: {body_patterns_text}
            Detected Deception Indicators: {key_indicators}
            Calculated Deception Probability: {probability:.1%}
            
            Please provide a psychological analysis that includes:
            1. Assessment of the deception likelihood and reasoning
            2. Explanation of what specific behaviors suggest potential deception
            3. Alternative explanations (stress, nervousness, discomfort)
            4. What the person might be thinking or feeling
            5. Confidence level in the assessment
            
            Keep response under 200 words and maintain a professional, analytical tone.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert behavioral analyst and forensic psychologist specializing in deception detection. 
                        You have extensive knowledge of micro-expressions, body language, and psychological indicators of deception.
                        Provide balanced, scientific analysis while acknowledging the limitations of behavioral analysis.
                        Always consider alternative explanations and avoid definitive accusations."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI analysis temporarily unavailable: {str(e)}"
    
    def reset_analysis_history(self):
        """Reset analysis history for new session"""
        self.analysis_history = []
        self.baseline_patterns = {}