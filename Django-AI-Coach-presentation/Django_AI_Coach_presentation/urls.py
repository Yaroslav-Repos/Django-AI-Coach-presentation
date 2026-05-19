"""
Definition of urls for Django_AI_Coach_presentation.
"""

from django.urls import path, include
from analyzer.views import LoginView, DashboardView, CoachView, SignupPageView, SessionReportView

urlpatterns = [
    path('api/', include('api.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', SignupPageView.as_view(), name='register_page'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('coach/', CoachView.as_view(), name='coach'),
    path('session/<uuid:uuid>/', SessionReportView.as_view(), name='session_detail'),
]
