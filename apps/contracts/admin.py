from django.contrib import admin
from .models import Contract

class ContractAdmin(admin.ModelAdmin):
    list_display = ['network', 'address']
admin.site.register(Contract, ContractAdmin)