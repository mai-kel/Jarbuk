from django.contrib import admin
from .models import GroupChat, PrivateChat, GroupMessage, PrivateMessage

admin.site.register(PrivateChat)
admin.site.register(GroupChat)
admin.site.register(GroupMessage)
admin.site.register(PrivateMessage)