from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'chat'

urlpatterns=[
    path('', views.list_chats, name='list_chats'),
    path('private-chat/<int:chat_pk>/', views.get_rendered_private_chat, name='get_private_chat'),
    path('group-chat/<int:chat_pk>/', views.get_rendered_group_chat, name='get_group_chat'),
    path('private-message/<int:message_pk>/', views.get_rendered_private_message, name='get_private_message'),
    path('group-message/<int:message_pk>/', views.get_rendered_group_message, name='get_group_message'),

]