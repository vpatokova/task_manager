from os import path, remove
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from feedback.forms import FeedbackForm
from feedback.models import Feedback, File, PersonalInfo


class FeedbackFormTest(TestCase):
    def setUp(self):
        self.feedback_url = reverse("feedback:feedback")
        self.temp_file = tempfile.NamedTemporaryFile()
        self.file_name = "test_file.txt"
        self.uploaded_file = SimpleUploadedFile(
            self.file_name, b"test content"
        )
        self.feedback_data = {
            "text": "test feedback",
            "email": "test@example.com",
            "files": [self.uploaded_file],
        }

    def tearDown(self):
        self.temp_file.close()
        for file in File.objects.all():
            remove(path.join(settings.MEDIA_ROOT, file.file.name))
        Feedback.objects.all().delete()
        PersonalInfo.objects.all().delete()
        File.objects.all().delete()
        super().tearDown()

    def test_form_context(self):
        self.assertIsInstance(
            self.client.get(self.feedback_url).context.get("form"),
            FeedbackForm,
        )

    def test_redirect(self):
        response = Client().post(
            self.feedback_url, self.feedback_data, follow=True
        )
        self.assertRedirects(response, self.feedback_url)

    def test_feedback_form_submission_creates_database_record(self):
        Client().post(self.feedback_url, self.feedback_data)
        self.assertEqual(Feedback.objects.count(), 1)

    def test_feedback_form_submission_doesnt_create_database_record(self):
        Client().post(
            self.feedback_url,
            {"text": "Test message", "email": "testexample.com"},
        )
        self.assertEqual(Feedback.objects.count(), 0)

    def test_feedback_form_with_file(self):
        response = Client().post(
            self.feedback_url,
            data=self.feedback_data,
        )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 302)
        feedback = Feedback.objects.last()
        with self.subTest("feedback"):
            self.assertIsNotNone(feedback)
        with self.subTest("feedback.text"):
            self.assertEqual(feedback.text, self.feedback_data["text"])
        with self.subTest("feedback.user.email"):
            self.assertEqual(
                feedback.personal_info.email, self.feedback_data["email"]
            )
        with self.subTest("feedback.status"):
            self.assertEqual(feedback.status, "received")
        with self.subTest("file"):
            self.assertEqual(File.objects.filter(feedback=feedback).count(), 1)
