from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.jobs.serializers import CompanySerializer, LocationSerializer, JobCategorySerializer, JobSerializer
from apps.common_serializers import MessageSerializer, ErrorSerializer
from .models import UserKeyword
from .serializers import (
    UserPreferenceSerializer,
    UserPreferenceUpdateSerializer,
    AddPreferredCompanySerializer,
    AddPreferredCategorySerializer,
    AddPreferredLocationSerializer,
    AddKeywordSerializer,
    UserKeywordSerializer,
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


class RecommendedJobsView(generics.GenericAPIView):
    """
    Returns a scored list of recommended jobs for the current user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: JobSerializer(many=True)})
    def get(self, request):
        limit = min(int(request.query_params.get('limit', 20)), 100)
        jobs = RecommendationService.get_recommended_jobs(request.user, limit=limit)
        return Response(JobSerializer(jobs, many=True).data)


# --- Preferred Companies ---

class PreferredCompanyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: CompanySerializer(many=True)})
    def get(self, request):
        pref = PreferenceService.get_or_create(request.user)
        return Response(CompanySerializer(pref.preferred_companies.all(), many=True).data)

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

class PreferredCategoryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: JobCategorySerializer(many=True)})
    def get(self, request):
        pref = PreferenceService.get_or_create(request.user)
        return Response(JobCategorySerializer(pref.preferred_categories.all(), many=True).data)

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

class PreferredLocationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LocationSerializer(many=True)})
    def get(self, request):
        pref = PreferenceService.get_or_create(request.user)
        return Response(LocationSerializer(pref.preferred_locations.all(), many=True).data)

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

class KeywordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserKeywordSerializer(many=True)})
    def get(self, request):
        keywords = UserKeyword.objects.filter(user=request.user)
        return Response(UserKeywordSerializer(keywords, many=True).data)

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
