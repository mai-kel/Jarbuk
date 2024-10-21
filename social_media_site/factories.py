import factory
from django.contrib.auth.models import User
from factory.faker import Faker
from .models import Profile


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory("social_media_site.factories.UserFactory", profile=None)
    date_of_birth = Faker('date_of_birth')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'my_username_{n}')
    email = factory.Sequence(lambda n: f'my_email_{n}@gmail.com')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = "MyPassword123"
    is_active = True
    is_staff = False
    is_superuser = False
    profile = factory.RelatedFactory(ProfileFactory,
                                     factory_related_name='user')

