from django.contrib import admin
from .models import Profilo

class ProfiloAdmin(admin.ModelAdmin):
    list_display = ('user', 'ente')
admin.site.register(Profilo)