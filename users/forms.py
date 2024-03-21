from re import compile

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import User, UserProfile
from users.utils import normalize_email

EMAIL_REGEX = compile(r"[^@]+@[^@]+\.[^@]+")
EMAIL_TEXT_BLOCKED_ACCOUNT = _("Email text blocked account")
EMAIL_SUBJECT_BLOCKED_ACCOUNT = _("Your account is blocked")


class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data["username"]
        self.cleaned_data["username"] = username = (
            normalize_email(username)
            if EMAIL_REGEX.match(username)
            else username
        )
        password = self.cleaned_data["password"]
        user = User.objects.filter(username=username) or User.objects.filter(
            email=username
        )
        if user and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                count = self.request.session.get("load_count", 0) + 1
                self.request.session["load_count"] = count
                if count == settings.MAX_LOGIN_ATTEMPTS:
                    user[0].is_active = False
                    profile = UserProfile.objects.get(user=user[0])
                    profile.last_login_attempt = timezone.now()
                    profile.save()
                    user[0].save()
                    url = reverse_lazy(
                        "users:activate_after_ban",
                        kwargs={"username": user[0].username},
                    )
                    send_mail(
                        EMAIL_SUBJECT_BLOCKED_ACCOUNT,
                        f"{EMAIL_TEXT_BLOCKED_ACCOUNT}\n"
                        f"{settings.ABSOLUTE_URL}:{settings.PORT}{url}",
                        settings.EMAIL_HOST_USER,
                        [user[0].email],
                    )
                    messages.error(
                        self.request,
                        _("Your account has been blocked"),
                    )
                    self.request.session["load_count"] = 0
        super().clean()


class RegistrationForm(UserCreationForm):
    def clean(self):
        self.cleaned_data["email"] = normalize_email(
            self.cleaned_data["email"]
        )
        if User.objects.filter(email=self.cleaned_data["email"]):
            raise ValidationError(_("Email is not unique"))
        super().clean()

    class Meta:
        model = User
        fields = (
            User.username.field.name,
            User.email.field.name,
            "password1",
            "password2",
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            UserProfile.birthday.field.name,
            UserProfile.image.field.name,
            UserProfile.coffee_count.field.name,
        )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = (
            User.username.field.name,
            User.email.field.name,
            User.first_name.field.name,
            User.last_name.field.name,
        )
