import requests
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthProvider
from .serializers import UserSerializer
from .exceptions import InvalidCredentialsException, UserAlreadyExistsException, OAuthException

User = get_user_model()


class UserService:
    @staticmethod
    def _generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

    @staticmethod
    def _build_auth_response(user):
        return {
            'user': UserSerializer(user).data,
            'tokens': UserService._generate_tokens(user)
        }

    @staticmethod
    def register_user(data: dict):
        if User.objects.filter(email=data['email']).exists():
            raise UserAlreadyExistsException()

        user_data = {'email': data['email'], 'password': data['password']}
        for field in ['username', 'first_name', 'last_name']:
            if data.get(field):
                user_data[field] = data[field]

        user = User.objects.create_user(**user_data)
        return UserService._build_auth_response(user)

    @staticmethod
    def login_user(data: dict):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise InvalidCredentialsException()
        return UserService._build_auth_response(user)

    @staticmethod
    def logout_user(data: dict):
        try:
            token = RefreshToken(data['refresh'])
            token.blacklist()
            return {'message': 'Successfully logged out.'}
        except Exception:
            return {'error': 'Invalid token.'}

    @staticmethod
    def get_user_profile(user):
        return UserSerializer(user).data

    @staticmethod
    def update_user_profile(user, data: dict):
        for field in ['username', 'first_name', 'last_name']:
            if data.get(field) is not None:
                setattr(user, field, data[field])
        user.save()
        return UserSerializer(user).data

    @staticmethod
    def change_user_password(user, data: dict):
        user.set_password(data['new_password'])
        user.save()
        return {'message': 'Password changed successfully.'}

    @staticmethod
    def oauth_google_callback(request, code: str):
        callback_url = request.build_absolute_uri('/api/users/oauth/google/callback/')
        google_settings = settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {})

        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': google_settings.get('client_id'),
                'client_secret': google_settings.get('secret'),
                'redirect_uri': callback_url,
                'grant_type': 'authorization_code',
            },
            timeout=10
        )

        if token_response.status_code != 200:
            raise OAuthException('Failed to exchange code for token')

        access_token = token_response.json().get('access_token')
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )

        if user_response.status_code != 200:
            raise OAuthException('Failed to fetch user info')

        user_info = user_response.json()
        return UserService._oauth_get_or_create_user(
            email=user_info.get('email'),
            provider=AuthProvider.GOOGLE.value,
            provider_id=user_info.get('id'),
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', '')
        )

    @staticmethod
    def oauth_github_callback(request, code: str):
        callback_url = request.build_absolute_uri('/api/users/oauth/github/callback/')
        github_settings = settings.SOCIALACCOUNT_PROVIDERS.get('github', {}).get('APP', {})

        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'code': code,
                'client_id': github_settings.get('client_id'),
                'client_secret': github_settings.get('secret'),
                'redirect_uri': callback_url,
            },
            headers={'Accept': 'application/json'},
            timeout=10
        )

        if token_response.status_code != 200:
            raise OAuthException('Failed to exchange code for token')

        access_token = token_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}

        user_response = requests.get(
            'https://api.github.com/user',
            headers=headers,
            timeout=10
        )

        if user_response.status_code != 200:
            raise OAuthException('Failed to fetch user info')

        user_info = user_response.json()
        email = user_info.get('email')

        if not email:
            email = UserService._fetch_github_primary_email(headers)

        first_name, last_name = '', ''
        if user_info.get('name'):
            name_parts = user_info['name'].split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

        return UserService._oauth_get_or_create_user(
            email=email,
            provider=AuthProvider.GITHUB.value,
            provider_id=str(user_info.get('id')),
            first_name=first_name,
            last_name=last_name,
            username=user_info.get('login')
        )

    @staticmethod
    def _fetch_github_primary_email(headers):
        emails_response = requests.get(
            'https://api.github.com/user/emails',
            headers=headers,
            timeout=10
        )

        if emails_response.status_code != 200:
            raise OAuthException('Failed to fetch user email')

        for email_data in emails_response.json():
            if email_data.get('primary') and email_data.get('verified'):
                return email_data.get('email')

        raise OAuthException('No verified primary email found')

    @staticmethod
    def _oauth_get_or_create_user(email, provider, provider_id, first_name='', last_name='', username=None):
        if not email:
            raise OAuthException('Email is required')

        user = User.objects.filter(email=email).first()

        if user:
            if not user.provider_id:
                user.auth_provider = provider
                user.provider_id = provider_id
                user.save()
            return UserService._build_auth_response(user)

        if not username:
            username = UserService._generate_unique_username(email)

        user = User.objects.create(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            auth_provider=provider,
            provider_id=provider_id
        )
        user.set_unusable_password()
        user.save()

        return UserService._build_auth_response(user)

    @staticmethod
    def _generate_unique_username(email):
        base_username = email.split('@')[0]
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username
