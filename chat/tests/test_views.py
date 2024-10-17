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


class TestCreateGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.user1.profile.friends.add(cls.user2.profile)

    def test_create_group_chat_empty_body(self):
        self.client.force_login(self.user1)
        url = reverse('chat:create_group_chat')
        response = self.client.post(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')

    def test_create_group_chat_participants_is_not_friend(self):
        self.client.force_login(self.user1)
        url = reverse('chat:create_group_chat')
        post_body = {
            'name': 'test',
            'participants': [self.user3.pk]
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')

    def test_create_group_chat_success(self):
        self.client.force_login(self.user1)
        url = reverse('chat:create_group_chat')
        post_body = {
            'name': 'test',
            'participants': [self.user2.pk],
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(GroupChat.objects.count(), 1)
        group_chat = GroupChat.objects.first()
        self.assertEqual(group_chat.name, 'test')
        self.assertEqual(group_chat.owner, self.user1)
        self.assertTrue(self.user1 in group_chat.participants.all())
        self.assertTrue(self.user2 in group_chat.participants.all())


class TestGetGroupChatInfo(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(4)
        cls.group_chat = GroupChatFactory(owner=cls.users[0],
                                          participants=[cls.users[0], cls.users[1], cls.users[2]],
                                          admins=[cls.users[1]])

    def test_user_try_get_info_of_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:get_group_chat_info', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_try_get_info_of_chat_he_is_not_participant_of(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:get_group_chat_info', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_user_gets_info(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:get_group_chat_info', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        rendered_template = response_json['rendered_template']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertTemplateUsed(response, 'chat/group_chat_info.html')
        self.assertIn(self.group_chat.name, rendered_template)
        for participant in self.users[:-1]:
            self.assertIn(participant.first_name+' '+participant.last_name, rendered_template)
        self.assertNotIn(self.users[-1].first_name+' '+self.users[-1].last_name, rendered_template)


class TestGetAddUsersPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)
        cls.group_chat = GroupChatFactory(owner=cls.users[0],
                                          participants=[cls.users[0], cls.users[1], cls.users[2]],
                                          admins=[cls.users[1]])
        cls.users[0].profile.friends.add(cls.users[3].profile)
        cls.users[0].profile.friends.add(cls.users[2].profile)

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:get_add_users_page', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:get_add_users_page', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to add users to this chat')

    def test_template(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:get_add_users_page', args=[self.group_chat.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'chat/add_users_to_chat.html')

    def test_only_friends_ot_of_group_are_shown(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:get_add_users_page', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        rendered_template = response_json['rendered_template']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertIn(self.users[3].first_name+' '+self.users[3].last_name, rendered_template)
        self.assertNotIn(self.users[4].first_name+' '+self.users[4].last_name, rendered_template)
        self.assertNotIn(self.users[2].first_name+' '+self.users[2].last_name, rendered_template)


class TestAddUserToGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)
        cls.group_chat = GroupChatFactory(owner=cls.users[0],
                                          participants=[cls.users[0], cls.users[1], cls.users[2]],
                                          admins=[cls.users[1]])
        cls.users[0].profile.friends.add(cls.users[3].profile)
        cls.users[0].profile.friends.add(cls.users[2].profile)

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': 100,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_user(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to add users to this chat')

    def test_not_admin(self):
        self.client.force_login(self.users[2])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to add users to this chat')

    def test_user_not_friend(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[4].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You can only add friends to the chat')

    def test_user_already_participant(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[2].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is already a participant of this chat')

    def test_success(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_user_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        self.assertFalse(self.users[3] in self.group_chat.participants.all())
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'User added to the chat')
        self.assertTrue(self.users[3] in self.group_chat.participants.all())


class TestGetManageGroupPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)
        cls.group_chat = GroupChatFactory(owner=cls.users[0],
                                          participants=[cls.users[0], cls.users[1], cls.users[2], cls.users[4]],
                                          admins=[cls.users[1], cls.users[4]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:manage_group_chat', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:manage_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to manage this chat')

    def test_participant_not_admin(self):
        self.client.force_login(self.users[2])
        url = reverse('chat:manage_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to manage this chat')

    def test_template(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:manage_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'chat/manage_group_chat.html')

    def test_admin_success(self):
        self.client.force_login(self.users[1])
        url = reverse('chat:manage_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        rendered_template = response_json['rendered_template']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertNotIn("Remove group", rendered_template)
        self.assertNotIn("Remove from admins", rendered_template)
        self.assertNotIn("Add to admins", rendered_template)
        self.assertNotIn("Transfer ownership", rendered_template)
        self.assertIn("Remove from group", rendered_template)

    def test_owner_success(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:manage_group_chat', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        rendered_template = response_json['rendered_template']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertIn("Remove group", rendered_template)
        self.assertIn("Remove from admins", rendered_template)
        self.assertIn("Add to admins", rendered_template)
        self.assertIn("Transfer ownership", rendered_template)
        self.assertIn("Remove from group", rendered_template)


class TestRemoveUserFromGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)

    def setUp(self):
        self.group_chat = GroupChatFactory(owner=self.users[0],
                                           participants=[self.users[0], self.users[1], self.users[2], self.users[3]],
                                           admins=[self.users[1], self.users[3]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': 100,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_user(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_remove_someone_who_is_not_participant(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[4].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is not a participant of this chat')

    def test_remove_as_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete users from this chat')

    def test_remove_as_participant(self):
        self.client.force_login(self.users[2])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete users from this chat')

    def test_remove_admin_as_admin(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[1].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete another admin from the chat')

    def test_remove_owner_as_admin(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[0].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete the owner from the chat')

    def test_remove_participant_as_admin(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[2].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'User deleted from the chat')
        self.assertFalse(self.users[2] in self.group_chat.participants.all())

    def test_remove_admin_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'User deleted from the chat')
        self.assertFalse(self.users[3] in self.group_chat.participants.all())
        self.assertFalse(self.users[3] in self.group_chat.admins.all())

    def test_remove_owner_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[0].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        err_msg = "You have to transfer the ownership to another user before deleting yourself from the chat"
        self.assertEqual(response_json['message'], err_msg)

    def test_remove_participant_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_user_from_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[2].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'User deleted from the chat')
        self.assertFalse(self.users[2] in self.group_chat.participants.all())


class TestRemoveFromAdmins(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)

    def setUp(self):
        self.group_chat = GroupChatFactory(owner=self.users[0],
                                           participants=[self.users[0], self.users[1], self.users[2], self.users[3]],
                                           admins=[self.users[1], self.users[2]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': 100,
            'user_pk': self.users[2].pk
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_user(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_remove_as_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[2].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete admins from this chat')

    def test_remove_not_participant(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[4].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is not an admin of this chat')

    def test_remove_not_admin(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is not an admin of this chat')
        self.assertTrue(self.users[3] in self.group_chat.participants.all())

    def test_remove_as_admin(self):
        self.client.force_login(self.users[2])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[1].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete admins from this chat')

    def test_remove_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:remove_from_admins')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[1].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'User removed from admins')
        self.assertFalse(self.users[1] in self.group_chat.admins.all())


class TestAddAdminToGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)

    def setUp(self):
        self.group_chat = GroupChatFactory(owner=self.users[0],
                                           participants=[self.users[0], self.users[1], self.users[2], self.users[3]],
                                           admins=[self.users[1], self.users[2]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': 100,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_user(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_add_as_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to add admins to this chat')

    def test_add_not_participant(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[4].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is not a participant of this chat')

    def test_add_as_admin(self):
        self.client.force_login(self.users[2])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to add admins to this chat')

    def test_add_already_admin(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[1].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is already an admin of this chat')

    def test_add_success(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:add_admin_to_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'User added to the admins')
        self.assertTrue(self.users[3] in self.group_chat.admins.all())


class ChangeChatName(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)

    def setUp(self):
        self.group_chat = GroupChatFactory(owner=self.users[0],
                                           participants=[self.users[0], self.users[1], self.users[2], self.users[3]],
                                           admins=[self.users[1], self.users[2]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:change_chat_name')
        post_body = {
            'chat_pk': 100,
            'new_name': 'test'
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:change_chat_name')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'new_name': 'test'
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to change the name of this chat')

    def test_not_admin(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:change_chat_name')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'new_name': 'test'
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to change the name of this chat')

    def test_as_admin(self):
        self.client.force_login(self.users[1])
        url = reverse('chat:change_chat_name')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'new_name': 'test'
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.group_chat.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'Name changed successfully')
        self.assertEqual(self.group_chat.name, 'test')

    def test_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:change_chat_name')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'new_name': 'test'
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.group_chat.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'Name changed successfully')
        self.assertEqual(self.group_chat.name, 'test')


class TestTransferOwnership(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)

    def setUp(self):
        self.group_chat = GroupChatFactory(owner=self.users[0],
                                           participants=[self.users[0], self.users[1], self.users[2], self.users[3]],
                                           admins=[self.users[1], self.users[2]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': 100,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_non_existing_user(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_as_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to transfer the ownership of this chat')

    def test_as_admin(self):
        self.client.force_login(self.users[1])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to transfer the ownership of this chat')

    def test_transfer_to_not_participant(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[4].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'User is not a participant of this chat')

    def test_transer_to_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[0].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are already the owner of this chat')

    def test_transfer_to_admin(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[1].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'Ownership transferred successfully')
        self.group_chat.refresh_from_db()
        self.assertEqual(self.group_chat.owner, self.users[1])
        self.assertTrue(self.users[1] not in self.group_chat.admins.all())
        self.assertTrue(self.users[1] in self.group_chat.participants.all())
        self.assertTrue(self.users[0] in self.group_chat.admins.all())
        self.assertTrue(self.users[0] in self.group_chat.participants.all())

    def test_transfer_to_participant(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:transfer_ownership')
        post_body = {
            'chat_pk': self.group_chat.pk,
            'user_pk': self.users[3].pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'Ownership transferred successfully')
        self.group_chat.refresh_from_db()
        self.assertEqual(self.group_chat.owner, self.users[3])
        self.assertTrue(self.users[3] not in self.group_chat.admins.all())
        self.assertTrue(self.users[3] in self.group_chat.participants.all())
        self.assertTrue(self.users[0] in self.group_chat.admins.all())
        self.assertTrue(self.users[0] in self.group_chat.participants.all())


class TestDeleteGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)
        cls.group_chat = GroupChatFactory(owner=cls.users[0],
                                          participants=[cls.users[0], cls.users[1], cls.users[2], cls.users[3]],
                                          admins=[cls.users[1], cls.users[2]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:delete_group_chat')
        post_body = {
            'chat_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:delete_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete this chat')

    def test_as_participant(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:delete_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete this chat')

    def test_as_admin(self):
        self.client.force_login(self.users[1])
        url = reverse('chat:delete_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You have no permission to delete this chat')

    def test_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:delete_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'Chat deleted successfully')
        self.assertFalse(GroupChat.objects.filter(pk=self.group_chat.pk).exists())

class TestLeaveGroupChat(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.users = UserFactory.create_batch(5)

    def setUp(self):
        self.group_chat = GroupChatFactory(owner=self.users[0],
                                           participants=[self.users[0], self.users[1], self.users[2], self.users[3]],
                                           admins=[self.users[1], self.users[2]])

    def test_non_existing_chat(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:leave_group_chat')
        post_body = {
            'chat_pk': 100
        }
        response = self.client.post(url, post_body)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.users[4])
        url = reverse('chat:leave_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_as_admin(self):
        self.client.force_login(self.users[1])
        url = reverse('chat:leave_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'You left the chat')
        self.assertFalse(self.users[1] in self.group_chat.participants.all())
        self.assertFalse(self.users[1] in self.group_chat.admins.all())

    def test_as_owner(self):
        self.client.force_login(self.users[0])
        url = reverse('chat:leave_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        err_msg = "You have to transfer the ownership to another user before leaving the chat"
        self.assertEqual(response_json['message'], err_msg)

    def test_as_participant(self):
        self.client.force_login(self.users[3])
        url = reverse('chat:leave_group_chat')
        post_body = {
            'chat_pk': self.group_chat.pk
        }
        response = self.client.post(url, post_body)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['message'], 'You left the chat')
        self.assertFalse(self.users[3] in self.group_chat.participants.all())
        self.assertFalse(self.users[3] in self.group_chat.admins.all())


class TestGetGroupChatMessages(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = UserFactory()
        cls.user2 = UserFactory()
        cls.group_chat = GroupChatFactory(owner=cls.user,
                                          participants=[cls.user])
        cls.group_msgs = GroupMessageFactory.create_batch(30, destination=cls.group_chat,
                                                          author=cls.user)

    def test_non_existing_chat(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_group_chat_messages', args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.user2)
        url = reverse('chat:get_group_chat_messages', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_pagination_correct(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_group_chat_messages', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        rendered_template = response_json['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['has_previous_page'], True)
        self.assertIn(self.group_msgs[29].text, rendered_template)
        self.assertIn(self.group_msgs[20].text, rendered_template)
        self.assertNotIn(self.group_msgs[19].text, rendered_template)


class TestGetGroupChatMessagesBeforeIdGiven(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = UserFactory()
        cls.user2 = UserFactory()
        cls.group_chat = GroupChatFactory(owner=cls.user,
                                          participants=[cls.user])
        cls.group_msgs = GroupMessageFactory.create_batch(30, destination=cls.group_chat,
                                                          author=cls.user)

    def test_non_existing_chat(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_group_chat_messages_before_id_given', args=[100, 1000])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.user2)
        url = reverse('chat:get_group_chat_messages_before_id_given', args=[self.group_chat.pk, 1000])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_before_id_given_incorrect(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_group_chat_messages_before_id_given', args=[self.group_chat.pk, 'eee'])
        response = self.client.get(url, {'cursor': 'eee'})
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid cursor')

    def test_before_id_given_correct(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_group_chat_messages', args=[self.group_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        first_id = response_json['first_id']
        rendered_template = response_json['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['has_previous_page'], True)
        self.assertTrue(first_id is not None)
        self.assertIn(self.group_msgs[29].text, rendered_template)
        self.assertIn(self.group_msgs[20].text, rendered_template)
        self.assertNotIn(self.group_msgs[19].text, rendered_template)

        url2 = reverse('chat:get_group_chat_messages_before_id_given', args=[self.group_chat.pk, first_id])
        response2 = self.client.get(url2)
        response_json2 = response2.json()
        first_id2 = response_json2['first_id']
        rendered_template2 = response_json2['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response_json2['status'], 'ok')
        self.assertEqual(response_json2['has_previous_page'], True)
        self.assertTrue(first_id2 is not None)
        self.assertIn(self.group_msgs[19].text, rendered_template2)
        self.assertIn(self.group_msgs[11].text, rendered_template2)
        self.assertNotIn(self.group_msgs[9].text, rendered_template2)

        url3 = reverse('chat:get_group_chat_messages_before_id_given', args=[self.group_chat.pk, first_id2])
        response3 = self.client.get(url3)
        response_json3 = response3.json()
        rendered_template3 = response_json3['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response_json3['status'], 'ok')
        self.assertEqual(response_json3['has_previous_page'], False)
        self.assertIn(self.group_msgs[9].text, rendered_template3)
        self.assertIn(self.group_msgs[0].text, rendered_template3)


class TestGetPrivateChatMessagesBeforeIdGiven(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = UserFactory()
        cls.user2 = UserFactory()
        cls.user3 = UserFactory()
        cls.user.profile.friends.add(cls.user2.profile)
        cls.private_chat = PrivateChat.objects.filter(participants=cls.user).filter(participants=cls.user2).first()
        cls.private_msgs = PrivateMessageFactory.create_batch(30, destination=cls.private_chat, author=cls.user)

    def test_non_existing_chat(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_private_chat_messages_before_id_given', args=[100, 1000])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_participant(self):
        self.client.force_login(self.user3)
        url = reverse('chat:get_private_chat_messages_before_id_given', args=[self.private_chat.pk, 1000])
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'You are not a participant of this chat')

    def test_before_id_given_incorrect(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_private_chat_messages_before_id_given', args=[self.private_chat.pk, 'eee'])
        response = self.client.get(url, {'cursor': 'eee'})
        response_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Invalid cursor')

    def test_before_id_given_correct(self):
        self.client.force_login(self.user)
        url = reverse('chat:get_private_chat_messages', args=[self.private_chat.pk])
        response = self.client.get(url)
        response_json = response.json()
        first_id = response_json['first_id']
        rendered_template = response_json['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['status'], 'ok')
        self.assertEqual(response_json['has_previous_page'], True)
        self.assertTrue(first_id is not None)
        self.assertIn(self.private_msgs[29].text, rendered_template)
        self.assertIn(self.private_msgs[20].text, rendered_template)
        self.assertNotIn(self.private_msgs[19].text, rendered_template)

        url2 = reverse('chat:get_private_chat_messages_before_id_given', args=[self.private_chat.pk, first_id])
        response2 = self.client.get(url2)
        response_json2 = response2.json()
        first_id2 = response_json2['first_id']
        rendered_template2 = response_json2['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response_json2['status'], 'ok')
        self.assertEqual(response_json2['has_previous_page'], True)
        self.assertTrue(first_id2 is not None)
        self.assertIn(self.private_msgs[19].text, rendered_template2)
        self.assertIn(self.private_msgs[11].text, rendered_template2)
        self.assertNotIn(self.private_msgs[9].text, rendered_template2)

        url3 = reverse('chat:get_private_chat_messages_before_id_given', args=[self.private_chat.pk, first_id2])
        response3 = self.client.get(url3)
        response_json3 = response3.json()
        rendered_template3 = response_json3['rendered_template'].replace('<br>', '\n')
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(response_json3['status'], 'ok')
        self.assertEqual(response_json3['has_previous_page'], False)
        self.assertIn(self.private_msgs[9].text, rendered_template3)
        self.assertIn(self.private_msgs[0].text, rendered_template3)
