from rest_framework.exceptions import APIException
from rest_framework import status


class CompanyNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Company not found.'
    default_code = 'company_not_found'


class CompanyAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Company with this name already exists.'
    default_code = 'company_exists'
