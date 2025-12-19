from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from auth_app.api.serializers import (
    RegistrationSerializer,
    EmailTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from auth_app.api.signals import user_registered, password_reset_requested


class RegisterView(APIView):
    """
    API view to handle user registration.
    Sends activation email with token upon successful registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token = default_token_generator.make_token(user)

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


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle user login and issue JWT tokens via HttpOnly cookies.
    Accepts email instead of username.
    """
    serializer_class = EmailTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get('access')
        refresh_token = serializer.validated_data.get('refresh')

        user = serializer.user

        if not user.is_active:
            return Response(
                {"detail": "Account not activated"},
                status=status.HTTP_403_FORBIDDEN
            )

        response = Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.email
            }
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Custom view to refresh JWT access token using HttpOnly cookies.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(
            'refresh_token') or request.data.get('refresh')

        if refresh_token is None:
            return Response(
                {"error": "Refresh token not found in cookies."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.get_serializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"error": "Refresh token invalid."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get('access')

        response = Response({
            "detail": "Token refreshed.",
            "access": access_token
        })

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            httponly=True,
            secure=True,
            samesite='Lax'
        )

        return response


class LogoutView(APIView):
    """
    API view to handle user logout.
    Deletes JWT cookies.
    """

    def post(self, request):
        response = Response({
            "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
        }, status=status.HTTP_200_OK)

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class PasswordResetView(APIView):
    """
    API view to handle password reset request.
    Sends password reset email if user exists.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)

                token = default_token_generator.make_token(user)

                password_reset_requested.send(
                    sender=self.__class__,
                    user=user,
                    token=token
                )
            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist for security reasons
                pass

            return Response({
                "detail": "An email has been sent to reset your password."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API view to handle password reset confirmation.
    Validates token and sets new password.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = User.objects.get(pk=uidb64)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    "error": "Invalid reset link."
                }, status=status.HTTP_400_BAD_REQUEST)

            if not default_token_generator.check_token(user, token):
                return Response({
                    "error": "Invalid or expired reset link."
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                "detail": "Your Password has been successfully reset."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
