import os
import json
import pandas as pd
from pathlib import Path

# 🎵 악기코드 → 악기 이름 매핑 (AI Hub 공식 기준)
instrument_map = {
    "SP01": "가야금", "SP02": "거문고", "SP03": "비파", "SP04": "철현금", "SP05": "금", "SP06": "슬",
    "SR01": "해금", "SR02": "아쟁",
    "WN01": "대금", "WN02": "소금", "WN03": "단소", "WN04": "퉁소", "WN05": "훈", "WN06": "지", "WN07": "소",
    "WR01": "피리", "WR02": "태평소", "WR03": "생황", "WR04": "나발", "WR05": "나각",
    "PN01": "장구", "PN02": "꽹과리", "PN03": "북", "PN04": "징", "PN05": "바라", "PN06": "목탁", "PN07": "종",
    "PN08": "소고", "PN09": "정주", "PN10": "축", "PN11": "어",
    "PT01": "양금", "PT02": "편종", "PT03": "편경",
    "VF01": "여성 성악", "VM02": "남성 성악", "VH03": "혼성 성악"
}

# 📁 폴더명에서 장르 추출 (ex. 유사국악_R_창작국악 → 창작국악)
def extract_subgenre(folder_name):
    parts = folder_name.split('_')
    return parts[-1] if len(parts) >= 3 else folder_name

# 📜 가사 유무 판단
def has_lyrics(annotation_data):
    return "있음" if annotation_data.get("lyrics") else "없음"

# 📝 가사 내용 추출
def extract_lyrics(annotation_data):
    if not annotation_data.get("lyrics"):
        return ""
    lyrics_lines = [line.get("lyric_text", "") for line in annotation_data["lyrics"]]
    return " ".join(lyrics_lines).strip()

# 🌊 시김새 정보 추출
def extract_sigimsae(annotation_data):
    sigimsae_data = annotation_data.get("single_tonguing_cd", [])
    sigimsae_list = [s.get("annotation_name", "") for s in sigimsae_data]
    return ", ".join(sigimsae_list), len(sigimsae_list)

# 🎯 json 1개 파일에서 메타데이터 추출
def extract_metadata(json_path, wav_path, mid_path, folder_name):
    with open(json_path, 'r', encoding='utf-8') as f:
        js = json.load(f)

    src = js["music_source_info"]
    info = js["music_type_info"]
    annotation = js["annotation_data_info"]

    tempo_val = annotation["tempo"][0]["annotation_code"]
    sigimsae_text, sigimsae_count = extract_sigimsae(annotation)

    return {
        "곡명": src["music_nm_kor"],
        "장르대분류": info["music_catagory_1"],
        "장르": extract_subgenre(folder_name),
        "장르코드": info["music_genre_cd"],
        "악기코드": info["instrument_cd"],
        "악기": instrument_map.get(info["instrument_cd"], "기타"),
        "연주자": info["main_instr_player"],
        "수집처": js["get_info"]["get_place"],
        "비트코드": annotation["gukak_beat_cd"],
        "템포": tempo_val,
        "곡길이": src["play_time"],
        "가사유무": has_lyrics(annotation),
        "가사": extract_lyrics(annotation),
        "시김새 목록": sigimsae_text,
        "시김새 개수": sigimsae_count,
        "오디오파일": str(wav_path),
        "MIDI파일": str(mid_path),
        "라벨파일": str(json_path)
    }

# 📦 전체 데이터 순회하며 처리
def collect_dataset(base_dir):
    base_dir = Path(base_dir)
    all_data = []

    for phase in ["Training", "Validation"]:
        json_root = base_dir / phase / "02.라벨링데이터"
        wav_root = base_dir / phase / "01.원천데이터"

        for genre_folder in json_root.glob("*/"):
            folder_name = genre_folder.name
            if folder_name.startswith("TL_"):
                wav_folder_name = folder_name.replace("TL_", "TS_")
            elif folder_name.startswith("VL_"):
                wav_folder_name = folder_name.replace("VL_", "VS_")
            else:
                continue

            wav_folder = wav_root / wav_folder_name

            for json_file in genre_folder.glob("*.json"):
                base_name = json_file.stem
                wav_file = wav_folder / f"{base_name}.wav"
                mid_file = wav_folder / f"{base_name}.mid"

                if wav_file.exists() and mid_file.exists():
                    try:
                        row = extract_metadata(json_file, wav_file, mid_file, wav_folder_name)
                        all_data.append(row)
                    except Exception as e:
                        print(f"[⚠️ 오류] {base_name}: {e}")
                else:
                    print(f"[❗ 누락] {base_name} - wav 또는 mid 없음")

    return pd.DataFrame(all_data)

# 🚀 실행
if __name__ == "__main__":
    base_path = r"d:\209.국악 악보 및 음원 데이터\01-1.정식개방데이터"
    df = collect_dataset(base_path)

    # ✅ 파일명만 추출한 컬럼 추가
    df["파일명"] = df["오디오파일"].apply(lambda x: os.path.basename(x))

    df.to_csv("국악_전체_전처리결과.csv", index=False, encoding="utf-8-sig")
    print("✅ 전처리 완료! 👉 저장된 파일: 국악_전체_전처리결과.csv")
