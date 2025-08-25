# app.py
# -------------------------------------------
# 체육 진로 맞춤: 운동 기록 + 루틴 추천 + 칼로리/체력 대시보드
# 필요 패키지: streamlit, pandas, numpy, altair
# -------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="운동 기록 & 루틴 추천", page_icon="🏋️", layout="wide")

# --------------------------
# 초기 상태
# --------------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(
        columns=[
            "날짜","운동","세트","반복수","중량(kg)","시간(분)","RPE","메모"
        ]
    )

# --------------------------
# 유틸 함수
# --------------------------
def bmi(height_cm, weight_kg):
    if height_cm == 0:
        return 0
    return weight_kg / ((height_cm/100)**2)

def bmr_mifflin(sex, age, height_cm, weight_kg):
    # Mifflin-St Jeor
    s = 5 if sex == "남" else -161
    return 10*weight_kg + 6.25*height_cm - 5*age + s

def activity_factor(level):
    return {
        "거의 안 함": 1.2,
        "가벼움(주1-3)": 1.375,
        "보통(주3-5)": 1.55,
        "적극적(주6+)": 1.725,
        "매우 적극적(스포츠/노동)": 1.9
    }[level]

# 대표 MET (간단 버전)
METS = {
    "걷기(빠르게)": 4.3,
    "조깅": 7.0,
    "달리기(빠르게)": 10.0,
    "자전거(중강도)": 7.5,
    "수영(자유형 중강도)": 8.0,
    "스쿼트(웨이트)": 6.0,
    "벤치프레스": 6.0,
    "데드리프트": 6.0,
    "요가/스트레칭": 2.5,
    "축구(아마추어)": 7.0,
    "농구(픽업게임)": 8.0
}

def kcal_from_mets(met, weight_kg, minutes):
    # kcal = MET * 3.5 * 체중(kg) / 200 * 시간(분)
    return met * 3.5 * weight_kg / 200 * minutes

def recommend_plan(goal, level):
    """
    요일별 추천 루틴 생성 (간단 예시)
    반환: {요일: [운동 dict...]}
    운동 dict: {"운동":"스쿼트","세트":3,"반복":10,"휴식(초)":90} 또는 {"운동":"조깅","시간(분)":30}
    """
    base_strength = [
        {"운동":"스쿼트","세트":3,"반복":10,"휴식(초)":90},
        {"운동":"벤치프레스","세트":3,"반복":8,"휴식(초)":120},
        {"운동":"바벨로우/랫풀","세트":3,"반복":10,"휴식(초)":90},
        {"운동":"플랭크","세트":3,"시간(초)":45,"휴식(초)":45},
    ]
    base_cut = [
        {"운동":"인터벌 러닝","패턴":"1분 빠르게/1분 걷기 × 8"},
        {"운동":"케틀벨 스윙","세트":4,"반복":15,"휴식(초)":60},
        {"운동":"버피","세트":3,"반복":12,"휴식(초)":60},
        {"운동":"코어(데드버그/사이드플랭크)","세트":3,"시간(초)":30,"휴식(초)":30},
    ]
    base_endurance = [
        {"운동":"조깅","시간(분)":35},
        {"운동":"사이클","시간(분)":25},
        {"운동":"스텝업/런지","세트":3,"반복":12,"휴식(초)":60},
        {"운동":"스트레칭","시간(분)":10},
    ]
    base_mobility = [
        {"운동":"전신 동적스트레칭","시간(분)":10},
        {"운동":"힙/발목 가동성","세트":3,"시간(초)":45},
        {"운동":"요가플로우","시간(분)":20},
        {"운동":"호흡 훈련(박스브리딩)","시간(분)":5},
    ]
    # 레벨별 볼륨 조정
    mult = {"초급":1.0,"중급":1.3,"고급":1.6}[level]

    def scale(plan):
        scaled=[]
        for w in plan:
            w=w.copy()
            if "세트" in w: w["세트"]=int(round(w["세트"]*mult))
            if "반복" in w: w["반복"]=int(round(w["반복"]*max(1, mult)))
            if "시간(분)" in w: w["시간(분)"]=int(round(w["시간(분)"]*mult))
            if "시간(초)" in w: w["시간(초)"]=int(round(w["시간(초)"]*mult))
            scaled.append(w)
        return scaled

    if goal == "근력 향상":
        week = {
            "월": scale(base_strength),
            "화": scale(base_mobility),
            "수": scale(base_strength),
            "목": [{"운동":"가볍게 걷기","시간(분)":30}],
            "금": scale(base_strength),
            "토": [{"운동":"조깅","시간(분)":25}],
            "일": [{"운동":"휴식/스트레칭","시간(분)":20}],
        }
    elif goal == "체지방 감량":
        week = {
            "월": scale(base_cut),
            "화": [{"운동":"조깅","시간(분)":30},{"운동":"스트레칭","시간(분)":10}],
            "수": scale(base_cut),
            "목": scale(base_mobility),
            "금": scale(base_cut),
            "토": [{"운동":"자전거","시간(분)":40}],
            "일": [{"운동":"휴식/걷기","시간(분)":30}],
        }
    elif goal == "지구력 향상":
        week = {
            "월": scale(base_endurance),
            "화": scale(base_mobility),
            "수": scale(base_endurance),
            "목": [{"운동":"인터벌 러닝","패턴":"2분 빠르게/1분 걷기 × 6"}],
            "금": scale(base_endurance),
            "토": [{"운동":"장거리 걷기/하이킹","시간(분)":60}],
            "일": [{"운동":"휴식/요가","시간(분)":25}],
        }
    else:  # 체력 종합
        week = {
            "월": scale(base_strength),
            "화": [{"운동":"조깅","시간(분)":25},{"운동":"스트레칭","시간(분)":10}],
            "수": scale(base_mobility),
            "목": scale(base_cut),
            "금": scale(base_strength),
            "토": [{"운동":"자전거","시간(분)":35}],
            "일": [{"운동":"휴식/산책","시간(분)":30}],
        }
    return week

