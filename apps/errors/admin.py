from django.contrib import admin
from .models import ErrorLog

class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'nickname', 'traceback']
admin.site.register(ErrorLog, ErrorLogAdmin)
