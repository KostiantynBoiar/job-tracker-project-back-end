import django_filters
from django.db.models import Q
from .models import Job


class JobFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    company = django_filters.NumberFilter(field_name='company__id', lookup_expr='exact')
    company_in = django_filters.BaseInFilter(field_name='company__id', lookup_expr='in')
    employment_type = django_filters.CharFilter(field_name='employment_type', lookup_expr='exact')
    employment_type_in = django_filters.BaseInFilter(field_name='employment_type', lookup_expr='in')
    experience_level = django_filters.CharFilter(field_name='experience_level', lookup_expr='exact')
    experience_level_in = django_filters.BaseInFilter(field_name='experience_level', lookup_expr='in')
    is_remote = django_filters.BooleanFilter(field_name='is_remote')
    salary_min = django_filters.NumberFilter(field_name='salary_max', lookup_expr='gte', label='Minimum Salary')
    salary_max = django_filters.NumberFilter(field_name='salary_min', lookup_expr='lte', label='Maximum Salary')
    
    class Meta:
        model = Job
        fields = []
    
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(company__name__icontains=value) |
            Q(location__city__icontains=value) |
            Q(location__country__icontains=value)
        )
