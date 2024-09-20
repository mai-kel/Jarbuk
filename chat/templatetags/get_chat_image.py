from django import template
from ..models import GroupChat, PrivateChat
from easy_thumbnails.files import get_thumbnailer
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def get_chat_image(chat: GroupChat|PrivateChat, user):
    if isinstance(chat, GroupChat):
        if chat.group_image:
            return get_thumbnailer(chat.group_image)['chat_image'].url
        else:
            return static('default_img/group_chat_def.png')
    elif isinstance(chat, PrivateChat):
        participants = chat.participants.all()
        other = participants.exclude(pk=user.pk).first()
        if other.profile.profile_photo:
            return get_thumbnailer(other.profile.profile_photo)['chat_image'].url
        else:
            return static('default_img/profile_def.png')
    else:
        return None