def weekly_volume(df):
    if df.empty:
        return pd.DataFrame(columns=["주","볼륨(추정)"])
    tmp=df.copy()
    # 추정 볼륨: (세트*반복*중량) 합 + 시간 기반 1분=50 점수로 환산 (러프)
    tmp["가중볼륨"]=tmp.fillna(0).apply(
        lambda r: (r.get("세트",0)*r.get("반복수",0)*r.get("중량(kg)",0)) + (r.get("시간(분)",0)*50),
        axis=1
    )
    tmp["주"] = pd.to_datetime(tmp["날짜"]).dt.to_period("W").astype(str)
    out = tmp.groupby("주")["가중볼륨"].sum().reset_index().rename(columns={"가중볼륨":"볼륨(추정)"})
    return out

# --------------------------
# 사이드바: 프로필 입력
# --------------------------
with st.sidebar:
    st.header("👤 프로필")
    name = st.text_input("이름 (선택)", "")
    colA, colB = st.columns(2)
    with colA:
        sex = st.selectbox("성별", ["남","여"])
        age = st.number_input("나이", 14, 80, 18)
    with colB:
        height = st.number_input("키(cm)", 120, 220, 170)
        weight = st.number_input("몸무게(kg)", 35.0, 200.0, 60.0, step=0.1)

    act = st.selectbox("활동 수준", ["거의 안 함","가벼움(주1-3)","보통(주3-5)","적극적(주6+)","매우 적극적(스포츠/노동)"])
    goal = st.selectbox("목표", ["근력 향상","체지방 감량","지구력 향상","체력 종합"])
    level = st.selectbox("숙련도", ["초급","중급","고급"])

    bmi_v = bmi(height, weight)
    bmr_v = bmr_mifflin(sex, age, height, weight)
    tdee_v = bmr_v * activity_factor(act)

    st.markdown("---")
    st.metric("BMI", f"{bmi_v:.1f}")
    st.metric("BMR(기초대사량)", f"{int(bmr_v)} kcal/일")
    st.metric("TDEE(일일 유지칼로리)", f"{int(tdee_v)} kcal/일")

# --------------------------
# 본문 탭
# --------------------------
st.title("🏋️ 운동 기록 & 맞춤 루틴 추천")
st.caption("체육 진로에 딱 맞는 개인 운동 대시보드")

tab1, tab2, tab3, tab4 = st.tabs(["📊 대시보드","📝 운동 기록","🗓️ 맞춤 루틴","🔥 칼로리/체력 계산"])

