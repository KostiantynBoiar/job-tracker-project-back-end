from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model

from .models import AuthProvider

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.auth_provider = AuthProvider.EMAIL.value
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            return

        email = sociallogin.account.extra_data.get('email')
        if not email and sociallogin.user:
            email = sociallogin.user.email

        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        user.auth_provider = self._get_auth_provider(provider)
        user.provider_id = sociallogin.account.uid
        self._populate_user_data(user, provider, extra_data)
        user.save()

        return user

    def _get_auth_provider(self, provider):
        provider_map = {
            'google': AuthProvider.GOOGLE.value,
            'github': AuthProvider.GITHUB.value,
        }
        return provider_map.get(provider, AuthProvider.EMAIL.value)

    def _populate_user_data(self, user, provider, extra_data):
        if provider == 'google':
            self._populate_google_data(user, extra_data)
        elif provider == 'github':
            self._populate_github_data(user, extra_data)

    def _populate_google_data(self, user, extra_data):
        if not user.first_name:
            user.first_name = extra_data.get('given_name', '')
        if not user.last_name:
            user.last_name = extra_data.get('family_name', '')

    def _populate_github_data(self, user, extra_data):
        if not user.first_name and extra_data.get('name'):
            name_parts = extra_data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        if not user.username and extra_data.get('login'):
            user.username = extra_data['login']

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        if not user.username:
            user.username = self._generate_unique_username(data.get('email', ''))

        return user

    def _generate_unique_username(self, email):
        if not email:
            return ''

        base_username = email.split('@')[0]
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def get_connect_redirect_url(self, request, socialaccount):
        from django.conf import settings
        return getattr(settings, 'FRONTEND_URL', '/')
