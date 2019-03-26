# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from django.views.decorators.csrf import ensure_csrf_cookie
import textwrap

from django.http import HttpResponse
from django.views.generic.base import View
from apps.users.views import Dashboard, APICreditList, MyAPICredits
from apps.subscriptions.views import TransactionList
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



class HomePageView(View):
    def dispatch(self, request, *args, **kwargs):
        response_text = textwrap.dedent('''\
            <html>
            <head>
                <title>Greetings to the world</title>
            </head>
            <body>
                <h1>Greetings to the world</h1>
                <p>Hello, world! %s</p>
            </body>
            </html>
        ''')
        return HttpResponse(response_text)

class StatusPageView(View):
    def dispatch(self, request, *args, **kwargs):
        from apps.networks.models import Scanner
        from apps.contracts.models import Contract
        main = Scanner.MAIN()
        import json
        data = {
            'latest_block': main.latest_block,
            'updated_at': str(main.updated_at),
            'contracts': Contract.objects.count()
        }
        return HttpResponse('<pre>'+json.dumps(data, indent=2))

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mgmt/', admin.site.urls),
    path('', include('apps.subscriptions.urls')),
    path('status', StatusPageView.as_view(), name='status'),
    path('dashboard', Dashboard.as_view(), name='dashboard'),
    path('accounts/', include('rest_registration.api.urls')),
    path('api_balance', MyAPICredits.as_view(), name='api_balance'),
    path('api_credit_statement', APICreditList.as_view(), name='api_credit_statement'),
    path('transactions/', TransactionList.as_view(), name='transactions'),
    
    path('', HomePageView.as_view(), name='home'),
]

