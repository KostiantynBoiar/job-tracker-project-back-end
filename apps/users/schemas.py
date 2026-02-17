from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Dict, Any


class UserRegistrationSchema(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Password fields did not match.')
        return self

    class Config:
        from_attributes = True


# Response schemas
class TokenResponse(BaseModel):
    """Schema for JWT tokens."""
    access: str
    refresh: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Schema for user login response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


# Response schemas
class TokenResponse(BaseModel):
    """Schema for JWT tokens."""
    access: str
    refresh: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Schema for user login response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str

    class Config:
        from_attributes = True


class UserLogoutSchema(BaseModel):
    """Schema for user logout."""
    refresh: str

    class Config:
        from_attributes = True


# Response schemas
class TokenResponse(BaseModel):
    """Schema for JWT tokens."""
    access: str
    refresh: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Schema for user login response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str

    class Config:
        from_attributes = True


class UserProfileUpdateSchema(BaseModel):
    """Schema for user profile update."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


# Response schemas
class TokenResponse(BaseModel):
    """Schema for JWT tokens."""
    access: str
    refresh: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Schema for user login response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str

    class Config:
        from_attributes = True


class UserPasswordChangeSchema(BaseModel):
    """Schema for password change."""
    old_password: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str = Field(..., min_length=8)

    @model_validator(mode='after')
    def passwords_match(self):
        if self.new_password != self.new_password_confirm:
            raise ValueError('Password fields did not match.')
        return self

    class Config:
        from_attributes = True


# Response schemas
class TokenResponse(BaseModel):
    """Schema for JWT tokens."""
    access: str
    refresh: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    date_joined: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserRegistrationResponse(BaseModel):
    """Schema for user registration response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Schema for user login response."""
    user: UserResponse
    tokens: TokenResponse

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message responses."""
    message: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str

    class Config:
        from_attributes = True
