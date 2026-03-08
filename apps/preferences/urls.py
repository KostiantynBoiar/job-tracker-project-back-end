from django.urls import path
from .views import (
    UserPreferenceView,
    RecommendedJobsView,
    PreferredCompanyListView,
    PreferredCompanyCreateView,
    PreferredCompanyDeleteView,
    PreferredCategoryListView,
    PreferredCategoryCreateView,
    PreferredCategoryDeleteView,
    PreferredLocationListView,
    PreferredLocationCreateView,
    PreferredLocationDeleteView,
    KeywordListView,
    KeywordCreateView,
    KeywordDeleteView,
    DailyRecapListView,
)

urlpatterns = [
    path('', UserPreferenceView.as_view(), name='preference'),
    path('recommended/', RecommendedJobsView.as_view(), name='recommended-jobs'),
    path('recaps/', DailyRecapListView.as_view(), name='daily-recaps'),

    path('companies/', PreferredCompanyListView.as_view(), name='preferred-companies'),
    path('companies/add/', PreferredCompanyCreateView.as_view(), name='preferred-company-add'),
    path('companies/<int:company_id>/', PreferredCompanyDeleteView.as_view(), name='preferred-company-delete'),

    path('categories/', PreferredCategoryListView.as_view(), name='preferred-categories'),
    path('categories/add/', PreferredCategoryCreateView.as_view(), name='preferred-category-add'),
    path('categories/<int:category_id>/', PreferredCategoryDeleteView.as_view(), name='preferred-category-delete'),

    path('locations/', PreferredLocationListView.as_view(), name='preferred-locations'),
    path('locations/add/', PreferredLocationCreateView.as_view(), name='preferred-location-add'),
    path('locations/<int:location_id>/', PreferredLocationDeleteView.as_view(), name='preferred-location-delete'),

    path('keywords/', KeywordListView.as_view(), name='keywords'),
    path('keywords/add/', KeywordCreateView.as_view(), name='keyword-add'),
    path('keywords/<int:keyword_id>/', KeywordDeleteView.as_view(), name='keyword-delete'),
]
