from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .exceptions import InvalidCredentialsException, UserAlreadyExistsException

User = get_user_model()


class UserService:
    """
    Service class containing business logic for user operations.
    """

    @staticmethod
    def register_user(data: dict):
        """
        Register a new user and return user data with JWT tokens.

        Args:
            data: validated_data dict from UserRegistrationSerializer

        Returns:
            dict: User data and tokens

        Raises:
            UserAlreadyExistsException: If user with email already exists
        """
        if User.objects.filter(email=data['email']).exists():
            raise UserAlreadyExistsException()

        user_data = {
            'email': data['email'],
            'password': data['password'],
        }
        if data.get('username'):
            user_data['username'] = data['username']
        if data.get('first_name'):
            user_data['first_name'] = data['first_name']
        if data.get('last_name'):
            user_data['last_name'] = data['last_name']

        user = User.objects.create_user(**user_data)

        refresh = RefreshToken.for_user(user)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

        user_serializer = UserSerializer(user)

        return {
            'user': user_serializer.data,
            'tokens': tokens
        }

    @staticmethod
    def login_user(data: dict):
        """
        Authenticate user and return user data with JWT tokens.

        Args:
            data: validated_data dict from UserLoginSerializer

        Returns:
            dict: User data and tokens

        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        user = authenticate(username=data['email'], password=data['password'])

        if not user:
            raise InvalidCredentialsException()

        refresh = RefreshToken.for_user(user)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

        user_serializer = UserSerializer(user)

        return {
            'user': user_serializer.data,
            'tokens': tokens
        }

    @staticmethod
    def logout_user(data: dict):
        """
        Logout user by blacklisting refresh token.

        Args:
            data: validated_data dict from UserLogoutSerializer

        Returns:
            dict: Success message
        """
        try:
            token = RefreshToken(data['refresh'])
            token.blacklist()
            return {'message': 'Successfully logged out.'}
        except Exception:
            return {'error': 'Invalid token.'}

    @staticmethod
    def get_user_profile(user):
        """
        Get user profile data.

        Args:
            user: User instance

        Returns:
            dict: User data
        """
        serializer = UserSerializer(user)
        return serializer.data

    @staticmethod
    def update_user_profile(user, data: dict):
        """
        Update user profile.

        Args:
            user: User instance
            data: validated_data dict from UserProfileSerializer

        Returns:
            dict: Updated user data
        """
        if data.get('username') is not None:
            user.username = data['username']
        if data.get('first_name') is not None:
            user.first_name = data['first_name']
        if data.get('last_name') is not None:
            user.last_name = data['last_name']

        user.save()

        serializer = UserSerializer(user)
        return serializer.data

    @staticmethod
    def change_user_password(user, data: dict):
        """
        Change user password.

        Args:
            user: User instance
            data: validated_data dict from UserPasswordChangeSerializer

        Returns:
            dict: Success message
        """
        user.set_password(data['new_password'])
        user.save()

        return {'message': 'Password changed successfully.'}
