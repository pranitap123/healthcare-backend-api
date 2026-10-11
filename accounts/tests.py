from django.urls import reverse

from accounts.models import User
from core.testing import PASSWORD, BaseAPITestCase


class RegisterTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("register")

    def test_register_creates_user(self):
        payload = {"name": "Carol", "email": "Carol@Example.com", "password": PASSWORD}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "carol@example.com")
        self.assertNotIn("password", response.data)
        user = User.objects.get(email="carol@example.com")
        self.assertTrue(user.check_password(PASSWORD))

    def test_register_duplicate_email_is_rejected_case_insensitively(self):
        payload = {"name": "Dup", "email": "ALICE@example.com", "password": PASSWORD}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data["error"]["details"])

    def test_register_requires_all_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)
        details = response.data["error"]["details"]
        for field in ("name", "email", "password"):
            self.assertIn(field, details)

    def test_register_rejects_weak_password(self):
        payload = {"name": "Weak", "email": "weak@example.com", "password": "12345678"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data["error"]["details"])

    def test_register_rejects_invalid_email(self):
        payload = {"name": "Bad", "email": "not-an-email", "password": PASSWORD}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data["error"]["details"])


class LoginTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("login")

    def test_login_returns_tokens(self):
        response = self.client.post(
            self.url, {"email": "alice@example.com", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "alice@example.com")

    def test_login_email_is_case_insensitive(self):
        response = self.client.post(
            self.url, {"email": "ALICE@example.com", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url, {"email": "alice@example.com", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "unauthorized")

    def test_login_unknown_user(self):
        response = self.client.post(
            self.url, {"email": "ghost@example.com", "password": PASSWORD}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_access_token_authenticates_requests(self):
        tokens = self.client.post(
            self.url, {"email": "alice@example.com", "password": PASSWORD}, format="json"
        ).data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        response = self.client.get(reverse("patient-list"))
        self.assertEqual(response.status_code, 200)

    def test_refresh_token_returns_new_access_token(self):
        tokens = self.client.post(
            self.url, {"email": "alice@example.com", "password": PASSWORD}, format="json"
        ).data
        response = self.client.post(
            reverse("token-refresh"), {"refresh": tokens["refresh"]}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.value")
        response = self.client.get(reverse("patient-list"))
        self.assertEqual(response.status_code, 401)


class HealthTests(BaseAPITestCase):
    def test_health_is_public(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "healthy")
