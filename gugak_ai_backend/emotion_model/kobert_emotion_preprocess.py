import json
import pandas as pd
import os

# 경로 설정
TRAIN_JSON_PATH = r"D:\018.감성대화\Training_221115_add\라벨링데이터\감성대화말뭉치(최종데이터)_Training.json"
VAL_JSON_PATH = r"D:\018.감성대화\Validation_221115_add\라벨링데이터\감성대화말뭉치(최종데이터)_Validation.json"

# CSV 저장 경로 (현재 폴더)
TRAIN_CSV_PATH = "./train.csv"
VAL_CSV_PATH = "./val.csv"

def load_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def preprocess(data):
    rows = []
    for item in data['data']:
        for dialog in item['paragraph']:
            for sentence in dialog['utterances']:
                text = sentence['utterance']
                emotion = sentence['emotion']['type']  # 'emotion' 키 안에 'type'이 있음
                rows.append((text, emotion))
    return pd.DataFrame(rows, columns=["sentence", "label"])

def main():
    print("▶️ Training 데이터 전처리 중...")
    train_data = load_json(TRAIN_JSON_PATH)
    train_df = preprocess(train_data)
    train_df.to_csv(TRAIN_CSV_PATH, index=False)
    print(f"✅ train.csv 저장 완료: {TRAIN_CSV_PATH}")

    print("▶️ Validation 데이터 전처리 중...")
    val_data = load_json(VAL_JSON_PATH)
    val_df = preprocess(val_data)
    val_df.to_csv(VAL_CSV_PATH, index=False)
    print(f"✅ val.csv 저장 완료: {VAL_CSV_PATH}")

if __name__ == "__main__":
    main()
