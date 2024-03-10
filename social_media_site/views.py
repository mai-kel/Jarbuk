from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post, Profile, PostLike
from django.db.models import Q
from .forms import UserForm
from django.views.decorators.http import require_GET, require_POST
# Create your views here.

@login_required
def posts_feed(request):
    friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    posts = Post.objects.filter(Q(author__in=friends) | Q(author=request.user)).order_by('creation_date')
    return render(request,
                  'site/posts_feed.html',
                  {'posts': posts})

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
    if user.profile in request.user.profile.friends.all():
        user_posts = user.posts
    else:
        user_posts = None

    return render(request, "site/user/user_detail.html",
                  {"user": user,
                   "user_posts" : user_posts})

@login_required
@require_POST
def post_like(request, id):
    post = get_object_or_404(Post, pk=id)
    like = PostLike(from_who=request.user, post=post)
    like.save()

@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, pk=id)

    return render(request, "site/post/post_detail.html",
                  {"post": post})



