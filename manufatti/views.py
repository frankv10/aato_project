import os

from django.db.models import Q
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ManufattoForm, InfoIdricheForm, InfoGeograficheForm, DocumentoForm


@login_required
def crea_manufatto(request):
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

            return redirect('lista_manufatti')  # oppure altra view
    else:
        form_manufatto = ManufattoForm()
        form_idriche = InfoIdricheForm()
        form_geografiche = InfoGeograficheForm()

    return render(request, 'manufatti/crea_manufatto.html', {
        'form_manufatto': form_manufatto,
        'form_idriche': form_idriche,
        'form_geografiche': form_geografiche,
    })

from .models import Manufatto, Documento


@login_required
@login_required
def lista_manufatti(request):

    query = request.GET.get('query')

    if query:
        manufatti = Manufatto.objects.filter(Q(nome__icontains=query) | Q(stato__icontains=query))
    else:
        manufatti = Manufatto.objects.all()

    return render(request, 'manufatti/lista_manufatti.html', {
        'manufatti': manufatti,
        'query': query
    })

def dettaglio_manufatto(request, manufatto_id):
    manufatto = get_object_or_404(Manufatto, id=manufatto_id)
    idriche = manufatto.info_idriche.all()
    geografiche = manufatto.info_geografiche.all()
    return render(request, 'manufatti/dettaglio_manufatto.html', {
        'manufatto': manufatto,
        'idriche': idriche,
        'geografiche': geografiche,
    })
@login_required
def modifica_manufatto(request, pk):
    manufatto = get_object_or_404(Manufatto, pk=pk)

    if request.method == 'POST':
        form_manufatto = ManufattoForm(request.POST, instance=manufatto)
        if form_manufatto.is_valid():
            form_manufatto.save()
            return redirect('lista_manufatti')
    else:
        form_manufatto = ManufattoForm(instance=manufatto)

    return render(request, 'manufatti/modifica_manufatto.html', {
        'form_manufatto': form_manufatto,
        'manufatto': manufatto,
    })

@login_required
def elimina_manufatto(request, pk):
    manufatto = get_object_or_404(Manufatto, pk=pk)

    if request.method == 'POST':
        manufatto.delete()
        return redirect('lista_manufatti')

    return render(request, 'manufatti/conferma_elimina.html', {
        'manufatto': manufatto
    })
@login_required
def visualizza_mappa(request):
    return render(request, "manufatti/visualizza_mappa.html")

@login_required
def gestione_documenti(request, manufatto_id):
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
        'documenti': documenti
    }
    return render(request, 'manufatti/gestione_documenti.html', context)



@login_required
def lista_documenti(request):

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento caricato con successo!')
            return redirect('lista_documenti')
    else:
        form = DocumentoForm()

    documenti = Documento.objects.select_related('manufatto').order_by('-data_caricamento')

    context = {
        'documenti': documenti,
        'form': form,
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
