import os

from django.db.models import Q
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Importazione aggiornata per includere tutti i form
from .forms import (
    ManufattoForm, InfoIdricheForm, InfoGeograficheForm, DocumentoForm
)
from accounts.models import Profilo
# Importazione aggiornata per includere tutti i modelli
from .models import (
    Manufatto, Documento, info_idriche, info_geografiche
)


# Funzione di utilità per ottenere l'ente utente in modo robusto
def get_user_ente(user):
    if user.is_authenticated:
        try:
            return user.profilo.ente
        except Profilo.DoesNotExist:
            return 'TEA'
        except AttributeError:
            return 'TEA'
    return 'TEA'


@login_required
def crea_manufatto(request):
    ente_utente = get_user_ente(request.user)
    if request.method == 'POST':
        form_manufatto = ManufattoForm(request.POST)
        form_idriche = InfoIdricheForm(request.POST)
        form_geografiche = InfoGeograficheForm(request.POST)

        if form_manufatto.is_valid() and form_idriche.is_valid() and form_geografiche.is_valid():
            manufatto = form_manufatto.save()
            idriche = form_idriche.save(commit=False)
            idriche.manufatto = manufatto
            idriche.save()
            geo = form_geografiche.save(commit=False)
            geo.manufatto = manufatto
            geo.save()
            return redirect('lista_manufatti')
    else:
        form_manufatto = ManufattoForm()
        form_idriche = InfoIdricheForm()
        form_geografiche = InfoGeograficheForm()

    return render(request, 'manufatti/crea_manufatto.html', {
        'form_manufatto': form_manufatto,
        'form_idriche': form_idriche,
        'form_geografiche': form_geografiche,
        'ente_utente': ente_utente,
    })


def lista_manufatti(request):
    ente_utente = get_user_ente(request.user)
    query = request.GET.get('query')
    if query:
        manufatti = Manufatto.objects.filter(Q(nome__icontains=query) | Q(stato__icontains=query))
    else:
        manufatti = Manufatto.objects.all()
    return render(request, 'manufatti/lista_manufatti.html', {
        'manufatti': manufatti,
        'query': query,
        'ente_utente': ente_utente,
    })


def dettaglio_manufatto(request, manufatto_id):
    ente_utente = get_user_ente(request.user)
    manufatto = get_object_or_404(Manufatto, id=manufatto_id)

    # Correzione per OneToOneField
    try:
        idriche = manufatto.info_idriche
    except info_idriche.DoesNotExist:
        idriche = None

    try:
        geografiche = manufatto.info_geografiche
    except info_geografiche.DoesNotExist:
        geografiche = None

    return render(request, 'manufatti/dettaglio_manufatto.html', {
        'manufatto': manufatto,
        'idriche': idriche,
        'geografiche': geografiche,
        'ente_utente': ente_utente,
    })


@login_required
def modifica_manufatto(request, pk):
    """
    Gestisce la modifica di Manufatto e delle sue relative info (Idriche, Geografiche)
    attraverso un unico form template.
    """
    ente_utente = get_user_ente(request.user)
    manufatto = get_object_or_404(Manufatto, pk=pk)

    # Carica le istanze OneToOne esistenti
    try:
        info_idriche_instance = manufatto.info_idriche
    except info_idriche.DoesNotExist:
        info_idriche_instance = None

    try:
        info_geografiche_instance = manufatto.info_geografiche
    except info_geografiche.DoesNotExist:
        info_geografiche_instance = None

    if request.method == 'POST':
        form_manufatto = ManufattoForm(request.POST, instance=manufatto)
        form_idriche = InfoIdricheForm(request.POST, instance=info_idriche_instance)
        form_geografiche = InfoGeograficheForm(request.POST, instance=info_geografiche_instance)

        if form_manufatto.is_valid() and form_idriche.is_valid() and form_geografiche.is_valid():
            form_manufatto.save()

            # Salvataggio e collegamento delle info idriche
            idriche = form_idriche.save(commit=False)
            idriche.manufatto = manufatto
            idriche.save()

            # Salvataggio e collegamento delle info geografiche
            geo = form_geografiche.save(commit=False)
            geo.manufatto = manufatto
            geo.save()

            messages.success(request, f"Manufatto {manufatto.nome} aggiornato con successo.")
            return redirect('dettaglio_manufatto', manufatto_id=manufatto.id)
    else:
        # Carica i form con i dati esistenti
        form_manufatto = ManufattoForm(instance=manufatto)
        form_idriche = InfoIdricheForm(instance=info_idriche_instance)
        form_geografiche = InfoGeograficheForm(instance=info_geografiche_instance)

    return render(request, 'manufatti/modifica_manufatto.html', {
        'form_manufatto': form_manufatto,
        'form_idriche': form_idriche,
        'form_geografiche': form_geografiche,
        'manufatto': manufatto,
        'ente_utente': ente_utente,
    })


