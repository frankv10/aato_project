from django.urls import path
from .import views


urlpatterns = [ path('crea/',views.crea_manufatto,name='crea_manufatto'),
                ]
