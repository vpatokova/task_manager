from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import ImageField

from users.managers import UserManager


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
    )
    birthday = models.DateField(_("Birthday"), null=True, blank=True)
    image = ImageField(
        _("Profile photo"), upload_to="avatars/", null=True, blank=True
    )
    coffee_count = models.PositiveIntegerField(
        _("Question about coffee"), default=0
    )
    last_login_attempt = models.DateTimeField(
        _("Last attempt to log in"), null=True, blank=True
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Users's profile")
        verbose_name_plural = _("Users' profiles")


class User(User):
    objects = UserManager()

    class Meta:
        proxy = True
