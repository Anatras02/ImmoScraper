import concurrent.futures
import datetime
import re

import numpy

from scrapers.abstract_scraper import AbstractScraper


class GabettiScraper(AbstractScraper):
    BASE_URL = "https://www.gabetti.it"
    URL = BASE_URL + "/casa/vendita/milano?page={page}"
    NUMERO_PAGINA_INIZIALE = 1

    def _is_fine_delle_pagine(self, bs4_page):
        """
        Verifica se la pagina fornita è l'ultima pagina di annunci sul sito.

        :param bs4_page: L'oggetto BeautifulSoup della pagina web corrente.
        :return: True se è l'ultima pagina, altrimenti False.
        """
        if bs4_page.find("div", {"class": "error-page___text"}):
            return True

        return False

    def _clean_prezzo(self, prezzo: str) -> float | None:
        """
        Trasforma la stringa del prezzo in un valore float o NaN.

        :param prezzo: Stringa rappresentante il prezzo.
        :return: Valore float del prezzo o NaN se è "Tratt. Riservata".
        """
        if prezzo == "Tratt. Riservata":
            return numpy.nan

        return super()._clean_prezzo(prezzo)

    @staticmethod
    def _get_dettaglio_annuncio_da_label(bs4_page, label: str) -> str:
        """
        Estrae il dettaglio dell'annuncio usando una label fornita.

        :param bs4_page: L'oggetto BeautifulSoup della pagina web dell'annuncio.
        :param label: Label utilizzata per trovare il dettaglio.
        :return: Dettaglio dell'annuncio o stringa vuota se non trovato.
        """
        pattern = re.compile(label)
        label = bs4_page.find('span', {"class": 'infos-real-estate-detail__label'}, string=pattern)

        if label:
            value = label.find_next_sibling('span', class_='infos-real-estate-detail__value').text
            if value:
                return value

        return ""

    def _get_annuncio(self, link: str) -> dict | None:
        """
        Estrae dettagli da un annuncio dato il suo link e restituisce un dizionario con le informazioni ottenute.

        Questa funzione visita il link dell'annuncio fornito come parametro, scarica la pagina dell'annuncio
        e ne estrae le informazioni dettagliate.

        :param link: Il link dell'annuncio da visitare.
        :return: Un dizionario con i dettagli dell'annuncio o None se ci sono stati problemi nello scaricamento.
        """
        if not link:
            return None

        pagina_annuncio = self._get_pagina(url=link)
        if not pagina_annuncio:
            return None

        return {
            "riferimento": int(self._get_dettaglio_annuncio_da_label(pagina_annuncio, "codice annuncio")), "agenzia": self.id, "link": link,
            "latitudine": self._clean_coordinate(
                pagina_annuncio.find("div", {"id": "map-detail"})["data-lat"]),
            "longitudine": self._clean_coordinate(
                pagina_annuncio.find("div", {"id": "map-detail"})["data-lng"]),
            "prezzo": self._clean_prezzo(
                pagina_annuncio.find("span", {"class": "price"}).text),
            "mq": self._clean_mq(pagina_annuncio.find("span", {"class": "icon-square-meters"}).text),
            "locali": self._clean_locali(pagina_annuncio.find("span", {"class": "icon-room"}).text),
            "tipologia": self._clean_tipologia(self._get_dettaglio_annuncio_da_label(pagina_annuncio, "tipologia")),
            "data_ultima_modifica_prezzo": datetime.datetime.now()
        }

    def _get_annunci_pagina_concurrent(self, pagina, max_workers=1):
        """
        Estrae annunci da una pagina utilizzando thread multipli.

        Questo metodo usa `ThreadPoolExecutor` per processare ogni annuncio in un thread separato.
        Tuttavia, l'uso di troppi thread simultaneamente può sovraccaricare il server del sito target.
        E' fondamentale utilizzare un numero ragionevole di `max_workers` e, se possibile, introdurre dei ritardi
        tra le richieste per evitare di essere bloccati o di causare problemi al sito.

        :param pagina: Pagina BeautifulSoup da cui estrarre gli annunci.
        :param max_workers: Numero massimo di thread da utilizzare.
        :return: Lista di annunci estratti dalla pagina.
        """
        annunci = pagina.find_all("div", {"class": "box-description-house"})
        annunci_pagina = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for annuncio in annunci:
                link = self.BASE_URL + annuncio.find("a", {"class": "real_estate_link"})["href"]

                futures.append(executor.submit(self._get_annuncio, link))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    annunci_pagina.append(result)

        return annunci_pagina
