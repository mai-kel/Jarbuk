from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post, Profile, FriendInvitation, Comment
from django.db.models import Q
from .forms import UserForm, RegistrationForm, PostCreateForm, CommentCreateForm
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator

# Create your views here.

@require_GET
@login_required
def posts_feed(request, page=1):
    friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    # retrieving posts created by friends of user in request or created by user himself
    posts = Post.objects.filter(Q(author__in=friends) | Q(author=request.user)).order_by('-creation_date')
    paginator = Paginator(posts, 15)

    page_obj = paginator.get_page(page)

    post_form = PostCreateForm()

    return render(request,
                  'site/posts_feed.html',
                  {'page_obj': page_obj,
                   'post_form': post_form})

@login_required
@require_POST
@ensure_csrf_cookie
def create_post(request):
    post_text = request.POST.get('text')
    post_photo = request.FILES.get('post_photo')
    response_data = {}

    post = Post(text=post_text, author=request.user)
    if post_photo:
        post.photo = post_photo

    post.save()

    response_data['status'] = 'ok'
    response_data['post'] = post.render(request)

    return JsonResponse(response_data)



@login_required
def search_for_users(request):
    users_found = None
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            first_name = user_form.cleaned_data["first_name"]
            last_name = user_form.cleaned_data["last_name"]
            form_sent_correctly = True

            if first_name and last_name:
                users_found = User.objects.filter(first_name=first_name, last_name=last_name)
            elif first_name:
                users_found = User.objects.filter(first_name=first_name)
            elif last_name:
                users_found = User.objects.filter(last_name=last_name)

            users_found = users_found.order_by('first_name', 'last_name')

        else:
            form_sent_correctly = False
    else:
        user_form = UserForm()
        form_sent_correctly = False

    return render(request, "site/user/users_list.html",
                   {"form": user_form,
                    "users_found": users_found,
                    "form_sent_correctly": form_sent_correctly})

@login_required
def user_detail(request, id):
    user = get_object_or_404(User, pk=id)
    friendship_status = determine_friendship_status(request, id)
    if user.profile in request.user.profile.friends.all() or id==request.user.pk:
        user_posts = user.posts.all()[:10]
    else:
        user_posts = None

    return render(request, "site/user/user_detail.html",
                  {"user_profile": user,
                   "user_posts": user_posts,
                   "friendship_status": friendship_status})


def determine_friendship_status(request, user_id):
    if request.user.pk == user_id:
        return "your_profile"
    user_recipient = get_object_or_404(User, pk=user_id)
    logged_user_friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    logged_user_sent_invitations = request.user.invitations_sent.all()
    recipient_user_sent_invitations = user_recipient.invitations_sent.all()

    # users are friends already- delete from friends list
    if user_recipient in logged_user_friends:
        return "friends"
    # logged user sent invitation to recipient user- withdraw invitation
    elif logged_user_sent_invitations.filter(to_who=user_recipient).exists():
        return "you_sent"
    # recipient user sent invitation to logged user
    elif recipient_user_sent_invitations.filter(to_who=request.user):
        return "sent_to_you"
    # there is no invitations nor friendship between users- send invitation
    else:
        return "none"


@login_required
@require_POST
def post_like(request):
    id = request.POST.get('id')
    try:
        post = Post.objects.get(pk=id)
    except:
        return JsonResponse({'status': 'error'})

    if post.author.profile not in request.user.profile.friends.all() and post.author != request.user:
        return JsonResponse({'status': 'error'})

    response_data = {}
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        response_data['action'] = 'unliked'
    else:
        post.likes.add(request.user)
        response_data['action'] = 'liked'
    response_data['status'] = 'ok'

    return JsonResponse(response_data)


@login_required
@require_POST
def comment_like(request):
    id = request.POST.get('id')
    try:
        comment = Comment.objects.get(pk=id)
    except:
        return JsonResponse({'status': 'error'})

    if comment.post.author.profile not in request.user.profile.friends.all() and comment.post.author != request.user:
        return JsonResponse({'status': 'error'})

    response_data = {}
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        response_data['action'] = 'unliked'
    else:
        comment.likes.add(request.user)
        response_data['action'] = 'liked'
    response_data['status'] = 'ok'

    return JsonResponse(response_data)


@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, pk=id)
    comment_form = CommentCreateForm()
    comments = post.comments.all().order_by('-creation_date')

    return render(request, "site/post/post_detail.html",
                  {"post": post,
                   "comments": comments,
                   "form": comment_form})


@login_required
@require_POST
def create_comment(request, id):
    post = get_object_or_404(Post, pk=id)
    if  request.user.profile not in post.author.profile.friends.all() and request.user != post.author:
        return JsonResponse({'status': 'error'})

    comment_text = request.POST.get('text')
    new_comment = Comment(text=comment_text, post=post, author=request.user)
    new_comment.save()

    response_data = {}
    response_data['status'] = 'ok'
    response_data['comment'] = new_comment.render(request)

    return JsonResponse(response_data)


