from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from tasks.consumers import create_group_name


def send_time_break(task, user):
    channel_layer = get_channel_layer()
    group_name = create_group_name(user)
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_timer_commands",
            "task_id": str(task.id),
            "command": "time_break",
            "time": str(task.breaks_duration),
        },
    )


def send_time_up(task, user):
    channel_layer = get_channel_layer()
    group_name = create_group_name(user)
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_timer_commands",
            "task_id": str(task.id),
            "command": "time_up",
            "time": str(task.breaks_duration),
        },
    )
