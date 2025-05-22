from django.shortcuts import render
from .recommend_engine import recommend_from_text
import os
import pandas as pd

METADATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'gugak_metadata.csv')
df = pd.read_csv(METADATA_PATH)

def home(request):
    return render(request, 'home.html')

def recommend_view(request):
    user_input = request.GET.get('query', '')
    results = recommend_from_text(user_input) if user_input else []
    return render(request, 'recommend.html', {'query': user_input, 'results': results})

def player_view(request):
    filename = request.GET.get("song", "").replace(".wav", "")
    
    # 메타데이터에서 해당 파일명에 맞는 곡 정보 찾기
    song_row = df[df["파일명"] == filename + ".wav"]
    
    if not song_row.empty:
        song_info = song_row.iloc[0]
        title = f"{song_info['곡명']} - {song_info['악기']}"
    else:
        title = "알 수 없는 곡"
    
    return render(request, "player.html", {
        "filename": filename,
        "title": title
    })
