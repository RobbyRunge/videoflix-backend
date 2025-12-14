from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.serializers import RegistrationSerializer, LoginSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from auth_app.api.signals import user_registered, password_reset_requested


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


class CookieTokenObtainPairView(APIView):
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


class CookieTokenRefreshView(APIView):
    """
    API view to handle JWT token refresh.
    Issues new access and refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)

            response = Response({
                "detail": "Token refreshed",
                "access_token": new_access_token,
            }, status=status.HTTP_200_OK)

            # Update cookies
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=new_refresh_token,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            return response

        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    API view to handle user logout.
    Deletes JWT cookies.
    """

    def post(self, request):
        if not RefreshToken:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response({
            "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
        }, status=status.HTTP_200_OK)

        # Delete cookies
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

                # Generate token
                token = default_token_generator.make_token(user)

                # Send custom signal with token to trigger email
                password_reset_requested.send(
                    sender=self.__class__,
                    user=user,
                    token=token
                )
            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist for security reasons
                pass

            # Always return success to prevent email enumeration
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

            # Validate token
            if not default_token_generator.check_token(user, token):
                return Response({
                    "error": "Invalid or expired reset link."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({
                "detail": "Your Password has been successfully reset."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
