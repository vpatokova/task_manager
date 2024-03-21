from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView

from feedback.forms import FeedbackForm


EMAIL_SUBJECT_FEEDBACK = _("Thanks for the feedback!")
EMAIL_TEXT_FEEDBACK = _("Thank you for the feedback")


class FeedbackView(FormView):
    template_name = "feedback/feedback.html"
    form_class = FeedbackForm
    success_url = reverse_lazy("feedback:feedback")

    def form_valid(self, form):
        form.save()
        send_mail(
            EMAIL_SUBJECT_FEEDBACK,
            EMAIL_TEXT_FEEDBACK,
            settings.EMAIL_HOST_USER,
            [form.cleaned_data.get("email")],
            fail_silently=False,
        )
        messages.success(
            self.request, _("The form has been successfully submitted.")
        )
        return super().form_valid(form)
