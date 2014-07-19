# -*- coding: utf-8 -*-
import lxml.html


class Parser:

    def __init__(self, html):
        self.root = lxml.html.fromstring(html)

    def prenotazioni_effettuate(self):
        tables = self.root.xpath('//table[@class="detail_table"]')

        result = []

        for table in tables:
            nome_corso, codice, descrizione = table.xpath('tr/th/text()')[0] \
                .split(' - ')
            numero_iscrizione = table.xpath('tr/th/a/text()')[0].split(': ')[1]

            date = table.xpath('tr[6]/td[1]')[0].text_content()
            time = table.xpath('tr[6]/td[2]')[0].text_content()
            place = table.xpath('tr[6]/td[3]')[0].text_content()

            result.append(
                {'nome_corso': str(nome_corso),
                 'codice_corso': str(codice[1:-1]),
                 'descrizione': str(descrizione),
                 'numero_iscrizione': str(numero_iscrizione),
                 'data': str(date),
                 'ora': str(time),
                 'luogo': str(place) if place else None
                 }
            )

        return result

    def home(self):
        # Custom XPath, thanks Chrome DevTools
        titolo = str(self.root.xpath('//table[2]/tbody/tr/td/div/text()')[0])

        # Unpack and capitalize first letter of name
        nome = titolo.split(' - ')[0].title()
        matricola = titolo.split(' - ')[1][6:-1]

        # Self-explaining
        info = [x.strip() for x
                in self.root.xpath('//td[@class="tplMaster"]/text()')
                if x.strip()]

        result = {
            'nome': str(nome),
            'matricola': str(matricola),
            'tipo_di_corso': str(info[0]),
            'profilo_studente': str(info[1]),
            'anno_di_corso': int(info[2]),
            'data_immatricolazione': str(info[3]),
            'corso_di_studio': str(info[4]),
            'ordinamento': str(info[5]),
            'percorso_di_studio': str(info[6])
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
            cells = [td for td in row.xpath('td/text() | td/a/text()')
                     if td.strip()]

            # Unpack codice, nome from cell
            codice, nome = cells[1].split(' - ')

            esame = {
                'anno_di_corso': int(cells[0]),
                'nome': str(nome),
                'codice': str(codice),
                'crediti': int(cells[2]),
                'anno_frequenza': str(cells[3]),
            }

            # Check if exam was passed
            if row.xpath('td[img/@alt="Superata"]'):
                esame['superato'] = True
                splitted_votodata = cells[4].split(u'\u00a0-\u00a0')
                esame['voto'] = str(splitted_votodata[0])
                esame['data'] = str(splitted_votodata[1])
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
                'codice_bollettino': str(cells[1]),
                'anno': str(cells[2]),
                'descrizione': str(cells[3]),
                'data_scadenza': str(cells[4]),
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
                'nome_corso': str(cells[0]),
                'data_esame': str(cells[1]),
                'periodo_iscrizione': {
                    'inizio': str(cells[2]),
                    'fine': str(cells[3])
                },
                'descrizione': str(cells[4]),
                'sessioni': str(cells[5]),
                'iscrizioni_aperte': iscrizioni_aperte
            }

            result.append(appello)

        return result
