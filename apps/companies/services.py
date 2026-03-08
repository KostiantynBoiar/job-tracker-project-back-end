from .models import Company
from .serializers import CompanySerializer
from .exceptions import CompanyNotFoundException, CompanyAlreadyExistsException


class CompanyService:
    """
    Service class containing business logic for company operations.
    """

    @staticmethod
    def create_company(data: dict):
        """
        Create a new company.

        Args:
            data: validated_data dict from CompanyCreateSerializer

        Returns:
            dict: Company data

        Raises:
            CompanyAlreadyExistsException: If company with name already exists
        """
        if Company.objects.filter(name__iexact=data['name']).exists():
            raise CompanyAlreadyExistsException()

        company_data = {
            'name': data['name'],
        }
        if data.get('logo_url') is not None:
            company_data['logo_url'] = data['logo_url']
        if data.get('careers_url') is not None:
            company_data['careers_url'] = data['careers_url']
        if data.get('is_active') is not None:
            company_data['is_active'] = data['is_active']

        company = Company.objects.create(**company_data)

        serializer = CompanySerializer(company)
        return serializer.data

    @staticmethod
    def get_company(company_id: int):
        """
        Get company by ID.

        Args:
            company_id: Company ID

        Returns:
            dict: Company data

        Raises:
            CompanyNotFoundException: If company doesn't exist
        """
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise CompanyNotFoundException()

        serializer = CompanySerializer(company)
        return serializer.data

    @staticmethod
    def get_companies_queryset():
        """
        Get companies queryset.

        Returns:
            QuerySet: Companies queryset (for pagination in view)
        """
        return Company.objects.all()

    @staticmethod
    def update_company(company_id: int, data: dict):
        """
        Update company.

        Args:
            company_id: Company ID
            data: validated_data dict from CompanyUpdateSerializer

        Returns:
            dict: Updated company data

        Raises:
            CompanyNotFoundException: If company doesn't exist
        """
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise CompanyNotFoundException()

        updatable_fields = ['name', 'logo_url', 'careers_url', 'is_active']
        for field in updatable_fields:
            if data.get(field) is not None:
                setattr(company, field, data[field])

        company.save()

        serializer = CompanySerializer(company)
        return serializer.data

    @staticmethod
    def delete_company(company_id: int):
        """
        Delete company.

        Args:
            company_id: Company ID

        Returns:
            dict: Success message

        Raises:
            CompanyNotFoundException: If company doesn't exist
        """
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise CompanyNotFoundException()

        company.delete()
        return {'message': 'Company deleted successfully.'}
