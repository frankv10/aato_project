from django.urls import path
from .import views

urlpatterns = [
    path('crea/', views.crea_manufatto, name='crea_manufatto'),
    path('lista/', views.lista_manufatti, name='lista_manufatti'),
    path('dettaglio/<int:manufatto_id>/', views.dettaglio_manufatto, name='dettaglio_manufatto'),
    path("mappa/", views.visualizza_mappa, name="visualizza_mappa"),
    path('modifica/<int:pk>/', views.modifica_manufatto, name='modifica_manufatto'),
    path('elimina/<int:pk>/', views.elimina_manufatto, name='elimina_manufatto'),
    path('manufatto/<int:manufatto_id>/documenti/', views.gestione_documenti, name='gestione_documenti'),
    path('documenti/', views.lista_documenti, name='lista_documenti'),
    path('documenti/<int:doc_id>/elimina/', views.elimina_documento, name='elimina_documento'),
    path('scarica/<int:doc_id>/', views.scarica_documento, name='scarica_documento'),

]
