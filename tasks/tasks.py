import logging
from time import sleep

from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from webpush import send_user_notification

from task_manager.celery import app
from tasks.models import Task

logger = logging.getLogger("push_logger")
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


@app.task
def start_task(task_id, break_function_name):
    task = Task.objects.get(id=task_id)
    now = timezone.now().replace(microsecond=0)
    task.status = "running"
    if (
        task.state == 1
        or task.breaks_duration
        and now + task.time_between_breaks < task.end_time
    ):
        last_sleep_start = task.sleep_start
        task.sleep_start = now
        if task.state != 1:
            task.break_start = now + task.time_between_breaks
            task.state = 1
            task.save()
            sleep(task.time_between_breaks.total_seconds())
        else:
            task.break_start += now - task.pause_time
            task.save()
            sleep(
                (
                    task.time_between_breaks
                    - (task.pause_time - last_sleep_start)
                ).total_seconds()
            )
        task.state = 0
        send_user_notification(
            task.user,
            {
                "head": force_text(_("Time to rest!")),
                "body": force_text(
                    _(
                        "It's time to take a break from the '%(name)s' for "
                        "%(breaks_duration)s!"
                    )
                    % {
                        "name": task.name,
                        "breaks_duration": task.breaks_duration,
                    }
                ),
            },
            1000,
        )
        logger.debug(
            _(
                "'It's time to take a break from the '%(name)s' for "
                "%(breaks_duration)s!' has been sent"
            )
            % {"name": task.name, "breaks_duration": task.breaks_duration},
        )
        task.task_id = globals()[break_function_name].delay(task_id)
        task.save()
    else:
        task.sleep_start = now
        task.state = 2 if task.state != 2 else task.state
        task.save()
        sleep((task.end_time - now).total_seconds())
        task.state = 0
        task.status = "completed"
        task.save()
        send_user_notification(
            task.user,
            {
                "head": force_text(_("Time's up!")),
                "body": force_text(
                    _("Task '%(name)s' is finished!") % {"name": task.name}
                ),
            },
            1000,
        )
        logger.debug(
            _("'Task '%(name)s' is finished!' has been sent")
            % {"name": task.name}
        )


@app.task
def take_break(task_id):
    task = Task.objects.get(id=task_id)
    now = timezone.now().replace(microsecond=0)
    task.status = "break"
    if task.state == 3 or now + task.breaks_duration < task.end_time:
        last_sleep_start = task.sleep_start
        task.sleep_start = now
        if task.state != 3:
            task.break_end = now + task.breaks_duration
            task.state = 3
            task.save()
            sleep(task.breaks_duration.total_seconds())
        else:
            task.break_end += now - task.pause_time
            task.save()
            sleep(
                (
                    task.breaks_duration - (task.pause_time - last_sleep_start)
                ).total_seconds()
            )
        task.state = 0
        send_user_notification(
            task.user,
            {
                "head": force_text(_("It's time to get back to work!")),
                "body": force_text(
                    _("It's time to continue the '%(name)s'!")
                    % {"name": task.name}
                ),
            },
            1000,
        )
        logger.debug(
            _("'It's time to continue the '%(name)s'!' has been sent")
            % {"name": task.name}
        )
        task.task_id = start_task.delay(task_id, "take_break")
        task.save()
    else:
        send_user_notification(
            task.user,
            {
                "head": force_text(_("Have a rest!")),
                "body": force_text(
                    _(
                        "The time of the '%(name)s' task is not over yet, "
                        "but according to the schedule there is only a break "
                        "left. Have a rest!"
                    )
                    % {"name": task.name}
                ),
            },
            1000,
        )
        logger.debug(
            _(
                "'The time of the '%(name)s' task is not over yet, but "
                "according to the schedule there is only a break left. Have a "
                "rest!' has been sent"
            )
            % {"name": task.name}
        )
        task.status = "completed"
        task.save()