# --------------------------
# 탭 1: 대시보드
# --------------------------
with tab1:
    st.subheader("주간 볼륨 추이")
    vol = weekly_volume(st.session_state.log)
    if vol.empty:
        st.info("아직 기록이 없습니다. ‘운동 기록’ 탭에서 기록을 추가해 보세요.")
    else:
        chart = alt.Chart(vol).mark_line(point=True).encode(
            x=alt.X("주:N", title="주(Week)"),
            y=alt.Y("볼륨(추정):Q", title="추정 볼륨"),
            tooltip=["주","볼륨(추정)"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    # 최근 14일 요약
    st.subheader("최근 14일 요약")
    if st.session_state.log.empty:
        st.write("기록 없음")
    else:
        df = st.session_state.log.copy()
        df["날짜"] = pd.to_datetime(df["날짜"])
        recent = df[df["날짜"] >= (datetime.now() - timedelta(days=14))]
        tot_min = recent["시간(분)"].fillna(0).sum()
        strength_sets = recent["세트"].fillna(0).sum()
        est_kcal = 0
        # 러프한 칼로리 추정: 기록된 '시간(분)'이 있는 행을 기준으로 평균 MET 6 가정
        est_kcal = kcal_from_mets(6.0, weight, tot_min)
        c1,c2,c3 = st.columns(3)
        c1.metric("운동 시간(분)", int(tot_min))
        c2.metric("총 세트 수", int(strength_sets))
        c3.metric("추정 칼로리 소모", f"{int(est_kcal)} kcal")

# --------------------------
# 탭 2: 운동 기록
# --------------------------
with tab2:
    st.subheader("운동 기록 추가")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        date = st.date_input("날짜", datetime.now().date())
        exercise = st.text_input("운동 이름", placeholder="예) 스쿼트 / 조깅")
    with c2:
        sets = st.number_input("세트", 0, 20, 3)
        reps = st.number_input("반복수", 0, 100, 10)
    with c3:
        weight_used = st.number_input("중량(kg)", 0.0, 500.0, 0.0, step=0.5)
        minutes = st.number_input("시간(분)", 0, 300, 0)
    with c4:
        rpe = st.slider("RPE(자각 난이도)", 1, 10, 7)
        memo = st.text_input("메모", placeholder="느낌/통증/기타")

    add = st.button("➕ 기록 추가")
    if add:
        new = {
            "날짜": str(date),
            "운동": exercise if exercise else "미지정",
            "세트": int(sets),
            "반복수": int(reps),
            "중량(kg)": float(weight_used),
            "시간(분)": int(minutes),
            "RPE": int(rpe),
            "메모": memo
        }
        st.session_state.log = pd.concat([st.session_state.log, pd.DataFrame([new])], ignore_index=True)
        st.success("기록이 추가되었습니다!")

    st.markdown("---")
    st.subheader("나의 운동 일지")
    st.dataframe(st.session_state.log, use_container_width=True, height=300)

    colx, coly = st.columns(2)
    with colx:
        if not st.session_state.log.empty:
            csv = st.session_state.log.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ CSV로 다운로드", csv, file_name="workout_log.csv", mime="text/csv")
    with coly:
        uploaded = st.file_uploader("CSV 불러오기(열 이름 동일)", type="csv")
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                # 필수 열 체크
                required = set(st.session_state.log.columns)
                if set(df.columns) >= required:
                    st.session_state.log = df[list(st.session_state.log.columns)]
                    st.success("불러오기 완료!")
                else:
                    st.error("열 이름이 맞지 않습니다. 예시 CSV를 참고하세요.")
            except Exception as e:
                st.error(f"불러오기 실패: {e}")

# --------------------------
# 탭 3: 맞춤 루틴
# --------------------------
with tab3:
    st.subheader(f"🗓️ {goal}용 주간 루틴 (숙련도: {level})")
    plan = recommend_plan(goal, level)

    # 요일별 카드
    days = ["월","화","수","목","금","토","일"]
    for d in days:
        with st.expander(f"{d}요일"):
            items = plan.get(d, [])
            if not items:
                st.write("휴식")
            else:
                for it in items:
                    st.write("• ", {k:v for k,v in it.items()})

    st.markdown("---")
    st.caption("TIP: 루틴 항목을 '운동 기록' 탭으로 그대로 옮겨 입력하면 진척도를 시각화할 수 있어요.")

# --------------------------
# 탭 4: 칼로리/체력 계산
# --------------------------
with tab4:
    st.subheader("🔥 활동 칼로리 계산기 (MET 기반)")
    c1,c2,c3 = st.columns(3)
    with c1:
        act_sel = st.selectbox("활동 선택", list(METS.keys()))
    with c2:
        min_sel = st.number_input("운동 시간(분)", 5, 300, 30)
    with c3:
        w_sel = st.number_input("계산용 체중(kg)", 30.0, 200.0, float(weight), step=0.5)

    met_val = METS[act_sel]
    kcal = kcal_from_mets(met_val, w_sel, min_sel)
    st.metric("추정 소모 칼로리", f"{int(kcal)} kcal")

    st.markdown("#### 간단 체력 테스트 가이드(자가평가)")
    st.write("""
    - **코퍼 테스트(12분 달리기)**: 지난 기록과 비교해 거리가 늘면 지구력 향상.
    - **최대 팔굽혀펴기 1세트**: 근지구력 확인 (주당 +2~3개 목표).
    - **스쿼트 점프 5회 평균 높이**: 폭발력/순발력 지표.
    - **앉아 윗몸 앞으로 굽히기**: 유연성 지표.
    """)

st.markdown("---")
st.caption("© 체육 진로 포트폴리오용 Streamlit 예제 · 수정/확장 자유")
