from django.urls import path
from . import views

# URL 패턴을 정의합니다. 
# 각 URL은 해당하는 뷰 함수와 연결됩니다.
urlpatterns = [
    path('', views.index, name='index'),  # 기본 URL이 index 뷰로 연결됩니다.
    path('capture/', views.capture, name='capture'),  # 'capture/' URL이 capture 뷰로 연결됩니다.
]