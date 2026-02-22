from rest_framework import serializers
from .models import Company, Location, JobCategory, Job, SavedJob


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for company data representation.
    """
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo_url', 'careers_url', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'state', 'country', 'is_remote']
        read_only_fields = ['id']


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for job creation.
    """
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company',
        write_only=True,
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='location',
        write_only=True,
        required=False,
        allow_null=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Job
        fields = [
            'company_id', 'location_id', 'category_id',
            'external_id', 'title', 'description', 'requirements',
            'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency',
            'external_url', 'is_remote', 'posted_at',
        ]


class JobUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for job update.
    """
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='location',
        write_only=True,
        required=False,
        allow_null=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=JobCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Job
        fields = [
            'location_id', 'category_id',
            'title', 'description', 'requirements',
            'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency',
            'external_url', 'is_remote', 'is_active', 'posted_at',
        ]
        extra_kwargs = {f: {'required': False} for f in [
            'title', 'description', 'requirements', 'employment_type',
            'experience_level', 'salary_min', 'salary_max', 'salary_currency',
            'external_url', 'is_remote', 'is_active', 'posted_at',
        ]}


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for job data representation.
    Includes nested company, location and category information.
    """
    company = CompanySerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company', 'location', 'category',
            'external_id', 'title', 'description', 'requirements',
            'employment_type', 'experience_level',
            'salary_min', 'salary_max', 'salary_currency',
            'external_url', 'is_remote', 'is_active',
            'posted_at', 'scraped_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'scraped_at', 'created_at', 'updated_at']


class SavedJobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for saved job creation.
    """
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        source='job',
        write_only=True,
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
        fields = ['id', 'job', 'status', 'notes', 'saved_at']
        read_only_fields = ['id', 'saved_at']
