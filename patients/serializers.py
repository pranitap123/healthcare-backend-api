from rest_framework import serializers

from core.validators import validate_phone_number
from patients.models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "age",
            "gender",
            "phone",
            "address",
            "medical_history",
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

    def validate_phone(self, value):
        return validate_phone_number(value)
