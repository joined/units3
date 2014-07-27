# -*- coding: utf-8 -*-
import lxml.html
from time import strptime, strftime


class Parser:

    def __init__(self, html):
        self.root = lxml.html.fromstring(html)

    def prenotazioni_effettuate(self):
        tables = self.root.xpath('//table[@class="detail_table"]')

        result = []

        for table in tables:
            nome_corso, codice, descrizione = \
                table.xpath('tr/th/text()')[0].split(' - ')

            numero_iscrizione = table.xpath('tr/th/a/text()')[0].split(': ')[1]

            date_time_place = table.xpath('tr[6]/td/text()')

            conv = strptime(date_time_place[0], "%d/%m/%Y")
            date = strftime("%Y/%m/%d", conv)
            time = date_time_place[1]
            place = date_time_place[2]

            result.append(
                {'nome_corso': nome_corso,
                 'codice_corso': codice[1:-1],
                 'descrizione': descrizione,
                 'numero_iscrizione': str(numero_iscrizione),
                 'data': str(date),
                 'ora': str(time),
                 'luogo': str(place) if place else None
                 }
            )

        return result

    def home(self):
        # Custom XPath, thanks Chrome DevTools
        titolo = self.root.xpath('//table[2]/tbody/tr/td/div/text()')[0]

        # Unpack and capitalize first letter of name
        nome = titolo.split(' - ')[0].title()
        matricola = titolo.split(' - ')[1][6:-1]

        # Self-explaining
        info = [x.strip() for x
                in self.root.xpath('//td[@class="tplMaster"]/text()')
                if x.strip()]

        conv = strptime(info[3], "%d/%m/%Y")
        data_immatricolazione = strftime("%Y/%m/%d", conv)

        result = {
            'nome': nome,
            'matricola': matricola,
            'tipo_di_corso': info[0],
            'profilo_studente': info[1],
            'anno_di_corso': int(info[2]),
            'data_immatricolazione': data_immatricolazione,
            'corso_di_studio': info[4],
            'ordinamento': info[5],
            'percorso_di_studio': info[6]
        }

        return result

    def libretto(self):
        # Select tr tags (skip the 1st) from table with class "detail_table"
        rows = self.root.xpath('//table[@class="detail_table"]' +
                               '//tr[position()>1]')

        result = []

        for row in rows:
            # Get text content from td tags with text inside
            # or with a link with text inside
            cells = [td.strip() for td
                     in row.xpath('td/text() | td/a/text()')
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
                conv = strptime(esame['data'], "%d/%m/%Y")
                esame['data'] = strftime("%Y/%m/%d", conv)
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
            cells = [td.strip() for td
                     in row.xpath('td/text() | td/a/text()')
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

            conv = strptime(cells[4], "%d/%m/%Y")
            data_scadenza = strftime("%Y/%m/%d", conv)

            tassa = {
                'codice_fattura': int(cells[0]),
                'codice_bollettino': cells[1],
                'anno': cells[2],
                'descrizione': cells[3],
                'data_scadenza': data_scadenza,
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

            cells = [td.strip() for td
                     in row.xpath('td/text() | td/a/text()')
                     if td.strip()]

            data_esame = strftime("%Y/%m/%d", strptime(cells[1], "%d/%m/%Y"))
            inizio_isc = strftime("%Y/%m/%d", strptime(cells[2], "%d/%m/%Y"))
            fine_isc = strftime("%Y/%m/%d", strptime(cells[3], "%d/%m/%Y"))

            appello = {
                'nome_corso': cells[0],
                'data_esame': data_esame,
                'periodo_iscrizione': {
                    'inizio': inizio_isc,
                    'fine': fine_isc
                },
                'descrizione': cells[4],
                'sessioni': cells[5],
                'iscrizioni_aperte': iscrizioni_aperte
            }

            result.append(appello)

        return result
