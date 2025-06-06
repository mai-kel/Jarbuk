from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'social_media_site'

urlpatterns = [
    path('', views.posts_feed, name='posts_feed'),
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
    path('settings/', views.show_settings, name='show_settings'),
    path('settings/edit-profile', views.edit_profile, name='edit_profile'),
    path('settings/change-password',
         auth_views.PasswordChangeView.as_view(template_name='site/settings/change_password.html',
                                               success_url=reverse_lazy('site:change_password_done')),
         name='change_password'),
     path('settings/change-password/done',
          auth_views.PasswordChangeDoneView.as_view(template_name='site/settings/change_password_done.html'),
          name='change_password_done'),
     path('settings/change-username/', views.change_username, name='change_username'),
     path('settings/change-username/done/', views.change_username_done, name='change_username_done'),
     path('settings/change-email/', views.change_email, name='change_email'),
     path('settings/change-email/done/', views.change_email_done, name='change_email_done'),
     path('password-reset/', auth_views.PasswordResetView.as_view(template_name='site/password_reset/password_reset.html',
                                                                 email_template_name='site/password_reset/password_reset_email.html',
                                                                 subject_template_name='site/password_reset/password_reset_subject.txt',
                                                                 success_url=reverse_lazy('site:password_reset_done')),
          name='password_reset'),
     path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='site/password_reset/password_reset_done.html'),
          name='password_reset_done'),
     path('password-reset-confirm/<uidb64>/<token>/',
          auth_views.PasswordResetConfirmView.as_view(template_name='site/password_reset/password_reset_confirm.html',
                                                      success_url=reverse_lazy('site:password_reset_complete')),
          name='password_reset_confirm'),
     path('password-reset-complete/',
          auth_views.PasswordResetCompleteView.as_view(template_name='site/password_reset/password_reset_complete.html'),
          name='password_reset_complete'),

]
