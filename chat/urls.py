from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'chat'

urlpatterns=[
    path('', views.list_chats, name='list_chats'),
    path('get-chat/<str:chat_type>/<int:chat_id>/', views.get_rendered_chat, name='get_chat'),
    path('get-message/<str:message_type>/<int:message_id>/', views.get_rendered_message, name='get_message'),

]