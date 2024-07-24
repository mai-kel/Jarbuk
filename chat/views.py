from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import GroupChat, PrivateChat, GroupMessage, PrivateMessage
from django.db.models import Q
from itertools import chain


@login_required
def list_chats(request):
    group_chats = request.user.group_chats.all()
    private_chats = request.user.private_chats.all()
    all_chats = list(chain(group_chats, private_chats))

    # sort chats by last message date, if there is no message, put the chat at the end
    all_chats.sort(key=lambda x: (x.get_last_message_date() is not None, x.get_last_message_date()), reverse=True)
    all_chats_last_messages = [chat.get_last_message() for chat in all_chats]
    all_chats_with_last_message = list(zip(all_chats, all_chats_last_messages))

    return render(request, 'chat/list_chats.html',
                  {'chats_with_messages': all_chats_with_last_message})


@login_required
def get_rendered_chat(request, chat_id, chat_type):
    if chat_type == "private_chat":
        chat = PrivateChat.objects.get(id=chat_id)
        messages = chat.private_messages.all()
    else:
        chat = GroupChat.objects.get(id=chat_id)
        messages = chat.group_messages.all()

    return render(request, 'chat/chat_detail.html',
                    {'chat': chat,
                     'messages': messages})


@login_required
def get_rendered_message(request, message_id, message_type):
    if message_type == "private_message":
        message = PrivateMessage.objects.get(id=message_id)
    else:
        message = GroupMessage.objects.get(id=message_id)

    return render(request, 'chat/message.html',
                  {'message': message})




