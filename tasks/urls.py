from django.urls import path
from . import views

urlpatterns = [
    path("", views.task_list, name="task-list"),
    path("add-task-form/", views.add_task_form, name="add-task-form"),
    path("add-task/", views.add_task, name="add-task"),
    path("<int:pk>/toggle/", views.toggle_task, name="toggle-task"),
    path("<int:pk>/edit-form/", views.edit_task_form, name="edit-task-form"),
    path("<int:pk>/edit/", views.edit_task, name="edit-task"),
    path("<int:pk>/delete/", views.delete_task, name="delete-task"),
]
