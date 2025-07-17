# LineBot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('chat/', views.chat_interface, name='chat'),  # Add this line
    path('api/', views.chat_api, name='chat_api'),
    path('clear/', views.clear_memory, name='clear_memory'),
    path('history/', views.get_chat_history, name='get_chat_history'),
]