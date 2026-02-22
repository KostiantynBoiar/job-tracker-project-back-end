from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from .services import JobService
from .serializers import JobSerializer, JobCreateSerializer, JobUpdateSerializer
from apps.common_serializers import MessageSerializer, ErrorSerializer
from .exceptions import JobNotFoundException, JobAlreadyExistsException


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


class JobListView(generics.GenericAPIView):
    """
    List all job postings.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: JobSerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        jobs = JobService.list_jobs()
        return Response(jobs, status=status.HTTP_200_OK)


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
