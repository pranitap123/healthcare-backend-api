from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from mappings.models import PatientDoctorMapping
from mappings.serializers import AssignedDoctorSerializer, MappingSerializer
from patients.models import Patient


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer

    def get_queryset(self):
        queryset = PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")
        patient_id = self.request.query_params.get("patient")
        doctor_id = self.request.query_params.get("doctor")
        if patient_id and patient_id.isdigit():
            queryset = queryset.filter(patient_id=patient_id)
        if doctor_id and doctor_id.isdigit():
            queryset = queryset.filter(doctor_id=doctor_id)
        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(assigned_by=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"non_field_errors": ["This doctor is already assigned to the patient."]}
            )


class MappingDetailView(APIView):
    @extend_schema(responses=AssignedDoctorSerializer(many=True))
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = (
            PatientDoctorMapping.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-created_at", "-id")
        )
        return Response(AssignedDoctorSerializer(mappings, many=True).data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        mapping = get_object_or_404(
            PatientDoctorMapping, pk=pk, patient__created_by=request.user
        )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
