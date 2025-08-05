# app.py
import streamlit as st
import torch
import clip
from PIL import Image
import pandas as pd
import os

# CLIP 모델 불러오기
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 닉네임 및 성향 코드 매핑 예시
nickname_map = {
    "WTIL": "엄마 껌딱지 겁쟁이형",
    "WTIA": "조심스러운 관찰형",
    "WNIA": "선긋는 외톨이 야생견형",
    "WNIL": "패닉에 빠진 극소심형",
    "WTEL": "초면엔 신중, 구면엔 친구",
    "WTEA": "허세 부리는 호기심쟁이",
    "WNEA": "동네 대장 일진형",
    "WNEL": "까칠한 지킬 앤 하이드형",
    "CTEL": "신이 내린 반려특화형",
    "CTEA": "인간 사회 적응 만렙형",
    "CNEA": "똥꼬발랄 핵인싸형",
    "CNEL": "곱게 자란 막내둥이형",
    "CTIA": "가족 빼곤 다 싫어형",
    "CTIL": "모범견계의 엄친아형",
    "CNIA": "주인에 관심없는 나혼자 산다형",
    "CNIL": "치고 빠지는 밀당 천재형",
}

# 성향 축 정의 [(왼쪽 코드, 왼쪽 문장), (오른쪽 코드, 오른쪽 문장)]
axis_prompts = [
    ("C", "이 강아지는 감정적으로 교류하고 신체 접촉을 좋아합니다."),
    ("W", "이 강아지는 반사적으로 본능적으로 행동합니다."),
    ("T", "이 강아지는 신뢰와 안정감을 보입니다."),
    ("N", "이 강아지는 독립적으로 행동하고 필요할 때만 교류합니다."),
    ("E", "이 강아지는 사람과 적극적으로 교류합니다."),
    ("I", "이 강아지는 혼자 있는 것을 좋아합니다."),
    ("A", "이 강아지는 새로운 환경에 호기심이 많고 활발하게 움직입니다."),
    ("L", "이 강아지는 낯선 환경에 적응하지 않고 익숙한 공간을 선호합니다.")
]

# 프롬프트를 텍스트로 변환하고 임베딩
@st.cache_resource
def encode_texts():
    result = []
    for i in range(0, len(axis_prompts), 2):
        left_code, left_prompt = axis_prompts[i]
        right_code, right_prompt = axis_prompts[i+1]
        texts = clip.tokenize([left_prompt, right_prompt]).to(device)
        with torch.no_grad():
            feats = model.encode_text(texts).float()
            feats /= feats.norm(dim=-1, keepdim=True)
        result.append((left_code, feats[0].unsqueeze(0), right_code, feats[1].unsqueeze(0)))
    return result

axis_text_features = encode_texts()

# 이미지 인코딩 함수
def encode_image(img):
    image = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        img_feat = model.encode_image(image).float()
        img_feat /= img_feat.norm(dim=-1, keepdim=True)
    return img_feat

# CLIP 매칭 함수
def predict_code(image_feat):
    code_letters = []
    for left_code, left_feat, right_code, right_feat in axis_text_features:
        left_sim = (image_feat @ left_feat.T).item()
        right_sim = (image_feat @ right_feat.T).item()
        code_letters.append(left_code if left_sim > right_sim else right_code)
    return "".join(code_letters)

# Streamlit 앱 UI
st.title("🐶 CLIP 기반 동물 성향(DBTI) 예측기")

uploaded_files = st.file_uploader("이미지를 업로드하세요", type=["jpg", "png"], accept_multiple_files=True)

if uploaded_files:
    results = []
    for uploaded in uploaded_files:
        img = Image.open(uploaded).convert("RGB")
        feat = encode_image(img)
        code = predict_code(feat)
        nickname = nickname_map.get(code, "알 수 없음")

        st.image(img, width=200)
        st.markdown(f"**DBTI 코드**: `{code}`")
        st.markdown(f"**성향 설명**: {nickname}")
        results.append({"파일명": uploaded.name, "DBTI": code, "닉네임": nickname})

    df = pd.DataFrame(results)
    st.dataframe(df)

    # CSV 다운로드
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 결과 CSV 다운로드", csv, "dbti_result.csv", "text/csv")
