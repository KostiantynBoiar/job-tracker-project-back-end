from rest_framework import serializers
from apps.jobs.models import Company, Location, JobCategory
from apps.jobs.serializers import CompanySerializer, LocationSerializer, JobCategorySerializer, JobSerializer
from .models import UserPreference, UserKeyword, DailyRecap, RecapJob


class UserKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKeyword
        fields = ['id', 'keyword']
        read_only_fields = ['id']


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Full read representation including nested lists."""
    preferred_companies = CompanySerializer(many=True, read_only=True)
    preferred_categories = JobCategorySerializer(many=True, read_only=True)
    preferred_locations = LocationSerializer(many=True, read_only=True)
    keywords = UserKeywordSerializer(many=True, read_only=True, source='user.keywords')

    class Meta:
        model = UserPreference
        fields = [
            'experience_level', 'min_salary', 'remote_only',
            'notification_frequency', 'preferred_send_time',
            'preferred_companies', 'preferred_categories', 'preferred_locations',
            'keywords', 'updated_at',
        ]
        read_only_fields = ['updated_at']


class UserPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Accepts scalar preference fields only."""
    class Meta:
        model = UserPreference
        fields = [
            'experience_level', 'min_salary', 'remote_only',
            'notification_frequency', 'preferred_send_time',
        ]
        extra_kwargs = {f: {'required': False} for f in [
            'experience_level', 'min_salary', 'remote_only',
            'notification_frequency', 'preferred_send_time',
        ]}


class AddPreferredCompanySerializer(serializers.Serializer):
    company_id = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())


class AddPreferredCategorySerializer(serializers.Serializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all())


class AddPreferredLocationSerializer(serializers.Serializer):
    location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())


class AddKeywordSerializer(serializers.Serializer):
    keyword = serializers.CharField(max_length=100)

    def validate_keyword(self, value):
        return value.strip().lower()


class RecapJobSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = RecapJob
        fields = ['job', 'was_clicked']


class DailyRecapSerializer(serializers.ModelSerializer):
    recap_jobs = RecapJobSerializer(many=True, read_only=True)

    class Meta:
        model = DailyRecap
        fields = ['id', 'jobs_count', 'sent_at', 'status', 'recap_jobs']
        read_only_fields = ['id', 'jobs_count', 'sent_at', 'status']
