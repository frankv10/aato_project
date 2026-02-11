import os
import mimetypes
from django.db.models import Q
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
from django.http import HttpResponse
from .models import Manufatto, info_idriche, info_geografiche

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
    ente_utente = get_user_ente(request.user)
    
    # Autorizziamo sia TEA che AATO
    autorizzati = ['TEA', 'AATO']
    
    if ente_utente not in autorizzati:
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
            messages.success(request, "Modifiche salvate.")
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
    
    # Autorizziamo sia TEA che AATO
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


@login_required
def visualizza_mappa(request):
    ente_utente = get_user_ente(request.user)
    # Usa select_related per caricare le coordinate in una volta sola (più veloce)
    manufatti = Manufatto.objects.all().select_related('info_geografiche')
    
    return render(request, "manufatti/visualizza_mappa.html", {
        'ente_utente': ente_utente,
        'manufatti': manufatti,
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
            # --- RIGA DA CORREGGERE SOTTO ---
            return redirect('lista_documenti') 
            # -------------------------------
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
    ente_utente = get_user_ente(request.user)
    
    # 1. Controllo permessi
    if ente_utente not in ['TEA', 'AATO']:
        messages.error(request, "Non hai i permessi per eliminare documenti.")
        return redirect('lista_documenti')

    # 2. Recupero del documento
    documento = get_object_or_404(Documento, id=doc_id)
    
    # Salviamo l'ID del manufatto (se esiste) prima di cancellare il record
    manufatto_id = getattr(documento.manufatto, 'id', None)

    # 3. Gestione della cancellazione (POST)
    if request.method == 'POST':
        documento.delete()
        messages.success(request, "Documento eliminato con successo.")
        
        # Se era un documento di un manufatto specifico, torna lì
        if manufatto_id:
            return redirect('gestione_documenti', manufatto_id=manufatto_id)
        return redirect('lista_documenti')

    # Se la richiesta non è POST o se qualcosa va storto, 
    # Django DEVE comunque ricevere un redirect.
    return redirect('lista_documenti')


@login_required
def scarica_documento(request, doc_id):
    documento = get_object_or_404(Documento, pk=doc_id)
    file_path = documento.file.path

    if not os.path.exists(file_path):
        raise Http404("Il file fisico non è stato trovato sul server.")

    # 1. Recuperiamo il nome originale del file
    nome_file = os.path.basename(documento.file.name)

    # 2. Indoviniamo il tipo di file (es. application/pdf, image/png, ecc.)
    content_type, encoding = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'

    # 3. Creiamo la risposta
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    
    # 4. Impostiamo l'header per il download con le virgolette (fondamentale per evitare estensioni doppie)
    response['Content-Disposition'] = f'attachment; filename="{nome_file}"'
    
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

# --- FUNZIONE ESPORTA EXCEL ---
@login_required
def export_manufatti(request):
    # 1. Recupera tutti i dati
    manufatti = Manufatto.objects.all().select_related('info_idriche', 'info_geografiche')
    data = []

    for m in manufatti:
        # Recupera le istanze collegate (se esistono)
        idr = getattr(m, 'info_idriche', None)
        geo = getattr(m, 'info_geografiche', None)

        row = {
            # Dati Manufatto
            'NOME': m.nome,
            'STATO': m.stato,
            'COMUNE': m.comune,
            'LOCALITA': m.localita,
            'UBICAZIONE': m.ubicazione,
            'DEPURATORE': m.depuratore_associato,
            'EMISSARIO': m.recapito_emissario,
            'TIPOLOGIA': m.tipologia_sfioratore,

            # Dati Geografici
            'LATITUDINE': geo.latitudine if geo else None,
            'LONGITUDINE': geo.longitudine if geo else None,

            # Dati Idrici (Principali)
            'AE_TOT': idr.ae_tot if idr else None,
            'QNM': idr.qnm if idr else None,
            'QS': idr.qs if idr else None,
            'AE_CIV': idr.ae_civ if idr else None,
            'AE_IND': idr.ae_ind if idr else None,
            'CONFORME': idr.e_conforme if idr else None,
            
            # Autorizzazioni
            'VASCA_PTUA': idr.vasca_ptua if idr else None,
            'CONSORZIO': idr.consorzio_competente if idr else None,
            'ATTO_PROVINCIA': idr.atto_provincia_n if idr else None,
            'SCADENZA_PROV': idr.scadenza_autorizzazione if idr else None,
            'ATTO_CONSORZIO': idr.atto_consorzio_n if idr else None,
            'SCADENZA_CONS': idr.scadenza_concessione if idr else None,
            'NOTE_AUTORIZZAZIONI': idr.note_autorizzazioni if idr else None,
        }
        data.append(row)

    # 2. Crea il DataFrame e il file Excel
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export_manufatti.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

# --- FUNZIONE IMPORTA EXCEL ---
@login_required
def import_manufatti(request):
    if request.method == 'POST' and request.FILES.get('myfile'):
        excel_file = request.FILES['myfile']
        
        try:
            df = pd.read_excel(excel_file)
            # Sostituisce i valori nan con None (altrimenti Django si arrabbia con i float)
            df = df.where(pd.notnull(df), None)

            count_created = 0
            count_updated = 0

            for index, row in df.iterrows():
                nome = row.get('NOME')
                if not nome:
                    continue # Salta righe senza nome

                # 1. Aggiorna o Crea Manufatto
                manufatto, created = Manufatto.objects.update_or_create(
                    nome=nome,
                    defaults={
                        'stato': row.get('STATO'),
                        'comune': row.get('COMUNE'),
                        'localita': row.get('LOCALITA'),
                        'ubicazione': row.get('UBICAZIONE'),
                        'depuratore_associato': row.get('DEPURATORE'),
                        'recapito_emissario': row.get('EMISSARIO'),
                        'tipologia_sfioratore': row.get('TIPOLOGIA'),
                    }
                )

                if created: count_created += 1
                else: count_updated += 1

                # 2. Aggiorna Info Geografiche
                info_geografiche.objects.update_or_create(
                    manufatto=manufatto,
                    defaults={
                        'latitudine': row.get('LATITUDINE'),
                        'longitudine': row.get('LONGITUDINE'),
                    }
                )

                # 3. Aggiorna Info Idriche
                info_idriche.objects.update_or_create(
                    manufatto=manufatto,
                    defaults={
                        'ae_tot': row.get('AE_TOT'),
                        'qnm': row.get('QNM'),
                        'qs': row.get('QS'),
                        'ae_civ': row.get('AE_CIV'),
                        'ae_ind': row.get('AE_IND'),
                        'e_conforme': row.get('CONFORME'),
                        'vasca_ptua': row.get('VASCA_PTUA'),
                        'consorzio_competente': row.get('CONSORZIO'),
                        'atto_provincia_n': row.get('ATTO_PROVINCIA'),
                        'scadenza_autorizzazione': row.get('SCADENZA_PROV'),
                        'atto_consorzio_n': row.get('ATTO_CONSORZIO'),
                        'scadenza_concessione': row.get('SCADENZA_CONS'),
                        'note_autorizzazioni': row.get('NOTE_AUTORIZZAZIONI'),
                    }
                )

            messages.success(request, f'Importazione completata: {count_created} creati, {count_updated} aggiornati.')
            return redirect('lista_manufatti')

        except Exception as e:
            messages.error(request, f"Errore durante l'importazione: {e}")
            return redirect('import_manufatti')

    return render(request, 'manufatti/upload_excel.html')
