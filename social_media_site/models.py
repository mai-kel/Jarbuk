from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True,
                                     blank=True)
    profile_photo = models.ImageField(upload_to='users/profile_pictures/%Y/%m/%d/',
                                      blank=True)
    profile_photo = models.ImageField(upload_to='users/profile_photos/%Y/%m/%d/',
                                      blank=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos/%Y/%m/%d/',
                                    blank=True)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='posts')
    creation_date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    creation_date = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    from_who = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE)
    class Meta:
        abstract = True

class PostLike(Like):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE)

class CommentLike(Like):
    comment = models.ForeignKey(Comment,
                                on_delete=models.CASCADE)
