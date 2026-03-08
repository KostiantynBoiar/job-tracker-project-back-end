from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .services import CompanyService
from .serializers import (
    CompanySerializer,
    CompanyCreateSerializer,
    CompanyUpdateSerializer,
)
from apps.common_serializers import MessageSerializer, ErrorSerializer
from apps.common_pagination import StandardPagination
from .exceptions import CompanyNotFoundException, CompanyAlreadyExistsException


class CompanyCreateView(generics.GenericAPIView):
    """
    Create a new company.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CompanyCreateSerializer,
        responses={
            201: CompanySerializer,
            400: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Company Creation Request',
                value={
                    'name': 'Acme Corporation',
                    'logo_url': 'https://example.com/logo.png',
                    'careers_url': 'https://example.com/careers',
                    'is_active': True
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = CompanyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = CompanyService.create_company(serializer.validated_data)
            return Response(result, status=status.HTTP_201_CREATED)
        except CompanyAlreadyExistsException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompanyListView(generics.ListAPIView):
    """
    List all companies with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    pagination_class = StandardPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                description='Page number (default: 1)',
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description='Number of items per page (default: 20, max: 100)',
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return CompanyService.get_companies_queryset()


class CompanyDetailView(generics.GenericAPIView):
    """
    Retrieve a specific company by ID.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: CompanySerializer,
            404: ErrorSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            company_id = kwargs.get('pk')
            company_data = CompanyService.get_company(company_id)
            return Response(company_data, status=status.HTTP_200_OK)
        except CompanyNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompanyUpdateView(generics.GenericAPIView):
    """
    Update a company.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CompanyUpdateSerializer,
        responses={
            200: CompanySerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Company Update Request',
                value={
                    'name': 'Updated Company Name',
                    'logo_url': 'https://example.com/new-logo.png',
                    'is_active': False
                }
            )
        ]
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        request=CompanyUpdateSerializer,
        responses={
            200: CompanySerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = CompanyUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            company_id = kwargs.get('pk')
            company_data = CompanyService.update_company(company_id, serializer.validated_data)
            return Response(company_data, status=status.HTTP_200_OK)
        except CompanyNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompanyDeleteView(generics.GenericAPIView):
    """
    Delete a company.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: MessageSerializer,
            404: ErrorSerializer,
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            company_id = kwargs.get('pk')
            result = CompanyService.delete_company(company_id)
            return Response(result, status=status.HTTP_200_OK)
        except CompanyNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
