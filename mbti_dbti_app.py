import streamlit as st

# --- MBTI → DBTI 매핑 함수 ---
def mbti_to_dbti(mbti):
    mbti = mbti.upper()
    if len(mbti) != 4:
        return None

    # 각 MBTI 축을 DBTI 코드로 변환
    mapping = {
        0: {"E": "E", "I": "I"},   # 외향/내향
        1: {"S": "L", "N": "A"},   # 감각/직관 → 낯익음/탐색
        2: {"T": "W", "F": "C"},   # 사고/감정 → 본능/감성
        3: {"J": "T", "P": "N"},   # 판단/인식 → 신뢰/자율
    }
    try:
        return mapping[2][mbti[2]] + mapping[3][mbti[3]] + mapping[0][mbti[0]] + mapping[1][mbti[1]]
    except:
        return None

# --- DBTI 성향 설명 ---
dbti_descriptions = {
    "C": "감정적으로 교류하며 신체 접촉을 좋아하는 성향",
    "W": "본능적으로 행동하며 반사적인 반응이 많은 성향",
    "T": "안정적이고 사람에 대한 신뢰를 나타내는 성향",
    "N": "자율적으로 행동하고 혼자 있어도 불안하지 않은 성향",
    "E": "사람이나 동물에게 적극적으로 다가가는 성향",
    "I": "혼자 있는 것을 선호하고 조용한 성향",
    "A": "새로운 환경에 호기심이 많고 활발한 성향",
    "L": "익숙한 장소를 선호하고 낯선 곳을 피하는 성향"
}

# --- 앱 구성 ---
st.set_page_config(page_title="MBTI → DBTI 매칭", page_icon="🐾")

# 페이지 1: MBTI 입력
st.title("🐶 MBTI → DBTI 성향 매칭")

mbti_input = st.text_input("당신의 MBTI를 입력하세요 (예: INFP)", max_chars=4)

if mbti_input:
    dbti_code = mbti_to_dbti(mbti_input)
    if dbti_code:
        st.success(f"✨ 변환된 DBTI 코드: `{dbti_code}`")
        if st.button("📌 다음 페이지로 보기"):
            st.session_state["mbti_entered"] = True
            st.session_state["mbti"] = mbti_input.upper()
            st.session_state["dbti"] = dbti_code
    else:
        st.error("올바른 MBTI 4자리 조합을 입력해주세요.")

# 페이지 2: 매칭 결과
if st.session_state.get("mbti_entered", False):
    st.markdown("---")
    st.header("🔍 매칭 결과 보기")

    st.markdown(f"**입력한 MBTI**: `{st.session_state['mbti']}`")
    st.markdown(f"**변환된 DBTI**: `{st.session_state['dbti']}`")

    st.subheader("📖 성향 설명")

    for letter in st.session_state["dbti"]:
        desc = dbti_descriptions.get(letter, "설명 없음")
        st.markdown(f"- **{letter}**: {desc}")