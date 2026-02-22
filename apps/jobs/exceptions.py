from rest_framework.exceptions import APIException
from rest_framework import status


class JobNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Job not found.'
    default_code = 'job_not_found'


class JobAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Job with this external_id already exists.'
    default_code = 'job_exists'
