from django.test import TestCase
from django.urls import reverse
from .models import Task
from .forms import TaskForm


class TaskListTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Task.objects.create(title="First Task")
        Task.objects.create(title="Second Task", completed=True)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_list_page.html")

    def test_view_displays_all_tasks(self):
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 2)

class TaskCreateTest(TestCase):

        def test_get_add_task_page_no_js(self):
            response = self.client.get(reverse("add-task-form"))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "tasks/add_task_page.html")
            self.assertIsInstance(response.context["form"], TaskForm)

        def test_get_add_task_form_htmx(self):
            headers = {"HTTP_HX_REQUEST": "true"}
            response = self.client.get(reverse("add-task-form"), **headers)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "tasks/partials/_add_task_form.html")

        def test_add_task_htmx_request(self):
            headers = {"HTTP_HX_REQUEST": "true"}
            response = self.client.post(
                reverse("add-task"), {"title": "New HTMX Task"}, **headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "tasks/partials/_task_row.html")
            self.assertTrue(Task.objects.filter(title="New HTMX Task").exists())

        def test_add_task_no_js_request(self):
            response = self.client.post(
                reverse("add-task"), {"title": "New Regular Task"}, follow=True
            )
            self.assertRedirects(
                response, reverse("task-list"), status_code=302,
            )
            self.assertContains(response, "New Regular Task")
            self.assertTrue(Task.objects.filter(title="New Regular Task").exists())

        def test_add_task_invalid_data(self):
            response = self.client.post(reverse("add-task"), {"title": ""})
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response.context["form"], "title", "This field is required.")


class TaskToggleTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.task = Task.objects.create(title="Toggle Me")

    def test_toggle_task_htmx_request(self):
        self.assertFalse(self.task.completed)

        headers = {"HTTP_HX_REQUEST": "true"}
        url = reverse("toggle-task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, **headers)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/partials/_task_row.html")

        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.assertContains(response, "Yes")

    def test_toggle_task_no_js_request(self):
        self.assertFalse(self.task.completed)

        url = reverse("toggle-task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, follow=True)

        self.assertRedirects(
            response, reverse("task-list"), status_code=302
        )

        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)
        self.assertContains(response, "Yes")

class TaskEditTest(TestCase):

        @classmethod
        def setUpTestData(cls):
            cls.task = Task.objects.create(title="Initial Title")

        def test_get_edit_task_page_no_js(self):
            url = reverse("edit-task-form", kwargs={"pk": self.task.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "tasks/edit_task_page.html")
            self.assertEqual(response.context["form"].instance, self.task)

        def test_get_edit_task_form_htmx(self):
            headers = {"HTTP_HX_REQUEST": "true"}
            url = reverse("edit-task-form", kwargs={"pk": self.task.pk})
            response = self.client.get(url, **headers)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "tasks/partials/_task_edit_form.html")

        def test_edit_task_htmx_request(self):
            url = reverse("edit-task", kwargs={"pk": self.task.pk})
            headers = {"HTTP_HX_REQUEST": "true"}
            response = self.client.post(url, {"title": "Updated HTMX Title"}, **headers)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "tasks/partials/_task_row.html")
            self.assertContains(response, "Updated HTMX Title")
            self.task.refresh_from_db()
            self.assertEqual(self.task.title, "Updated HTMX Title")

        def test_edit_task_no_js_request(self):
            url = reverse("edit-task", kwargs={"pk": self.task.pk})
            response = self.client.post(url, {"title": "Updated Regular Title"}, follow=True)
            self.assertRedirects(response, reverse("task-list"), status_code=302)
            self.assertContains(response, "Updated Regular Title")
            self.task.refresh_from_db()
            self.assertEqual(self.task.title, "Updated Regular Title")

        def test_edit_task_invalid_data(self):
            url = reverse("edit-task", kwargs={"pk": self.task.pk})
            response = self.client.post(url, {"title": ""})
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response.context["form"], "title", "This field is required.")


class TaskDeleteTest(TestCase):

    def setUp(self):
        self.task = Task.objects.create(title="Task to be deleted")
        self.htmx_headers = {"HTTP_HX_REQUEST": "true"}

    def test_delete_task_htmx_request(self):
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

        url = reverse("delete-task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, **self.htmx_headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_delete_task_no_js_request(self):
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

        url = reverse("delete-task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, follow=True)

        self.assertRedirects(response, reverse("task-list"), status_code=302)
        self.assertNotContains(response, self.task.title)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
