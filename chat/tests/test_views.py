from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user
from chat.models import GroupMessage, PrivateMessage, GroupChat, PrivateChat
from social_media_site.models import Profile
from django.contrib.auth.models import User
from datetime import datetime, date
from chat.factories import GroupChatFactory, PrivateChatFactory, GroupMessageFactory, PrivateMessageFactory
from social_media_site.factories import UserFactory, ProfileFactory
from django.contrib import auth
from django.template import defaultfilters


class TestListChats(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.group_chat = GroupChatFactory(owner=cls.user, participants=[cls.user, cls.user2])
        cls.group_chat2 = GroupChatFactory(owner=cls.user2, participants=[cls.user2, cls.user])
        cls.group_chat3 = GroupChatFactory(owner=cls.user3, participants=[cls.user3, cls.user2])
        cls.group_message = GroupMessageFactory(destination=cls.group_chat, author=cls.user)
        cls.user.profile.friends.add(cls.user2.profile)
        cls.user2.profile.friends.add(cls.user3.profile)

    def test_template(self):
        self.client.force_login(self.user)
        url = reverse('chat:list_chats')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'chat/list_chats.html')

    def test_user_sees_group_chats(self):
        self.client.force_login(self.user)
        url = reverse('chat:list_chats')
        response = self.client.get(url)
        self.assertContains(response, self.group_chat.name)
        self.assertContains(response, self.group_chat2.name)

    def test_user_does_not_see_group_chats_he_is_not_participant_of(self):
        self.client.force_login(self.user)
        url = reverse('chat:list_chats')
        response = self.client.get(url)
        self.assertNotContains(response, self.group_chat3.name)

    def test_chat_last_message_visible(self):
        self.client.force_login(self.user)
        url = reverse('chat:list_chats')
        response = self.client.get(url)
        last_message = self.group_chat.get_last_message()
        last_message_truncated = defaultfilters.truncatechars(last_message.text, 30)
        last_message_truncated = f'{last_message.author.first_name} {last_message.author.last_name}: {last_message_truncated}'
        self.assertContains(response, last_message_truncated)

    def test_user_sees_private_chats(self):
        self.client.force_login(self.user)
        url = reverse('chat:list_chats')
        response = self.client.get(url)
        self.assertContains(response, self.user2.first_name+' '+self.user2.last_name)

    def test_user_does_not_see_private_chats_he_is_not_participant_of(self):
        self.client.force_login(self.user)
        url = reverse('chat:list_chats')
        response = self.client.get(url)
        self.assertNotContains(response, self.user3.first_name+' '+self.user3.last_name)


class TestGetPrivateChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.user1.profile.friends.add(cls.user2.profile)
        cls.priv_chat1 = PrivateChat.objects.filter(participants=cls.user1).filter(participants=cls.user2).first()
        cls.priv_msgs = PrivateMessageFactory.create_batch(10, destination=cls.priv_chat1, author=cls.user1)
        cls.priv_msg1 = PrivateMessageFactory(destination=cls.priv_chat1, author=cls.user1)
        cls.priv_msg2 = PrivateMessageFactory(destination=cls.priv_chat1, author=cls.user2)

    def test_user_try_get_non_existing_chat(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_private_chat', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_try_get_chat_he_is_not_participant_of(self):
        self.client.force_login(self.user3)
        url = reverse('chat:get_private_chat', args=[self.priv_chat1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_user_gets_chat(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_private_chat', args=[self.priv_chat1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        rendered_chat = response.json()['rendered_chat'].replace('<br>', '\n')
        self.assertIn(self.priv_msg1.text, rendered_chat)
        self.assertIn(self.priv_msg2.text, rendered_chat)
        self.assertIn(self.priv_msgs[2].text, rendered_chat)
        self.assertNotIn(self.priv_msgs[0].text, rendered_chat)
        self.assertNotIn(self.priv_msgs[1].text, rendered_chat)


class TestGetGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.group_chat = GroupChatFactory(owner=cls.user1, participants=[cls.user1, cls.user2])
        cls.group_msgs = GroupMessageFactory.create_batch(10, destination=cls.group_chat, author=cls.user1)
        cls.group_msg1 = GroupMessageFactory(destination=cls.group_chat, author=cls.user1)
        cls.group_msg2 = GroupMessageFactory(destination=cls.group_chat, author=cls.user2)

    def test_user_try_get_non_existing_chat(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_group_chat', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_try_get_chat_he_is_not_participant_of(self):
        self.client.force_login(self.user3)
        url = reverse('chat:get_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_user_gets_chat(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        rendered_chat = response.json()['rendered_chat'].replace('<br>', '\n')
        self.assertIn(self.group_msg1.text, rendered_chat)
        self.assertIn(self.group_msg2.text, rendered_chat)
        self.assertIn(self.group_msgs[2].text, rendered_chat)
        self.assertNotIn(self.group_msgs[0].text, rendered_chat)
        self.assertNotIn(self.group_msgs[1].text, rendered_chat)


class TestGetPrivateMessage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.user1.profile.friends.add(cls.user2.profile)
        cls.priv_chat1 = PrivateChat.objects.filter(participants=cls.user1).filter(participants=cls.user2).first()
        cls.priv_msg1 = PrivateMessageFactory(destination=cls.priv_chat1, author=cls.user1)

    def test_user_try_get_non_existing_message(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_private_message', args=[100])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Message not found')

    def test_user_try_get_message_from_chat_he_is_not_participant_of(self):
        self.client.force_login(self.user3)
        url = reverse('chat:get_private_message', args=[self.priv_msg1.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of the chat, where this message was sent')

    def test_user_gets_message(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_private_message', args=[self.priv_msg1.pk])
        response = self.client.get(url)
        response_json = response.json()
        message_br = self.priv_msg1.text.replace('\n', '<br>')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertIn(message_br, response_json['rendered_message'])


class TestGetGroupMessage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.group_chat = GroupChatFactory(owner=cls.user1, participants=[cls.user1, cls.user2])
        cls.group_msg1 = GroupMessageFactory(destination=cls.group_chat, author=cls.user1)

    def test_user_try_get_non_existing_message(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_group_message', args=[100])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Message not found')

    def test_user_try_get_message_from_chat_he_is_not_participant_of(self):
        self.client.force_login(self.user3)
        url = reverse('chat:get_group_message', args=[self.group_msg1.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of the chat, where this message was sent')

    def test_user_gets_message(self):
        self.client.force_login(self.user1)
        url = reverse('chat:get_group_message', args=[self.group_msg1.pk])
        response = self.client.get(url)
        response_json = response.json()
        message_br = self.group_msg1.text.replace('\n', '<br>')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertIn(message_br, response_json['rendered_message'])