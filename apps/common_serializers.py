from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()


class PaginatedResponseSerializer(serializers.Serializer):
    """
    Base serializer for paginated responses.
    Used for Swagger documentation.
    """
    count = serializers.IntegerField(help_text='Total number of items')
    next = serializers.URLField(allow_null=True, help_text='URL to next page')
    previous = serializers.URLField(allow_null=True, help_text='URL to previous page')
