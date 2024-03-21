from re import compile

from django.contrib.auth.backends import ModelBackend

from users.models import User

EMAIL_REGEX = compile(r"[^@]+@[^@]+\.[^@]+")


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if EMAIL_REGEX.match(username):
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
