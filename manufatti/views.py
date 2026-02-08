import os
from django.db.models import Q
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importazione form e modelli
from .forms import (
    ManufattoForm, InfoIdricheForm, InfoGeograficheForm, DocumentoForm
)
from accounts.models import Profilo
from .models import (
    Manufatto, Documento, info_idriche, info_geografiche
)

# --- Utility ---
def get_user_ente(user):
    """Recupera l'ente associato al profilo utente."""
    if user.is_authenticated:
        try:
            return user.profilo.ente
        except (Profilo.DoesNotExist, AttributeError):
            return 'TEA'
    return 'TEA'

# --- Sezione Manufatti ---

@login_required
def crea_manufatto(request):
    ente_utente = get_user_ente(request.user)
    if request.method == 'POST':
        form_manufatto = ManufattoForm(request.POST)
        form_idriche = InfoIdricheForm(request.POST)
        form_geografiche = InfoGeograficheForm(request.POST)

        if form_manufatto.is_valid() and form_idriche.is_valid() and form_geografiche.is_valid():
            manufatto = form_manufatto.save()
            # Collega info idriche
            idriche = form_idriche.save(commit=False)
            idriche.manufatto = manufatto
            idriche.save()
            # Collega info geografiche
            geo = form_geografiche.save(commit=False)
            geo.manufatto = manufatto
            geo.save()
            messages.success(request, "Manufatto creato con successo.")
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

    # Uso di getattr per gestire OneToOne in modo sicuro
    idriche = getattr(manufatto, 'info_idriche', None)
    geografiche = getattr(manufatto, 'info_geografiche', None)

    return render(request, 'manufatti/dettaglio_manufatto.html', {
        'manufatto': manufatto,
        'idriche': idriche,
        'geografiche': geografiche,
        'ente_utente': ente_utente,
    })

@login_required
def modifica_manufatto(request, pk):
    ente_utente = get_user_ente(request.user)
    if ente_utente not in ['TEA', 'AATO']:
        messages.error(request, "Accesso negato: non hai i permessi per modificare.")
        return redirect('lista_manufatti')

    manufatto = get_object_or_404(Manufatto, pk=pk)
    idriche_inst = getattr(manufatto, 'info_idriche', None)
    geo_inst = getattr(manufatto, 'info_geografiche', None)

    if request.method == 'POST':
        f_m = ManufattoForm(request.POST, instance=manufatto)
        f_i = InfoIdricheForm(request.POST, instance=idriche_inst)
        f_g = InfoGeograficheForm(request.POST, instance=geo_inst)

        if f_m.is_valid() and f_i.is_valid() and f_g.is_valid():
            f_m.save()
            i = f_i.save(commit=False)
            i.manufatto = manufatto
            i.save()
            g = f_g.save(commit=False)
            g.manufatto = manufatto
            g.save()
            messages.success(request, "Modifiche salvate con successo.")
            return redirect('dettaglio_manufatto', manufatto_id=manufatto.id)
    else:
        f_m = ManufattoForm(instance=manufatto)
        f_i = InfoIdricheForm(instance=idriche_inst)
        f_g = InfoGeograficheForm(instance=geo_inst)

    return render(request, 'manufatti/modifica_manufatto.html', {
        'form_manufatto': f_m, 'form_idriche': f_i, 'form_geografiche': f_g,
        'manufatto': manufatto, 'ente_utente': ente_utente
    })

@login_required
def elimina_manufatto(request, pk):
    ente_utente = get_user_ente(request.user)
    if ente_utente not in ['TEA', 'AATO']:
        messages.error(request, "Accesso negato: non puoi eliminare manufatti.")
        return redirect('lista_manufatti')

    manufatto = get_object_or_404(Manufatto, pk=pk)
    if request.method == 'POST':
        manufatto.delete()
        messages.success(request, "Manufatto eliminato.")
        return redirect('lista_manufatti')
    
    return render(request, 'manufatti/conferma_elimina.html', {
        'manufatto': manufatto, 
        'ente_utente': ente_utente
    })

# --- Sezione Documenti ---

@login_required
def gestione_documenti(request, manufatto_id):
    """Carica e visualizza documenti relativi a un singolo manufatto."""
    ente_utente = get_user_ente(request.user)
    manufatto = get_object_or_404(Manufatto, id=manufatto_id)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            nuovo_documento = form.save(commit=False)
            nuovo_documento.manufatto = manufatto
            nuovo_documento.save()
            messages.success(request, "Documento aggiunto correttamente.")
            return redirect('gestione_documenti', manufatto_id=manufatto.id)
    else:
        form = DocumentoForm()
        
    documenti = manufatto.documenti.all()
    return render(request, 'manufatti/gestione_documenti.html', {
        'manufatto': manufatto,
        'form': form,
        'documenti': documenti,
        'ente_utente': ente_utente
    })

@login_required
def lista_documenti(request):
    """Visualizza e ricerca tra tutti i documenti caricati."""
    ente_utente = get_user_ente(request.user)
    query = request.GET.get('query')
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento caricato con successo!')
            return redirect('lista_documenti') # Corretto: punta al name dell'URL
    else:
        form = DocumentoForm()
        
    documenti = Documento.objects.select_related('manufatto').order_by('-data_caricamento')
    if query:
        documenti = documenti.filter(Q(titolo__icontains=query) | Q(manufatto__nome__icontains=query))
    
    return render(request, 'manufatti/lista_documenti.html', {
        'documenti': documenti,
        'form': form,
        'query': query,
        'ente_utente': ente_utente,
    })

@login_required
def elimina_documento(request, doc_id):
    ente_utente = get_user_ente(request.user)
    
    # 1. Controllo permessi
    if ente_utente not in ['TEA', 'AATO']:
        messages.error(request, "Non hai i permessi per eliminare documenti.")
        return redirect('lista_documenti')

    # 2. Recupero del documento
    documento = get_object_or_404(Documento, pk=doc_id)
    
    # 3. Recupero l'ID in modo ultra-sicuro (getattr non crasha mai)
    # Se documento.manufatto è None, manufatto_id diventa None
    manufatto_id = getattr(documento.manufatto, 'id', None)

    if request.method == 'POST':
        documento.delete()
        messages.success(request, "Documento eliminato con successo.")
        
        # 4. Redirect intelligente
        if manufatto_id:
            return redirect('gestione_documenti', manufatto_id=manufatto_id)
        return redirect('lista_documenti')

    # 5. Se qualcuno arriva qui via GET, lo rimandiamo alla lista per sicurezza
    # (Oppure potresti mostrare una pagina di conferma se preferisci)
    return redirect('lista_documenti')


@login_required
def scarica_documento(request, doc_id):
    """Permette il download del file associato al documento."""
    documento = get_object_or_404(Documento, pk=doc_id)
    file_path = documento.file.path
    if not os.path.exists(file_path):
        raise Http404("Il file fisico non è stato trovato sul server.")
    
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response

# --- Altro ---

@login_required
def visualizza_mappa(request):
    ente_utente = get_user_ente(request.user)
    return render(request, "manufatti/visualizza_mappa.html", {
        'ente_utente': ente_utente,
    })

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
        
    return render(request, 'manufatti/ricerca_interventi.html', {
        'query': query,
        'stato': stato,
        'data': data,
        'risultati': risultati,
        'ente_utente': ente_utente,
    })