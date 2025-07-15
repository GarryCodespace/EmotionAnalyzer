import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

# Initialize OpenAI client with API key from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_expression(event_text):
    """
    Analyze facial expressions and gestures using OpenAI GPT-4o
    
    Args:
        event_text (str): Comma-separated list of detected gestures/expressions
        
    Returns:
        str: AI-generated emotional analysis and interpretation
    """
    try:
        # Check if body language patterns are included
        body_language_patterns = [
            "crossed_arms", "hands_on_hips", "arms_open", "defensive_posture", 
            "confident_stance", "leaning_forward", "leaning_back", "crossed_legs",
            "wide_stance", "closed_stance", "hand_to_face", "hand_to_neck",
            "hand_to_chest", "covering_mouth", "covering_eyes", "fidgeting",
            "pointing", "open_palms", "clenched_fists", "self_soothing",
            "territorial_stance", "submissive_posture", "power_pose",
            "anxiety_indicators", "engagement_signals"
        ]
        
        has_body_language = any(pattern in event_text for pattern in body_language_patterns)
        
        if has_body_language:
            prompt = f"""The user displayed the following facial expressions, gestures, and body language: {event_text}.
            
            Please provide a comprehensive emotional analysis that includes:
            1. The likely emotional state or mood
            2. Possible underlying feelings or thoughts
            3. Social or psychological context if applicable
            4. How their body language and posture reflect their confidence, comfort level, or emotional barriers
            5. What their positioning and gestures might suggest about their intentions or psychological state
            
            Keep your response between 150-250 words and focus on comprehensive psychological insights combining both facial and body language. Provide detailed interpretation and behavioral analysis."""
            
            system_content = """You are an expert psychologist specializing in facial expression analysis, body language, and emotional intelligence. 
            You have deep knowledge of micro-expressions, emotional psychology, non-verbal communication, and body language interpretation. 
            Provide insightful, empathetic, and accurate emotional interpretations based on facial gestures, expressions, and body positioning.
            Always maintain a professional and supportive tone."""
        else:
            prompt = f"""The user displayed the following facial expressions and gestures: {event_text}.
            
            Please provide a concise emotional analysis that includes:
            1. The likely emotional state or mood
            2. Possible underlying feelings or thoughts
            3. Social or psychological context if applicable
            
            Keep your response between 150-250 words and focus on comprehensive psychological insights rather than technical descriptions. Provide detailed emotional interpretation and behavioral analysis."""
            
            system_content = """You are an expert psychologist specializing in facial expression analysis and emotional intelligence. 
            You have deep knowledge of micro-expressions, emotional psychology, and non-verbal communication. 
            Provide insightful, empathetic, and accurate emotional interpretations based on facial gestures and expressions.
            Always maintain a professional and supportive tone."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": system_content
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=200,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Unable to analyze expression at this time: {str(e)}"

def analyze_emotion_pattern(expressions_history):
    """
    Analyze patterns in emotional expressions over time
    
    Args:
        expressions_history (list): List of detected expressions over time
        
    Returns:
        str: Pattern analysis and emotional trend insights
    """
    try:
        if not expressions_history:
            return "No expression history available for pattern analysis."
        
        # Join all expressions into a timeline
        timeline = " → ".join(expressions_history)
        
        prompt = f"""Analyze this sequence of facial expressions over time: {timeline}
        
        Please provide insights about:
        1. Overall emotional trend or pattern
        2. Emotional stability or volatility
        3. Potential emotional triggers or themes
        4. General psychological state assessment
        
        Keep your response concise and focused on meaningful patterns."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert in emotional pattern analysis and psychological assessment. 
                    You specialize in interpreting sequences of facial expressions to understand emotional states, 
                    mood patterns, and psychological wellbeing over time."""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=250,
            temperature=0.6
        )

        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Unable to analyze expression patterns: {str(e)}"

def get_emotion_suggestions(current_emotion):
    """
    Provide suggestions for emotional regulation based on detected emotions
    
    Args:
        current_emotion (str): Current detected emotional state
        
    Returns:
        str: Suggestions for emotional wellbeing and regulation
    """
    try:
        prompt = f"""Based on the detected emotional state: {current_emotion}
        
        Please provide:
        1. Brief validation of the emotional experience
        2. 2-3 practical suggestions for emotional regulation or wellbeing
        3. Positive affirmation or encouragement
        
        Keep the tone supportive, non-judgmental, and empowering."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a compassionate emotional wellness coach with expertise in emotional intelligence 
                    and psychological wellbeing. You provide supportive, practical, and empowering guidance for emotional regulation 
                    and mental health. Always maintain a warm, understanding, and non-judgmental approach."""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=180,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Unable to provide emotional suggestions: {str(e)}"
