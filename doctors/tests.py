from django.urls import reverse

from core.testing import BaseAPITestCase
from doctors.models import Doctor

VALID = {
    "name": "Dr. House",
    "specialization": "Diagnostics",
    "email": "House@Example.com",
    "phone": "+1 555-000-1111",
    "experience_years": 15,
}


class DoctorTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("doctor-list")

    def detail_url(self, pk):
        return reverse("doctor-detail", args=[pk])

    def test_endpoints_require_authentication(self):
        doctor = self.make_doctor(self.user)
        self.assertEqual(self.client.get(self.list_url).status_code, 401)
        self.assertEqual(self.client.post(self.list_url, VALID, format="json").status_code, 401)
        self.assertEqual(self.client.get(self.detail_url(doctor.pk)).status_code, 401)

    def test_create_doctor(self):
        self.login()
        response = self.client.post(self.list_url, VALID, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "house@example.com")
        self.assertEqual(response.data["created_by"], self.user.pk)

    def test_create_validates_input(self):
        self.login()
        response = self.client.post(
            self.list_url,
            {"name": "", "specialization": "", "email": "bad", "experience_years": 500},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        details = response.data["error"]["details"]
        for field in ("name", "specialization", "email", "experience_years"):
            self.assertIn(field, details)

    def test_duplicate_email_rejected(self):
        self.make_doctor(self.user, email="house@example.com")
        self.login()
        response = self.client.post(self.list_url, VALID, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data["error"]["details"])

    def test_list_shows_all_doctors_to_any_user(self):
        self.make_doctor(self.user)
        self.make_doctor(self.other)
        self.login(self.other)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_specialization(self):
        self.make_doctor(self.user, specialization="Cardiology")
        self.make_doctor(self.user, specialization="Neurology")
        self.login()
        response = self.client.get(self.list_url, {"specialization": "neurology"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["specialization"], "Neurology")

    def test_retrieve_doctor_created_by_someone_else(self):
        doctor = self.make_doctor(self.other)
        self.login()
        response = self.client.get(self.detail_url(doctor.pk))
        self.assertEqual(response.status_code, 200)

    def test_creator_can_update_doctor(self):
        doctor = self.make_doctor(self.user)
        self.login()
        response = self.client.put(self.detail_url(doctor.pk), VALID, format="json")
        self.assertEqual(response.status_code, 200)
        doctor.refresh_from_db()
        self.assertEqual(doctor.name, "Dr. House")

    def test_update_keeping_same_email_is_allowed(self):
        doctor = self.make_doctor(self.user, email="house@example.com")
        self.login()
        response = self.client.put(self.detail_url(doctor.pk), VALID, format="json")
        self.assertEqual(response.status_code, 200)

    def test_non_creator_cannot_modify_or_delete(self):
        doctor = self.make_doctor(self.other)
        self.login()
        self.assertEqual(self.client.put(self.detail_url(doctor.pk), VALID, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url(doctor.pk)).status_code, 403)
        self.assertTrue(Doctor.objects.filter(pk=doctor.pk).exists())

    def test_creator_can_delete_doctor(self):
        doctor = self.make_doctor(self.user)
        self.login()
        response = self.client.delete(self.detail_url(doctor.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Doctor.objects.filter(pk=doctor.pk).exists())

    def test_missing_doctor_returns_404(self):
        self.login()
        self.assertEqual(self.client.get(self.detail_url(9999)).status_code, 404)
