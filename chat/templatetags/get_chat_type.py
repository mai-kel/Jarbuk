from django import template
from ..models import GroupChat, PrivateChat, GroupMessage, PrivateMessage


register = template.Library()

@register.simple_tag
def get_chat_type(chat):
    return "group_chat" if isinstance(chat, GroupChat) else "private_chat"
