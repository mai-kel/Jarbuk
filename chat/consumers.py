import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import PrivateChat, GroupChat, PrivateMessage, GroupMessage
from django.utils.html import escape

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            self.close()

        private_chats = self.user.private_chats.all()
        group_chats = self.user.group_chats.all()

        self.groups = []
        for chat in private_chats:
            self.groups.append(f"private_chat_{chat.pk}")
        for chat in group_chats:
            self.groups.append(f"group_chat_{chat.pk}")

        for group in self.groups:
            async_to_sync(self.channel_layer.group_add)(
                group, self.channel_name
            )

        self.accept()

    def disconnect(self, close_code):
        for group in self.groups:
            async_to_sync(self.channel_layer.group_discard)(
                group, self.channel_name
            )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        chat_pk = text_data_json["chat_pk"]
        chat_type = text_data_json["chat_type"]
        group_name = f"{chat_type}_{chat_pk}"

        if chat_type == "private_chat":
            message_type = "private_message"
            chat = self.user.private_chats.get(pk=chat_pk)
            new_message = PrivateMessage.objects.create(destination=chat, author=self.user, text=message)
            message_pk = new_message.pk
        elif chat_type == "group_chat":
            chat = self.user.group_chats.get(pk=chat_pk)
            message_type = "group_message"
            new_message = GroupMessage.objects.create(destination=chat, author=self.user, text=message)
            message_pk = new_message.pk

        async_to_sync(self.channel_layer.group_send)(
            group_name, {"type": "chat.message",
                                   "message": escape(message),
                                   "chat_pk": chat_pk,
                                   "chat_type": chat_type,
                                   "author_pk": self.user.pk,
                                   "message_type": message_type,
                                   "message_pk": message_pk}
        )


    def chat_message(self, event):
        self.send(text_data=json.dumps(event))