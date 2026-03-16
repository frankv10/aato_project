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
    """Recupera l'ente dell'utente in modo sicuro."""
    if not user.is_authenticated:
        return 'GUEST'
    try:
        # Forza il caricamento del profilo
        profilo = Profilo.objects.get(user=user)
        return profilo.ente if profilo.ente else 'TEA'
    except Profilo.DoesNotExist:
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
    
    # 1. Recupero parametri GET
    query = request.GET.get('query', '')
    comune_selezionato = request.GET.get('comune', '')
    depuratore_selezionato = request.GET.get('depuratore', '')

    # 2. Queryset base
    manufatti = Manufatto.objects.all().order_by('comune', 'nome')

    # 3. Applicazione Filtri
    if query:
        manufatti = manufatti.filter(Q(nome__icontains=query) | Q(stato__icontains=query))
    
    if comune_selezionato:
        manufatti = manufatti.filter(comune=comune_selezionato)
        
    if depuratore_selezionato:
        manufatti = manufatti.filter(depuratore_associato=depuratore_selezionato)

    # 4. Recupero liste per i menu a tendina (Dropdown)
    # Estraiamo solo valori unici, ordinati e non nulli/vuoti
    lista_comuni = Manufatto.objects.values_list('comune', flat=True)\
        .exclude(comune__isnull=True).exclude(comune__exact='')\
        .distinct().order_by('comune')

    lista_depuratori = Manufatto.objects.values_list('depuratore_associato', flat=True)\
        .exclude(depuratore_associato__isnull=True).exclude(depuratore_associato__exact='')\
        .distinct().order_by('depuratore_associato')

    return render(request, 'manufatti/lista_manufatti.html', {
        'manufatti': manufatti,
        'ente_utente': ente_utente,
        # Passiamo i valori correnti per mantenerli selezionati nel form
        'query': query,
        'comune_selezionato': comune_selezionato,
        'depuratore_selezionato': depuratore_selezionato,
        # Passiamo le liste per popolare le <select>
        'lista_comuni': lista_comuni,
        'lista_depuratori': lista_depuratori,
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
        # Recuperiamo la lista di tutti i file caricati
        files = request.FILES.getlist('file')
        
        if form.is_valid():
            titolo_base = form.cleaned_data.get('titolo')
            
            for f in files:
                # Se l'utente specifica un titolo lo usiamo, altrimenti usiamo il nome del file
                titolo_finale = titolo_base if titolo_base else f.name
                Documento.objects.create(
                    manufatto=manufatto,
                    titolo=titolo_finale,
                    file=f
                )
            
            messages.success(request, f"Caricati con successo {len(files)} documenti.")
            return redirect('gestione_documenti', manufatto_id=manufatto.id)
    else:
        form = DocumentoForm()
        
    documenti = manufatto.documenti.all().order_by('-data_caricamento')
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
def risolvi_alert(request, manufatto_id):
    manufatto = get_object_or_404(Manufatto, id=manufatto_id)
    manufatto.alert_messaggio = None  # Cancella il messaggio
    manufatto.save()
    messages.success(request, f"Alert rimosso per {manufatto.nome}.")
    return redirect('dettaglio_manufatto', manufatto_id=manufatto.id)

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
    
    # Recupero parametri dalla URL (GET)
    query = request.GET.get('q', '')
    stato = request.GET.get('stato', '')
    comune_sel = request.GET.get('comune', '')

    # Queryset base
    risultati = Manufatto.objects.all().order_by('comune', 'nome')
    # Applicazione filtri
    if query:
        risultati = risultati.filter(nome__icontains=query)
    
    if stato:
        risultati = risultati.filter(stato=stato)
        
    if comune_sel:
        risultati = risultati.filter(comune=comune_sel)

    # Lista unica dei comuni per il dropdown
    lista_comuni = Manufatto.objects.values_list('comune', flat=True)\
        .exclude(comune__isnull=True).exclude(comune__exact='')\
        .distinct().order_by('comune')

    context = {
        'query': query,
        'stato': stato,
        'comune_selezionato': comune_sel,
        'lista_comuni': lista_comuni,
        'risultati': risultati,
        'ente_utente': ente_utente,
    }
    return render(request, 'manufatti/ricerca_interventi.html', context)

# --- FUNZIONE ESPORTA EXCEL ---
@login_required
def export_manufatti(request):
    manufatti = Manufatto.objects.all().select_related('info_idriche', 'info_geografiche')
    data = []

    for m in manufatti:
        idr = getattr(m, 'info_idriche', None)
        geo = getattr(m, 'info_geografiche', None)

        # Creiamo il formato "lat, lon" come richiesto dall'importatore
        coord_string = ""
        if geo and geo.latitudine and geo.longitudine:
            coord_string = f"{geo.latitudine}, {geo.longitudine}"

        row = {
            # Usiamo i nomi esatti che la funzione import_manufatti si aspetta (minuscoli o come cercati)
            'codice': m.nome,
            'comune': m.comune,
            'localita': m.localita,
            'ubicazione': m.ubicazione,
            'depuratore associato': m.depuratore_associato,
            'recapito emissario': m.recapito_emissario,
            'tipo': m.tipologia_sfioratore,
            'coordinate': coord_string,

            # Dati Idrici con nomi compatibili
            'ae civ': idr.ae_civ if idr else 0,
            'ae ind': idr.ae_ind if idr else 0,
            'ae tot': idr.ae_tot if idr else 0,
            'q civ': idr.q_civ if idr else 0,
            'q ind': idr.q_ind if idr else 0,
            'qnm': idr.qnm if idr else 0,
            'qs': idr.qs if idr else 0,
            'pavv': idr.pavv if idr else 0,
            'qs/qnm': idr.qs_qnm_ratio if idr else "-",
            'qs > pavv': idr.qs_gt_pavv if idr else "-",
            'qs/pavv': idr.qs_pavv_ratio if idr else "-",
            'tipologia': idr.tipologia_sfioro_rr6 if idr else "",
            'è conforme?': idr.e_conforme if idr else "",
            'vasca reg. regionale': idr.vasca_reg_regionale if idr else "",
            'bacino proprio (ha)': idr.bacino_proprio_ha if idr else 0,
            'q meteo in ingresso al manufatto (l/s)': idr.q_meteo_ingresso_ls if idr else 0,
            'q limite ingresso al manufatto (l/s)': idr.q_limite_ingresso_ls if idr else 0,
            'manufatto limitante': idr.manufatto_limitante if idr else "",
            'portata specifica allo scarico [l/s haimp]': idr.portata_specifica_scarico if idr else 0,
            'ha imp': idr.ha_imp if idr else 0,
            'qscolmata l/s': idr.qscolmata_ls if idr else 0,
            'vasca ptua': idr.vasca_ptua if idr else "",
            'scadenza autorizzazione provincia': idr.scadenza_autorizzazione if idr else "",
            'atto provincia n°': idr.atto_provincia_n if idr else "",
            'consorzio competente': idr.consorzio_competente if idr else "",
            'scadenza concessione consorzio': idr.scadenza_concessione if idr else "",
            'atto consorzio n°': idr.atto_consorzio_n if idr else "",
            'note autorizzazioni /concessioni': idr.note_autorizzazioni if idr else "",
        }
        data.append(row)

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export_manufatti.xlsx'
    
    # IMPORTANTE: Nominiamo il foglio 'Riassuntiva' perché l'importatore lo cerca per nome
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Riassuntiva')
    
    return response
    # 2. Crea il DataFrame e il file Excel
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=export_manufatti.xlsx'
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

# --- FUNZIONE IMPORTA EXCEL ---

# 1. FUNZIONE PER CONVERTIRE IN NUMERO IN MODO SICURO
def clean_float(value):
    """Converte errori Excel (#DIV/0!), NaN o stringhe sporche in un numero o None."""
    if pd.isna(value):
        return None
    val_str = str(value).strip().lower()
    if val_str in ['#div/0!', 'nan', 'inf', '-inf', '', 'none']:
        return None
    try:
        # Gestisce anche il caso in cui il numero sia scritto con la virgola (es: 10,5)
        return float(val_str.replace(',', '.'))
    except (ValueError, TypeError):
        return None

def clean_ratio(val):
    try:
        if pd.isna(val) or str(val).strip().lower() in ['', 'nan', 'none', '-']:
            return "-"
        f = float(str(val).replace(',', '.'))
        return "{:.2f}".format(f).replace('.', ',')
    except:
        return str(val)

# --- VISTA IMPORTAZIONE ---

@login_required
def import_manufatti(request):
    if request.method == 'POST' and request.FILES.get('myfile'):
        excel_file = request.FILES['myfile']
        try:
            xls = pd.ExcelFile(excel_file)
            # Cerca il foglio che contiene 'riassuntiva' nel nome
            target_sheet = next((s for s in xls.sheet_names if 'riassuntiva' in s.lower()), xls.sheet_names[0])
            df_raw = pd.read_excel(excel_file, sheet_name=target_sheet, header=None)
            
            df_finale = None
            # Cerca la riga di intestazione che contiene la parola 'codice'
            for i in range(min(100, len(df_raw))):
                row_values = [str(val).lower().strip() for val in df_raw.iloc[i].values]
                if 'codice' in row_values:
                    df_finale = pd.read_excel(excel_file, sheet_name=target_sheet, header=i)
                    df_finale.columns = [str(c).lower().strip() for c in df_finale.columns]
                    break

            if df_finale is not None:
                codici_presenti_nel_file = []
                count_created = 0
                count_updated = 0
                
                # Funzione interna per cercare colonne con nomi simili
                def find_in_row(row, keys):
                    for k in keys:
                        val = row.get(k.lower().strip())
                        if val is not None and str(val).lower() != 'nan': 
                            return str(val).strip()
                    return None

                for _, row in df_finale.iterrows():
                    codice = str(row.get('codice', '')).strip()
                    if not codice or codice == 'nan': 
                        continue

                    codici_presenti_nel_file.append(codice)

                    # --- 1. RECUPERO DATI PER CONFRONTO ---
                    nuovo_atto_prov = find_in_row(row, ['atto provincia n°', 'atto provincia n', 'atto provincia'])
                    nuovo_atto_cons = find_in_row(row, ['atto consorzio n°', 'atto consorzio n', 'atto consorzio'])
                    
                    # Logica Stato (SOLO colonna Note)
                    testo_note = str(row.get('note', '')).lower()
                    stato_calcolato = 'DISMESSO' if 'dismesso' in testo_note else 'IN ESERCIZIO'

                    # --- 2. GESTIONE ALERT E SALVATAGGIO MANUFATTO ---
                    manufatto, created = Manufatto.objects.get_or_create(nome=codice)
                    alert_testo = ""

                    if not created:
                        idriche_vecchie = getattr(manufatto, 'info_idriche', None)
                        if idriche_vecchie:
                            # Confronto Provincia
                            if idriche_vecchie.atto_provincia_n and nuovo_atto_prov and idriche_vecchie.atto_provincia_n != nuovo_atto_prov:
                                alert_testo += f"⚠️ Cambio Atto Provincia: da {idriche_vecchie.atto_provincia_n} a {nuovo_atto_prov}. "
                            
                            # Confronto Consorzio
                            if idriche_vecchie.atto_consorzio_n and nuovo_atto_cons and idriche_vecchie.atto_consorzio_n != nuovo_atto_cons:
                                alert_testo += f"⚠️ Cambio Atto Consorzio: da {idriche_vecchie.atto_consorzio_n} a {nuovo_atto_cons}. "

                    # Aggiorna campi base Manufatto
                    manufatto.stato = stato_calcolato
                    manufatto.comune = row.get('comune')
                    manufatto.localita = row.get('localita')
                    manufatto.ubicazione = row.get('ubicazione')
                    manufatto.depuratore_associato = row.get('depuratore associato')
                    manufatto.recapito_emissario = row.get('recapito emissario')
                    manufatto.tipologia_sfioratore = row.get('tipo')
                    manufatto.alert_messaggio = alert_testo if alert_testo else None # Salva l'alert nel DB
                    manufatto.save()

                    if created: count_created += 1
                    else: count_updated += 1

                    # --- 3. AGGIORNAMENTO INFO IDRICHE (Senza PTUA e Note) ---
                    info_idriche.objects.update_or_create(
                        manufatto=manufatto,
                        defaults={
                            'ae_civ': clean_float(row.get('ae civ')),
                            'ae_ind': clean_float(row.get('ae ind')),
                            'ae_tot': clean_float(row.get('ae tot')),
                            'q_civ': clean_float(row.get('q civ [l/s]')),
                            'q_ind': clean_float(row.get('q ind [l/s]')),
                            'qnm': clean_float(row.get('qnm [l/s]')),
                            'qs': clean_float(row.get('qs [l/s]')),
                            'pavv': clean_float(row.get('pavv [l/s]')),
                            'bacino_proprio_ha': clean_float(row.get('bacino proprio (ha)')),
                            'q_meteo_ingresso_ls': clean_float(row.get('q meteo in ingresso al manufatto (l/s)')),
                            'q_limite_ingresso_ls': clean_float(row.get('q limite ingresso al manufatto (l/s)')),
                            'portata_specifica_scarico': clean_float(row.get('portata specifica allo scarico [l/s haimp]')),
                            'ha_imp': clean_float(row.get('sup imp [ha]')),
                            'qscolmata_ls': clean_float(row.get('qscolmata [l/s]')),
                            'qs_qnm_ratio': row.get('qs/qnm'),
                            'qs_gt_pavv': row.get('qs > pavv'),
                            'qs_pavv_ratio': row.get('qs/pavv'),
                            'tipologia_sfioro_rr6': row.get('tipologia'),
                            'e_conforme': row.get('è conforme?'),
                            'vasca_reg_regionale': row.get('vasca rr'),
                            'scadenza_autorizzazione': row.get('scadenza autorizzazione provincia'),
                            'atto_provincia_n': nuovo_atto_prov,
                            'consorzio_competente': find_in_row(row, ['consorzio competente', 'consorzio']),
                            'atto_consorzio_n': nuovo_atto_cons,
                            'sistema_rilevamento': str(row.get('rilevamento', '')).strip().upper(),
                            'scadenza_concessione': row.get('scadenza concessione consorzio'),
                            'codice_provincia_manufatto': row.get('cod prov manufa sf'),
                            'codice_provincia_scarico': row.get('cod prov scarico sf'),
                            'bacino_maggiore_10000': row.get("10'000 ae"),
                            'qs_maggiore_20': row.get('qs>20'),
                            'scarica_lago_suolo': row.get('scarica a lago o suolo?'),
                            'manufatto_limitante': row.get('manufatto limitante'),
                        }
                    )

                    # --- 4. COORDINATE GPS ---
                    coord_raw = str(row.get('coordinate', '')).strip()
                    if coord_raw and ',' in coord_raw and coord_raw != 'nan':
                        try:
                            lat_s, lon_s = coord_raw.split(',')
                            info_geografiche.objects.update_or_create(
                                manufatto=manufatto,
                                defaults={
                                    'latitudine': float(lat_s.strip()),
                                    'longitudine': float(lon_s.strip())
                                }
                            )
                        except: pass

                # --- 5. RIMOZIONE MANUFATTI NON PRESENTI ---
                Manufatto.objects.exclude(nome__in=codici_presenti_nel_file).delete()

                messages.success(request, f"Importazione riuscita. Creati: {count_created}, Aggiornati: {count_updated}.")
                return redirect('lista_manufatti')
                
        except Exception as e:
            messages.error(request, f"Errore durante l'importazione: {str(e)}")
            
        return redirect('lista_manufatti')
    return render(request, 'manufatti/upload_excel.html')