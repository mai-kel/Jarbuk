from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.shortcuts import render
import social_media_site.views as my_views
from django.contrib.auth import views as auth_views, get_user
import social_media_site.models as my_models
from django.contrib.auth.models import User
from datetime import datetime, date
from social_media_site.models import Profile, Post, FriendInvitation, Comment

def register_user(request_data: dict):
    user = User.objects.create_user(username=request_data['username'],
                             email=request_data['email'],
                             password=request_data['password'],
                             first_name=request_data['first_name'],
                             last_name=request_data['last_name'])
    Profile.objects.create(user=user,
                           date_of_birth=datetime.strptime(request_data['birthdate'], '%Y-%m-%d').date())
    return user


def login_client(client, request_data: dict):
    url = reverse('site:login')
    return client.post(url, request_data)

class TestRegistrationView(TestCase):

    def setUp(self):
        self.client = Client()

    def test_registration_get(self):
        url = reverse('site:register')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'registration/registration.html')

    def test_correct_registration_post(self):
        url = reverse('site:register')
        request_data = {
                'username': 'testuser123',
                'first_name': 'TestName',
                'last_name': 'TestSurname',
                'email': 'qwertyuiop@gmail.com',
                'password': 'testpassword',
                'password2': 'testpassword',
                'birthdate': '2021-01-01',
                }
        response = self.client.post(url, request_data)

        new_user = User.objects.get(email='qwertyuiop@gmail.com')
        self.assertTemplateUsed(response, 'registration/registration_complete.html')
        self.assertTrue(new_user)
        self.assertEquals(new_user.profile.date_of_birth, date(2021, 1, 1))
        self.assertEquals(new_user.username, 'testuser123')
        self.assertEquals(new_user.first_name, 'TestName')
        self.assertEquals(new_user.last_name, 'TestSurname')
        self.assertTrue(new_user.check_password('testpassword'))

    def test_existing_username(self):
        url = reverse('site:register')
        request_data = {
                'username': 'testuser123',
                'first_name': 'TestName',
                'last_name': 'TestSurname',
                'email': 'test_email@gmail.com',
                'password': 'testpassword',
                'password2': 'testpassword',
                'birthdate': '2021-01-01',
                }
        self.client.post(url, request_data)

        request_data2 = {
                'username': 'testuser123',
                'first_name': 'TestName',
                'last_name': 'TestSurname',
                'email': 'qwertyuiop@gmail.com',
                'password': 'testpassword',
                'password2': 'testpassword',
                'birthdate': '2021-01-01',
                }
        response = self.client.post(url, request_data2)
        self.assertTemplateUsed(response, 'registration/registration.html')
        self.assertInHTML('Username already used', response.content.decode())
        self.assertFalse(User.objects.filter(email='qwertyuiop@gmail.com').exists())

    def test_existing_email(self):
        url = reverse('site:register')
        request_data = {
                'username': 'testuser123456',
                'first_name': 'TestName',
                'last_name': 'TestSurname',
                'email': 'test_email@gmail.com',
                'password': 'testpassword',
                'password2': 'testpassword',
                'birthdate': '2021-01-01',
                }
        self.client.post(url, request_data)

        request_data2 = {
                'username': 'testuser123',
                'first_name': 'TestName',
                'last_name': 'TestSurname',
                'email': 'test_email@gmail.com',
                'password': 'testpassword',
                'password2': 'testpassword',
                'birthdate': '2021-01-01',
                }
        response = self.client.post(url, request_data2)
        self.assertTemplateUsed(response, 'registration/registration.html')
        self.assertInHTML('Email already used', response.content.decode())
        self.assertFalse(User.objects.filter(username='testuser123').exists())


class TestLogin(TestCase):

    @classmethod
    def setUpTestData(cls):
        request_data = {
                'username': 'testuser123',
                'first_name': 'TestName',
                'last_name': 'TestSurname',
                'email': 'qwertyuiop@gmail.com',
                'password': 'testpassword',
                'password2': 'testpassword',
                'birthdate': '2021-01-01',
                }
        register_user(request_data)

    def setUp(self):
        self.client = Client()

    def test_login_get(self):
        url = reverse('site:login')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_correct_login_post(self):
        self.assertFalse(get_user(self.client).is_authenticated)

        url = reverse('site:login')
        request_data = {
                'username': 'testuser123',
                'password': 'testpassword',
                }
        response = self.client.post(url, request_data)

        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertRedirects(response, reverse('site:posts_feed'))


