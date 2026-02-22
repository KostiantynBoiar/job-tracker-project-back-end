from .models import Job
from .serializers import JobSerializer
from .exceptions import JobNotFoundException, JobAlreadyExistsException


class JobService:
    """
    Service class containing business logic for job operations.
    """

    @staticmethod
    def create_job(data: dict):
        """
        Create a new job.

        Args:
            data: validated_data dict from JobCreateSerializer

        Returns:
            dict: Job data

        Raises:
            JobAlreadyExistsException: If job with external_id already exists
        """
        if Job.objects.filter(external_id=data['external_id']).exists():
            raise JobAlreadyExistsException()

        optional_fields = ['description', 'location', 'salary_min', 'salary_max',
                           'experience_level', 'is_remote', 'posted_at']
        job_data = {
            'company': data['company'],
            'external_id': data['external_id'],
            'title': data['title'],
            'external_url': data['external_url'],
            **{k: data[k] for k in optional_fields if data.get(k) is not None},
        }

        job = Job.objects.create(**job_data)

        serializer = JobSerializer(job)
        return serializer.data

    @staticmethod
    def get_job(job_id: int):
        """
        Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            dict: Job data

        Raises:
            JobNotFoundException: If job doesn't exist
        """
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise JobNotFoundException()

        serializer = JobSerializer(job)
        return serializer.data

    @staticmethod
    def list_jobs():
        """
        List all jobs.

        Returns:
            list: List of job data dictionaries
        """
        jobs = Job.objects.select_related('company').all()
        serializer = JobSerializer(jobs, many=True)
        return serializer.data

    @staticmethod
    def update_job(job_id: int, data: dict):
        """
        Update job.

        Args:
            job_id: Job ID
            data: validated_data dict from JobUpdateSerializer

        Returns:
            dict: Updated job data

        Raises:
            JobNotFoundException: If job doesn't exist
        """
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise JobNotFoundException()

        updatable_fields = ['title', 'description', 'location', 'salary_min', 'salary_max',
                            'external_url', 'experience_level', 'is_remote', 'posted_at']
        for field in updatable_fields:
            if data.get(field) is not None:
                setattr(job, field, data[field])

        job.save()

        serializer = JobSerializer(job)
        return serializer.data

    @staticmethod
    def delete_job(job_id: int):
        """
        Delete job.

        Raises:
            JobNotFoundException: If job doesn't exist
        """
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise JobNotFoundException()

        job.delete()
        return {'message': 'Job deleted successfully.'}
