from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status


from auth_app.api.serializers import RegistrationSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            activation_token = default_token_generator.make_token(user)

            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "uidb64": uidb64,
                "token": activation_token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)
