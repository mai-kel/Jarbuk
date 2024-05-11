from django.contrib import admin
from .models import Comment, Profile, Post
from django.contrib.auth.models import User


class CommentInline(admin.TabularInline):
    model=Comment

class PostLikesInline(admin.TabularInline):
    model = Post.likes.through

class CommentLikesInline(admin.TabularInline):
    model = Comment.likes.through

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'creation_date', 'text']
    inlines = [CommentInline, PostLikesInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'creation_date', 'text']
    inlines = [CommentLikesInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'profile_photo', 'cover_photo']


