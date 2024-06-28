from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.shortcuts import render
import social_media_site.views as my_views
from django.contrib.auth import views as auth_views, get_user
import social_media_site.models as my_models
from django.contrib.auth.models import User
from datetime import datetime, date

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
        self.assertFalse(User.objects.filter(username='testuser123').exists())


class TestLogin(TestCase):

    @classmethod
    def setUpTestData(cls):
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
        Client().post(url, request_data)

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



