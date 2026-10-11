from django.urls import reverse

from core.testing import BaseAPITestCase
from patients.models import Patient

VALID = {
    "name": "Jane Roe",
    "age": 32,
    "gender": "female",
    "phone": "+1 555-123-4567",
    "address": "12 Main St",
    "medical_history": "Asthma",
}


class PatientTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("patient-list")

    def detail_url(self, pk):
        return reverse("patient-detail", args=[pk])

    def test_endpoints_require_authentication(self):
        patient = self.make_patient(self.user)
        self.assertEqual(self.client.get(self.list_url).status_code, 401)
        self.assertEqual(self.client.post(self.list_url, VALID, format="json").status_code, 401)
        self.assertEqual(self.client.get(self.detail_url(patient.pk)).status_code, 401)
        self.assertEqual(self.client.delete(self.detail_url(patient.pk)).status_code, 401)

    def test_create_assigns_authenticated_user_as_owner(self):
        self.login()
        response = self.client.post(self.list_url, {**VALID, "created_by": self.other.pk}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["created_by"], self.user.pk)
        self.assertEqual(Patient.objects.get(pk=response.data["id"]).created_by, self.user)

    def test_create_validates_input(self):
        self.login()
        response = self.client.post(
            self.list_url, {"name": " ", "age": 200, "gender": "x", "phone": "abc"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        details = response.data["error"]["details"]
        for field in ("name", "age", "gender", "phone"):
            self.assertIn(field, details)

    def test_list_returns_only_own_patients(self):
        mine = self.make_patient(self.user, name="Mine")
        self.make_patient(self.other, name="Theirs")
        self.login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], mine.pk)

    def test_retrieve_own_patient(self):
        patient = self.make_patient(self.user)
        self.login()
        response = self.client.get(self.detail_url(patient.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], patient.name)

    def test_other_users_patient_is_not_accessible(self):
        patient = self.make_patient(self.other)
        self.login()
        self.assertEqual(self.client.get(self.detail_url(patient.pk)).status_code, 404)
        self.assertEqual(self.client.put(self.detail_url(patient.pk), VALID, format="json").status_code, 404)
        self.assertEqual(self.client.delete(self.detail_url(patient.pk)).status_code, 404)
        self.assertTrue(Patient.objects.filter(pk=patient.pk).exists())

    def test_update_patient(self):
        patient = self.make_patient(self.user)
        self.login()
        response = self.client.put(self.detail_url(patient.pk), VALID, format="json")
        self.assertEqual(response.status_code, 200)
        patient.refresh_from_db()
        self.assertEqual(patient.name, "Jane Roe")
        self.assertEqual(patient.gender, "female")

    def test_put_requires_full_payload(self):
        patient = self.make_patient(self.user)
        self.login()
        response = self.client.put(self.detail_url(patient.pk), {"name": "Only"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_delete_patient(self):
        patient = self.make_patient(self.user)
        self.login()
        response = self.client.delete(self.detail_url(patient.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Patient.objects.filter(pk=patient.pk).exists())

    def test_missing_patient_returns_404_envelope(self):
        self.login()
        response = self.client.get(self.detail_url(9999))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"]["code"], "not_found")

    def test_list_is_paginated(self):
        for index in range(25):
            self.make_patient(self.user, name=f"P{index}")
        self.login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIsNotNone(response.data["next"])
