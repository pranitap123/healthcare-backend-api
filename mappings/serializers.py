from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from mappings.models import PatientDoctorMapping
from patients.models import Patient


class MappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.none())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "assigned_by",
            "created_at",
        )
        read_only_fields = ("id", "assigned_by", "created_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            self.fields["patient"].queryset = Patient.objects.filter(created_by=request.user)

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(
            patient=attrs["patient"], doctor=attrs["doctor"]
        ).exists():
            raise serializers.ValidationError(
                {"non_field_errors": ["This doctor is already assigned to the patient."]}
            )
        return attrs


class AssignedDoctorSerializer(serializers.ModelSerializer):
    mapping_id = serializers.IntegerField(source="id", read_only=True)
    assigned_at = serializers.DateTimeField(source="created_at", read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("mapping_id", "assigned_at", "doctor")
        read_only_fields = fields
