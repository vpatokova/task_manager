from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import FormView, View

from users.forms import RegistrationForm, UserProfileForm, UserUpdateForm
from users.models import User, UserProfile

HOME = "homepage:home"
LOGIN = "users:login"


class ActivateView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        if user.is_active:
            messages.info(request, _("This user is already activated"))
            return redirect(HOME)
        if (timezone.now() - user.date_joined).total_seconds() < 43200:
            user.is_active = True
            user.save()
            messages.success(
                request, _("The account has been successfully activated")
            )
            return redirect(LOGIN)
        messages.error(request, _("The activation link has expired"))
        return redirect("users:register")


class ActivateAfterBanView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        if user.is_active:
            messages.info(request, _("This user is already activated"))
            return redirect(HOME)
        if (
            timezone.now()
            - User.objects.get(username=username).profile.last_login_attempt
        ).total_seconds() < 604800:
            user.is_active = True
            User.objects.get(
                username=username
            ).profile.last_login_attempt = None
            user.save()
            messages.success(
                request, _("The account has been successfully activated")
            )
            return redirect(LOGIN)
        messages.error(request, _("The activation link has expired"))
        return redirect("users:register")


class ProfileView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(
            instance=User.objects.get(pk=request.user.id).profile
        )
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def post(self, request):
        if "drink_coffee" in request.POST:
            profile = User.objects.get(pk=request.user.id).profile
            profile.coffee_count += 1
            print(profile.coffee_count)
            profile.save()
            messages.success(request, _("You have successfully drunk coffee!"))
            return redirect("users:profile")
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=User.objects.get(pk=request.user.id).profile,
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _("Your profile has been updated!"))
            return redirect("users:profile")


class RegistrationView(FormView):
    template_name = "users/signup.html"
    form_class = RegistrationForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = settings.USER_IS_ACTIVE
        user.save()
        user_profile = UserProfile(user=user)
        user_profile.save()
        if not settings.USER_IS_ACTIVE:
            url = reverse_lazy(
                "users:activate",
                kwargs={"username": form.cleaned_data["username"]},
            )
            email_subject = _("Activate your account")
            email_text = _(
                "Hello, %(name)s\nPlease follow the link below"
                " to activate your account"
            ) % {"name": form.cleaned_data["username"]}
            send_mail(
                email_subject,
                f"{email_text}\n{settings.ABSOLUTE_URL}:{settings.PORT}{url}",
                settings.EMAIL_HOST_USER,
                [form.cleaned_data["email"]],
            )
            messages.success(
                self.request,
                _(
                    "A link to activate your account"
                    " has been sent to your email"
                ),
            )
            return redirect(HOME)
        return redirect(LOGIN)
