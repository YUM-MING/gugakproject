from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 메인 페이지
    path('recommend/', views.recommend_view, name='recommend_view'),  # 추천 결과
     path("player/", views.player_view, name="player"),  # 곡 플레이어
]
