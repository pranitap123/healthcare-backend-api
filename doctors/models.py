from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

from core.models import TimeStampedModel


class Doctor(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctors",
    )
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    experience_years = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(80)]
    )

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name
