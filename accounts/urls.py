from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login_view,name='login'),
    path('registrazione/', views.registra_utente, name='registrazione'),
    path("tea/",views.tea_view,name="tea"),
    path("aato/",views.aato_view,name="aato"),
    path('logout/', views.logout_view, name='logout'),
]