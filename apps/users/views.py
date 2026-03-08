from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample

from .services import UserService
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserPasswordChangeSerializer,
    UserSerializer,
    UserAuthResponseSerializer,
    OAuthURLSerializer,
)
from apps.common_serializers import MessageSerializer, ErrorSerializer
from .exceptions import InvalidCredentialsException, UserAlreadyExistsException


class UserRegistrationView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserAuthResponseSerializer, 400: ErrorSerializer},
        examples=[
            OpenApiExample(
                'Registration Request',
                value={
                    'email': 'user@example.com',
                    'password': 'securepassword123',
                    'password_confirm': 'securepassword123',
                    'username': 'johndoe',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = UserService.register_user(serializer.validated_data)
            return Response(result, status=status.HTTP_201_CREATED)
        except UserAlreadyExistsException:
            raise


class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserAuthResponseSerializer, 401: ErrorSerializer},
        examples=[
            OpenApiExample(
                'Login Request',
                value={'email': 'user@example.com', 'password': 'securepassword123'}
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = UserService.login_user(serializer.validated_data)
            return Response(result, status=status.HTTP_200_OK)
        except InvalidCredentialsException:
            raise


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserLogoutSerializer,
        responses={200: MessageSerializer, 400: ErrorSerializer},
        examples=[OpenApiExample('Logout Request', value={'refresh': 'your_refresh_token_here'})]
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = UserService.logout_user(serializer.validated_data)
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request, *args, **kwargs):
        return Response(UserService.get_user_profile(request.user), status=status.HTTP_200_OK)

    @extend_schema(request=UserProfileSerializer, responses={200: UserSerializer, 400: ErrorSerializer})
    def put(self, request, *args, **kwargs):
        return self._update(request)

    @extend_schema(request=UserProfileSerializer, responses={200: UserSerializer, 400: ErrorSerializer})
    def patch(self, request, *args, **kwargs):
        return self._update(request)

    def _update(self, request):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = UserService.update_user_profile(request.user, serializer.validated_data)
        return Response(user_data, status=status.HTTP_200_OK)


class UserPasswordChangeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserPasswordChangeSerializer,
        responses={200: MessageSerializer, 400: ErrorSerializer},
        examples=[
            OpenApiExample(
                'Password Change Request',
                value={
                    'old_password': 'oldpassword123',
                    'new_password': 'newpassword123',
                    'new_password_confirm': 'newpassword123'
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = UserPasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = UserService.change_user_password(request.user, serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OAuthURLSerializer})
    def get(self, request, *args, **kwargs):
        callback_url = request.build_absolute_uri('/api/users/oauth/google/callback/')
        google_settings = settings.SOCIALACCOUNT_PROVIDERS.get('google', {})
        client_id = google_settings.get('APP', {}).get('client_id', '')

        if not client_id:
            return Response({'error': 'Google OAuth is not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        params = {
            'client_id': client_id,
            'redirect_uri': callback_url,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'online',
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return Response({'authorization_url': auth_url})


class GitHubLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OAuthURLSerializer})
    def get(self, request, *args, **kwargs):
        callback_url = request.build_absolute_uri('/api/users/oauth/github/callback/')
        github_settings = settings.SOCIALACCOUNT_PROVIDERS.get('github', {})
        client_id = github_settings.get('APP', {}).get('client_id', '')

        if not client_id:
            return Response({'error': 'GitHub OAuth is not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        params = {
            'client_id': client_id,
            'redirect_uri': callback_url,
            'scope': 'user:email read:user',
        }
        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
        return Response({'authorization_url': auth_url})


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        error = request.query_params.get('error')
        frontend_url = settings.FRONTEND_URL

        if error:
            return redirect(f"{frontend_url}/auth/callback?error={error}")

        if not code:
            return redirect(f"{frontend_url}/auth/callback?error=no_code")

        try:
            result = UserService.oauth_google_callback(request, code)
            params = urlencode({
                'access': result['tokens']['access'],
                'refresh': result['tokens']['refresh'],
            })
            return redirect(f"{frontend_url}/auth/callback?{params}")
        except Exception as e:
            return redirect(f"{frontend_url}/auth/callback?error={str(e)}")


class GitHubCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        error = request.query_params.get('error')
        frontend_url = settings.FRONTEND_URL

        if error:
            return redirect(f"{frontend_url}/auth/callback?error={error}")

        if not code:
            return redirect(f"{frontend_url}/auth/callback?error=no_code")

        try:
            result = UserService.oauth_github_callback(request, code)
            params = urlencode({
                'access': result['tokens']['access'],
                'refresh': result['tokens']['refresh'],
            })
            return redirect(f"{frontend_url}/auth/callback?{params}")
        except Exception as e:
            return redirect(f"{frontend_url}/auth/callback?error={str(e)}")
