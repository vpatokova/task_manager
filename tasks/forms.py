from django import forms
from django.utils.translation import gettext_lazy as _

from core.inputs import DurationInput
from tasks.models import Task


class TaskForm(forms.ModelForm):
    def clean(self):
        if bool(
            self.cleaned_data.get(Task.time_between_breaks.field.name)
        ) != bool(self.cleaned_data.get(Task.breaks_duration.field.name)):
            raise forms.ValidationError(
                _(
                    "If you want to add breaks to the task, you need to fill "
                    "in all the fields, otherwise leave the last two fields "
                    "empty."
                )
            )
        super().clean()

    class Meta:
        model = Task
        fields = [
            Task.name.field.name,
            Task.duration.field.name,
            Task.time_between_breaks.field.name,
            Task.breaks_duration.field.name,
        ]
        labels = {
            Task.duration.field.name: _("Duration in hh:mm:ss format"),
            Task.time_between_breaks.field.name: _(
                "Time between breaks in hh:mm:ss format"
            ),
            Task.breaks_duration.field.name: _(
                "Duration of breaks in hh:mm:ss format"
            ),
        }
        widgets = {
            Task.duration.field.name: DurationInput(),
            Task.time_between_breaks.field.name: DurationInput(
                attrs={"required": False}
            ),
            Task.breaks_duration.field.name: DurationInput(
                attrs={"required": False}
            ),
        }
