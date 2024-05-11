from django.db import models
from django.conf import settings
from django.template.loader import render_to_string

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True,
                                     blank=True)
    profile_photo = models.ImageField(upload_to='users/profile_photos/%Y/%m/%d/',
                                      blank=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos/%Y/%m/%d/',
                                    blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='posts')
    creation_date = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='users/post_photos/%Y/%m/%d/',
                              blank=True)
    text = models.TextField()
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posts_liked')

    def render(self, request):
        return render_to_string(request=request,
                                template_name='site/general/post_general.html',
                                context={'post': self})


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='comments_liked')

    def render(self, request):
        return render_to_string(request=request,
                                template_name='site/general/comment_general.html',
                                context={'comment': self})


class FriendInvitation(models.Model):
    from_who = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name='invitations_sent')
    to_who = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='invitations_received')
    date = models.DateTimeField(auto_now_add=True)