class TestCreatePost(TestCase):

    def setUp(self):
        self.client = Client()
        request_data = {
        'username': 'testuser123',
        'first_name': 'TestName',
        'last_name': 'TestSurname',
        'email': 'qwertyuiop@gmail.com',
        'password': 'testpassword',
        'password2': 'testpassword',
        'birthdate': '2021-01-01',
        }
        register_user(request_data)
        login_client(self.client, {'username': 'testuser123', 'password': 'testpassword'})

    def test_create_post(self):
        url = reverse('site:post_create')
        request_data = {
            'text': 'Test post text',
        }
        response = self.client.post(url, request_data)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(my_models.Post.objects.filter(text='Test post text').exists())


class TestSearchForUsers(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'test_username1',
            'first_name': 'Juan',
            'last_name': 'Rodriguez',
            'email': 'test_email1@gmail.com',
            'password': 'test_password1',
            'password2': 'test_password1',
            'birthdate': '2021-01-01',
        }

        user2_data = {
            'username': 'test_username2',
            'first_name': 'Juan',
            'last_name': 'Sanchez',
            'email': 'test_email2@gmail.com',
            'password': 'test_password2',
            'password2': 'test_password2',
            'birthdate': '2021-01-01',
        }

        user3_data = {
            'username': 'test_username3',
            'first_name': 'Pablo',
            'last_name': 'Rodriguez',
            'email': 'test_email3@gmail.com',
            'password': 'test_password3',
            'password2': 'test_password3',
            'birthdate': '2021-01-01',
        }
        client = Client()
        register_user(user1_data)
        register_user(user2_data)
        register_user(user3_data)

    def setUp(self):
        self.client = Client()
        login_client(self.client, {'username': 'test_username1', 'password': 'test_password1'})

    def test_search_for_users_get(self):
        url = reverse('site:users_search')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'site/user/users_list.html')

    def test_search_by_first_name(self):
        url = reverse('site:users_search')
        response = self.client.post(url, {'first_name': 'Juan'})
        self.assertInHTML('Juan Rodriguez', response.content.decode())
        self.assertInHTML('Juan Sanchez', response.content.decode())

    def test_search_by_last_name(self):
        url = reverse('site:users_search')
        response = self.client.post(url, {'last_name': 'Rodriguez'})
        self.assertInHTML('Juan Rodriguez', response.content.decode())
        self.assertInHTML('Pablo Rodriguez', response.content.decode())

    def test_search_by_both_names(self):
        url = reverse('site:users_search')
        response = self.client.post(url, {'first_name': 'Juan', 'last_name': 'Rodriguez'})
        self.assertInHTML('Juan Rodriguez', response.content.decode())
        self.assertNotContains(response, 'Juan Sanchez')
        self.assertNotContains(response, 'Pablo Rodriguez')

    def test_search_no_users_found(self):
        url = reverse('site:users_search')
        response = self.client.post(url, {'first_name': 'Pablo', 'last_name': 'Sanchez'})
        self.assertInHTML('No users found', response.content.decode())


class TestPostsFeed(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'test_username1',
            'first_name': 'Juan',
            'last_name': 'Rodriguez',
            'email': 'test_email1@gmail.com',
            'password': 'test_password1',
            'password2': 'test_password1',
            'birthdate': '2021-01-01',
        }

        user2_data = {
            'username': 'test_username2',
            'first_name': 'Juan',
            'last_name': 'Sanchez',
            'email': 'test_email2@gmail.com',
            'password': 'test_password2',
            'password2': 'test_password2',
            'birthdate': '2021-01-01',
        }

        user3_data = {
            'username': 'test_username3',
            'first_name': 'Pablo',
            'last_name': 'Rodriguez',
            'email': 'test_email3@gmail.com',
            'password': 'test_password3',
            'password2': 'test_password3',
            'birthdate': '2021-01-01',
        }
        register_user(user1_data)
        register_user(user2_data)
        register_user(user3_data)

        post1 = Post.objects.create(author=User.objects.get(username='test_username1'),
                                    text='Test post 1 text')
        post2 = Post.objects.create(author=User.objects.get(username='test_username2'),
                                    text='Test post 2 text')
        post3 = Post.objects.create(author=User.objects.get(username='test_username3'),
                                    text='Test post 3 text')

        User.objects.get(username='test_username1').profile.friends.add(User.objects.get(username='test_username2').profile)

    def test_template_used(self):
        client = Client()
        login_client(client, {'username': 'test_username1', 'password': 'test_password1'})
        url = reverse('site:posts_feed')
        response = client.get(url)
        self.assertTemplateUsed(response, 'site/posts_feed.html')

    def test_posts_visibility(self):
        client = Client()
        login_client(client, {'username': 'test_username1', 'password': 'test_password1'})
        url = reverse('site:posts_feed')
        response = client.get(url)
        self.assertInHTML('Test post 1 text', response.content.decode())
        self.assertInHTML('Test post 2 text', response.content.decode())
        self.assertNotContains(response, 'Test post 3 text')


