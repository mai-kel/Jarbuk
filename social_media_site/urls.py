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
    path('post/like/<int:id>', views.post_like, name='post_like'),
    path('post/<int:id>', views.post_detail, name="post_detail"),
    path('post/create/', views.create_post, name='post_create'),
    path('friends/', views.firends_list, name='friends_list'),
    path('', views.posts_feed, name='posts_feed'),
]
