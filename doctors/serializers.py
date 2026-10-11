from rest_framework import serializers

from core.validators import validate_phone_number
from doctors.models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "specialization",
            "email",
            "phone",
            "experience_years",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        queryset = Doctor.objects.filter(email__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value

    def validate_phone(self, value):
        return validate_phone_number(value)
