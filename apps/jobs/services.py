from .models import Job, SavedJob
from .serializers import JobSerializer, SavedJobSerializer
from .exceptions import (
    JobNotFoundException,
    JobAlreadyExistsException,
    SavedJobNotFoundException,
    SavedJobAlreadyExistsException,
)


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


class SavedJobService:
    """
    Service class containing business logic for saved job operations.
    """

    @staticmethod
    def create_saved_job(user, data: dict):
        """
        Create a new saved job.

        Args:
            user: User instance
            data: validated_data dict from SavedJobCreateSerializer

        Returns:
            dict: Saved job data

        Raises:
            SavedJobAlreadyExistsException: If user already saved this job
        """
        if SavedJob.objects.filter(user=user, job=data['job']).exists():
            raise SavedJobAlreadyExistsException()

        saved_job_data = {
            'user': user,
            'job': data['job'],
            'status': data.get('status', 'active'),
        }
        if data.get('notes') is not None:
            saved_job_data['notes'] = data['notes']

        saved_job = SavedJob.objects.create(**saved_job_data)

        serializer = SavedJobSerializer(saved_job)
        return serializer.data

    @staticmethod
    def get_saved_job(user, saved_job_id: int):
        """
        Get saved job by ID.

        Args:
            user: User instance
            saved_job_id: Saved job ID

        Returns:
            dict: Saved job data

        Raises:
            SavedJobNotFoundException: If saved job doesn't exist or doesn't belong to user
        """
        try:
            saved_job = SavedJob.objects.get(id=saved_job_id, user=user)
        except SavedJob.DoesNotExist:
            raise SavedJobNotFoundException()

        serializer = SavedJobSerializer(saved_job)
        return serializer.data

    @staticmethod
    def list_saved_jobs(user):
        """
        List all saved jobs for the authenticated user.

        Args:
            user: User instance

        Returns:
            list: List of saved job data dictionaries
        """
        saved_jobs = SavedJob.objects.filter(user=user).select_related('job', 'job__company').all()
        serializer = SavedJobSerializer(saved_jobs, many=True)
        return serializer.data

    @staticmethod
    def update_saved_job(user, saved_job_id: int, data: dict):
        """
        Update saved job.

        Args:
            user: User instance
            saved_job_id: Saved job ID
            data: validated_data dict from SavedJobUpdateSerializer

        Returns:
            dict: Updated saved job data

        Raises:
            SavedJobNotFoundException: If saved job doesn't exist or doesn't belong to user
        """
        try:
            saved_job = SavedJob.objects.get(id=saved_job_id, user=user)
        except SavedJob.DoesNotExist:
            raise SavedJobNotFoundException()

        updatable_fields = ['status', 'notes']
        for field in updatable_fields:
            if data.get(field) is not None:
                setattr(saved_job, field, data[field])

        saved_job.save()

        serializer = SavedJobSerializer(saved_job)
        return serializer.data

    @staticmethod
    def delete_saved_job(user, saved_job_id: int):
        """
        Delete saved job.

        Args:
            user: User instance
            saved_job_id: Saved job ID

        Returns:
            dict: Success message

        Raises:
            SavedJobNotFoundException: If saved job doesn't exist or doesn't belong to user
        """
        try:
            saved_job = SavedJob.objects.get(id=saved_job_id, user=user)
        except SavedJob.DoesNotExist:
            raise SavedJobNotFoundException()

        saved_job.delete()
        return {'message': 'Saved job deleted successfully.'}
