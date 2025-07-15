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
        
        prompt = """Analyze this image for facial expressions and emotional states with HIGH SENSITIVITY. Look for even the most subtle expressions.

CRITICAL: Only use "neutral" if the person shows absolutely zero emotional expression. Be highly sensitive to detect ANY emotional cues.

1. FACIAL EXPRESSIONS: Identify specific micro-expressions like:
   - Smile variations (genuine, forced, subtle, smirk)
   - Frown, scowl, concern, or sadness expressions
   - Eye expressions (squinting, wide eyes, eye contact, eye roll)
   - Eyebrow positions (raised, furrowed, asymmetrical)
   - Mouth expressions (open, pursed, bite lip, compressed)
   - Cheek tension, forehead wrinkles, jaw position
   - Overall emotional state (happy, sad, angry, surprised, fearful, disgusted, contempt)

2. BODY LANGUAGE: Analyze posture and gestures:
   - Arm positions (crossed, open, defensive, gesturing)
   - Hand gestures and positioning
   - Head position and tilt
   - Shoulder positioning
   - Overall body posture (confident, defensive, relaxed, tense)

3. DECEPTION INDICATORS: Look for potential signs of deception:
   - Micro-expressions that don't match overall expression
   - Forced or fake smiles
   - Defensive body language
   - Hand-to-face touching
   - Inconsistent expressions

IMPORTANT: Be extremely observant and detect subtle emotions. Look for:
- Slight mouth curves indicating happiness or sadness
- Eyebrow micro-movements suggesting surprise or concern
- Eye tension patterns indicating stress or focus
- Head positioning suggesting confidence or submission

Return a JSON object with:
{
    "facial_expressions": ["expression1", "expression2", ...],
    "body_language": ["pattern1", "pattern2", ...],
    "emotional_state": "primary emotional state - be specific and avoid neutral",
    "deception_indicators": ["indicator1", "indicator2", ...],
    "confidence_level": "high/medium/low",
    "detailed_analysis": "comprehensive analysis in 4-6 sentences describing what you actually observe, including psychological insights, emotional context, and behavioral interpretation"
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
                max_tokens=1500
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
    
    def analyze_emotion_context(self, image, context: List[str]) -> Dict:
        """Get contextual emotional analysis with user-provided scenario"""
        base64_image = self.encode_image(image)
        
        scenario_context = context[0] if context else ""
        
        prompt = f"""Analyze this image for facial expressions and emotions with the following context: {scenario_context}

Provide detailed analysis focusing on:
- Specific facial expressions and micro-expressions
- Body language patterns visible
- Emotional state relevant to the given context
- Confidence levels and authenticity
- Stress or anxiety indicators
- Overall psychological assessment for this scenario

Return a JSON object with:
{{
    "facial_expressions": ["expression1", "expression2", ...],
    "body_language": ["pattern1", "pattern2", ...],
    "emotional_state": "primary emotional state - be specific and avoid neutral",
    "confidence_level": "high/medium/low",
    "detailed_analysis": "comprehensive analysis in 4-6 sentences describing what you observe in relation to the context, including psychological insights, emotional patterns, and behavioral interpretation"
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
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "facial_expressions": [],
                "body_language": [],
                "emotional_state": "unknown",
                "confidence_level": "low",
                "detailed_analysis": f"Context analysis error: {str(e)}"
            }
    
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
    "interpretation": "comprehensive 4-6 sentence explanation of behavioral patterns, psychological insights, and deception assessment with specific reasoning"
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
                max_tokens=800
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