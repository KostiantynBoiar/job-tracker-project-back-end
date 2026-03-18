from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from .services import JobService, SavedJobService
from .serializers import (
    JobSerializer,
    JobCreateSerializer,
    JobUpdateSerializer,
    SavedJobSerializer,
    SavedJobCreateSerializer,
    SavedJobUpdateSerializer,
)
from apps.common_serializers import MessageSerializer, ErrorSerializer
from apps.common_pagination import StandardPagination
from .exceptions import (
    JobNotFoundException,
    JobAlreadyExistsException,
    SavedJobNotFoundException,
    SavedJobAlreadyExistsException,
)
from .filters import JobFilter
from apps.companies.models import Company


class JobCreateView(generics.GenericAPIView):
    """
    Create a new job posting.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=JobCreateSerializer,
        responses={
            201: JobSerializer,
            400: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Job Creation Request',
                value={
                    'company_id': 1,
                    'external_id': 'job-12345',
                    'title': 'Senior Software Engineer',
                    'description': 'We are looking for an experienced software engineer...',
                    'location': 'San Francisco, CA',
                    'salary_min': 120000.00,
                    'salary_max': 180000.00,
                    'external_url': 'https://example.com/jobs/12345',
                    'experience_level': 'senior',
                    'is_remote': True,
                    'posted_at': '2024-01-15T10:00:00Z'
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = JobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = JobService.create_job(serializer.validated_data)
            return Response(result, status=status.HTTP_201_CREATED)
        except JobAlreadyExistsException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobListView(generics.ListAPIView):
    """
    List all job postings with pagination and filtering.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='sort_by',
                type=OpenApiTypes.STR,
                enum=['preference', 'date', 'salary', 'company'],
                default='date',
                description='Sort jobs by: preference, date, salary, or company name.',
            ),
            OpenApiParameter(
                name='order',
                type=OpenApiTypes.STR,
                enum=['asc', 'desc'],
                default='desc',
                description='Sort direction.',
            ),
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
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search in job title, company name, and location',
            ),
            OpenApiParameter(
                name='company',
                type=OpenApiTypes.INT,
                description='Filter by company ID',
            ),
            OpenApiParameter(
                name='company_in',
                type=OpenApiTypes.STR,
                description='Filter by multiple company IDs (comma-separated)',
            ),
            OpenApiParameter(
                name='employment_type',
                type=OpenApiTypes.STR,
                enum=['full_time', 'part_time', 'contract', 'freelance', 'internship'],
                description='Filter by employment type',
            ),
            OpenApiParameter(
                name='employment_type_in',
                type=OpenApiTypes.STR,
                description='Filter by multiple employment types (comma-separated)',
            ),
            OpenApiParameter(
                name='experience_level',
                type=OpenApiTypes.STR,
                enum=['entry', 'mid', 'senior', 'executive'],
                description='Filter by experience level',
            ),
            OpenApiParameter(
                name='experience_level_in',
                type=OpenApiTypes.STR,
                description='Filter by multiple experience levels (comma-separated)',
            ),
            OpenApiParameter(
                name='is_remote',
                type=OpenApiTypes.BOOL,
                description='Filter remote jobs only',
            ),
            OpenApiParameter(
                name='salary_min',
                type=OpenApiTypes.NUMBER,
                description='Minimum salary filter',
            ),
            OpenApiParameter(
                name='salary_max',
                type=OpenApiTypes.NUMBER,
                description='Maximum salary filter',
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        sort_by = self.request.query_params.get('sort_by', 'date')
        order = self.request.query_params.get('order', 'desc')
        return JobService.get_jobs_queryset(sort_by=sort_by, order=order, user=self.request.user)


class JobDetailView(generics.GenericAPIView):
    """
    Retrieve a specific job posting by ID.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: JobSerializer,
            404: ErrorSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            job_id = kwargs.get('pk')
            job_data = JobService.get_job(job_id)
            return Response(job_data, status=status.HTTP_200_OK)
        except JobNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobUpdateView(generics.GenericAPIView):
    """
    Update a job posting.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=JobUpdateSerializer,
        responses={
            200: JobSerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Job Update Request',
                value={
                    'title': 'Updated Job Title',
                    'description': 'Updated description',
                    'salary_max': 200000.00,
                    'is_remote': False
                }
            )
        ]
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        request=JobUpdateSerializer,
        responses={
            200: JobSerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = JobUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            job_id = kwargs.get('pk')
            job_data = JobService.update_job(job_id, serializer.validated_data)
            return Response(job_data, status=status.HTTP_200_OK)
        except JobNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobDeleteView(generics.GenericAPIView):
    """
    Delete a job posting.
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
            job_id = kwargs.get('pk')
            result = JobService.delete_job(job_id)
            return Response(result, status=status.HTTP_200_OK)
        except JobNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SavedJobCreateView(generics.GenericAPIView):
    """
    Create a new saved job.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SavedJobCreateSerializer,
        responses={
            201: SavedJobSerializer,
            400: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Saved Job Creation Request',
                value={
                    'job_id': 1,
                    'status': 'active',
                    'notes': 'Interested in this position'
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        serializer = SavedJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = SavedJobService.create_saved_job(request.user, serializer.validated_data)
            return Response(result, status=status.HTTP_201_CREATED)
        except SavedJobAlreadyExistsException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SavedJobListView(generics.ListAPIView):
    """
    List all saved jobs for the authenticated user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SavedJobSerializer
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
        return SavedJobService.get_saved_jobs_queryset(self.request.user)


class SavedJobDetailView(generics.GenericAPIView):
    """
    Retrieve a specific saved job by ID.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: SavedJobSerializer,
            404: ErrorSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            saved_job_id = kwargs.get('pk')
            saved_job_data = SavedJobService.get_saved_job(request.user, saved_job_id)
            return Response(saved_job_data, status=status.HTTP_200_OK)
        except SavedJobNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SavedJobUpdateView(generics.GenericAPIView):
    """
    Update a saved job.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SavedJobUpdateSerializer,
        responses={
            200: SavedJobSerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
        },
        examples=[
            OpenApiExample(
                'Saved Job Update Request',
                value={
                    'status': 'expired',
                    'notes': 'Job posting has expired'
                }
            )
        ]
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        request=SavedJobUpdateSerializer,
        responses={
            200: SavedJobSerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = SavedJobUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            saved_job_id = kwargs.get('pk')
            saved_job_data = SavedJobService.update_saved_job(
                request.user,
                saved_job_id,
                serializer.validated_data
            )
            return Response(saved_job_data, status=status.HTTP_200_OK)
        except SavedJobNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SavedJobDeleteView(generics.GenericAPIView):
    """
    Delete a saved job.
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
            saved_job_id = kwargs.get('pk')
            result = SavedJobService.delete_saved_job(request.user, saved_job_id)
            return Response(result, status=status.HTTP_200_OK)
        except SavedJobNotFoundException:
            raise
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobCompaniesView(generics.GenericAPIView):
    """
    Get all companies that have job postings.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'logo_url': {'type': 'string', 'nullable': True},
                        'jobs_count': {'type': 'integer'},
                    }
                }
            }
        }
    )
    def get(self, request, *args, **kwargs):
        companies = Company.objects.filter(
            jobs__isnull=False
        ).annotate(
            jobs_count=Count('jobs')
        ).values(
            'id', 'name', 'logo_url', 'jobs_count'
        ).order_by('name').distinct()
        
        return Response(list(companies), status=status.HTTP_200_OK)
