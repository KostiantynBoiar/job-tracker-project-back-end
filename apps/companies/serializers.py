from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for company data representation.
    """
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo_url', 'careers_url', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for company creation.
    """
    class Meta:
        model = Company
        fields = ['name', 'logo_url', 'careers_url', 'is_active']
        extra_kwargs = {
            'logo_url': {'required': False},
            'careers_url': {'required': False},
            'is_active': {'required': False},
        }


class CompanyUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for company update.
    """
    class Meta:
        model = Company
        fields = ['name', 'logo_url', 'careers_url', 'is_active']
        extra_kwargs = {f: {'required': False} for f in ['name', 'logo_url', 'careers_url', 'is_active']}
