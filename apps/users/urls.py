from django.urls import path

from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    CustomTokenRefreshView,
    UserProfileView,
    UserPasswordChangeView,
    GoogleLoginView,
    GitHubLoginView,
    GoogleCallbackView,
    GitHubCallbackView,
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('me/change-password/', UserPasswordChangeView.as_view(), name='change_password'),

    path('oauth/google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('oauth/google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
    path('oauth/github/login/', GitHubLoginView.as_view(), name='github_login'),
    path('oauth/github/callback/', GitHubCallbackView.as_view(), name='github_callback'),
]
