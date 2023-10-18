import datetime
import re
import concurrent.futures
import warnings

import numpy
import pandas as pd

from scrapers.abstract_scraper import AbstractScraper


class GabettiScraper(AbstractScraper):
    BASE_URL = "https://www.gabetti.it"
    URL = BASE_URL + "/casa/vendita/milano?page={page}"
    NUMERO_PAGINA_INIZIALE = 1

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

    def _get_annuncio(self, pagina_annuncio, link):
        return {
            "riferimento": int(self._get_riferimento(pagina_annuncio)), "agenzia": self.id, "link": link,
            "latitudine": self._clean_coordinate(
                pagina_annuncio.find("div", {"id": "map-detail"})["data-lat"]),
            "longitudine": self._clean_coordinate(
                pagina_annuncio.find("div", {"id": "map-detail"})["data-lng"]),
            "prezzo": self._clean_prezzo(
                pagina_annuncio.find("span", {"class": "price"}).text),
            "mq": self._clean_mq(pagina_annuncio.find("span", {"class": "icon-square-meters"}).text),
            "locali": self._clean_locali(pagina_annuncio.find("span", {"class": "icon-room"}).text),
            "data_ultima_modifica_prezzo": datetime.datetime.now()
        }

    def _get_annunci_pagina(self, pagina):
        annunci = pagina.find_all("div", {"class": "box-description-house"})
        annunci_pagina = []

        for annuncio in annunci:
            link = self.BASE_URL + annuncio.find("a", {"class": "real_estate_link"})["href"]
            if not link:
                continue

            pagina_annuncio = self._get_pagina(url=link)
            if not pagina_annuncio:
                continue

            annunci_pagina.append(self._get_annuncio(pagina_annuncio, link))

        return annunci_pagina

    def _get_annunci_pagina_concurrent(self, pagina):
        """
        Ottiene annunci dalla pagina fornita e processa ogni annuncio in un thread separato.

        Questo metodo è pericoloso perché effettua un gran numero di richieste simultanee,
        il che potrebbe portare al crash del sito web target.

        :param pagina: La pagina web da cui estrarre gli annunci.
        :type pagina: bs4.BeautifulSoup
        :return: Una lista di annunci estratti dalla pagina.
        :rtype: list
        """
        warnings.warn(
            "Questo metodo è pericoloso perché effettua molte richieste simultanee e potrebbe "
            "crashare il sito web target. Usa con cautela!",
            UserWarning
        )

        annunci = pagina.find_all("div", {"class": "box-description-house"})
        annunci_pagina = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for annuncio in annunci:
                link = self.BASE_URL + annuncio.find("a", {"class": "real_estate_link"})["href"]
                if not link:
                    continue

                pagina_annuncio = self._get_pagina(url=link)
                if not pagina_annuncio:
                    continue

                futures.append(executor.submit(self._get_annuncio, pagina_annuncio, link))

            for future in concurrent.futures.as_completed(futures):
                annunci_pagina.append(future.result())

        return annunci_pagina
