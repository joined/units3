# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html)

    def libretto(self):
        # List of of table rows I need
        rows_list = self.soup.find('table', {'class': 'detail_table'}).find_all('tr')

        result = []

        # Skip the first line, garbage
        for row in rows_list[1:]:
            # Row in a nice list format
            f_row = row.get_text('|', strip=True).split('|')

            codice, nome = f_row[1].split(' - ')

            esame = {'anno_di_corso': int(f_row[0]),
                     'nome': nome,
                     'codice': codice,
                     'crediti': int(f_row[2]),
                     'anno_frequenza': f_row[3],
                     }

            # Verify if "voto - data" is present, they could be not
            if len(f_row) < 5:
                esame['superato'] = False
            else:
                esame['superato'] = True
                esame['voto'], esame['data'] = f_row[4].split(u'\u00a0-\u00a0')

            result.append(esame)

        return result

    def pagamenti(self):
        rows_list = self.soup.find('table', {'class': 'detail_table'}).find_all('tr')

        result = []

        # Skip the first line, garbage
        for row in rows_list[1:]:
            if len(row.contents) > 3:
                # If there's the green semaphore the fee is payed
                stato = 'pagato' if 'semaf_v' in str(row.contents[7]) else 'da_pagare'

                # Row in a nice list format
                f_row = row.get_text('|', strip=True).split('|')

                # Convert to float the value
                importo = float(f_row[5][2:].replace(',', '.'))

                tassa = {'codice_fattura': int(f_row[0]),
                         'codice_bollettino': f_row[1],
                         'anno': f_row[2],
                         'descrizione': f_row[3],
                         'data_scadenza': f_row[4],
                         'importo': importo,
                         'stato': stato
                         }

                result.append(tassa)

        return result

    def prenotazione_appelli(self):
        rows_list = self.soup.find('table', {'class': 'detail_table'}).find_all('tr')

        result = []

        # Skip the first line, garbage
        for row in rows_list[1:]:
            stato = 'chiuso' if 'chiuse' in str(row.contents[1]) else 'aperto'

            # Row in a nice list format
            f_row = row.get_text('|', strip=True).split('|')

            appello = {'nome_corso': f_row[0],
                       'data': f_row[1],
                       'inizio_periodo_iscrizione': f_row[2],
                       'termine_periodo_iscrizione': f_row[3],
                       'descrizione': f_row[4],
                       'sessioni': f_row[5],
                       'stato': stato
                       }

            result.append(appello)

        return result
