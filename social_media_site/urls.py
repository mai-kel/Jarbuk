from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'social_media_site'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('users/', views.search_for_users, name='users_search'),
    path('user/<int:id>/', views.user_detail, name='user_detail'),
    path('user/friendship/send/<int:id>/', views.profile_send_invitation,
         name='profile_friendship_send'),
    path('user/friendship/withdraw/<int:id>/', views.profile_withdraw_invitation,
         name='profile_friendship_withdraw'),
    path('user/friendship/accept/<int:id>/', views.profile_accept_invitation,
         name='profile_friendship_accept'),
    path('user/friendship/decline/<int:id>/', views.profile_decline_invitation,
         name='profile_friendship_decline'),
    path('user/friendship/delete/<int:id>/', views.profile_delete_friend,
         name='profile_friendship_delete'),
    path('post/like/', views.post_like, name='post_like'),
    path('post/<int:id>', views.post_detail, name="post_detail"),
    path('post/<int:id>/add-comment/', views.create_comment, name="create_comment"),
    path('comment/like-comment/', views.comment_like, name="comment_like"),
    path('post/create/', views.create_post, name='post_create'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friends/delete/<int:id>/', views.delete_friend_friendslist, name='friends_list_delete'),
    path('friends/invitations-sent/', views.invitations_sent_list, name='invitations_sent'),
    path('friends/invitations-sent/withdraw/<int:id>/', views.invitations_sent_withdraw,
         name='invitations_sent_withdraw'),
    path('friends/invitations-received/', views.invitations_received_list, name='invitations_received'),
    path('friends/invitations-received/accept/<int:id>/', views.invitations_received_accept,
         name='invitations_received_accept'),
    path('friends/invitations-received/decline/<int:id>/', views.invitations_received_decline,
         name='invitations_received_decline'),
    path('posts/page/<int:page>/', views.posts_feed, name='posts_feed_page'),
    path('', views.posts_feed, name='posts_feed'),
]
