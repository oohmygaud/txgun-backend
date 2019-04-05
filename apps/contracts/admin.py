from django.contrib import admin
from .models import Contract, PriceLookup

class ContractAdmin(admin.ModelAdmin):
    list_display = ['network', 'address']
admin.site.register(Contract, ContractAdmin)

class PriceLookupAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'asset', 'currency', 'price']
admin.site.register(PriceLookup, PriceLookupAdmin)