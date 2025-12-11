from django.urls import path

from .views import (
    LogoutView,
    RegisterView,
    ActivateAccountView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
