import os
from django.db import models


class Manufatto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    stato = models.CharField(
        max_length=50, 
        choices=[
                ('IN ESERCIZIO', 'IN ESERCIZIO'),
                ('PROGRAMMATO', 'PROGRAMMATO'),
        ],
        default='IN ESERCIZIO'
    )
    data_creazione = models.DateTimeField(auto_now_add=True)

    comune = models.CharField(max_length=100, null=True, blank=True)
    localita = models.CharField(max_length=100, null=True, blank=True)
    ubicazione = models.CharField(max_length=255, null=True, blank=True)
    depuratore_associato = models.CharField(max_length=255, null=True, blank=True)
    recapito_emissario = models.CharField(max_length=255, null=True, blank=True)
    tipologia_sfioratore = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        # Questo garantisce che ogni query sia ordinata per Comune e poi per Nome
        ordering = ['comune', 'nome']

    def __str__(self):
        return self.nome


class info_idriche(models.Model):
    manufatto = models.OneToOneField('Manufatto', on_delete=models.CASCADE, related_name='info_idriche')
    ae_civ = models.FloatField(null=True, blank=True, verbose_name="AE CIV")
    ae_ind = models.FloatField(null=True, blank=True, verbose_name="AE IND")
    ae_tot = models.FloatField(null=True, blank=True, verbose_name="AE TOT")
    q_civ = models.FloatField(null=True, blank=True, verbose_name="Q CIV")
    q_ind = models.FloatField(null=True, blank=True, verbose_name="Q IND")
    qnm = models.FloatField(null=True, blank=True, verbose_name="Qnm")
    qs = models.FloatField(null=True, blank=True, verbose_name="Qs")
    pavv = models.FloatField(null=True, blank=True, verbose_name="Pavv")
    qs_qnm_ratio = models.CharField(max_length=50, null=True, blank=True)
    qs_gt_pavv = models.CharField(max_length=100, null=True, blank=True)
    qs_pavv_ratio = models.CharField(max_length=50, null=True, blank=True)
    tipologia_sfioro_rr6 = models.CharField(max_length=50, null=True, blank=True)
    e_conforme = models.CharField(max_length=50, null=True, blank=True)
    vasca_reg_regionale = models.CharField(max_length=100, null=True, blank=True)
    bacino_proprio_ha = models.FloatField(null=True, blank=True)
    q_meteo_ingresso_ls = models.FloatField(null=True, blank=True)
    q_limite_ingresso_ls = models.FloatField(null=True, blank=True)
    manufatto_limitante = models.CharField(max_length=100, null=True, blank=True)
    portata_specifica_scarico = models.FloatField(null=True, blank=True)
    ha_imp = models.FloatField(null=True, blank=True)
    qscolmata_ls = models.FloatField(null=True, blank=True)
    vasca_ptua = models.CharField(max_length=100, null=True, blank=True)
    scadenza_autorizzazione = models.CharField(max_length=100, null=True, blank=True)
    atto_provincia_n = models.CharField(max_length=100, null=True, blank=True)
    consorzio_competente = models.CharField(max_length=255, null=True, blank=True)
    scadenza_concessione = models.CharField(max_length=100, null=True, blank=True)
    atto_consorzio_n = models.CharField(max_length=100, null=True, blank=True)
    note_autorizzazioni = models.TextField(null=True, blank=True)

class info_geografiche(models.Model):
    manufatto = models.OneToOneField('Manufatto', on_delete=models.CASCADE, related_name='info_geografiche')
    latitudine = models.FloatField(null=True, blank=True)
    longitudine = models.FloatField(null=True, blank=True)

class Documento(models.Model):
    manufatto = models.ForeignKey(Manufatto, on_delete=models.SET_NULL, related_name='documenti', null=True, blank=True)
    titolo = models.CharField(max_length=200)
    file = models.FileField(upload_to='documenti/%Y/%m/%d/')
    data_caricamento = models.DateTimeField(auto_now_add=True)

def ente_utente_context(request):
    if request.user.is_authenticated:
        try:
            # Recupera l'ente dal profilo collegato all'utente loggato
            return {'ente_utente': request.user.profilo.ente}
        except:
            return {'ente_utente': 'TEA'} # Fallback di sicurezza
    return {'ente_utente': None}