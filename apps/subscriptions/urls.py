from . import views
from apps.users import views as user_views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    #path('subscriptions/', views.SubscriptionViewSet, name='subscription-list'),
    #path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('keys/', user_views.APIKeyList.as_view(), name='api-key-list')
]

urlpatterns = format_suffix_patterns(urlpatterns)