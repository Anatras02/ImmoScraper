import abc
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup


class AbstractScraper(abc.ABC):
    def __init__(self, id_agenzia):
        self.id = id_agenzia

    @property
    @abc.abstractmethod
    def URL(self):
        pass

    def _get_page_url(self, pagina=None):
        return self.URL.format(page=pagina) if pagina else self.URL

    def is_end_of_pages(self, bs4_page: BeautifulSoup):
        return False

    def _clean_coordinate(self, coordinate: str) -> float | None:
        try:
            return float(coordinate)
        except ValueError:
            logging.error(f"Coordinate {coordinate} non valide")
            return None

    def _clean_locali(self, locali: str) -> int | None:
        try:
            return int(locali)
        except ValueError:
            logging.error(f"Locali {locali} non validi")
            return None

    def _clean_price(self, price: str) -> float:
        return float(price.replace("€", "").replace(".", "").replace(" ", ""))

    def _clean_mq(self, mq: str) -> float | None:
        return float(mq.replace("m²", "").replace(".", "").replace(" ", "").replace(",", ".").replace("mq", ""))

    def _get_page(self, pagina=None, url=None):
        if url:
            page_url = url
        else:
            page_url = self._get_page_url(pagina)

        logging.info(f"Getting page {page_url}")

        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        if not self.is_end_of_pages(soup) and response.status_code == 200:
            return soup
        else:
            return None

    @abc.abstractmethod
    def _get_annunci_dict(self):
        pass

    def get_annunci(self):
        annunci_dict = self._get_annunci_dict()

        annunci_df = pd.DataFrame(annunci_dict)
        return annunci_df.set_index("riferimento")
