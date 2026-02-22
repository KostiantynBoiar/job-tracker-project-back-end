from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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
)
from apps.common_serializers import MessageSerializer, ErrorSerializer
from .exceptions import InvalidCredentialsException, UserAlreadyExistsException


class UserRegistrationView(generics.GenericAPIView):
    """
    Register a new user and return JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: UserAuthResponseSerializer,
            400: ErrorSerializer,
        },
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
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    """
    Authenticate user and return JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: UserAuthResponseSerializer,
            400: ErrorSerializer,
            401: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'email': 'user@example.com',
                    'password': 'securepassword123'
                }
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
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(generics.GenericAPIView):
    """
    Logout user by blacklisting refresh token.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserLogoutSerializer,
        responses={
            200: MessageSerializer,
            400: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Logout Request',
                value={'refresh': 'your_refresh_token_here'}
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = UserService.logout_user(serializer.validated_data)
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /api/users/token/refresh/
    Refresh access token using refresh token.
    """
    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: UserSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        user_data = UserService.get_user_profile(request.user)
        return Response(user_data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: UserSerializer,
            400: ErrorSerializer,
        }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: UserSerializer,
            400: ErrorSerializer,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_data = UserService.update_user_profile(
                user=request.user,
                data=serializer.validated_data
            )
            return Response(user_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordChangeView(generics.GenericAPIView):
    """
    Change user password.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserPasswordChangeSerializer,
        responses={
            200: MessageSerializer,
            400: ErrorSerializer,
        },
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
        serializer = UserPasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        try:
            result = UserService.change_user_password(
                user=request.user,
                data=serializer.validated_data
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
