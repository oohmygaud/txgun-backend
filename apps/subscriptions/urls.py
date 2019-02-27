from . import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.api_root),
    path('subscriptions/', views.SubscriptionList.as_view(), name='subscription-list'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetail.as_view(), name='subscription-detail'),
    #path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)