from django import template
from ..models import GroupChat, PrivateChat, GroupMessage, PrivateMessage


register = template.Library()

@register.simple_tag
def get_chat_name(chat, user):
    if isinstance(chat, GroupChat):
        return chat.name
    else:
        participants = chat.participants.all()
        other = participants.exclude(pk=user.pk).first()
        return other.first_name + ' ' + other.last_name