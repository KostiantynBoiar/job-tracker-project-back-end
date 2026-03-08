from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from apps.companies.serializers import CompanySerializer
from apps.jobs.serializers import LocationSerializer, JobCategorySerializer, JobSerializer
from apps.common_serializers import MessageSerializer, ErrorSerializer
from apps.common_pagination import StandardPagination
from .models import UserKeyword, DailyRecap
from .serializers import (
    UserPreferenceSerializer,
    UserPreferenceUpdateSerializer,
    AddPreferredCompanySerializer,
    AddPreferredCategorySerializer,
    AddPreferredLocationSerializer,
    AddKeywordSerializer,
    UserKeywordSerializer,
    DailyRecapSerializer,
)
from .services import PreferenceService, RecommendationService
from .exceptions import PreferenceNotFoundException, PreferenceAlreadyExistsException


class UserPreferenceView(generics.GenericAPIView):
    """
    GET/PUT/PATCH the current user's preference settings.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserPreferenceSerializer})
    def get(self, request):
        pref = PreferenceService.get_or_create(request.user)
        return Response(UserPreferenceSerializer(pref).data)

    @extend_schema(request=UserPreferenceUpdateSerializer, responses={200: UserPreferenceSerializer})
    def put(self, request):
        return self._update(request)

    @extend_schema(request=UserPreferenceUpdateSerializer, responses={200: UserPreferenceSerializer})
    def patch(self, request):
        return self._update(request)

    def _update(self, request):
        serializer = UserPreferenceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pref = PreferenceService.update(request.user, serializer.validated_data)
        return Response(UserPreferenceSerializer(pref).data)


class RecommendedJobsView(generics.ListAPIView):
    """
    Returns a scored list of recommended jobs for the current user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
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
        return RecommendationService.get_recommended_jobs_queryset(self.request.user)


# --- Preferred Companies ---

class PreferredCompanyListView(generics.ListAPIView):
    """
    List all preferred companies for the current user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
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
        pref = PreferenceService.get_or_create(self.request.user)
        return pref.preferred_companies.all()


class PreferredCompanyCreateView(generics.GenericAPIView):
    """
    Add a company to preferences.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddPreferredCompanySerializer,
        responses={201: MessageSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        serializer = AddPreferredCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            PreferenceService.add_company(request.user, serializer.validated_data['company_id'])
            return Response({'message': 'Company added to preferences.'}, status=status.HTTP_201_CREATED)
        except PreferenceAlreadyExistsException:
            raise


class PreferredCompanyDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: MessageSerializer, 404: ErrorSerializer})
    def delete(self, request, company_id):
        try:
            PreferenceService.remove_company(request.user, company_id)
            return Response({'message': 'Company removed from preferences.'})
        except PreferenceNotFoundException:
            raise


# --- Preferred Categories ---

class PreferredCategoryListView(generics.ListAPIView):
    """
    List all preferred categories for the current user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = JobCategorySerializer
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
        pref = PreferenceService.get_or_create(self.request.user)
        return pref.preferred_categories.all()


class PreferredCategoryCreateView(generics.GenericAPIView):
    """
    Add a category to preferences.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddPreferredCategorySerializer,
        responses={201: MessageSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        serializer = AddPreferredCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            PreferenceService.add_category(request.user, serializer.validated_data['category_id'])
            return Response({'message': 'Category added to preferences.'}, status=status.HTTP_201_CREATED)
        except PreferenceAlreadyExistsException:
            raise


class PreferredCategoryDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: MessageSerializer, 404: ErrorSerializer})
    def delete(self, request, category_id):
        try:
            PreferenceService.remove_category(request.user, category_id)
            return Response({'message': 'Category removed from preferences.'})
        except PreferenceNotFoundException:
            raise


# --- Preferred Locations ---

class PreferredLocationListView(generics.ListAPIView):
    """
    List all preferred locations for the current user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer
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
        pref = PreferenceService.get_or_create(self.request.user)
        return pref.preferred_locations.all()


class PreferredLocationCreateView(generics.GenericAPIView):
    """
    Add a location to preferences.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddPreferredLocationSerializer,
        responses={201: MessageSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        serializer = AddPreferredLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            PreferenceService.add_location(request.user, serializer.validated_data['location_id'])
            return Response({'message': 'Location added to preferences.'}, status=status.HTTP_201_CREATED)
        except PreferenceAlreadyExistsException:
            raise


class PreferredLocationDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: MessageSerializer, 404: ErrorSerializer})
    def delete(self, request, location_id):
        try:
            PreferenceService.remove_location(request.user, location_id)
            return Response({'message': 'Location removed from preferences.'})
        except PreferenceNotFoundException:
            raise


# --- Keywords ---

class KeywordListView(generics.ListAPIView):
    """
    List all keywords for the current user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserKeywordSerializer
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
        return UserKeyword.objects.filter(user=self.request.user)


class KeywordCreateView(generics.GenericAPIView):
    """
    Add a keyword to preferences.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AddKeywordSerializer,
        responses={201: UserKeywordSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        serializer = AddKeywordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            PreferenceService.add_keyword(request.user, serializer.validated_data['keyword'])
            kw = UserKeyword.objects.get(user=request.user, keyword=serializer.validated_data['keyword'])
            return Response(UserKeywordSerializer(kw).data, status=status.HTTP_201_CREATED)
        except PreferenceAlreadyExistsException:
            raise


class KeywordDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: MessageSerializer, 404: ErrorSerializer})
    def delete(self, request, keyword_id):
        try:
            PreferenceService.remove_keyword(request.user, keyword_id)
            return Response({'message': 'Keyword removed.'})
        except PreferenceNotFoundException:
            raise



class DailyRecapListView(generics.ListAPIView):
    """
    List all daily recaps for the current user with pagination.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DailyRecapSerializer
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
        return DailyRecap.objects.filter(user=self.request.user)
