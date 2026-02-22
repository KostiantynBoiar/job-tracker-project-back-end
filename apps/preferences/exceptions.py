from rest_framework.exceptions import APIException
from rest_framework import status


class PreferenceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Preference item not found.'
    default_code = 'preference_not_found'


class PreferenceAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This preference item already exists.'
    default_code = 'preference_exists'
