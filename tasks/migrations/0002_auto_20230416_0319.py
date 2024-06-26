# Generated by Django 3.2.18 on 2023-04-15 22:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="break_end",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="время конца текущего перерыва",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="break_start",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="время начала следующего перерыва",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="breaks_duration",
            field=models.DurationField(
                blank=True, null=True, verbose_name="длительность перерыва"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="end_time",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="время конца"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="is_running",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="task",
            name="is_with_breaks",
            field=models.BooleanField(
                default=False,
                verbose_name="присутствуют ли перерывы в задаче?",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="time_between_breaks",
            field=models.DurationField(
                blank=True, null=True, verbose_name="время между перерывами"
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="duration",
            field=models.DurationField(verbose_name="длительность"),
        ),
    ]
