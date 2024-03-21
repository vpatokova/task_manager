from django.test import TestCase


class StaticURLTests(TestCase):
    def test_homepage_endpoint(self):
        self.assertEqual(self.client.get("/").status_code, 200)
