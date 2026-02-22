from django.urls import path
from .views import (
    UserPreferenceView,
    RecommendedJobsView,
    PreferredCompanyView,
    PreferredCompanyDeleteView,
    PreferredCategoryView,
    PreferredCategoryDeleteView,
    PreferredLocationView,
    PreferredLocationDeleteView,
    KeywordView,
    KeywordDeleteView,
)

urlpatterns = [
    path('', UserPreferenceView.as_view(), name='preference'),
    path('recommended/', RecommendedJobsView.as_view(), name='recommended-jobs'),

    path('companies/', PreferredCompanyView.as_view(), name='preferred-companies'),
    path('companies/<int:company_id>/', PreferredCompanyDeleteView.as_view(), name='preferred-company-delete'),

    path('categories/', PreferredCategoryView.as_view(), name='preferred-categories'),
    path('categories/<int:category_id>/', PreferredCategoryDeleteView.as_view(), name='preferred-category-delete'),

    path('locations/', PreferredLocationView.as_view(), name='preferred-locations'),
    path('locations/<int:location_id>/', PreferredLocationDeleteView.as_view(), name='preferred-location-delete'),

    path('keywords/', KeywordView.as_view(), name='keywords'),
    path('keywords/<int:keyword_id>/', KeywordDeleteView.as_view(), name='keyword-delete'),
]
