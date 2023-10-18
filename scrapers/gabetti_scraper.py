import datetime
import re

import numpy
import pandas as pd

from scrapers.abstract_scraper import AbstractScraper


class GabettiScraper(AbstractScraper):
    BASE_URL = "https://www.gabetti.it"
    URL = BASE_URL + "/casa/vendita/milano?page={page}"
    NUMERO_PAGINA_INIZIALE = 33

    def is_end_of_pages(self, bs4_page):
        if bs4_page.find("div", {"class": "error-page___text"}):
            return True

        return False

    def _clean_price(self, price: str) -> float | None:
        if price == "Tratt. Riservata":
            return numpy.nan

        return super()._clean_price(price)

    def _get_riferimento(self, bs4_page) -> str:
        pattern = re.compile('codice annuncio')
        label = bs4_page.find('span', {"class": 'infos-real-estate-detail__label'}, string=pattern)

        if label:
            value = label.find_next_sibling('span', class_='infos-real-estate-detail__value').text
            if value:
                return value

        return ""

    def _get_annunci_dict(self):
        numero_pagina = self.NUMERO_PAGINA_INIZIALE
        annunci_totali = []

        annuncio_id = 1
        while page := self._get_page(numero_pagina):
            annunci = page.find_all("div", {"class": "box-description-house"})
            for annuncio in annunci:
                annuncio_dict = {}

                link = self.BASE_URL + annuncio.find("a", {"class": "real_estate_link"})["href"]
                if not link:
                    continue

                pagina_annuncio = self._get_page(url=link)
                if not pagina_annuncio:
                    continue

                annuncio_dict["riferimento"] = int(self._get_riferimento(pagina_annuncio))
                annuncio_dict["agenzia"] = self.id
                annuncio_dict["link"] = link
                annuncio_dict["latitudine"] = self._clean_coordinate(
                    pagina_annuncio.find("div", {"id": "map-detail"})["data-lat"])
                annuncio_dict["longitudine"] = self._clean_coordinate(
                    pagina_annuncio.find("div", {"id": "map-detail"})["data-lng"])
                annuncio_dict["prezzo"] = self._clean_price(
                    pagina_annuncio.find("span", {"class": "price"}).text)
                annuncio_dict["mq"] = self._clean_mq(pagina_annuncio.find("span", {"class": "icon-square-meters"}).text)
                annuncio_dict["locali"] = self._clean_locali(pagina_annuncio.find("span", {"class": "icon-room"}).text)
                annuncio_dict["data_ultima_modifica_prezzo"] = datetime.datetime.now()

                annunci_totali.append(annuncio_dict)
                annuncio_id += 1

                break

            numero_pagina += 1

        return pd.DataFrame(annunci_totali)
