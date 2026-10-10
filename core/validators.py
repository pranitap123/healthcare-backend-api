import re

from rest_framework import serializers

PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s\-()]{6,18}$")


def validate_phone_number(value):
    value = value.strip()
    if value and not PHONE_PATTERN.match(value):
        raise serializers.ValidationError("Enter a valid phone number.")
    return value
