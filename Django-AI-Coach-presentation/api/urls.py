from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from analyzer.views import (
    SessionListView, RegisterView, SessionDetailView, VerifyAuthView,
    CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', VerifyAuthView.as_view(), name='verify_auth'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('sessions/', SessionListView.as_view(), name='session_list'),
    path('sessions/<uuid:uuid>/', SessionDetailView.as_view(), name='session_detail_api'),
    path('register/', RegisterView.as_view(), name='api_register'),
]
