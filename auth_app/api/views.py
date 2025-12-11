from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.serializers import RegistrationSerializer, LoginSerializer
from auth_app.api.signals import user_registered


class RegisterView(APIView):
    """
    API view to handle user registration.
    Sends activation email with token upon successful registration.
    """
    permission_classes = [AllowAny]

    # Post method to register user
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Generate token
            token = default_token_generator.make_token(user)

            # Send custom signal with token to trigger email
            user_registered.send(
                sender=self.__class__,
                user=user,
                token=token
            )

            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "token": token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    """
    API view to handle account activation via token.
    """
    permission_classes = [AllowAny]

    # Get method to activate account
    def get(self, request, uidb64, token):
        try:
            user = User.objects.get(pk=uidb64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view to handle user login.
    Issues JWT tokens upon successful authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(request, username=user.username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active:
            return Response(
                {"detail": "Account not activated"},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        response = Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.email
            }
        }, status=status.HTTP_200_OK)

        # Set HttpOnly cookies
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response
