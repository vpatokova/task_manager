import django.contrib.auth.views
import django.urls
from django.views.generic import TemplateView

from users.forms import CustomAuthenticationForm
import users.views

app_name = "users"
urlpatterns = [
    django.urls.path(
        "activate/<str:username>/",
        users.views.ActivateView.as_view(),
        name="activate",
    ),
    django.urls.path(
        "activate_after_ban/<str:username>/",
        users.views.ActivateAfterBanView.as_view(),
        name="activate_after_ban",
    ),
    django.urls.path(
        "login/",
        django.contrib.auth.views.LoginView.as_view(
            template_name="users/login.html",
            form_class=CustomAuthenticationForm,
        ),
        name="login",
    ),
    django.urls.path(
        "logout/",
        django.contrib.auth.views.LogoutView.as_view(),
        name="logout",
    ),
    django.urls.path(
        "logout_success/",
        TemplateView.as_view(template_name="users/logout_success.html"),
        name="logout_success",
    ),
    django.urls.path(
        "password_change/",
        django.contrib.auth.views.PasswordChangeView.as_view(
            template_name="users/password_change.html",
            success_url="done",
        ),
        name="password_change",
    ),
    django.urls.path(
        "password_change/done/",
        django.contrib.auth.views.PasswordChangeDoneView.as_view(
            template_name="users/password_change_done_my.html"
        ),
        name="password_change_done",
    ),
    django.urls.path(
        "password_reset/",
        django.contrib.auth.views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            success_url="done",
        ),
        name="password_reset",
    ),
    django.urls.path(
        "reset/done/",
        django.contrib.auth.views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete_my.html"
        ),
        name="password_reset_complete",
    ),
    django.urls.path(
        "reset/<uidb64>/<token>/",
        django.contrib.auth.views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm_my.html"
        ),
        name="password_reset_confirm",
    ),
    django.urls.path(
        "password_reset/done/",
        django.contrib.auth.views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done_my.html"
        ),
        name="password_reset_done",
    ),
    django.urls.path(
        "profile/", users.views.ProfileView.as_view(), name="profile"
    ),
    django.urls.path(
        "register/", users.views.RegistrationView.as_view(), name="register"
    ),
]
