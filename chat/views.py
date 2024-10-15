from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import GroupChat, PrivateChat, GroupMessage, PrivateMessage
from django.contrib.auth.models import User
from django.db.models import Q
from itertools import chain
from django.http import JsonResponse
from .forms import GroupChatForm
from django.contrib import messages
from easy_thumbnails.files import get_thumbnailer
from cursor_pagination import CursorPaginator


@require_http_methods(['GET'])
@login_required
def list_chats(request):
    group_chats = request.user.group_chats.all()
    private_chats = request.user.private_chats.all()
    all_chats = list(chain(group_chats, private_chats))

    # sort chats by last message date, if there is no message, put the chat at the end
    all_chats.sort(key=lambda x: (x.get_last_message_date() is not None, x.get_last_message_date()),
                   reverse=True)
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


def determine_users_group_chat_role(user: User, chat: GroupChat|PrivateChat)->str:
    if isinstance(chat, GroupChat):
        if user == chat.owner:
            return 'owner'
        elif user in chat.admins.all():
            return 'admin'
        elif user in chat.participants.all():
            return 'participant'
        else:
            return 'none'
    else:
        if user in chat.participants.all():
            return 'participant'
        else:
            return 'none'


def render_chat_to_string(chat: GroupChat|PrivateChat, request)->str:
    if isinstance(chat, GroupChat):
        qs = chat.group_messages.all()
    else:
        qs = chat.private_messages.all()
    page_size = 10+1
    paginator = CursorPaginator(qs, ordering=('creation_date', 'id'))
    page = paginator.page(last=page_size, before=None)
    messages = [message for message in page]
    if page.has_previous:
        messages = messages[1:]
    first_cursor = paginator.cursor(page[0]) if messages else None
    return render_to_string('chat/chat_detail.html',
                            {'chat': chat,
                             'messages': messages,
                             'user_role': determine_users_group_chat_role(request.user, chat),
                             'has_previous_page': page.has_previous,
                             'first_cursor': first_cursor},
                            request)


def get_rendered_chat(request, chat_pk, model: GroupChat|PrivateChat):
    data = {}
    try:
        chat = model.objects.get(pk=chat_pk)
    except:
        chat = None
    if chat is None:
        data['status'] = 'error'
        data['message'] = 'Chat not found'
        return JsonResponse(data, status=404)
    if request.user not in chat.participants.all():
        data['status'] = 'error'
        data['message'] = 'You are not a participant of this chat'
        return JsonResponse(data, status=403)

    data['status'] = 'ok'
    data['rendered_chat'] = render_chat_to_string(chat, request)

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
    try:
        message = model.objects.get(pk=message_pk)
    except:
        message = None
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


@require_http_methods(['GET', 'POST'])
@login_required
def create_group_chat(request):
    data={}
    if request.method == 'POST':
        form = GroupChatForm(data=request.POST, files=request.FILES, logged_user=request.user)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.owner = request.user
            chat.save()
            form.save_m2m()
            chat.participants.add(request.user)
            chat.save()
            data['status'] = 'ok'
            data['chat_pk'] = chat.pk
            data['rendered_template'] = render_to_string('chat/chat_element.html',
                                                              {'chat': chat,
                                                               'message': chat.get_last_message(),},
                                                               request=request)
            status = 200
        else:
            data['status'] = 'error'
            data['errors'] = form.errors
            status = 400
    else:
        form = GroupChatForm(logged_user=request.user)
        rendered_template = render_to_string('chat/create_group_chat.html',
                                             {'form': form},
                                             request=request)
        data['status'] = 'ok'
        data['rendered_template'] = rendered_template
        status = 200

    return JsonResponse(data, status=status)


@require_http_methods(['GET'])
@login_required
def get_group_chat_info(request, chat_pk):
    response_data = {}
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    if not request.user in chat.participants.all():
        response_data['status'] = 'error'
        response_data['message'] = 'You are not a participant of this chat'
        return JsonResponse(response_data, status=403)
    template_data = {}
    template_data['chat'] = chat
    owner = chat.owner
    admins = chat.admins.all()
    rest_participants = chat.participants.all().exclude(pk=owner.pk).difference(admins)
    template_data['owner'] = owner
    template_data['admins'] = admins
    template_data['rest_participants'] = rest_participants
    rendered_template = render_to_string('chat/group_chat_info.html', template_data,
                                         request=request)
    response_data['status'] = 'ok'
    response_data['rendered_template'] = rendered_template
    return JsonResponse(response_data, status=200)


def delete_user_from_group_chat_as_owner(chat: GroupChat, user_to_delete: User)->tuple[dict, int]:
    data={}
    if user_to_delete == chat.owner:
            data['status'] = 'error'
            data['message'] = 'You have to transfer the ownership to another user before deleting yourself from the chat'
            status_code=403
    elif user_to_delete not in chat.participants.all():
        data['status'] = 'error'
        data['message'] = 'User is not a participant of this chat'
        status_code=403
    else:
        if user_to_delete in chat.admins.all():
            chat.admins.remove(user_to_delete)
        chat.participants.remove(user_to_delete)
        data['status'] = 'ok'
        data['message'] = 'User deleted from the chat'
        status_code=200
    return (data, status_code)


