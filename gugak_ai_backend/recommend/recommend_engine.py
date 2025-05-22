import pandas as pd
import random

# 📂 메타데이터 로딩
METADATA_PATH = r"D:\gugak_ai_backend\data\gugak_metadata.csv"
df = pd.read_csv(METADATA_PATH)

# 🎵 악기 이름 목록
instrument_names = df["악기"].dropna().unique().tolist()

# 💫 감정 키워드 매핑 및 단계 완화 조건
emotion_map = {
    "슬퍼": "차분", "서정": "차분", "차분": "차분", "잔잔": "차분",
    "평온": "평온", "조용": "평온", "편안": "평온",
    "신나": "신남", "빠른": "신남", "활기": "신남", "힘": "신남",
    "긴장": "긴장", "격정": "긴장", "강렬": "긴장"
}
emotion_steps = {
    "차분": [(100, 2), (110, 3), (120, 4)],
    "평온": [(140, 3), (150, 4), (160, 5)],
    "신남": [(150, 2), (160, 3), (170, 4)],
    "긴장": [(180, 3), (190, 4)]
}

# 🧠 감정 필터링 (점진 완화)
def apply_emotion_filter(df, label):
    if label not in emotion_steps:
        return df
    for tempo, sigim in emotion_steps[label]:
        filtered = df[(df["템포"] <= tempo) & (df["시김새 개수"] <= sigim)]
        if not filtered.empty:
            return filtered
    return df

# 🔍 키워드 기반 필터링
def filter_songs_by_keywords(df, user_input):
    user_input = user_input.lower()
    result = df.copy()

    # 🎼 장르 필터링
    genre_keywords = {
        "창작": "창작국악", "퓨전": "퓨전국악", "궁중": "궁중국악",
        "풍류": "풍류국악", "민속": "민속악"
    }
    for keyword, genre in genre_keywords.items():
        if keyword in user_input:
            result = result[result["장르"].str.contains(genre)]

    # 🗣️ 가사 여부
    if "가사 있는" in user_input or "노랫말" in user_input:
        result = result[result["가사유무"] == "있음"]
    elif "가사 없는" in user_input or "연주곡" in user_input:
        result = result[result["가사유무"] == "없음"]

    # 🎵 악기 필터링 (우선순위 최고)
    selected_instruments = []

    # 구체적 악기
    for name in instrument_names:
        if name in user_input:
            selected_instruments.append(name)

    # 포괄 키워드 대응
    if "성악" in user_input:
        selected_instruments += [name for name in instrument_names if "성악" in name]
    if "관악" in user_input:
        selected_instruments += [name for name in instrument_names if name in ["대금", "단소", "피리", "태평소", "소금", "생황", "훈", "퉁소", "지", "소"]]
    if "현악" in user_input:
        selected_instruments += [name for name in instrument_names if name in ["가야금", "거문고", "해금", "비파", "아쟁", "철현금"]]
    if "타악" in user_input:
        selected_instruments += [name for name in instrument_names if name in ["장구", "북", "징", "꽹과리", "소고", "바라", "정주", "축", "어"]]

    selected_instruments = list(set(selected_instruments))  # 중복 제거

    if selected_instruments:
        result = result[result["악기"].isin(selected_instruments)]

    # 🎧 감정 필터링
    emotion_label = None
    for word, label in emotion_map.items():
        if word in user_input:
            emotion_label = label
            break
    if emotion_label:
        result = apply_emotion_filter(result, emotion_label)

    # 📝 곡명 키워드 검색
    title_keywords = [word for word in user_input.split() if len(word) >= 2]
    if title_keywords:
        title_filtered = df[df["곡명"].str.contains('|'.join(title_keywords), case=False, na=False)]
        if result.empty:
            result = title_filtered
        else:
            result = pd.concat([result, title_filtered]).drop_duplicates()

    # 📌 악기 fallback
    if result.empty and selected_instruments:
        fallback = df[df["악기"].isin(selected_instruments)]
        if not fallback.empty:
            result = fallback

    # 🔀 결과 섞기 & 최대 10곡
    return result.sample(frac=1).head(10)

# 🎤 사용자 입력 → 추천 결과
def recommend_from_text(user_input):
    recommendations = filter_songs_by_keywords(df, user_input)
    if recommendations.empty:
        return ["❗ 조건에 맞는 추천 결과가 없습니다."]
    return [
        f"🎵 {row['곡명']} - {row['악기']} / 템포: {row['템포']} / 시김새: {row['시김새 목록'] or '없음'}"
        for _, row in recommendations.iterrows()
    ]

# ✅ 실행 루프
if __name__ == "__main__":
    while True:
        query = input("무엇을 듣고 싶나요? (예: 차분한 가야금 음악 or 타령 같은 곡) ")
        results = recommend_from_text(query)
        for r in results:
            print(r)
        print()
