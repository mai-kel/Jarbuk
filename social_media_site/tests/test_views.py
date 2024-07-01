from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.shortcuts import render
import social_media_site.views as my_views
from django.contrib.auth import views as auth_views, get_user
import social_media_site.models as my_models
from django.contrib.auth.models import User
from datetime import datetime, date
from social_media_site.models import Profile

def register_user(request_data: dict):
    user = User.objects.create_user(username=request_data['username'],
                             email=request_data['email'],
                             password=request_data['password'],
                             first_name=request_data['first_name'],
                             last_name=request_data['last_name'])

    Profile.objects.create(user=user,
                           date_of_birth=datetime.strptime(request_data['birthdate'], '%Y-%m-%d').date())


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


