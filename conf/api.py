from apps.subscriptions.views import SubscriptionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
print('URLS', router.urls)
urlpatterns = router.urls