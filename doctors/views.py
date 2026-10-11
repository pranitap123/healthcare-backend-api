from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsCreatorOrReadOnly
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = Doctor.objects.all()
        specialization = self.request.query_params.get("specialization")
        if specialization:
            queryset = queryset.filter(specialization__iexact=specialization)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]
