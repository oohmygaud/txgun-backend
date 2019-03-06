# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from django.views.decorators.csrf import ensure_csrf_cookie
import textwrap

from django.http import HttpResponse
from django.views.generic.base import View
from apps.users.views import Dashboard


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
    url(r'^mgmt/', admin.site.urls),
    url(r'^', include('apps.subscriptions.urls')),
    url(r'^status', StatusPageView.as_view(), name='status'),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^dashboard', Dashboard.as_view(), name='dashboard')
]

