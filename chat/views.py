from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import GroupChat, PrivateChat, GroupMessage, PrivateMessage
from django.db.models import Q
from itertools import chain
from django.http import JsonResponse


@require_http_methods(['GET'])
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


@require_http_methods(['GET'])
@login_required
def get_rendered_private_chat(request, chat_pk):
    return get_rendered_chat(request, chat_pk, PrivateChat)


@require_http_methods(['GET'])
@login_required
def get_rendered_group_chat(request, chat_pk):
    return get_rendered_chat(request, chat_pk, GroupChat)


def get_rendered_chat(request, chat_pk, model: GroupChat|PrivateChat):
    data = {}
    chat = model.objects.get(pk=chat_pk)
    if chat is None:
        data['status'] = 'error'
        data['message'] = 'Chat not found'
        return JsonResponse(data, status=404)
    if request.user not in chat.participants.all():
        data['status'] = 'error'
        data['message'] = 'You are not a participant of this chat'
        return JsonResponse(data, status=403)

    data['status'] = 'ok'
    data['rendered_chat'] = chat.render(request)
    return JsonResponse(data, status=200)


@require_http_methods(['GET'])
@login_required
def get_rendered_private_message(request, message_pk):
    return get_rendered_message(request, message_pk, PrivateMessage)


@require_http_methods(['GET'])
@login_required
def get_rendered_group_message(request, message_pk):
    return get_rendered_message(request, message_pk, GroupMessage)


def get_rendered_message(request, message_pk, model: GroupMessage|PrivateMessage):
    data = {}
    message = model.objects.get(pk=message_pk)
    if message is None:
        data['status'] = 'error'
        data['message'] = 'Message not found'
        return JsonResponse(data, status=404)
    if request.user not in message.destination.participants.all():
        data['status'] = 'error'
        data['message'] = 'You are not a participant of the chat, where this message was sent'
        return JsonResponse(data, status=403)

    data['status'] = 'ok'
    data['rendered_message'] = message.render(request)
    return JsonResponse(data, status=200)


