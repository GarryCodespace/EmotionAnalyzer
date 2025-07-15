import base64
import cv2
import json
from openai import OpenAI
import os
from typing import Dict, List, Optional

class AIVisionAnalyzer:
    def __init__(self):
        """Initialize AI Vision Analyzer with OpenAI GPT-4o"""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def encode_image(self, image) -> str:
        """Encode OpenCV image to base64 string"""
        _, buffer = cv2.imencode('.jpg', image)
        return base64.b64encode(buffer).decode('utf-8')
    
    def analyze_facial_expressions(self, image) -> Dict:
        """Analyze facial expressions using OpenAI Vision API"""
        base64_image = self.encode_image(image)
        
        prompt = """Analyze this image for facial expressions and emotional states. Focus on:

1. FACIAL EXPRESSIONS: Identify specific micro-expressions like:
   - Smile variations (genuine, forced, subtle)
   - Frown, scowl, or concern expressions
   - Eye expressions (squinting, wide eyes, eye contact)
   - Eyebrow positions (raised, furrowed, asymmetrical)
   - Mouth expressions (open, pursed, bite lip)
   - Overall emotional state

2. BODY LANGUAGE: Analyze posture and gestures:
   - Arm positions (crossed, open, defensive)
   - Hand gestures and positioning
   - Leg stance and positioning
   - Overall body posture (confident, defensive, relaxed)

3. DECEPTION INDICATORS: Look for potential signs of deception:
   - Micro-expressions that don't match overall expression
   - Forced or fake smiles
   - Defensive body language
   - Hand-to-face touching
   - Inconsistent expressions

Return a JSON object with:
{
    "facial_expressions": ["expression1", "expression2", ...],
    "body_language": ["pattern1", "pattern2", ...],
    "emotional_state": "primary emotional state",
    "deception_indicators": ["indicator1", "indicator2", ...],
    "confidence_level": "high/medium/low",
    "detailed_analysis": "comprehensive analysis in 2-3 sentences"
}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "facial_expressions": [],
                "body_language": [],
                "emotional_state": "unknown",
                "deception_indicators": [],
                "confidence_level": "low",
                "detailed_analysis": f"Analysis error: {str(e)}"
            }
    
    def analyze_emotion_context(self, image, expressions: List[str]) -> str:
        """Get contextual emotional analysis"""
        base64_image = self.encode_image(image)
        
        prompt = f"""Based on the detected expressions: {', '.join(expressions)}, provide a comprehensive emotional analysis of this person.

Focus on:
- Underlying emotional state and mood
- Social context and interpersonal dynamics
- Confidence levels and self-assurance
- Potential stress or anxiety indicators
- Overall psychological assessment

Keep response to 150 words maximum. Be insightful and professional."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def analyze_deception_probability(self, image, detected_indicators: List[str]) -> Dict:
        """Analyze deception probability using AI vision"""
        base64_image = self.encode_image(image)
        
        prompt = f"""Analyze this image for deception indicators. Current detected indicators: {', '.join(detected_indicators)}

Assess the likelihood of deception based on:
1. Facial micro-expressions and authenticity
2. Body language and defensive postures
3. Inconsistencies between facial expressions and body language
4. Overall behavioral patterns

Return a JSON object with:
{{
    "deception_probability": 0.0-1.0,
    "confidence_level": "low/medium/high",
    "key_indicators": ["indicator1", "indicator2", ...],
    "risk_assessment": "low/medium/high",
    "interpretation": "detailed explanation of findings"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "deception_probability": 0.0,
                "confidence_level": "low",
                "key_indicators": [],
                "risk_assessment": "low",
                "interpretation": f"Analysis error: {str(e)}"
            }
    
    def analyze_video_frame(self, frame) -> Dict:
        """Analyze a single video frame"""
        return self.analyze_facial_expressions(frame)
    
    def get_expression_confidence(self, expressions: List[str]) -> Dict:
        """Generate confidence scores for detected expressions"""
        confidence_scores = {}
        for expr in expressions:
            # Simulate confidence based on expression complexity
            if any(word in expr.lower() for word in ['smile', 'frown', 'happy', 'sad']):
                confidence_scores[expr] = 0.8 + (hash(expr) % 20) / 100
            else:
                confidence_scores[expr] = 0.6 + (hash(expr) % 30) / 100
        return confidence_scores