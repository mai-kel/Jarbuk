import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import PrivateChat, GroupChat, PrivateMessage, GroupMessage
from django.utils.html import escape
from django.template import defaultfilters

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
        message = text_data_json.get("message")
        chat_pk = text_data_json.get("chat_pk")
        chat_type = text_data_json.get("chat_type")
        group_name = f"{chat_type}_{chat_pk}"
        if message.strip() == "":
            self.send(text_data=json.dumps({"status": "error",
                                            "message": "Message cannot be empty"}))
            return

        if chat_type == "private_chat":
            message_type = "private_message"
            try:
                chat = self.user.private_chats.get(pk=chat_pk)
            except:
                self.send(text_data=json.dumps({"status": "error",
                                                "message": "Chat does not exist"}))
                return
            new_message = PrivateMessage.objects.create(destination=chat, author=self.user, text=message)
            message_pk = new_message.pk

        elif chat_type == "group_chat":
            message_type = "group_message"
            try:
                chat = self.user.group_chats.get(pk=chat_pk)
            except:
                self.send(text_data=json.dumps({"status": "error",
                                                "message": "Chat does not exist"}))
                return
            new_message = GroupMessage.objects.create(destination=chat, author=self.user, text=message)
            message_pk = new_message.pk
        else:
            self.send(text_data=json.dumps({"status": "error",
                                            "message": "Invalid chat type"}))
            return

        author_name = self.user.first_name + " " + self.user.last_name
        self.send(text_data=json.dumps({"status": "ok",
                                        'message': "Message sent"}))
        async_to_sync(self.channel_layer.group_send)(
            group_name, {"type": "chat.message",
                                   "message": escape(defaultfilters.truncatechars(message, 30)),
                                   "author_name": author_name,
                                   "chat_pk": chat_pk,
                                   "chat_type": chat_type,
                                   "author_pk": self.user.pk,
                                   "message_type": message_type,
                                   "message_pk": message_pk}
        )


    def chat_message(self, event):
        self.send(text_data=json.dumps(event))