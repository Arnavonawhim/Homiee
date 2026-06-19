from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ResidentProfile
from userdetails.serializers import ResidentAddressSerializer

class ResidentAddressView(generics.UpdateAPIView):
    serializer_class = ResidentAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = ResidentProfile.objects.get_or_create(user=self.request.user)
        return profile