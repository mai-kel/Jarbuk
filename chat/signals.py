from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from social_media_site.models import Profile
from .models import PrivateChat

@receiver(m2m_changed, sender=Profile.friends.through)
def friend_added(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for profile_pk in pk_set:
            user = Profile.objects.get(pk=profile_pk).user
            if not PrivateChat.objects.filter(participants=instance.user).filter(participants=user).exists():
                private_chat = PrivateChat.objects.create()
                private_chat.participants.add(instance.user, user)
                private_chat.save()

