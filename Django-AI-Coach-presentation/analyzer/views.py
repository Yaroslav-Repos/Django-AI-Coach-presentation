# Create your views here.

from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from .models import Session


class SessionSerializer(ModelSerializer):
    class Meta:
        model = Session
        fields = ['uuid', 'id', 'start_time', 'end_time', 'score']
        read_only_fields = ['uuid', 'id']


class SessionListView(generics.ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user).order_by('-start_time')

class SessionDetailView(generics.RetrieveDestroyAPIView):

    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uuid'  

    def get_queryset(self):

        return Session.objects.filter(user=self.request.user)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=username, password=password)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data.get('access')
            refresh = response.data.get('refresh')


            from rest_framework_simplejwt.tokens import AccessToken
            try:
                token = AccessToken(access)
                user_id = token.get('user_id')
                request.session['user_id'] = user_id
            except Exception as e:
                print(f"Warning: Could not set session: {e}")

            response.set_cookie(
                'access_token',
                access,
                max_age=15 * 60,
                httponly=True,
                secure=False,
                samesite='Lax',
                path='/'
            )

            response.set_cookie(
                'refresh_token',
                refresh,
                max_age=7 * 24 * 60 * 60, 
                httponly=True,
                secure=False, 
                samesite='Lax',
                path='/'
            )

            response.data = {'message': 'Login successful'}

        return response


class CustomTokenRefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh_token')

        if refresh:
            if hasattr(request.data, '_mutable'):
                request.data._mutable = True
                request.data['refresh'] = refresh
                request.data._mutable = False
            else:
                request.data.refresh = refresh

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data.get('access')

            from rest_framework_simplejwt.tokens import AccessToken
            try:
                token = AccessToken(access)
                user_id = token.get('user_id')
                request.session['user_id'] = user_id
            except Exception as e:
                print(f"Warning: Could not update session: {e}")

            response.set_cookie(
                'access_token',
                access,
                max_age=15 * 60,
                httponly=True,
                secure=False, 
                samesite='Lax',
                path='/'
            )

            response.data = {'message': 'Token refreshed'}

        return response


class VerifyAuthView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'authenticated': True,
            'user': request.user.username,
            'user_id': request.user.id
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response({'message': 'Logout successful'})
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

class LoginView(TemplateView):

    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return super().get(request, *args, **kwargs)

class SignupPageView(TemplateView):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return super().get(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/login/'
    redirect_field_name = 'next'

class CoachView(LoginRequiredMixin, TemplateView):
    template_name = 'coach.html'
    login_url = '/login/'
    redirect_field_name = 'next'

class SessionReportView(LoginRequiredMixin, TemplateView):
    template_name = 'session_report.html'
    login_url = '/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uuid = self.kwargs['uuid']

        try:
            session = Session.objects.get(uuid=uuid, user=self.request.user)
            context['session_uuid'] = uuid
            context['session'] = session
        except Session.DoesNotExist:
            raise Http404("Session not found")

        return context