import streamlit as st
import cv2
import mediapipe as mp
import time
from openai_analyzer import analyze_expression

# Setup MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Define 100+ gestures (some with reduced sensitivity thresholds)
GESTURES = [
    ("raised left eyebrow", lambda lm: (lm[159].y - lm[65].y) > 0.06),
    ("raised right eyebrow", lambda lm: (lm[386].y - lm[295].y) > 0.06),
    ("mouth open", lambda lm: abs(lm[13].y - lm[14].y) > 0.05),
    ("frown", lambda lm: abs(lm[61].x - lm[291].x) < 0.035),
    ("pursed lips", lambda lm: abs(lm[61].x - lm[291].x) < 0.025),
    ("smirk left", lambda lm: lm[61].y > lm[291].y + 0.015),
    ("smirk right", lambda lm: lm[291].y > lm[61].y + 0.015),
    ("cheek puff", lambda lm: abs(lm[50].x - lm[280].x) > 0.25),
    ("nostril flare", lambda lm: abs(lm[94].x - lm[331].x) > 0.05),
    ("lip bite", lambda lm: abs(lm[13].y - lm[14].y) < 0.008 and abs(lm[61].x - lm[291].x) < 0.01),
    ("brow furrow", lambda lm: abs(lm[65].x - lm[295].x) < 0.03),
    ("brow lift", lambda lm: (lm[65].y + lm[295].y) / 2 < lm[10].y - 0.03),
    ("eye roll up", lambda lm: lm[468].y < lm[474].y - 0.02),
    ("eye roll down", lambda lm: lm[468].y > lm[474].y + 0.02),
    ("chin thrust forward", lambda lm: lm[152].z < -0.1),
    ("chin tuck", lambda lm: lm[152].z > 0.1),
    ("eye blink left", lambda lm: abs(lm[159].y - lm[145].y) < 0.005),
    ("eye blink right", lambda lm: abs(lm[386].y - lm[374].y) < 0.005),
    ("eyes wide open", lambda lm: abs(lm[159].y - lm[145].y) > 0.035),
    ("glare left", lambda lm: lm[33].x - lm[133].x > 0.02),
    ("glare right", lambda lm: lm[263].x - lm[362].x > 0.02),
    ("glare up", lambda lm: (lm[159].y + lm[386].y)/2 < (lm[145].y + lm[374].y)/2 - 0.02),
    ("glare down", lambda lm: (lm[159].y + lm[386].y)/2 > (lm[145].y + lm[374].y)/2 + 0.02),
    ("brows raised and mouth open", lambda lm: (lm[159].y - lm[65].y) > 0.03 and abs(lm[13].y - lm[14].y) > 0.04),
    ("brows lowered and lips pressed", lambda lm: (lm[159].y - lm[65].y) < 0.01 and abs(lm[13].y - lm[14].y) < 0.01),
    ("eye squint left", lambda lm: abs(lm[159].y - lm[145].y) < 0.007),
    ("eye squint right", lambda lm: abs(lm[386].y - lm[374].y) < 0.007),
    ("jaw drop", lambda lm: abs(lm[152].y - lm[13].y) > 0.15),
    ("head tilt left", lambda lm: lm[234].y - lm[454].y > 0.03),
    ("head tilt right", lambda lm: lm[454].y - lm[234].y > 0.03),
    ("head turn right", lambda lm: lm[454].x < lm[234].x - 0.05),
    ("head turn down", lambda lm: lm[10].y > lm[152].y + 0.08), 
    ("nose wrinkle", lambda lm: abs(lm[6].y - lm[168].y) < 0.02),
    ("brow raise + smile", lambda lm: (lm[159].y - lm[65].y) > 0.1 and abs(lm[61].x - lm[291].x) > 0.08),
    ("brow furrow + frown", lambda lm: abs(lm[65].x - lm[295].x) < 0.03 and abs(lm[61].x - lm[291].x) < 0.035),
    ("mouth open + head tilt", lambda lm: abs(lm[13].y - lm[14].y) > 0.04 and abs(lm[234].y - lm[454].y) > 0.03),
]

last_detected = set()
last_detect_time = {}
cooldown_seconds = 5

st.set_page_config(page_title="Emoticon – Emotion Detector", layout="wide")
st.title("🎭 Emoticon")
st.write("Live AI Emotion Interpretation from Micro-Expressions")

frame_display = st.empty()
detected_display = st.empty()
gpt_display = st.empty()

run = st.button('▶ Start Webcam')
refresh = st.button('🔄 Refresh')

if run or refresh:
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break


        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        current_time = time.time()
        detected_now = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                for name, condition in GESTURES:
                    try:
                        if condition(landmarks):
                            if name not in last_detected or (current_time - last_detect_time.get(name, 0)) > cooldown_seconds:
                                detected_now.append(name)
                                last_detected.add(name)
                                last_detect_time[name] = current_time
                    except Exception as e:
                        print(f"⚠️ Error in gesture '{name}': {e}")

        frame_display.image(frame, channels="BGR")

        if detected_now:
            detected_display.markdown(f"🟢 **Detected Gesture(s)**: {', '.join(detected_now)}")
            description = analyze_expression(", ".join(detected_now))
            gpt_display.markdown(f"💬 **GPT Insight:** _{description}_")

        if st.button("⏹ Stop"):
            break

    cap.release()
    cv2.destroyAllWindows()
