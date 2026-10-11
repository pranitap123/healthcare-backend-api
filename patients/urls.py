from django.urls import path

from patients.views import PatientDetailView, PatientListCreateView

urlpatterns = [
    path("", PatientListCreateView.as_view(), name="patient-list"),
    path("<int:pk>/", PatientDetailView.as_view(), name="patient-detail"),
]
