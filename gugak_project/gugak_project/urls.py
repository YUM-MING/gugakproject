from django.contrib import admin
from django.urls import path, include
from recommend.views import player_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recommend.urls')),  # recommend.urls 연결
    path("player/", player_view, name="player"),
]