class TestUserDetail(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }
        user4_data = {
            'username': 'username4',
            'first_name': 'first_name4',
            'last_name': 'last_name4',
            'email': 'email4@gmail.com',
            'password': 'password4',
            'password2': 'password4',
            'birthdate': '2021-01-01',
        }
        user5_data = {
            'username': 'username5',
            'first_name': 'first_name5',
            'last_name': 'last_name5',
            'email': 'email5@gmail.com',
            'password': 'password5',
            'password2': 'password5',
            'birthdate': '2021-01-01',
        }
        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)
        user4 = register_user(user4_data)
        user5 = register_user(user5_data)

        user1.profile.friends.add(user2.profile)
        FriendInvitation.objects.create(from_who=user1, to_who=user4)
        FriendInvitation.objects.create(from_who=user3, to_who=user1)

        for i in range(1, 6):
            Post.objects.create(author=locals()[f'user{i}'], text=f'User{i} post text 1')

        for i in range(2, 15):
            Post.objects.create(author=user1, text=f'User1 post text {i}')

    def setUp(self):
        self.client = Client()

    def test_template_used(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username1').pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'site/user/user_detail.html')

    def test_user_sees_his_last_10_posts(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username1').pk])
        response = self.client.get(url)
        self.assertInHTML('User1 post text 1', response.content.decode())
        self.assertInHTML('User1 post text 10', response.content.decode())
        self.assertNotContains(response, 'User1 post text 12')
        self.assertNotContains(response, 'User1 post text 11')

    def test_user_sees_his_friends_posts(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username2').pk])
        response = self.client.get(url)
        self.assertContains(response, 'User2 post text 1')

    def test_user_can_delete_friend(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username2').pk])
        response = self.client.get(url)
        self.assertContains(response, 'Delete from friends')
        self.assertContains(response, reverse('site:profile_friendship_delete',
                                              args=[User.objects.get(username='username2').pk]))

    def test_user_cant_see_strangers_posts(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username5').pk])
        response = self.client.get(url)
        self.assertNotContains(response, 'User5 post text 1')

    def test_user_cant_see_invited_user_posts(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username4').pk])
        response = self.client.get(url)
        self.assertNotContains(response, 'User4 post text 1')

    def test_user_cant_see_inviting_user_posts(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username3').pk])
        response = self.client.get(url)
        self.assertNotContains(response, 'User3 post text 1')

    def test_user_can_invite(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username5').pk])
        response = self.client.get(url)
        self.assertContains(response, 'Invite to friends')
        self.assertContains(response, reverse('site:profile_friendship_send',
                                              args=[User.objects.get(username='username5').pk]))

    def test_user_can_accept_and_decline_invitation(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:user_detail', args=[User.objects.get(username='username3').pk])
        response = self.client.get(url)
        self.assertContains(response, 'Accept friendship invitation')
        self.assertContains(response, reverse('site:profile_friendship_accept',
                                              args=[User.objects.get(username='username3').pk]))
        self.assertContains(response, 'Decline friendship invitation')
        self.assertContains(response, reverse('site:profile_friendship_decline',
                                              args=[User.objects.get(username='username3').pk]))


class TestPostLike(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }
        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)

        user1.profile.friends.add(user2.profile)

        Post.objects.create(author=user1, text='User1 post text')
        Post.objects.create(author=user2, text='User2 post text')
        Post.objects.create(author=user3, text='User3 post text')

    def setUp(self):
        self.client = Client()
        self.post1 = Post.objects.get(author__username='username1')
        self.post2 = Post.objects.get(author__username='username2')
        self.post3 = Post.objects.get(author__username='username3')

    def test_user_liking_his_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:post_like')
        response = self.client.post(url, {'id': self.post1.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'liked')
        self.assertTrue(self.post1.likes.count() == 1)

    def test_user_unliking_his_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.post1.likes.add(User.objects.get(username='username1'))
        url = reverse('site:post_like')
        response = self.client.post(url, {'id': self.post1.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'unliked')
        self.assertTrue(self.post1.likes.count() == 0)

    def test_user_liking_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:post_like')
        response = self.client.post(url, {'id': self.post2.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'liked')
        self.assertTrue(self.post2.likes.count() == 1)

    def test_user_unliking_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.post2.likes.add(User.objects.get(username='username1'))
        url = reverse('site:post_like')
        response = self.client.post(url, {'id': self.post2.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'unliked')
        self.assertTrue(self.post2.likes.count() == 0)

    def test_user_liking_strangers_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:post_like')
        response = self.client.post(url, {'id': self.post3.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'error')
        self.assertTrue(self.post3.likes.count() == 0)


class TestCommentLike(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }
        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)

        user1.profile.friends.add(user2.profile)
        user2.profile.friends.add(user3.profile)

        post1=Post.objects.create(author=user1, text='User1 post text')
        post2=Post.objects.create(author=user2, text='User2 post text')
        post3=Post.objects.create(author=user3, text='User3 post text')

        Comment.objects.create(author=user1, post=post1, text='User1 comment post1')
        Comment.objects.create(author=user1, post=post2, text='User1 comment post2')
        Comment.objects.create(author=user2, post=post3, text='User2 comment post3')
        Comment.objects.create(author=user3, post=post2, text='User3 comment post2')

    def setUp(self):
        self.client = Client()
        self.comment1 = Comment.objects.get(text='User1 comment post1')
        self.comment2 = Comment.objects.get(text='User1 comment post2')
        self.comment3 = Comment.objects.get(text='User2 comment post3')
        self.comment4 = Comment.objects.get(text='User3 comment post2')


    def test_user_liking_his_comment_under_his_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment1.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'liked')
        self.assertTrue(self.comment1.likes.count() == 1)

    def test_user_unliking_his_comment_under_his_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.comment1.likes.add(User.objects.get(username='username1'))
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment1.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'unliked')
        self.assertTrue(self.comment1.likes.count() == 0)

    def test_user_liking_his_comment_under_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment2.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'liked')
        self.assertTrue(self.comment2.likes.count() == 1)

    def test_user_unliking_his_comment_under_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.comment2.likes.add(User.objects.get(username='username1'))
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment2.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'unliked')
        self.assertTrue(self.comment2.likes.count() == 0)

    def test_user_liking_strangers_comment_under_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment4.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'liked')
        self.assertTrue(self.comment4.likes.count() == 1)

    def test_user_unliking_strangers_comment_under_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.comment4.likes.add(User.objects.get(username='username1'))
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment4.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(response.json()['action'] == 'unliked')
        self.assertTrue(self.comment4.likes.count() == 0)

    def test_user_liking_friends_comment_under_strangers_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:comment_like')
        response = self.client.post(url, {'id': self.comment3.pk})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'error')
        self.assertTrue(self.comment3.likes.count() == 0)


class TestPostDetail(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }
        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)

        user1.profile.friends.add(user2.profile)

        post1=Post.objects.create(author=user1, text='User1 post text')
        post2=Post.objects.create(author=user2, text='User2 post text')
        post3=Post.objects.create(author=user3, text='User3 post text')

        Comment.objects.create(author=user1, post=post1, text='User1 comment post1')
        Comment.objects.create(author=user2, post=post1, text='User2 comment post1')
        Comment.objects.create(author=user1, post=post2, text='User1 comment post2')
        Comment.objects.create(author=user3, post=post2, text='User3 comment post2')

    def setUp(self):
        self.client = Client()
        self.post1 = Post.objects.get(text='User1 post text')
        self.post2 = Post.objects.get(text='User2 post text')
        self.post3 = Post.objects.get(text='User3 post text')

    def test_user_sees_his_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:post_detail', args=[self.post1.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'site/post/post_detail.html')
        self.assertInHTML('User1 post text', response.content.decode())
        self.assertInHTML('User1 comment post1', response.content.decode())
        self.assertInHTML('User2 comment post1', response.content.decode())

    def test_user_sees_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:post_detail', args=[self.post2.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'site/post/post_detail.html')
        self.assertInHTML('User2 post text', response.content.decode())
        self.assertInHTML('User1 comment post2', response.content.decode())
        self.assertInHTML('User3 comment post2', response.content.decode())

    def test_user_cant_see_strangers_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:post_detail', args=[self.post3.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'site/post/post_no_auth.html')
        self.assertInHTML('Author of this post is not on your friends list. You need to be friends with the author to see the post.',
                          response.content.decode())


class TestCreateComment(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }
        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)

        user1.profile.friends.add(user2.profile)

        post1=Post.objects.create(author=user1, text='User1 post text')
        post2=Post.objects.create(author=user2, text='User2 post text')
        post3=Post.objects.create(author=user3, text='User3 post text')

    def setUp(self):
        self.client = Client()
        self.post1 = Post.objects.get(text='User1 post text')
        self.post2 = Post.objects.get(text='User2 post text')
        self.post3 = Post.objects.get(text='User3 post text')

    def test_user_commenting_his_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:create_comment', args=[self.post1.pk])
        response = self.client.post(url, {'text': 'User1 comment post1'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(Comment.objects.filter(text='User1 comment post1').exists())

    def test_user_commenting_friends_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:create_comment', args=[self.post2.pk])
        response = self.client.post(url, {'text': 'User1 comment post2'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'ok')
        self.assertTrue(Comment.objects.filter(text='User1 comment post2').exists())

    def test_user_cant_comment_strangers_post(self):
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        url = reverse('site:create_comment', args=[self.post3.pk])
        response = self.client.post(url, {'text': 'User1 comment post3'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['status'] == 'error')
        self.assertFalse(Comment.objects.filter(text='User1 comment post3').exists())


class TestProfileSendInvitation(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }

        user4_data = {
            'username': 'username4',
            'first_name': 'first_name4',
            'last_name': 'last_name4',
            'email': 'email4@gmail.com',
            'password': 'password4',
            'password2': 'password4',
            'birthdate': '2021-01-01',
        }

        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)
        user4 = register_user(user4_data)

        user1.profile.friends.add(user2.profile)
        FriendInvitation.objects.create(from_who=user3, to_who=user1)

    def setUp(self):
        self.client = Client()
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.user1 = User.objects.get(username='username1')
        self.user2 = User.objects.get(username='username2')
        self.user3 = User.objects.get(username='username3')
        self.user4 = User.objects.get(username='username4')

    def test_user_invites_himself(self):
        url = reverse('site:profile_friendship_send', args=[self.user1.pk])
        self.client.post(url)
        self.assertFalse(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user1).exists())

    def test_user_invites_his_friend(self):
        url = reverse('site:profile_friendship_send', args=[self.user2.pk])
        self.client.post(url)
        self.assertFalse(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user2).exists())

    def test_user_invites_user_who_had_invited_him_before(self):
        url = reverse('site:profile_friendship_send', args=[self.user3.pk])
        self.client.post(url)
        self.assertFalse(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user3).exists())

    def test_user_invites_stranger(self):
        url = reverse('site:profile_friendship_send', args=[self.user4.pk])
        self.client.post(url)
        self.assertTrue(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user4).exists())


class TestProfileWithdrawInvitation(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }

        user4_data = {
            'username': 'username4',
            'first_name': 'first_name4',
            'last_name': 'last_name4',
            'email': 'email4@gmail.com',
            'password': 'password4',
            'password2': 'password4',
            'birthdate': '2021-01-01',
        }

        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)
        user4 = register_user(user4_data)

        user1.profile.friends.add(user2.profile)
        FriendInvitation.objects.create(from_who=user3, to_who=user1)
        FriendInvitation.objects.create(from_who=user1, to_who=user4)

    def setUp(self):
        self.client = Client()
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.user1 = User.objects.get(username='username1')
        self.user2 = User.objects.get(username='username2')
        self.user3 = User.objects.get(username='username3')
        self.user4 = User.objects.get(username='username4')

    def test_withdraw_invitation_friends(self):
        url = reverse('site:profile_friendship_withdraw', args=[self.user2.pk])
        self.client.post(url)
        self.assertTrue(self.user2.profile in self.user1.profile.friends.all())

    def test_withdraw_received_invitation(self):
        url = reverse('site:profile_friendship_withdraw', args=[self.user3.pk])
        self.client.post(url)
        self.assertTrue(FriendInvitation.objects.filter(from_who=self.user3, to_who=self.user1).exists())

    def test_withdraw_sent_invitation(self):
        url = reverse('site:profile_friendship_withdraw', args=[self.user4.pk])
        response = self.client.post(url)
        print(response.content.decode())
        self.assertFalse(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user4).exists())


class TestProfileAcceptInvitation(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }

        user4_data = {
            'username': 'username4',
            'first_name': 'first_name4',
            'last_name': 'last_name4',
            'email': 'email4@gmail.com',
            'password': 'password4',
            'password2': 'password4',
            'birthdate': '2021-01-01',
        }

        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)
        user4 = register_user(user4_data)

        FriendInvitation.objects.create(from_who=user2, to_who=user1)
        FriendInvitation.objects.create(from_who=user1, to_who=user3)

    def setUp(self):
        self.client = Client()
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.user1 = User.objects.get(username='username1')
        self.user2 = User.objects.get(username='username2')
        self.user3 = User.objects.get(username='username3')
        self.user4 = User.objects.get(username='username4')

    def test_user_accept_his_invitation(self):
        url = reverse('site:profile_friendship_accept', args=[self.user3.pk])
        self.client.post(url)
        self.assertFalse(self.user3.profile in self.user1.profile.friends.all())
        self.assertTrue(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user3).exists())

    def test_user_accept_non_existing_invitation(self):
        url = reverse('site:profile_friendship_accept', args=[self.user4.pk])
        response = self.client.post(url)
        self.assertFalse(self.user4.profile in self.user1.profile.friends.all())

    def test_user_accept_received_invitation(self):
        url = reverse('site:profile_friendship_accept', args=[self.user2.pk])
        self.client.post(url)
        self.assertTrue(self.user2.profile in self.user1.profile.friends.all())
        self.assertFalse(FriendInvitation.objects.filter(from_who=self.user2, to_who=self.user1).exists())


