from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post, Profile
from django.db.models import Q
from .forms import UserForm
# Create your views here.

@login_required
def posts_feed(request):
    # posts = Post.objects.filter(author__in=User.objects.filter(profile__in=request.user.profile.friends))
    # posts = Post.objects.filter(author__in=User.objects.all())
    friends = User.objects.filter(profile__in=request.user.profile.friends.all())
    posts = Post.objects.filter(Q(author__in=friends) | Q(author=request.user))
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
            if first_name and last_name:
                users_found = User.objects.filter(first_name=first_name, last_name=last_name)
            elif first_name:
                users_found = User.objects.filter(first_name=first_name)
            elif last_name:
                users_found = User.objects.filter(last_name=last_name)
    else:
        user_form = UserForm()

    return render(request, "site/user/users_list.html",
                   {"form": user_form,
                    "users_found": users_found})


