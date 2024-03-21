from django.db import models
from django.utils.translation import gettext_lazy as _
from django_cleanup import cleanup


class PersonalInfo(models.Model):
    email = models.EmailField(_("email"))

    class Meta:
        verbose_name = _("personal information")


class Feedback(models.Model):
    text = models.TextField(_("messsage text"))
    created_on = models.DateTimeField(_("creation time"), auto_now_add=True)
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=[
            ("received", _("received")),
            ("processing", _("processing")),
            ("replied", _("replied")),
        ],
        default="received",
    )
    personal_info = models.ForeignKey(
        PersonalInfo,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        verbose_name=_("personal information"),
    )

    def delete(self, *args, **kwargs):
        cleanup.delete_files(self.files)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _("feedback")


def feedback_files_path(instance, filename):
    return f"feedback/{instance.feedback.id}/{filename}"


class File(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name=_("feedback"),
    )
    file = models.FileField(_("file"), upload_to=feedback_files_path)

    class Meta:
        verbose_name = _("file")
        verbose_name_plural = _("files")
