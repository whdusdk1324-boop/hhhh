import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

st.title("🏋️ 실시간 자세 교정 피드백 (웹캠)")
st.write("웹캠을 켜서 운동 자세를 확인해보세요!")

# Mediapipe pose 초기화
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """세 점의 좌표(a, b, c)로 각도 계산"""
    a = np.array(a)  
    b = np.array(b)  
    c = np.array(c)  
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

# 웹캠 실행
run = st.checkbox("웹캠 켜기")

FRAME_WINDOW = st.image([])

if run:
    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("웹캠을 찾을 수 없습니다.")
                break

            # 색상 변환
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            # 랜드마크가 감지되면
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # 스쿼트 예시: 왼쪽 무릎 각도 측정
                landmarks = results.pose_landmarks.landmark
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                angle = calculate_angle(hip, knee, ankle)

                # 화면에 각도 표시
                cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(knee, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # 피드백 조건
                if angle > 160:
                    feedback = "🟢 다리가 곧게 펴져 있어요! (준비 자세)"
                elif 70 < angle <= 160:
                    feedback = "🟡 무릎이 굽혀지고 있어요 (스쿼트 중)"
                else:
                    feedback = "🔴 너무 깊이 앉았어요! 무릎에 무리 갈 수 있음"
                    
                cv2.putText(image, feedback, (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            FRAME_WINDOW.image(image)

    cap.release()
