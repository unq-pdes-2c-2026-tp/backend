import factory

from users.constants import UserType
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    user_type = UserType.END_USER
    email = factory.Faker("email")

    class Meta:
        model = User
