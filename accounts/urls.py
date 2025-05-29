from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('registrazione/', views.registra_utente, name='registrazione'),
]