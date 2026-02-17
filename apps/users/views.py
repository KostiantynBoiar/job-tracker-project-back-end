from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .services import UserService
from .schemas import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserLogoutSchema,
    UserProfileUpdateSchema,
    UserPasswordChangeSchema,
    UserRegistrationResponse,
    UserLoginResponse,
    MessageResponse,
    ErrorResponse,
    UserResponse,
)
from .exceptions import InvalidCredentialsException, UserAlreadyExistsException


class UserRegistrationView(generics.GenericAPIView):
    """
    Register a new user and return JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegistrationSchema,
        responses={
            201: UserRegistrationResponse,
            400: ErrorResponse,
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
        try:
            schema = UserRegistrationSchema(**request.data)
            result = UserService.register_user(schema)
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
        request=UserLoginSchema,
        responses={
            200: UserLoginResponse,
            400: ErrorResponse,
            401: ErrorResponse,
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
        try:
            schema = UserLoginSchema(**request.data)
            result = UserService.login_user(schema)
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
        request=UserLogoutSchema,
        responses={
            200: MessageResponse,
            400: ErrorResponse,
        },
        examples=[
            OpenApiExample(
                'Logout Request',
                value={'refresh': 'your_refresh_token_here'}
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        try:
            schema = UserLogoutSchema(**request.data)
            result = UserService.logout_user(schema)
            
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            200: UserResponse,
        }
    )
    def get(self, request, *args, **kwargs):
        user_data = UserService.get_user_profile(request.user)
        return Response(user_data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserProfileUpdateSchema,
        responses={
            200: UserResponse,
            400: ErrorResponse,
        }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        request=UserProfileUpdateSchema,
        responses={
            200: UserResponse,
            400: ErrorResponse,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            schema = UserProfileUpdateSchema(**request.data)
            user_data = UserService.update_user_profile(
                user=request.user,
                schema=schema
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
        request=UserPasswordChangeSchema,
        responses={
            200: MessageResponse,
            400: ErrorResponse,
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
        try:
            schema = UserPasswordChangeSchema(**request.data)
            result = UserService.change_user_password(
                user=request.user,
                schema=schema
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