@login_required
def elimina_manufatto(request, pk):
    ente_utente = get_user_ente(request.user)
    manufatto = get_object_or_404(Manufatto, pk=pk)
    if request.method == 'POST':
        manufatto.delete()
        return redirect('lista_manufatti')
    return render(request, 'manufatti/conferma_elimina.html', {
        'manufatto': manufatto,
        'ente_utente': ente_utente,
    })


@login_required
def visualizza_mappa(request):
    ente_utente = get_user_ente(request.user)
    return render(request, "manufatti/visualizza_mappa.html", {
        'ente_utente': ente_utente,
    })


@login_required
def gestione_documenti(request, manufatto_id):
    ente_utente = get_user_ente(request.user)
    manufatto = get_object_or_404(Manufatto, id=manufatto_id)
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            nuovo_documento = form.save(commit=False)
            nuovo_documento.manufatto = manufatto
            nuovo_documento.save()
            return redirect('gestione_documenti', manufatto_id=manufatto.id)
    else:
        form = DocumentoForm()
    documenti = manufatto.documenti.all()
    context = {
        'manufatto': manufatto,
        'form': form,
        'documenti': documenti,
        'ente_utente': ente_utente
    }
    return render(request, 'manufatti/gestione_documenti.html', context)


@login_required
def lista_documenti(request):
    ente_utente = get_user_ente(request.user)
    query = request.GET.get('query')
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento caricato con successo!')
            return redirect('lista_content')
    else:
        form = DocumentoForm()
    documenti = Documento.objects.select_related('manufatto').order_by('-data_caricamento')
    if query:
        documenti = documenti.filter(Q(titolo__icontains=query) | Q(manufatto__nome__icontains=query))
    context = {
        'documenti': documenti,
        'form': form,
        'query': query,
        'ente_utente': ente_utente,
    }
    return render(request, 'manufatti/lista_documenti.html', context)


@login_required
def elimina_documento(request, doc_id):
    documento = get_object_or_404(Documento, id=doc_id)
    if request.method == 'POST':
        documento.delete()
        messages.success(request, 'Documento eliminato correttamente.')
    return redirect('lista_documenti')


def scarica_documento(request, doc_id):
    try:
        documento = Documento.objects.get(pk=doc_id)
    except Documento.DoesNotExist:
        raise Http404("Il documento non esiste.")
    file_path = documento.file.path
    if not os.path.exists(file_path):
        raise Http404("Il file non è stato trovato.")
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response


@login_required
def ricerca_interventi(request):
    ente_utente = get_user_ente(request.user)
    query = request.GET.get('q', '')
    stato = request.GET.get('stato', '')
    data = request.GET.get('data', '')
    risultati = Manufatto.objects.all()
    if query:
        risultati = risultati.filter(nome__icontains=query)
    if stato:
        risultati = risultati.filter(stato=stato)
    if data:
        risultati = risultati.filter(data_creazione__date=data)
    context = {
        'query': query,
        'stato': stato,
        'data': data,
        'risultati': risultati,
        'ente_utente': ente_utente,
    }
    return render(request, 'manufatti/ricerca_interventi.html', context)