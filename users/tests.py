from datetime import timedelta

from django.core import mail
from django.test import Client, override_settings, TestCase
from django.urls import reverse, reverse_lazy
from freezegun import freeze_time

from users.models import User, UserProfile

REGISTER = "users:register"
EMAIL = "testuser@test.ru"
SECOND_EMAIL = "testuser2@test.ru"
ACTIVATE = "users:activate"
LOGIN = "users:login"
HOME = "homepage:home"
USERNAME = "testuser"
SECOND_USERNAME = "testuser2"
PASSWORD = "testpass123"
DEFAULT_TIMEZONE = "Europe/Moscow"
SECOND_TIMEZONE = "Asia/Tokyo"


class RegistrationTests(TestCase):
    def tearDown(self):
        User.objects.all().delete()
        super().tearDown()

    def test_registration_page_loads(self):
        response = self.client.get(reverse(REGISTER))
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 200)
        with self.subTest("TemplateUsed"):
            self.assertTemplateUsed(response, "users/signup.html")

    @override_settings(USER_IS_ACTIVE=False)
    def test_registration(self):
        response = self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": EMAIL,
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 302)
        with self.subTest("User.objects.count()"):
            self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username=USERNAME)
        with self.subTest("is_active"):
            self.assertFalse(user.is_active)
        with self.subTest("len(mail.outbox)"):
            self.assertEqual(len(mail.outbox), 1)

    @override_settings(USER_IS_ACTIVE=True)
    def test_registration_active(self):
        self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": EMAIL,
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertTrue(User.objects.get(username=USERNAME).is_active)

    @override_settings(USER_IS_ACTIVE=False)
    def test_activation(self):
        self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": EMAIL,
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        user = User.objects.get(username=USERNAME)
        with self.subTest("is_active"):
            self.assertFalse(user.is_active)
        with freeze_time(user.date_joined + timedelta(hours=10)):
            response = self.client.get(
                reverse(ACTIVATE, kwargs={"username": user.username})
            )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        with self.subTest("is_active_2"):
            self.assertTrue(user.is_active)

    @override_settings(USER_IS_ACTIVE=False)
    def test_activation_overdue(self):
        self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": EMAIL,
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        user = User.objects.get(username=USERNAME)
        with self.subTest("is_active"):
            self.assertFalse(user.is_active)
        with freeze_time(user.date_joined + timedelta(hours=13)):
            response = self.client.get(
                reverse(ACTIVATE, kwargs={"username": user.username})
            )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        with self.subTest("is_active_2"):
            self.assertFalse(user.is_active)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD,
        )

    def tearDown(self):
        User.objects.all().delete()
        super().tearDown()

    def test_login_with_username(self):
        response = self.client.post(
            reverse(LOGIN),
            {"username": USERNAME, "password": PASSWORD},
        )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 302)
        with self.subTest("redirects"):
            self.assertRedirects(response, reverse(HOME))

    def test_login_with_email(self):
        response = self.client.post(
            reverse(LOGIN),
            {"username": EMAIL, "password": PASSWORD},
        )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 302)
        with self.subTest("redirects"):
            self.assertRedirects(response, reverse(HOME))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse(LOGIN),
            {"username": USERNAME, "password": "wrongpassword"},
        )
        with self.subTest("status_code"):
            self.assertEqual(response.status_code, 200)


class EmailNormalizationTestCase(TestCase):
    def tearDown(self):
        User.objects.all().delete()
        super().tearDown()

    def test_email_normalization_gmail(self):
        self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": "test.user+test@gmail.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(
            User.objects.get(username=USERNAME).email, "testuser@gmail.com"
        )

    def test_email_normalization_yandex(self):
        self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": "test.user@yandex.ru",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(
            User.objects.get(username=USERNAME).email, "test-user@yandex.ru"
        )

    def test_email_normalization_ya(self):
        self.client.post(
            reverse(REGISTER),
            {
                "username": USERNAME,
                "email": "test.user@ya.ru",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(
            User.objects.get(username=USERNAME).email, "test-user@yandex.ru"
        )


class LoginBlockAndRestoreTestCase(TestCase):
    def tearDown(self):
        User.objects.all().delete()
        super().tearDown()

    @override_settings(USER_IS_ACTIVE=True)
    def setUp(self):
        self.user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )
        UserProfile.objects.create(user=self.user)

    @override_settings(MAX_LOGIN_ATTEMPTS=2)
    def test_block_and_restore(self):
        client = Client()
        client.post(reverse(LOGIN), {"username": USERNAME, "password": "q"})
        client.post(reverse(LOGIN), {"username": EMAIL, "password": "qw"})
        with self.subTest("User banned?"):
            self.assertEqual(User.objects.get(email=EMAIL).is_active, False)
        with self.subTest("len(mail.outbox)"):
            self.assertEqual(len(mail.outbox), 1)
        with self.subTest("mail.outbox[0].to"):
            self.assertEqual(mail.outbox[0].to, [self.user.email])
        url = reverse_lazy(
            "users:activate_after_ban", kwargs={"username": self.user.username}
        )
        self.client.get(f"http://127.0.0.1:8000{url}")
        with self.subTest("User restored?"):
            self.assertEqual(self.user.is_active, True)

    @override_settings(MAX_LOGIN_ATTEMPTS=2)
    def test_block_and_restore_overdue(self):
        client = Client()
        client.post(reverse(LOGIN), {"username": USERNAME, "password": "q"})
        client.post(reverse(LOGIN), {"username": EMAIL, "password": "qw"})
        with self.subTest("User banned?"):
            self.assertEqual(User.objects.get(email=EMAIL).is_active, False)
        with self.subTest("len(mail.outbox)"):
            self.assertEqual(len(mail.outbox), 1)
        with self.subTest("mail.outbox[0].to"):
            self.assertEqual(mail.outbox[0].to, [self.user.email])
        with freeze_time(
            User.objects.get(username=USERNAME).profile.last_login_attempt
            + timedelta(days=8)
        ):
            url = reverse_lazy(
                "users:activate_after_ban",
                kwargs={"username": USERNAME},
            )
            client.get(f"http://127.0.0.1:8000{url}")
        with self.subTest("User restored?"):
            self.assertEqual(User.objects.get(email=EMAIL).is_active, False)
