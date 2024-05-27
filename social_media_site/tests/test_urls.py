from django.test import TestCase, SimpleTestCase
from django.urls import resolve, reverse
import social_media_site.views as my_views
from django.contrib.auth import views as auth_views


class TestUrls(SimpleTestCase):

    def test_login_url_resolves(self):
        url = reverse('site:login')
        self.assertEquals(resolve(url).func.view_class, auth_views.LoginView)

    def test_logout_url_resolves(self):
        url = reverse('site:logout')
        self.assertEquals(resolve(url).func.view_class, auth_views.LogoutView)

    def test_register_url_resolves(self):
        url = reverse('site:register')
        self.assertEquals(resolve(url).func, my_views.register)

    def test_users_search_url_resolves(self):
        url = reverse('site:users_search')
        self.assertEquals(resolve(url).func, my_views.search_for_users)

    def test_user_detail_url_resolves(self):
        url = reverse('site:user_detail', args=[1234])
        self.assertEquals(resolve(url).func, my_views.user_detail)

    def test_profile_friendship_send_url_resolves(self):
        url = reverse('site:profile_friendship_send', args=[1234])
        self.assertEquals(resolve(url).func, my_views.profile_send_invitation)

    def test_profile_friendship_withdraw_url_resolves(self):
        url = reverse('site:profile_friendship_withdraw', args=[1234])
        self.assertEquals(resolve(url).func, my_views.profile_withdraw_invitation)

    def test_profile_friendship_accept_url_resolves(self):
        url = reverse('site:profile_friendship_accept', args=[1234])
        self.assertEquals(resolve(url).func, my_views.profile_accept_invitation)

    def test_profile_friendship_decline_url_resolves(self):
        url = reverse('site:profile_friendship_decline', args=[1234])
        self.assertEquals(resolve(url).func, my_views.profile_decline_invitation)

    def test_profile_friendship_delete_url_resolves(self):
        url = reverse('site:profile_friendship_delete', args=[1234])
        self.assertEquals(resolve(url).func, my_views.profile_delete_friend)

    def test_post_like_url_resolves(self):
        url = reverse('site:post_like')
        self.assertEquals(resolve(url).func, my_views.post_like)

    def test_post_detail_url_resolves(self):
        url = reverse('site:post_detail', args=[1234])
        self.assertEquals(resolve(url).func, my_views.post_detail)

    def test_create_comment_url_resolves(self):
        url = reverse('site:create_comment', args=[1234])
        self.assertEquals(resolve(url).func, my_views.create_comment)

    def test_comment_like_url_resolves(self):
        url = reverse('site:comment_like')
        self.assertEquals(resolve(url).func, my_views.comment_like)

    def test_post_create_url_resolves(self):
        url = reverse('site:post_create')
        self.assertEquals(resolve(url).func, my_views.create_post)

    def test_friends_list_url_resolves(self):
        url = reverse('site:friends_list')
        self.assertEquals(resolve(url).func, my_views.friends_list)

    def test_friends_list_delete_url_resolves(self):
        url = reverse('site:friends_list_delete', args=[1234])
        self.assertEquals(resolve(url).func, my_views.delete_friend_friendslist)

    def test_invitations_sent_url_resolves(self):
        url = reverse('site:invitations_sent')
        self.assertEquals(resolve(url).func, my_views.invitations_sent_list)

    def test_invitations_sent_withdraw_url_resolves(self):
        url = reverse('site:invitations_sent_withdraw', args=[1234])
        self.assertEquals(resolve(url).func, my_views.invitations_sent_withdraw)

    def test_invitations_received_url_resolves(self):
        url = reverse('site:invitations_received')
        self.assertEquals(resolve(url).func, my_views.invitations_received_list)

    def test_invitations_received_accept_url_resolves(self):
        url = reverse('site:invitations_received_accept', args=[1234])
        self.assertEquals(resolve(url).func, my_views.invitations_received_accept)

    def test_invitations_received_decline_url_resolves(self):
        url = reverse('site:invitations_received_decline', args=[1234])
        self.assertEquals(resolve(url).func, my_views.invitations_received_decline)

    def test_posts_feed_page_url_resolves(self):
        url = reverse('site:posts_feed_page', args=[1234])
        self.assertEquals(resolve(url).func, my_views.posts_feed)

    def test_posts_feed_url_resolves(self):
        url = reverse('site:posts_feed')
        self.assertEquals(resolve(url).func, my_views.posts_feed)




