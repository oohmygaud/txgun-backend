from django.contrib import admin
from .models import Network, Software, Scanner

admin.site.register(Network)
admin.site.register(Software)
admin.site.register(Scanner)