def register(request):
    if request.user.is_authenticated:
        return redirect('site:posts_feed')

    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST, request.FILES)
        if registration_form.is_valid():
            cd = registration_form.cleaned_data
            username = cd['username']
            first_name = cd['first_name']
            last_name = cd['last_name']
            email = cd['email']
            password = cd['password']
            user = User.objects.create_user(username=username,
                                            first_name=first_name,
                                            last_name=last_name,
                                            email=email,
                                            password=password)
            profile = Profile.objects.create(user=user)

            birthdate = cd['birthdate']
            profile_photo = cd['profile_photo']
            cover_photo = cd['cover_photo']

            if birthdate:
                profile.date_of_birth = birthdate
            if profile_photo:
                profile.profile_photo = profile_photo
            if cover_photo:
                profile.cover_photo = cover_photo

            profile.save()

            return render(request,
                          'registration/registration_complete.html',
                          {})
    else:
        registration_form = RegistrationForm()

    return render(request,
                  'registration/registration.html',
                  {'form': registration_form})



@require_POST
@login_required
def profile_send_invitation(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    logged_user_friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    logged_user_sent_invitations = request.user.invitations_sent.all()
    recipient_user_sent_invitations = user_recipient.invitations_sent.all()

    # logged user tries to invite himself
    if request.user.pk == id:
       # TODO implement appropriate message
       pass
    # users are friends already
    elif user_recipient in logged_user_friends:
        # TODO implement appropriate message
        pass
    # logged user had already sent invitation to recipient user
    elif logged_user_sent_invitations.filter(to_who=user_recipient).exists():
        # TODO implement appropriate message
        pass
    # recipient user had already sent invitation to logged user
    elif recipient_user_sent_invitations.filter(to_who=request.user):
        # TODO implement appropriate message
        pass
    # there is no invitations nor friendship between users- send invitation
    else:
        FriendInvitation.objects.create(from_who=request.user, to_who=user_recipient)

    return redirect('site:user_detail', id=id)


@require_POST
@login_required
def profile_withdraw_invitation(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    logged_user_sent_invitations = request.user.invitations_sent.all()

    # recipient user had already sent invitation to logged user
    if logged_user_sent_invitations.filter(to_who=user_recipient).exists():
        logged_user_sent_invitations.filter(to_who=user_recipient).delete()
    # there is no invitation to withdraw
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:user_detail', id=id)


@require_POST
@login_required
def profile_accept_invitation(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    recipient_user_sent_invitations = user_recipient.invitations_sent.all()

    # recipient user had already sent invitation to logged user
    if recipient_user_sent_invitations.filter(to_who=request.user).exists():
        recipient_user_sent_invitations.filter(to_who=request.user).delete()
        request.user.profile.friends.add(user_recipient.profile)
    # there is no invitation to accept
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:user_detail', id=id)


@require_POST
@login_required
def profile_decline_invitation(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    recipient_user_sent_invitations = user_recipient.invitations_sent.all()

    # recipient user had already sent invitation to logged user
    if recipient_user_sent_invitations.filter(to_who=request.user).exists():
        recipient_user_sent_invitations.filter(to_who=request.user).delete()
    # there is no invitation to accept
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:user_detail', id=id)


@require_POST
@login_required
def profile_delete_friend(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    logged_user_friends = User.objects.filter(profile__in=request.user.profile.friends.all())

    # users are friends already
    if user_recipient in logged_user_friends:
        request.user.profile.friends.remove(user_recipient.profile)
    # users are no longer friends
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:user_detail', id=id)


@require_POST
@login_required
def delete_friend_friendslist(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    logged_user_friends = User.objects.filter(profile__in=request.user.profile.friends.all())

    # users are friends already
    if user_recipient in logged_user_friends:
        request.user.profile.friends.remove(user_recipient.profile)
    # users are no longer friends
    else:
        # TODO implement appropriate message
        pass
    return redirect('site:friends_list')


@login_required
def friends_list(request):
    friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    return render(request, 'site/friends/friends_list.html',
                  {'friends': friends})


@login_required
def invitations_sent_list(request):
    logged_user_sent_invitations = request.user.invitations_sent.all()
    return render(request, 'site/friends/invitations_sent.html',
                  {'invitations': logged_user_sent_invitations})


@require_POST
@login_required
def invitations_sent_withdraw(request, id):
    user_recipient = get_object_or_404(User, pk=id)
    logged_user_sent_invitations = request.user.invitations_sent.all()

    # recipient user had already sent invitation to logged user
    if logged_user_sent_invitations.filter(to_who=user_recipient).exists():
        logged_user_sent_invitations.filter(to_who=user_recipient).delete()
    # there is no invitation to withdraw
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:invitations_sent')


@login_required
def invitations_received_list(request):
    invitations_received = FriendInvitation.objects.filter(to_who=request.user)
    return render(request, 'site/friends/invitations_received.html',
                  {'invitations': invitations_received})


@require_POST
@login_required
def invitations_received_accept(request, id):
    sender = get_object_or_404(User, pk=id)
    sender_invitations = sender.invitations_sent.all()

    # recipient user had already sent invitation to logged user
    if sender_invitations.filter(to_who=request.user).exists():
        request.user.profile.friends.add(sender.profile)
        sender_invitations.filter(to_who=request.user).delete()
    # there is no invitation to accept
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:invitations_received')


@require_POST
@login_required
def invitations_received_decline(request, id):
    sender = get_object_or_404(User, pk=id)
    sender_invitations = sender.invitations_sent.all()

    # recipient user had already sent invitation to logged user
    if sender_invitations.filter(to_who=request.user).exists():
        sender_invitations.filter(to_who=request.user).delete()
    # there is no invitation to accept
    else:
        # TODO implement appropriate message
        pass

    return redirect('site:invitations_received')
