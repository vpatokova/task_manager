from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, View

from task_manager.celery import app
from tasks.forms import TaskForm
from tasks.models import Task
from tasks.tasks import start_task, take_break

TASK_LIST = "tasks:list"


class TaskCreateView(LoginRequiredMixin, CreateView):
    template_name = "tasks/create.html"
    form_class = TaskForm
    model = Task
    success_url = reverse_lazy(TASK_LIST)

    def form_valid(self, form):
        task = form.save(commit=False)
        task.user = self.request.user
        task.start_time = timezone.now().replace(microsecond=0)
        task.end_time = task.start_time + task.duration
        task.is_with_breaks = True if task.breaks_duration else False
        task.save()
        task.task_id = start_task.delay(task.id, "take_break")
        task.save()
        return super().form_valid(form)


class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy(TASK_LIST)


class TaskListView(LoginRequiredMixin, ListView):
    template_name = "tasks/list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return Task.objects.get_list(self.request.user)


class TaskSuspendView(View):
    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        if task.status == "paused":
            task.end_time += (
                timezone.now().replace(microsecond=0) - task.pause_time
            )
            if task.state == 3:
                task.task_id = take_break.delay(task.id)
            else:
                task.task_id = start_task.delay(task.id, "take_break")
        else:
            app.control.revoke(task.task_id, terminate=True)
            task.status = "paused"
            task.pause_time = timezone.now().replace(microsecond=0)
        task.save()
        return redirect(TASK_LIST)


class TaskTimeView(LoginRequiredMixin, View):
    def get(self, reqeust):
        tasks = Task.objects.get_list(self.request.user)

        return JsonResponse(
            [
                {
                    "task_id": task.id,
                    "remaining_time": str(task.remaining_time),
                    "time_to": str(task.time_to),
                    "status_text": str(task.get_status_display()),
                    "status": str(task.status),
                    "is_with_breaks": task.is_with_breaks,
                }
                for task in tasks
            ],
            safe=False,
        )
