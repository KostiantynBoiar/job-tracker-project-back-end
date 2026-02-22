from django.urls import path
from .views import (
    JobCreateView,
    JobListView,
    JobDetailView,
    JobUpdateView,
    JobDeleteView,
    SavedJobCreateView,
    SavedJobListView,
    SavedJobDetailView,
    SavedJobUpdateView,
    SavedJobDeleteView,
)

app_name = 'jobs'

urlpatterns = [
    path('', JobListView.as_view(), name='list'),
    path('create/', JobCreateView.as_view(), name='create'),
    path('<int:pk>/', JobDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', JobUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', JobDeleteView.as_view(), name='delete'),
    path('saved/', SavedJobListView.as_view(), name='saved-list'),
    path('saved/create/', SavedJobCreateView.as_view(), name='saved-create'),
    path('saved/<int:pk>/', SavedJobDetailView.as_view(), name='saved-detail'),
    path('saved/<int:pk>/update/', SavedJobUpdateView.as_view(), name='saved-update'),
    path('saved/<int:pk>/delete/', SavedJobDeleteView.as_view(), name='saved-delete'),
]
