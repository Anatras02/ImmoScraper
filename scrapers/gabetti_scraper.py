import datetime
import re

import numpy
import pandas as pd

from scrapers.abstract_scraper import AbstractScraper


class GabettiScraper(AbstractScraper):
    BASE_URL = "https://www.gabetti.it"
    URL = BASE_URL + "/casa/vendita/milano?page={page}"
    NUMERO_PAGINA_INIZIALE = 33

    def _is_fine_delle_pagine(self, bs4_page):
        """
        Determina se la pagina corrente è l'ultima pagina di annunci disponibile sul sito.

        :param bs4_page: L'oggetto BeautifulSoup della pagina web corrente.
        :return: True se è l'ultima pagina, altrimenti False.
        """
        if bs4_page.find("div", {"class": "error-page___text"}):
            return True

        return False

    def _clean_prezzo(self, prezzo: str) -> float | None:
        """
        Pulisce e converte la stringa del prezzo in un valore float. Se il prezzo è "Tratt. Riservata",
        viene restituito NaN.

        :param prezzo: La stringa del prezzo da pulire.
        :return: Il prezzo come un float o NaN se è "Tratt. Riservata".
        """
        if prezzo == "Tratt. Riservata":
            return numpy.nan

        return super()._clean_prezzo(prezzo)

    def _get_riferimento(self, bs4_page) -> str:
        """
        Estrae il riferimento dell'annuncio dalla pagina.

        :param bs4_page: L'oggetto BeautifulSoup della pagina dell'annuncio.
        :return: La stringa del riferimento dell'annuncio.
        """
        pattern = re.compile('codice annuncio')
        label = bs4_page.find('span', {"class": 'infos-real-estate-detail__label'}, string=pattern)

        if label:
            value = label.find_next_sibling('span', class_='infos-real-estate-detail__value').text
            if value:
                return value

        return ""

    def _get_annunci_dict(self):
        """
        Estrae e restituisce un DataFrame di annunci da Gabetti. Ogni annuncio viene estratto
        e le sue informazioni vengono pulite e convertite nei tipi di dati appropriati.

        :return: Un DataFrame contenente tutti gli annunci estratti.
        """
        numero_pagina = self.NUMERO_PAGINA_INIZIALE
        annunci_totali = []

        annuncio_id = 1
        while page := self._get_pagina(numero_pagina):
            annunci = page.find_all("div", {"class": "box-description-house"})
            for annuncio in annunci:
                annuncio_dict = {}

                link = self.BASE_URL + annuncio.find("a", {"class": "real_estate_link"})["href"]
                if not link:
                    continue

                pagina_annuncio = self._get_pagina(url=link)
                if not pagina_annuncio:
                    continue

                annuncio_dict["riferimento"] = int(self._get_riferimento(pagina_annuncio))
                annuncio_dict["agenzia"] = self.id
                annuncio_dict["link"] = link
                annuncio_dict["latitudine"] = self._clean_coordinate(
                    pagina_annuncio.find("div", {"id": "map-detail"})["data-lat"])
                annuncio_dict["longitudine"] = self._clean_coordinate(
                    pagina_annuncio.find("div", {"id": "map-detail"})["data-lng"])
                annuncio_dict["prezzo"] = self._clean_prezzo(
                    pagina_annuncio.find("span", {"class": "price"}).text)
                annuncio_dict["mq"] = self._clean_mq(pagina_annuncio.find("span", {"class": "icon-square-meters"}).text)
                annuncio_dict["locali"] = self._clean_locali(pagina_annuncio.find("span", {"class": "icon-room"}).text)
                annuncio_dict["data_ultima_modifica_prezzo"] = datetime.datetime.now()

                annunci_totali.append(annuncio_dict)
                annuncio_id += 1

                break

            numero_pagina += 1

        return pd.DataFrame(annunci_totali)
