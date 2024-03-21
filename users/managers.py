from django.contrib.auth.models import UserManager


class UserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().select_related("profile")

    def get_active(self):
        return self.get_queryset().filter(is_active=True)
