from django.contrib import admin
from .models import Comment, Profile, PostLike, CommentLike, Post


class CommentInline(admin.TabularInline):
    model=Comment

class CommentLiketInline(admin.TabularInline):
    model=CommentLike

class PostLikeInline(admin.TabularInline):
    model=PostLike

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'creation_date', 'text']
    inlines=[CommentInline, PostLikeInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'creation_date', 'text']
    inlines = [CommentLiketInline]

@admin.register(PostLike)
class PostLike(admin.ModelAdmin):
    list_display = ['creation_date', 'from_who', 'post']

@admin.register(CommentLike)
class PostLike(admin.ModelAdmin):
    list_display = ['creation_date', 'from_who', 'comment']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'profile_photo', 'cover_photo']