class TestProfileDeclineInvitation(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1_data = {
            'username': 'username1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'email': 'email1@gmail.com',
            'password': 'password1',
            'password2': 'password1',
            'birthdate': '2021-01-01',
        }
        user2_data = {
            'username': 'username2',
            'first_name': 'first_name2',
            'last_name': 'last_name2',
            'email': 'email2@gmail.com',
            'password': 'password2',
            'password2': 'password2',
            'birthdate': '2021-01-01',
        }
        user3_data = {
            'username': 'username3',
            'first_name': 'first_name3',
            'last_name': 'last_name3',
            'email': 'email3@gmail.com',
            'password': 'password3',
            'password2': 'password3',
            'birthdate': '2021-01-01',
        }

        user4_data = {
            'username': 'username4',
            'first_name': 'first_name4',
            'last_name': 'last_name4',
            'email': 'email4@gmail.com',
            'password': 'password4',
            'password2': 'password4',
            'birthdate': '2021-01-01',
        }

        user1 = register_user(user1_data)
        user2 = register_user(user2_data)
        user3 = register_user(user3_data)
        user4 = register_user(user4_data)

        FriendInvitation.objects.create(from_who=user2, to_who=user1)
        FriendInvitation.objects.create(from_who=user1, to_who=user3)
        user1.profile.friends.add(user4.profile)

    def setUp(self):
        self.client = Client()
        login_client(self.client, {'username': 'username1', 'password': 'password1'})
        self.user1 = User.objects.get(username='username1')
        self.user2 = User.objects.get(username='username2')
        self.user3 = User.objects.get(username='username3')
        self.user4 = User.objects.get(username='username4')

    def test_decline_invitation_friends(self):
        url = reverse('site:profile_friendship_decline', args=[self.user4.pk])
        self.client.post(url)
        self.assertTrue(self.user4.profile in self.user1.profile.friends.all())

    def test_user_declines_his_invitation(self):
        url = reverse('site:profile_friendship_decline', args=[self.user3.pk])
        self.client.post(url)
        self.assertTrue(FriendInvitation.objects.filter(from_who=self.user1, to_who=self.user3).exists())

    def test_user_declines_received_invitation(self):
        url = reverse('site:profile_friendship_decline', args=[self.user2.pk])
        self.client.post(url)
        self.assertFalse(FriendInvitation.objects.filter(from_who=self.user2, to_who=self.user1).exists())
        self.assertFalse(self.user2.profile in self.user1.profile.friends.all())


