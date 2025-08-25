import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

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

st.title("🏋️ 자세 교정 피드백 웹앱")
st.write("사진을 업로드하면 간단한 관절 각도를 분석해 피드백을 드립니다!")

uploaded_file = st.file_uploader("운동 사진을 업로드하세요", type=["jpg","jpeg","png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img = np.array(image)

    # Pose 모델 실행
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if results.pose_landmarks:
            # 랜드마크 그리기
            mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # 예: 스쿼트 분석 (무릎 각도)
            landmarks = results.pose_landmarks.landmark
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            angle = calculate_angle(hip, knee, ankle)

            st.image(img, caption="분석된 자세", use_column_width=True)
            st.write(f"왼쪽 무릎 각도: **{int(angle)}°**")

            # 피드백 조건
            if angle > 160:
                st.success("🟢 다리가 곧게 펴져 있어요! (준비 자세)")
            elif 70 < angle <= 160:
                st.info("🟡 무릎이 굽혀지고 있어요 (스쿼트 동작 중)")
            else:
                st.error("🔴 너무 깊이 앉았어요! 무릎에 무리 갈 수 있음")
        else:
            st.warning("사람을 인식하지 못했어요. 다른 사진을 올려주세요.")
