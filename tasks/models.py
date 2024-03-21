from django.db import models
from django.utils.translation import gettext_lazy as _

from task_manager.celery import app
from tasks.managers import TaskManager
from users.models import User


class Task(models.Model):
    objects = TaskManager()
    name = models.CharField(_("name"), max_length=150)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("user")
    )
    start_time = models.DateTimeField(_("start time"))
    duration = models.DurationField(_("duration"))
    is_with_breaks = models.BooleanField(_("is with breaks?"), default=False)
    time_between_breaks = models.DurationField(
        _("time between breaks"), null=True, blank=True
    )
    breaks_duration = models.DurationField(
        _("breaks duration"), null=True, blank=True
    )
    break_start = models.DateTimeField(
        _("next break starts"), null=True, blank=True
    )
    break_end = models.DateTimeField(
        _("current break ends"), null=True, blank=True
    )
    end_time = models.DateTimeField(_("ending time"), null=True, blank=True)
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=[
            ("running", _("running")),
            ("break", _("break")),
            ("completed", _("completed")),
            ("paused", _("paused")),
        ],
        default="running",
    )
    pause_time = models.DateTimeField(
        _("task suspension time"), null=True, blank=True
    )
    task_id = models.CharField(
        _("celery-task's id"), max_length=255, null=True, blank=True
    )
    state = models.PositiveSmallIntegerField(
        _("where was the task suspended"),
        default=0,
        choices=[
            (
                0,
                _(
                    "the task has not been suspended yet or the error has "
                    "already been taken into account"
                ),
            ),
            (1, _("the task was suspended during the first sleep")),
            (2, _("the task was suspended during the second sleep")),
            (3, _("the task was suspended during the third sleep")),
        ],
    )
    sleep_start = models.DateTimeField(
        _("sleep start time"), null=True, blank=True
    )

    def delete(self, *args, **kwargs):
        app.control.revoke(self.task_id, terminate=True)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        ordering = ("start_time",)
