from django.urls import path
from . import views

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
    path('ricerca/', views.ricerca_interventi, name='ricerca_interventi'),
    path('export/', views.export_manufatti, name='export_manufatti'),
    path('import/', views.import_manufatti, name='import_manufatti'),
    path('manufatto/<int:manufatto_id>/risolvi-alert/', views.risolvi_alert, name='risolvi_alert'),

    # --- RIGHE RIMOSSE ---
    # Le seguenti righe sono state rimosse per evitare l'errore "pagina bianca"
    # (Usiamo i popup, non pagine separate)
    # path('modifica_idriche/<int:pk>/', views.modifica_info_idriche, name='modifica_idriche'),
    # path('modifica_geografiche/<int:pk>/', views.modifica_info_geografiche, name='modifica_geografiche'),
]
