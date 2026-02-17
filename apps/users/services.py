from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .exceptions import InvalidCredentialsException, UserAlreadyExistsException
from .schemas import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserLogoutSchema,
    UserProfileUpdateSchema,
    UserPasswordChangeSchema,
)

User = get_user_model()


class UserService:
    """
    Service class containing business logic for user operations.
    """

    @staticmethod
    def register_user(schema: UserRegistrationSchema):
        """
        Register a new user and return user data with JWT tokens.
        
        Args:
            schema: UserRegistrationSchema with user data
            
        Returns:
            dict: User data and tokens
            
        Raises:
            UserAlreadyExistsException: If user with email already exists
        """
        if User.objects.filter(email=schema.email).exists():
            raise UserAlreadyExistsException()
        
        user_data = {
            'email': schema.email,
            'password': schema.password,
        }
        if schema.username:
            user_data['username'] = schema.username
        if schema.first_name:
            user_data['first_name'] = schema.first_name
        if schema.last_name:
            user_data['last_name'] = schema.last_name
        
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
    def login_user(schema: UserLoginSchema):
        """
        Authenticate user and return user data with JWT tokens.
        
        Args:
            schema: UserLoginSchema with email and password
            
        Returns:
            dict: User data and tokens
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        if not schema.email or not schema.password:
            raise ValueError("Email and password are required.")
        
        user = authenticate(username=schema.email, password=schema.password)
        
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
    def logout_user(schema: UserLogoutSchema):
        """
        Logout user by blacklisting refresh token.
        
        Args:
            schema: UserLogoutSchema with refresh token
            
        Returns:
            dict: Success message
        """
        try:
            if schema.refresh:
                token = RefreshToken(schema.refresh)
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
    def update_user_profile(user, schema: UserProfileUpdateSchema):
        """
        Update user profile.
        
        Args:
            user: User instance
            schema: UserProfileUpdateSchema with update data
            
        Returns:
            dict: Updated user data
        """
        if schema.username is not None:
            user.username = schema.username
        if schema.first_name is not None:
            user.first_name = schema.first_name
        if schema.last_name is not None:
            user.last_name = schema.last_name
        
        user.save()
        
        serializer = UserSerializer(user)
        return serializer.data

    @staticmethod
    def change_user_password(user, schema: UserPasswordChangeSchema):
        """
        Change user password.
        
        Args:
            user: User instance
            schema: UserPasswordChangeSchema with password data
            
        Returns:
            dict: Success message
            
        Raises:
            ValueError: If old password is incorrect
        """
        if not user.check_password(schema.old_password):
            raise ValueError("Old password is incorrect.")
        
        user.set_password(schema.new_password)
        user.save()
        
        return {'message': 'Password changed successfully.'}
