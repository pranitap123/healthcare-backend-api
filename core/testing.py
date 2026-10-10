from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase

from accounts.models import User
from doctors.models import Doctor
from patients.models import Patient

PASSWORD = "Str0ng-Passw0rd!"


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class BaseAPITestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = self.make_user("alice@example.com", "Alice")
        self.other = self.make_user("bob@example.com", "Bob")

    def make_user(self, email, name):
        return User.objects.create_user(email=email, password=PASSWORD, name=name)

    def make_patient(self, owner, **overrides):
        data = {"name": "John Doe", "age": 40, "gender": "male"}
        data.update(overrides)
        return Patient.objects.create(created_by=owner, **data)

    def make_doctor(self, owner, **overrides):
        data = {
            "name": "Dr. Grey",
            "specialization": "Cardiology",
            "email": f"doc{Doctor.objects.count()}@example.com",
            "experience_years": 10,
        }
        data.update(overrides)
        return Doctor.objects.create(created_by=owner, **data)

    def login(self, user=None):
        self.client.force_authenticate(user=user or self.user)
