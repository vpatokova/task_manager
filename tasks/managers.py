from django.db import models
from django.utils import timezone


class TaskManager(models.Manager):
    def get_list(self, user):
        now = timezone.now().replace(microsecond=0)
        return (
            self.filter(user=user)
            .only(
                self.model.id.field.name,
                self.model.name.field.name,
                self.model.start_time.field.name,
                self.model.status.field.name,
                self.model.breaks_duration.field.name,
                self.model.is_with_breaks.field.name,
            )
            .annotate(
                remaining_time=models.Case(
                    models.When(
                        status="completed", then=timezone.timedelta(-1)
                    ),
                    models.When(
                        status="paused",
                        then=models.F(self.model.end_time.field.name)
                        - models.F(self.model.pause_time.field.name),
                    ),
                    default=models.F(self.model.end_time.field.name) - now,
                    output_field=models.fields.DurationField(),
                ),
                time_to=models.Case(
                    models.When(
                        status="running",
                        then=models.F(self.model.break_start.field.name) - now,
                    ),
                    models.When(
                        status="break",
                        then=models.F(self.model.break_end.field.name) - now,
                    ),
                    models.When(
                        state=3,
                        then=models.F(self.model.break_end.field.name)
                        - models.F(self.model.pause_time.field.name),
                    ),
                    models.When(
                        state=1,
                        then=models.F(self.model.break_start.field.name)
                        - models.F(self.model.pause_time.field.name),
                    ),
                    default=models.F(self.model.end_time.field.name)
                    - models.F(self.model.pause_time.field.name),
                    output_field=models.fields.DurationField(),
                ),
            )
        )
