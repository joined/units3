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
            esame = {'anno_di_corso': int(row.contents[1].string),
                     'nome': row.contents[2].string.split(' - ')[1],
                     'codice': row.contents[2].string.split(' - ')[0],
                     'crediti': int(row.contents[7].string),
                     'anno_frequenza': row.contents[9].string,
                     }

            # Verify if "voto - data" is present, they could be not
            if row.contents[10].string is None:
                esame['superato'] = False
            else:
                esame['superato'] = True
                esame['voto'], esame['data'] = row.contents[10].string.split(u'\u00a0-\u00a0')

            result.append(esame)

        return result

    def pagamenti(self):
        rows_list = self.soup.find('table', {'class': 'detail_table'}).find_all('tr')

        result = []

        # Skip the first line, garbage
        for row in rows_list[1:]:
            if len(row.contents) > 3:
                # Convert to float the value
                importo = float(row.contents[6].string[2:].replace(',', '.'))

                # If there's the green semaphore the fee is payed
                if ('semaf_v' in str(row.contents[7])):
                    stato = 'pagato'
                # Otherwise not
                else:
                    stato = 'da_pagare'

                tassa = {'codice_fattura': int(row.contents[1].string),
                         'codice_bollettino': int(row.contents[2].string),
                         'anno': row.contents[3].string,
                         'descrizione': row.contents[4].string,
                         'data_scadenza': row.contents[5].string,
                         'importo': importo,
                         'stato': stato
                         }

                result.append(tassa)

        return result