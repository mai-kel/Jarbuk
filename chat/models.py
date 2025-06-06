from django.db import models
from django.conf import settings
from django.template.loader import render_to_string


class GroupChat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_chats')
    name = models.CharField(max_length=50)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admin_group_chats', blank=True)
    group_image = models.ImageField(upload_to='chat/images/%Y/%m/%d/', blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_group_chats')

    def get_last_message(self):
        return self.group_messages.last()

    def get_last_message_date(self):
        last_message = self.get_last_message()
        if last_message is not None:
            return last_message.creation_date
        return None

    # def render(self, request):
    #     return render_to_string('chat/chat_detail.html',
    #                             {'chat': self,
    #                              'messages': self.group_messages.all().order_by('creation_date')},
    #                             request)


class PrivateChat(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='private_chats')

    def get_last_message(self):
        return self.private_messages.last()

    def get_last_message_date(self):
        last_message = self.get_last_message()
        if last_message is not None:
            return last_message.creation_date
        return None

    # def render(self, request):
    #     return render_to_string('chat/chat_detail.html',
    #                             {'chat': self,
    #                              'messages': self.private_messages.all().order_by('creation_date')},
    #                             request)



class Message(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    image = models.ImageField(upload_to='chat/images/%Y/%m/%d/', blank=True)

    class Meta:
        abstract = True

    def render(self, request):
        return render_to_string('chat/message.html',
                                {'message': self},
                                request)


class GroupMessage(Message):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_messages_sent')
    destination = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name='group_messages')


class PrivateMessage(Message):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='private_messages_sent')
    destination = models.ForeignKey(PrivateChat, on_delete=models.CASCADE, related_name='private_messages')



