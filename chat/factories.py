import factory
from django.contrib.auth.models import User
from factory.faker import Faker
from . import models



class GroupChatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GroupChat

    name = Faker('name')
    owner = factory.SubFactory("social_media_site.factories.UserFactory")

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for participant in extracted:
                self.participants.add(participant)


    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for admin in extracted:
                self.admins.add(admin)


class PrivateChatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PrivateChat

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for participant in extracted:
                self.participants.add(participant)


class GroupMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GroupMessage

    text = Faker('text')
    destination = factory.SubFactory(GroupChatFactory)
    author = factory.SubFactory("social_media_site.factories.UserFactory")



class PrivateMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PrivateMessage

    text = Faker('text')
    destination = factory.SubFactory(PrivateChatFactory)
    author = factory.SubFactory("social_media_site.factories.UserFactory")
