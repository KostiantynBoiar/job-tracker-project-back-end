from rest_framework import serializers
from .models import Company, Job, SavedJob


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for company data representation.
    """
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo_url', 'careers_url', 'is_active', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for job creation.
    """
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company',
        write_only=True
    )

    class Meta:
        model = Job
        fields = [
            'company_id', 'external_id', 'title', 'description',
            'location', 'salary_min', 'salary_max', 'external_url',
            'experience_level', 'is_remote', 'posted_at'
        ]


class JobUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for job update.
    """
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'location', 'salary_min', 'salary_max',
            'external_url', 'experience_level', 'is_remote', 'posted_at'
        ]
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'location': {'required': False},
            'salary_min': {'required': False},
            'salary_max': {'required': False},
            'external_url': {'required': False},
            'experience_level': {'required': False},
            'is_remote': {'required': False},
            'posted_at': {'required': False},
        }


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for job data representation.
    Includes nested company information.
    """
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company', 'external_id', 'title', 'description',
            'location', 'salary_min', 'salary_max', 'external_url',
            'experience_level', 'is_remote', 'posted_at', 'scraped_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'scraped_at', 'created_at', 'updated_at']


class SavedJobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for saved job creation.
    """
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        source='job',
        write_only=True
    )

    class Meta:
        model = SavedJob
        fields = ['job_id', 'status', 'notes']
        extra_kwargs = {
            'status': {'required': False},
            'notes': {'required': False},
        }


class SavedJobUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for saved job update.
    """
    class Meta:
        model = SavedJob
        fields = ['status', 'notes']
        extra_kwargs = {
            'status': {'required': False},
            'notes': {'required': False},
        }


class SavedJobSerializer(serializers.ModelSerializer):
    """
    Serializer for saved job data representation.
    Includes nested job information.
    """
    job = JobSerializer(read_only=True)

    class Meta:
        model = SavedJob
        fields = [
            'id', 'job', 'status', 'notes', 'saved_at'
        ]
        read_only_fields = ['id', 'saved_at']

