import os
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from manufatti.models import Manufatto, info_idriche, info_geografiche


# Funzione helper per convertire in float in modo sicuro
def safe_float(value, default=None):
    if value is None or pd.isna(value):
        return default
    try:
        # Tenta di convertire, sostituendo eventuali virgole
        return float(str(value).replace(',', '.').strip())
    except (ValueError, TypeError):
        return default


class Command(BaseCommand):
    help = 'Importa i manufatti (sfiori) dal file Excel "tabella_Sfiori.xlsx"'

    def handle(self, *args, **options):

        management_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_name = 'tabella_Sfiori.xlsx'
        file_path = os.path.join(management_dir, file_name)
        sheet_name = 'Tabella riassuntiva'

        self.stdout.write(self.style.NOTICE(f"Inizio importazione da: {file_path} (Foglio: {sheet_name})"))

        try:
            # Legge il file Excel. header=2 significa che le intestazioni sono nella TERZA riga
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=2)

            df = df.where(pd.notna(df), None)

            contatore_creati = 0
            contatore_aggiornati = 0

            for index, row in df.iterrows():
                codice_manufatto = row.get('Codice')
                if not codice_manufatto:
                    continue

                # Mappatura Manufatto
                manufatto_data = {
                    'stato': 'PROGRAMMATO',
                    'comune': row.get('COMUNE'),
                    'localita': row.get('LOCALITA'),
                    'ubicazione': row.get('UBICAZIONE'),
                    'depuratore_associato': row.get('DEPURATORE ASSOCIATO'),
                    'recapito_emissario': row.get('RECAPITO EMISSARIO'),
                    'tipologia_sfioratore': row.get('TIPO'),
                }
                manufatto, created = Manufatto.objects.update_or_create(
                    nome=codice_manufatto,
                    defaults=manufatto_data
                )

                # Mappatura info_idriche (M-AG)
                idriche_data = {
                    'ae_civ': safe_float(row.get('AE CIV')),
                    'ae_ind': safe_float(row.get('AE IND')),
                    'ae_tot': safe_float(row.get('AE TOT')),
                    'q_civ': safe_float(row.get('Q CIV')),
                    'q_ind': safe_float(row.get('Q IND')),
                    'qnm': safe_float(row.get('Qnm')),
                    'qs': safe_float(row.get('Qs')),
                    'pavv': safe_float(row.get('Pavv')),
                    'qs_qnm_ratio': row.get('Qs/Qnm'),
                    'qs_gt_pavv': row.get('Qs > Pavv'),
                    'qs_pavv_ratio': row.get('Qs/Pavv'),
                    'tipologia_sfioro_rr6': row.get('TIPOLOGIA'),
                    'e_conforme': row.get('è conforme?'),
                    'vasca_reg_regionale': row.get('Vasca Reg. Regionale'),
                    'bacino_proprio_ha': safe_float(row.get('Bacino proprio (ha)')),
                    'q_meteo_ingresso_ls': safe_float(row.get('Q meteo in ingresso al manufatto (l/s)')),
                    'q_limite_ingresso_ls': safe_float(row.get('Q limite ingresso al manufatto (l/s)')),
                    'manufatto_limitante': row.get('Manufatto limitante'),
                    'portata_specifica_scarico': safe_float(row.get('Portata specifica allo scarico [l/s haimp]')),
                    'ha_imp': safe_float(row.get('ha imp')),
                    'qscolmata_ls': safe_float(row.get('Qscolmata l/s')),

                    # --- 🌟 NUOVI CAMPI AGGIUNTI (COLONNE AH-AN) 🌟 ---
                    'vasca_ptua': row.get('Vasca PTUA'),
                    'scadenza_autorizzazione': row.get('Scadenza autorizzazione Provincia'),
                    'atto_provincia_n': row.get('Atto Provincia n°'),
                    'consorzio_competente': row.get('Consorzio competente'),
                    'scadenza_concessione': row.get('Scadenza concessione Consorzio'),
                    'atto_consorzio_n': row.get('Atto Consorzio n°'),
                    'note_autorizzazioni': row.get('Note Autorizzazioni /Concessioni'),
                }
                info_idriche.objects.update_or_create(
                    manufatto=manufatto,
                    defaults=idriche_data
                )

                # Mappatura info_geografiche
                lat_val, lon_val = None, None
                coordinate_str = row.get('Coordinate')
                if coordinate_str:
                    try:
                        coords = str(coordinate_str).split(',')
                        if len(coords) == 2:
                            lat_val = safe_float(coords[0])
                            lon_val = safe_float(coords[1])
                    except Exception:
                        pass

                info_geografiche.objects.update_or_create(
                    manufatto=manufatto,
                    defaults={'latitudine': lat_val, 'longitudine': lon_val}
                )

                if created:
                    contatore_creati += 1
                else:
                    contatore_aggiornati += 1

            self.stdout.write(self.style.SUCCESS(f"Importazione completata!"))
            self.stdout.write(self.style.SUCCESS(f"Manufatti creati: {contatore_creati}"))
            self.stdout.write(self.style.WARNING(f"Manufatti aggiornati: {contatore_aggiornati}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File non trovato: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Errore durante l'importazione: {e}"))
            self.stdout.write(self.style.ERROR(
                f"Controlla che 'pandas' e 'openpyxl' siano installati e che il nome del foglio ('{sheet_name}') sia corretto."))