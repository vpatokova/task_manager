from django import forms
from django.utils.translation import gettext_lazy as _

from feedback.models import Feedback, File, PersonalInfo


class FeedbackForm(forms.Form):
    text = forms.CharField(
        label=_("Message text"),
        help_text=_("Enter the text of your message"),
    )
    email = forms.EmailField(
        label=_("Email address"),
        help_text=_("Enter your email address"),
    )
    files = forms.FileField(
        label=_("Attached files"),
        help_text=_("Select the files you want to attach to the message"),
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        required=False,
    )

    def save(self):
        personal_info = PersonalInfo.objects.filter(
            email=self.cleaned_data["email"]
        )
        if personal_info:
            personal_info = personal_info.first()
        else:
            personal_info = PersonalInfo.objects.create(
                email=self.cleaned_data["email"]
            )
        feedback = Feedback.objects.create(
            text=self.cleaned_data["text"], personal_info=personal_info
        )
        for file in self.files.getlist("files"):
            File.objects.create(feedback=feedback, file=file)
