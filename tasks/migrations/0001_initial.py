# Generated by Django 3.2.18 on 2023-04-12 14:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0002_auto_20230407_1921"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=150, verbose_name="название"),
                ),
                (
                    "start_time",
                    models.DateTimeField(verbose_name="время начала"),
                ),
                (
                    "duration",
                    models.DurationField(
                        verbose_name="длительность в минутах"
                    ),
                ),
                (
                    "is_completed",
                    models.BooleanField(
                        default=False, verbose_name="выполнена ли задача"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.user",
                        verbose_name="пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "задача",
                "verbose_name_plural": "задачи",
            },
        ),
    ]