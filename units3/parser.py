# -*- coding: utf-8 -*-
import lxml.html


class Parser:

    def __init__(self, html):
        self.root = lxml.html.fromstring(html)

    def home(self):
        titolo = str(self.root.xpath('//table[2]/tbody/tr/td/div/text()')[0])

        nome = titolo.split(' - ')[0]
        matricola = titolo.split(' - ')[1][6:-1]

        return [{'nome': nome, 'matricola': matricola}]

    def libretto(self):
        # Select tr tags (skip the 1st) from table with class "detail_table"
        rows = self.root.xpath('//table[@class="detail_table"]' +
                               '//tr[position()>1]')

        result = []

        for row in rows:
            # Get text content from td tags with text inside
            # or with a link with text inside
            cells = [td for td in row.xpath('td/text() | td/a/text()')
                     if td.strip()]

            # Unpack codice, nome from cell
            codice, nome = cells[1].split(' - ')

            esame = {
                'anno_di_corso': int(cells[0]),
                'nome': nome,
                'codice': codice,
                'crediti': int(cells[2]),
                'anno_frequenza': cells[3],
            }

            # Check if exam was passed
            if row.xpath('td[img/@alt="Superata"]'):
                esame['superato'] = True
                esame['voto'], esame['data'] = cells[4].split(u'\u00a0-\u00a0')
            else:
                esame['superato'] = False

            result.append(esame)

        return result

    def pagamenti(self):
        # Select tr tags (skip the 1st) from table with class "detail_table"
        rows = self.root.xpath('//table[@class="detail_table"]' +
                               '//tr[position()>2]')

        result = []

        for idx, row in enumerate(rows):
            # Get text content from td tags with text inside
            # or with a link with text inside
            cells = [td for td in row.xpath('td/text() | td/a/text()')
                     if td.strip()]

            # This is needed to handle the case of multiple fees,
            # which is managed through rowspans...
            if len(cells) == 1:
                result[idx - 1]['descrizione'] += " | " + cells[0]
                continue

            # Check if fee was payed
            if row.xpath('td[img/@alt="pagamento confermato"]'):
                pagata = True
            else:
                pagata = False

            tassa = {
                'codice_fattura': int(cells[0]),
                'codice_bollettino': cells[1],
                'anno': cells[2],
                'descrizione': cells[3],
                'data_scadenza': cells[4],
                'importo': float(cells[5][2:].replace(',', '.')),
                'pagata': pagata
            }

            result.append(tassa)

        return result

    def prenotazione_appelli(self):
        # Select tr tags (skip the 1st) from table with class "detail_table"
        rows = self.root.xpath('//table[@class="detail_table"]' +
                               '//tr[position()>1]')

        result = []

        # Skip the first line, garbage
        for row in rows:
            # Check if subscription is still opened
            if row.xpath('td[img/@alt="iscrizioni chiuse"]'):
                iscrizioni_aperte = False
            else:
                iscrizioni_aperte = True

            cells = [td for td in row.xpath('td/text() | td/a/text()')
                     if td.strip()]

            appello = {
                'nome_corso': cells[0],
                'data_esame': cells[1],
                'periodo_iscrizione': {
                    'inizio': cells[2],
                    'fine': cells[3]
                },
                'descrizione': cells[4],
                'sessioni': cells[5],
                'iscrizioni_aperte': iscrizioni_aperte
            }

            result.append(appello)

        return result
