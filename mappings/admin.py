from django.contrib import admin

from mappings.models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "assigned_by", "created_at")
    search_fields = ("patient__name", "doctor__name")
    raw_id_fields = ("patient", "doctor", "assigned_by")
