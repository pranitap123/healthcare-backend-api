from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

from core.models import TimeStampedModel


class Patient(TimeStampedModel):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField(validators=[MaxValueValidator(150)])
    gender = models.CharField(max_length=10, choices=Gender.choices)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["created_by", "-created_at"])]

    def __str__(self):
        return self.name
