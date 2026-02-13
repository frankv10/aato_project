import os
from django.db import models


class Manufatto(models.Model):
    nome = models.CharField(max_length=100) 
    stato = models.CharField(
        max_length=50, 
        choices=[
            ('PROGRAMMATO', 'PROGRAMMATO'),
            ('IN ESECUZIONE', 'IN ESECUZIONE'),
            ('COMPLETATO', 'COMPLETATO') # Aggiunto per coerenza con i badge visti prima
        ],
        default='IN ESECUZIONE'  # <--- IMPOSTA IL DEFAULT QUI
    )
    data_creazione = models.DateTimeField(auto_now_add=True)

    # Dati anagrafici principali (spostati da info_geografiche per coerenza)
    comune = models.CharField(max_length=100, null=True, blank=True)
    localita = models.CharField(max_length=100, null=True, blank=True)
    ubicazione = models.CharField(max_length=255, null=True, blank=True)

    # Dati aggiuntivi dal CSV
    depuratore_associato = models.CharField(max_length=255, null=True, blank=True)
    recapito_emissario = models.CharField(max_length=255, null=True, blank=True)
    tipologia_sfioratore = models.CharField(max_length=100, null=True, blank=True)  # 'TIPO'

    def __str__(self):
        return self.nome


class info_idriche(models.Model):
    manufatto = models.OneToOneField('Manufatto', on_delete=models.CASCADE, related_name='info_idriche')

    # Campi COLONNE M-AG (già definiti)
    ae_civ = models.FloatField(null=True, blank=True, verbose_name="AE CIV")
    ae_ind = models.FloatField(null=True, blank=True, verbose_name="AE IND")
    ae_tot = models.FloatField(null=True, blank=True, verbose_name="AE TOT")
    q_civ = models.FloatField(null=True, blank=True, verbose_name="Q CIV")
    q_ind = models.FloatField(null=True, blank=True, verbose_name="Q IND")
    qnm = models.FloatField(null=True, blank=True, verbose_name="Qnm")
    qs = models.FloatField(null=True, blank=True, verbose_name="Qs")
    pavv = models.FloatField(null=True, blank=True, verbose_name="Pavv")
    qs_qnm_ratio = models.CharField(max_length=50, null=True, blank=True, verbose_name="Qs/Qnm")
    qs_gt_pavv = models.CharField(max_length=100, null=True, blank=True, verbose_name="Qs > Pavv")
    qs_pavv_ratio = models.CharField(max_length=50, null=True, blank=True, verbose_name="Qs/Pavv")
    tipologia_sfioro_rr6 = models.CharField(max_length=50, null=True, blank=True, verbose_name="TIPOLOGIA")
    e_conforme = models.CharField(max_length=50, null=True, blank=True, verbose_name="è conforme?")
    vasca_reg_regionale = models.CharField(max_length=100, null=True, blank=True, verbose_name="Vasca Reg. Regionale")
    bacino_proprio_ha = models.FloatField(null=True, blank=True, verbose_name="Bacino proprio (ha)")
    q_meteo_ingresso_ls = models.FloatField(null=True, blank=True,
                                            verbose_name="Q meteo in ingresso al manufatto (l/s)")
    q_limite_ingresso_ls = models.FloatField(null=True, blank=True, verbose_name="Q limite ingresso al manufatto (l/s)")
    manufatto_limitante = models.CharField(max_length=100, null=True, blank=True, verbose_name="Manufatto limitante")
    portata_specifica_scarico = models.FloatField(null=True, blank=True,
                                                  verbose_name="Portata specifica allo scarico [l/s haimp]")
    ha_imp = models.FloatField(null=True, blank=True, verbose_name="ha imp")
    qscolmata_ls = models.FloatField(null=True, blank=True, verbose_name="Qscolmata l/s")

    # --- 🌟 NUOVI CAMPI AGGIUNTI (COLONNE AH-AN) 🌟 ---
    vasca_ptua = models.CharField(max_length=100, null=True, blank=True, verbose_name="Vasca PTUA")  # Colonna AI
    scadenza_autorizzazione = models.CharField(max_length=100, null=True, blank=True,
                                               verbose_name="Scadenza autorizzazione Provincia")  # Colonna AJ
    atto_provincia_n = models.CharField(max_length=100, null=True, blank=True,
                                        verbose_name="Atto Provincia n°")  # Colonna AK
    consorzio_competente = models.CharField(max_length=255, null=True, blank=True,
                                            verbose_name="Consorzio competente")  # Colonna AL
    scadenza_concessione = models.CharField(max_length=100, null=True, blank=True,
                                            verbose_name="Scadenza concessione Consorzio")  # Colonna AM
    atto_consorzio_n = models.CharField(max_length=100, null=True, blank=True,
                                        verbose_name="Atto Consorzio n°")  # Colonna AN
    note_autorizzazioni = models.TextField(null=True, blank=True,
                                           verbose_name="Note Autorizzazioni /Concessioni")  # Colonna AO

    def __str__(self):
        return f"Info idriche di {self.manufatto.nome}"


class info_geografiche(models.Model):
    manufatto = models.OneToOneField('Manufatto', on_delete=models.CASCADE, related_name='info_geografiche')
    latitudine = models.FloatField(null=True, blank=True)
    longitudine = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"info geografiche {self.manufatto.nome}"


class Documento(models.Model):
    manufatto = models.ForeignKey(
        Manufatto,
        on_delete=models.SET_NULL,
        related_name='documenti',
        null=True,
        blank=True
    )
    titolo = models.CharField(max_length=200)
    file = models.FileField(upload_to='documenti/%Y/%m/%d/')
    data_caricamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titolo