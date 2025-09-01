from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import TaskForm
from .models import Task


def task_list(request):
    """Renders the main page displaying the list of all tasks."""
    tasks = Task.objects.order_by("created_at")
    return render(request, "tasks/task_list_page.html", {"tasks": tasks})


def add_task_form(request):
    """
    Renders the task form.
    - If HTMX request, returns a partial.
    - If standard request, returns full page.
    """
    form = TaskForm()
    if request.htmx:
        return render(request, "tasks/partials/_add_task_form.html", {"form": form})

    tasks = Task.objects.order_by("created_at")
    return render(request, "tasks/add_task_page.html", {"form": form, "tasks": tasks})


def add_task(request):
    """
    Handles the creation of a new task.
    Supports both HTMX and standard form submissions.
    """
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            if request.htmx:
                # Return multi-part response render for adding task and replacing button.
                return render(request, "tasks/partials/_add_task_response.html", {"task": task})
            return redirect(reverse("task-list"))
        else:
            return render(request, "tasks/partials/_add_task_form.html", {"form": form})
    return redirect(reverse("task-list"))


def toggle_task(request, pk):
    """Handles toggling the completed status of a task."""
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.completed = not task.completed
        task.save()

        if request.htmx:
            return render(request, "tasks/partials/_task_row.html", {"task": task})
    # Redirect GET & non HTMX requests.
    return redirect(reverse("task-list"))


def edit_task_form(request, pk):
    """
    Renders the edit form for a specific task.
    - If HTMX request, returns a partial.
    - If standard request, returns full page.
    """
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(instance=task)

    if request.htmx:
        return render(request, "tasks/partials/_task_edit_form.html", {"task": task, "form": form})
    tasks = Task.objects.order_by("created_at")
    return render(request, "tasks/edit_task_page.html", {"task": task, "form": form, "tasks": tasks})



def edit_task(request, pk):
    """Handles updating a task's title."""
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            if request.htmx:
                return render(request, "tasks/partials/_task_row.html", {"task": task})
            return redirect(reverse("task-list"))
        else:
            return render(
                request,
                "tasks/partials/_task_edit_form.html",
                {"task": task, "form": form},
            )
    # Redirect GET requests.
    return redirect(reverse("task-list"))


def delete_task(request, pk):
    """Handles the deletion of a task."""
    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)
        task.delete()

        if request.htmx:
            return HttpResponse("")
    return redirect(reverse("task-list"))
