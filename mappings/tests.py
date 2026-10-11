from django.urls import reverse

from core.testing import BaseAPITestCase
from mappings.models import PatientDoctorMapping


class MappingTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.list_url = reverse("mapping-list")
        self.patient = self.make_patient(self.user)
        self.doctor = self.make_doctor(self.user)
        self.other_patient = self.make_patient(self.other, name="Other Patient")

    def detail_url(self, pk):
        return reverse("mapping-detail", args=[pk])

    def assign(self, patient=None, doctor=None):
        return PatientDoctorMapping.objects.create(
            patient=patient or self.patient,
            doctor=doctor or self.doctor,
            assigned_by=self.user,
        )

    def test_endpoints_require_authentication(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 401)
        self.assertEqual(self.client.post(self.list_url, {}, format="json").status_code, 401)
        self.assertEqual(self.client.get(self.detail_url(self.patient.pk)).status_code, 401)
        self.assertEqual(self.client.delete(self.detail_url(1)).status_code, 401)

    def test_assign_doctor_to_patient(self):
        self.login()
        response = self.client.post(
            self.list_url, {"patient": self.patient.pk, "doctor": self.doctor.pk}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["patient_name"], self.patient.name)
        self.assertEqual(response.data["doctor_name"], self.doctor.name)
        self.assertEqual(response.data["assigned_by"], self.user.pk)

    def test_duplicate_assignment_rejected(self):
        self.assign()
        self.login()
        response = self.client.post(
            self.list_url, {"patient": self.patient.pk, "doctor": self.doctor.pk}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)

    def test_cannot_assign_to_another_users_patient(self):
        self.login()
        response = self.client.post(
            self.list_url, {"patient": self.other_patient.pk, "doctor": self.doctor.pk}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("patient", response.data["error"]["details"])
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)

    def test_assign_requires_existing_doctor(self):
        self.login()
        response = self.client.post(
            self.list_url, {"patient": self.patient.pk, "doctor": 9999}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("doctor", response.data["error"]["details"])

    def test_assign_requires_fields(self):
        self.login()
        response = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("patient", response.data["error"]["details"])
        self.assertIn("doctor", response.data["error"]["details"])

    def test_doctor_created_by_other_user_can_be_assigned(self):
        foreign_doctor = self.make_doctor(self.other)
        self.login()
        response = self.client.post(
            self.list_url, {"patient": self.patient.pk, "doctor": foreign_doctor.pk}, format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_list_returns_only_mappings_of_own_patients(self):
        mine = self.assign()
        PatientDoctorMapping.objects.create(
            patient=self.other_patient, doctor=self.doctor, assigned_by=self.other
        )
        self.login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], mine.pk)

    def test_list_can_be_filtered(self):
        second_patient = self.make_patient(self.user, name="Second")
        self.assign()
        self.assign(patient=second_patient)
        self.login()
        response = self.client.get(self.list_url, {"patient": second_patient.pk})
        self.assertEqual(response.data["count"], 1)

    def test_get_doctors_for_patient(self):
        second_doctor = self.make_doctor(self.user, name="Dr. Second")
        self.assign()
        self.assign(doctor=second_doctor)
        self.login()
        response = self.client.get(self.detail_url(self.patient.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        names = {item["doctor"]["name"] for item in response.data}
        self.assertEqual(names, {self.doctor.name, "Dr. Second"})
        self.assertIn("mapping_id", response.data[0])

    def test_get_doctors_for_patient_with_none_assigned(self):
        self.login()
        response = self.client.get(self.detail_url(self.patient.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_doctors_for_another_users_patient_is_404(self):
        self.login()
        response = self.client.get(self.detail_url(self.other_patient.pk))
        self.assertEqual(response.status_code, 404)

    def test_delete_mapping(self):
        mapping = self.assign()
        self.login()
        response = self.client.delete(self.detail_url(mapping.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())

    def test_cannot_delete_mapping_of_another_users_patient(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.other_patient, doctor=self.doctor, assigned_by=self.other
        )
        self.login()
        response = self.client.delete(self.detail_url(mapping.pk))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())

    def test_deleting_patient_removes_mappings(self):
        self.assign()
        self.patient.delete()
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)

    def test_deleting_doctor_removes_mappings(self):
        self.assign()
        self.doctor.delete()
        self.assertEqual(PatientDoctorMapping.objects.count(), 0)