def delete_user_from_group_chat_as_admin(chat: GroupChat, user_to_delete: User)->tuple[dict, int]:
    data={}
    if user_to_delete == chat.owner:
        data['status'] = 'error'
        data['message'] = 'You have no permission to delete the owner from the chat'
        status_code=403
    elif user_to_delete in chat.admins.all():
        data['status'] = 'error'
        data['message'] = 'You have no permission to delete another admin from the chat'
        status_code=403
    elif user_to_delete not in chat.participants.all():
        data['status'] = 'error'
        data['message'] = 'User is not a participant of this chat'
        status_code=403
    else:
        chat.participants.remove(user_to_delete)
        data['status'] = 'ok'
        data['message'] = 'User deleted from the chat'
        status_code=200
    return (data, status_code)


@require_http_methods(['POST'])
@login_required
def remove_user_from_group_chat(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    user_pk = request.POST.get('user_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    user_to_delete = get_object_or_404(User, pk=user_pk)

    if request.user == chat.owner:
        data, status_code = delete_user_from_group_chat_as_owner(chat, user_to_delete)

    elif request.user in chat.admins.all():
        data, status_code = delete_user_from_group_chat_as_admin(chat, user_to_delete)
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to delete users from this chat'
        status_code=403

    return JsonResponse(data, status=status_code)


@require_http_methods(['POST'])
@login_required
def add_user_to_group_chat(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    user_pk = request.POST.get('user_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    user_to_add = get_object_or_404(User, pk=user_pk)

    if request.user == chat.owner or request.user in chat.admins.all():
        if user_to_add in chat.participants.all():
            data['status'] = 'error'
            data['message'] = 'User is already a participant of this chat'
            status_code=403
        elif user_to_add.profile not in request.user.profile.friends.all():
            data['status'] = 'error'
            data['message'] = 'You can only add friends to the chat'
            status_code=403
        else:
            chat.participants.add(user_to_add)
            data['status'] = 'ok'
            data['message'] = 'User added to the chat'
            status_code=200
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to add users to this chat'
        status_code=403

    return JsonResponse(data, status=status_code)


@require_http_methods(['POST'])
@login_required
def transfer_ownership(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    user_pk = request.POST.get('user_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    user_to_transfer = get_object_or_404(User, pk=user_pk)

    if request.user == chat.owner:
        if user_to_transfer not in chat.participants.all():
            data['status'] = 'error'
            data['message'] = 'User is not a participant of this chat'
            status_code=403
        elif user_to_transfer == chat.owner:
            data['status'] = 'error'
            data['message'] = 'You is already the owner of this chat'
            status_code=403
        else:
            chat.owner = user_to_transfer
            chat.save()
            chat.admins.add(request.user)
            chat.admins.remove(user_to_transfer)
            data['status'] = 'ok'
            data['message'] = 'Ownership transferred successfully'
            status_code=200
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to transfer the ownership of this chat'
        status_code=403

    return JsonResponse(data, status=status_code)


@require_http_methods(['POST'])
@login_required
def leave_group_chat(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)

    if request.user == chat.owner:
        data['status'] = 'error'
        data['message'] = 'You have to transfer the ownership to another user before leaving the chat'
        status_code=403
    elif request.user not in chat.participants.all():
        data['status'] = 'error'
        data['message'] = 'You are not a participant of this chat'
        status_code=403
    else:
        chat.participants.remove(request.user)
        chat.admins.remove(request.user)
        data['status'] = 'ok'
        data['message'] = 'You left the chat'
        status_code=200

    return JsonResponse(data, status=status_code)


@require_http_methods(['POST'])
@login_required
def delete_group_chat(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)

    if request.user == chat.owner:
        chat.delete()
        data['status'] = 'ok'
        data['message'] = 'Chat deleted successfully'
        status_code=200
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to delete this chat'
        status_code=403

    return JsonResponse(data, status=status_code)


@require_http_methods(['POST'])
@login_required
def add_admin_to_group_chat(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    user_pk = request.POST.get('user_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    user_to_add = get_object_or_404(User, pk=user_pk)

    if request.user == chat.owner:
        if user_to_add in chat.admins.all():
            data['status'] = 'error'
            data['message'] = 'User is already an admin of this chat'
            status_code=403
        elif user_to_add == chat.owner:
            data['status'] = 'error'
            data['message'] = 'You cannot be admin and owner at the same time'
            status_code=403
        elif user_to_add not in chat.participants.all():
            data['status'] = 'error'
            data['message'] = 'User is not a participant of this chat'
            status_code=403
        else:
            chat.admins.add(user_to_add)
            data['status'] = 'ok'
            data['message'] = 'User added to the admins'
            status_code=200
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to add admins to this chat'
        status_code=403

    return JsonResponse(data, status=status_code)


@require_http_methods(['POST'])
@login_required
def remove_from_admins(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    user_pk = request.POST.get('user_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    user_to_delete = get_object_or_404(User, pk=user_pk)

    if request.user == chat.owner:
        if user_to_delete in chat.admins.all():
            chat.admins.remove(user_to_delete)
            data['status'] = 'ok'
            data['message'] = 'User removed from admins'
            status_code=200
        else:
            data['status'] = 'error'
            data['message'] = 'User is not an admin of this chat'
            status_code=403
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to delete admins from this chat'
        status_code=403

    return JsonResponse(data, status=status_code)


@require_http_methods(['GET'])
@login_required
def get_add_users_page(request, chat_pk):
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    data = {}
    if not(request.user == chat.owner or request.user in chat.admins.all()):
        data['status'] = 'error'
        data['message'] = 'You have no permission to add users to this chat'
        return JsonResponse(data, status=403)
    else:
        addable_users = User.objects.filter(
            profile__in=request.user.profile.friends.all()).difference(chat.participants.all())
        data['status'] = 'ok'
        data['rendered_template'] = render_to_string('chat/add_users_to_chat.html',
                                                     {'addable_users': addable_users, 'chat': chat})
        return JsonResponse(data, status=200)


@require_http_methods(['GET'])
@login_required
def get_manage_group_page(request, chat_pk):
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    response_data = {}
    role = determine_users_group_chat_role(request.user, chat)
    if role != 'owner' and role != 'admin':
        response_data['status'] = 'error'
        response_data['message'] = 'You have no permission to manage this chat'
        return JsonResponse(response_data, status=403)
    else:
        owner = chat.owner
        admins = chat.admins.all()
        rest_participants = chat.participants.all().exclude(pk=owner.pk).difference(admins)
        template_data = {}
        template_data['role'] = role
        template_data['rest_participants'] = rest_participants
        template_data['chat'] = chat

        rendered_template= render_to_string('chat/manage_group_chat.html', template_data)
        response_data['status'] = 'ok'
        response_data['rendered_template'] = rendered_template
        return JsonResponse(response_data, status=200)


@require_http_methods(['POST'])
@login_required
def change_chat_image(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    image = request.FILES['image']
    if request.user == chat.owner or request.user in chat.admins.all():
        chat.group_image = image
        chat.save()
        image_url = get_thumbnailer(chat.group_image)['chat_image_info'].url
        data['image_url'] = image_url
        data['status'] = 'ok'
        data['message'] = 'Image changed successfully'
        return JsonResponse(data, status=200)
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to change the image of this chat'
        return JsonResponse(data, status=403)


@require_http_methods(['POST'])
@login_required
def change_chat_name(request):
    data = {}
    chat_pk = request.POST.get('chat_pk')
    chat = get_object_or_404(GroupChat, pk=chat_pk)
    new_name = request.POST.get('new_name')
    if request.user == chat.owner or request.user in chat.admins.all():
        chat.name = new_name
        chat.save()
        data['status'] = 'ok'
        data['message'] = 'Name changed successfully'
        return JsonResponse(data, status=200)
    else:
        data['status'] = 'error'
        data['message'] = 'You have no permission to change the name of this chat'
        return JsonResponse(data, status=403)


def get_chat_messages(request, chat_pk, model, before_cursor=None):
    chat = get_object_or_404(model, pk=chat_pk)
    if request.user not in chat.participants.all():
        return JsonResponse({'status': 'error', 'message': 'You are not a participant of this chat'}, status=403)

    qs = chat.group_messages.all() if isinstance(chat, GroupChat) else chat.private_messages.all()
    page_size = 10+1
    paginator = CursorPaginator(qs, ordering=('creation_date', 'id'))
    page = paginator.page(last=page_size, before=before_cursor)
    messages = [message for message in page]
    if page.has_previous:
        messages = messages[1:]
    first_cursor = paginator.cursor(page[0]) if messages else None
    rendered_messages = render_to_string('chat/rendered_messages.html',
                                         {'messages': messages},
                                         request=request)
    data = {
        'status': 'ok',
        'rendered_template': rendered_messages,
        'has_previous_page': page.has_previous,
        'first_cursor': first_cursor,
    }
    return JsonResponse(data, status=200)


@require_http_methods(['GET'])
@login_required
def get_paginated_private_chat_messages(request, chat_pk, before_cursor=None):
    return get_chat_messages(request, chat_pk, PrivateChat, before_cursor)


@require_http_methods(['GET'])
@login_required
def get_paginated_group_chat_messages(request, chat_pk, before_cursor=None):
    return get_chat_messages(request, chat_pk, GroupChat, before_cursor)
