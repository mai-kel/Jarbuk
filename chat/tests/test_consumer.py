from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from chat.consumers import ChatConsumer
from social_media_site.factories import UserFactory
from chat.factories import GroupChatFactory

class TestChatConsumer(TransactionTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.group_chat = GroupChatFactory(owner=self.user, participants=[self.user, self.user2])
        self.group_msg_json = {
            "message": "Hello Consumer",
            "chat_pk": self.group_chat.pk,
            "chat_type": "group_chat"
        }
        self.empty_group_msg_json = {
            "message": "",
            "chat_pk": self.group_chat.pk,
            "chat_type": "group_chat"
        }
        self.invalid_chat_msg_json = {
            "message": "Hello Consumer",
            "chat_pk": 100,
            "chat_type": "group_chat"
        }


    async def test_consumer_receive_empty_message(self):
        communicator =  WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat")
        communicator.scope['user'] = self.user
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.send_json_to(self.empty_group_msg_json)
        response = await communicator.receive_json_from()
        self.assertEqual(response.get("status"), "error")
        self.assertEqual(response.get("message"), "Message cannot be empty")
        await communicator.disconnect()

    async def test_consumer_receive_invalid_chat(self):
        communicator =  WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat")
        communicator.scope['user'] = self.user
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.send_json_to(self.invalid_chat_msg_json)
        response = await communicator.receive_json_from()
        self.assertEqual(response.get("status"), "error")
        self.assertEqual(response.get("message"), "Chat does not exist")
        await communicator.disconnect()

    async def test_consumer_receive_message(self):
        communicator =  WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat")
        communicator.scope['user'] = self.user
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.send_json_to(self.group_msg_json)
        response = await communicator.receive_json_from()
        self.assertEqual(response.get("status"), "ok")
        self.assertEqual(response.get("message"), "Message sent")
        await communicator.disconnect()
