from rest_framework import generics

from patients.models import Patient
from patients.serializers import PatientSerializer


class PatientQuerysetMixin:
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)


class PatientListCreateView(PatientQuerysetMixin, generics.ListCreateAPIView):
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(PatientQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    pass
