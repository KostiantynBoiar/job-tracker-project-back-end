from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
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
from .exceptions import (
    JobNotFoundException,
    JobAlreadyExistsException,
    SavedJobNotFoundException,
    SavedJobAlreadyExistsException,
)


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


class SavedJobListView(generics.GenericAPIView):
    """
    List all saved jobs for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: SavedJobSerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        saved_jobs = SavedJobService.list_saved_jobs(request.user)
        return Response(saved_jobs, status=status.HTTP_200_OK)


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
