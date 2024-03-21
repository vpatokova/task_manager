from datetime import timedelta

from django.forms.widgets import TextInput
from django.utils.dateparse import parse_duration


class DurationInput(TextInput):
    def _format_value(self, value):
        return timedelta(seconds=parse_duration(value).total_seconds())
