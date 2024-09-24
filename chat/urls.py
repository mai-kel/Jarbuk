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
    path('group-chat-create/', views.create_group_chat, name='create_group_chat'),
    path('edit-group-chat/<int:chat_pk>/', views.edit_group_chat, name='edit_group_chat'),
    path('group-chat-info/<int:chat_pk>/', views.get_group_chat_info, name='get_group_chat_info'),
    path('group-chat-add-users/<int:chat_pk>/', views.get_add_users_page, name='get_add_users_page'),
    path('group-chat-add-user/', views.add_user_to_group_chat, name='add_user_to_group_chat'),
    path('group-chat-manage/<int:chat_pk>/', views.get_manage_group_page, name='manage_group_chat'),
    path('group-chat-remove-user/', views.remove_user_from_group_chat, name='remove_user_from_group_chat'),
    path('group-chat-remove-from-admins/', views.remove_from_admins, name='remove_from_admins'),
    path('group-chat-add-to-admins/', views.add_admin_to_group_chat, name='add_admin_to_group_chat'),
    path('group-chat-change-image/', views.change_chat_image, name='change_chat_image'),
    path('group-chat-change-name/', views.change_chat_name, name='change_chat_name'),
    path('group-chat-transfer-ownership/', views.transfer_ownership, name='transfer_ownership'),
    path('group-chat-delete/', views.delete_group_chat, name='delete_group_chat'),
    path('group-chat-leave/', views.leave_group_chat, name='leave_group_chat'),
    path('group-chat/paginated-messages/<int:chat_pk>/',
         views.get_paginated_group_chat_messages, name='get_group_chat_messages'),
    path('group-chat/paginated-messages/<int:chat_pk>/<str:before_cursor>/',
         views.get_paginated_group_chat_messages, name='get_group_chat_messages_cursor_given'),
    path('private-chat/paginated-messages/<int:chat_pk>/',
         views.get_paginated_private_chat_messages, name='get_private_chat_messages'),
    path('private-chat/paginated-messages/<int:chat_pk>/<str:before_cursor>/',
         views.get_paginated_private_chat_messages, name='get_private_chat_messages_cursor_given'),
]