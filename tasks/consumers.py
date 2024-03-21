from channels.generic.websocket import AsyncJsonWebsocketConsumer


def create_group_name(user):
    return f"tasks-{user.id}"


class TasksConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.get_user()

        if user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(
            create_group_name(user), self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        user = self.get_user()

        await self.channel_layer.group_discard(
            create_group_name(user), self.channel_name
        )

    async def send_timer_commands(self, event):
        await self.send_json(
            {
                "command": event["command"],
                "time": event["time"],
                "task_id": event["task_id"],
            }
        )

    def get_user(self):
        return self.scope["user"]
