from rest_framework.generics import CreateAPIView
from .serializers import CustomUserSerializer


class RegisterView(CreateAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
