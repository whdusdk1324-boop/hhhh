import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="인터랙티브 교과서", layout="wide")

st.title("📖 인터랙티브 교과서")
st.write("교과 개념을 직접 실험하고 시각화해보세요!")

# --- 사이드바에서 교과 개념 선택 ---
concept = st.sidebar.selectbox(
    "학습할 교과 개념을 선택하세요:",
    ["수학: 함수 그래프", "수학: 확률 시뮬레이션"]
)

# --- 수학: 함수 그래프 ---
if concept == "수학: 함수 그래프":
    st.header("📊 함수 그래프 탐구")
    st.write("아래에서 함수를 선택하고, 파라미터를 조절해 그래프를 확인하세요!")

    func = st.selectbox("함수 선택:", ["sin(x)", "cos(x)", "x^2", "e^x"])
    x = np.linspace(-10, 10, 400)

    if func == "sin(x)":
        a = st.slider("진폭 a", 1, 5, 1)
        y = a * np.sin(x)
        st.latex(r"y = a \cdot \sin(x)")
    elif func == "cos(x)":
        b = st.slider("배율 b", 1, 5, 1)
        y = np.cos(b * x)
        st.latex(r"y = \cos(bx)")
    elif func == "x^2":
        c = st.slider("계수 c", 1, 5, 1)
        y = c * x**2
        st.latex(r"y = c \cdot x^2")
    elif func == "e^x":
        y = np.exp(x)
        st.latex(r"y = e^x")

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(f"{func} 그래프")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("💡 탐구 질문")
    st.write("- 파라미터를 바꾸면 그래프의 모양이 어떻게 변하나요?")
    st.write("- 주기, 진폭, 증가율 같은 수학적 개념과 연결 지어 설명해보세요.")

# --- 수학: 확률 ---
elif concept == "수학: 확률 시뮬레이션":
    st.header("🎲 확률 실험: 주사위 던지기")
    st.write("주사위를 여러 번 던져서, 결과 분포를 확인해보세요!")

    trials = st.slider("실험 횟수", 10, 5000, 100)
    results = [random.randint(1, 6) for _ in range(trials)]

    counts = [results.count(i) for i in range(1, 7)]

    fig, ax = plt.subplots()
    ax.bar(range(1, 7), counts, tick_label=[1, 2, 3, 4, 5, 6])
    ax.set_title(f"{trials}번 주사위 던지기 결과")
    ax.set_xlabel("눈")
    ax.set_ylabel("빈도")
    st.pyplot(fig)

    st.subheader("💡 탐구 질문")
    st.write("- 실험 횟수를 늘릴수록, 분포는 어떻게 변하나요?")
    st.write("- 실제 확률(1/6)과 결과를 비교해보세요.")
