import abc
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup


class AbstractScraper(abc.ABC):
    def __init__(self, id_agenzia):
        """
        Inizializza l'estrattore con un dato ID di agenzia.

        :param id_agenzia: ID dell'agenzia da utilizzare.
        """
        self.id = id_agenzia

    @property
    @abc.abstractmethod
    def URL(self):
        """
        Proprietà astratta URL da sovrascrivere nelle sottoclassi.
        """
        pass

    def _get_url_pagina(self, pagina=None):
        """
        Ritorna l'URL formattato per una specifica pagina di annunci.

        :param pagina: Numero della pagina di annunci. Se None, ritorna l'URL (alcune agenzie non hanno pagine).
        :return: URL formattato.
        """
        return self.URL.format(page=pagina) if pagina else self.URL

    def _is_fine_delle_pagine(self, bs4_page: BeautifulSoup):
        """
        Determina se la pagina fornita è l'ultima tra quelle disponibili.
        Di default, restituisce sempre False. Da sovrascrivere nelle sottoclassi se necessario.

        :param bs4_page: Oggetto BeautifulSoup della pagina corrente.
        :return: True se è l'ultima pagina, altrimenti False.
        """
        return False

    def _clean_coordinate(self, coordinate: str) -> float | None:
        """
        Pulisce e converte una stringa di coordinate in un valore float.

        :param coordinate: La stringa delle coordinate da pulire.
        :return: Coordinate come float o None se la conversione non riesce.
        """
        try:
            return float(coordinate)
        except ValueError:
            logging.error(f"Coordinate {coordinate} non valide")
            return None

    def _clean_locali(self, locali: str) -> int | None:
        """
        Pulisce e converte una stringa rappresentante il numero di locali in un valore intero.

        :param locali: Stringa dei locali da pulire.
        :return: Numero di locali come int o None se la conversione non riesce.
        """
        try:
            return int(locali)
        except ValueError:
            logging.error(f"Locali {locali} non validi")
            return None

    def _clean_prezzo(self, prezzo: str) -> float:
        """
        Pulisce e converte una stringa di prezzo in un valore float.

        :param prezzo: Stringa di prezzo da pulire.
        :return: Prezzo come float.
        """
        return float(prezzo.replace("€", "").replace(".", "").replace(" ", ""))

    def _clean_mq(self, mq: str) -> float | None:
        """
        Pulisce e converte una stringa rappresentante metri quadrati in un valore float.

        :param mq: Stringa dei metri quadrati da pulire.
        :return: Metri quadrati come float o None se la conversione non riesce.
        """
        return float(mq.replace("m²", "").replace(".", "").replace(" ", "").replace(",", ".").replace("mq", ""))

    def _get_pagina(self, pagina=None, url=None):
        """
        Recupera il contenuto di una data pagina di annunci utilizzando l'URL fornito o generandolo.

        :param pagina: Numero della pagina da recuperare.
        :param url: URL specifico da utilizzare invece di generarne uno.
        :return: Oggetto BeautifulSoup della pagina o None se ci sono problemi con il recupero.
        """
        if url:
            url_pagina = url
        else:
            url_pagina = self._get_url_pagina(pagina)

        logging.info(f"Scraping pagina {url_pagina}")

        response = requests.get(url_pagina)
        soup = BeautifulSoup(response.text, 'html.parser')

        if response.status_code == 200 and not self._is_fine_delle_pagine(soup):
            return soup
        else:
            return None

    @abc.abstractmethod
    def _get_annunci_dict(self):
        """
        Metodo astratto per ottenere un dizionario di annunci. Da sovrascrivere nelle sottoclassi.

        :return: Dizionario degli annunci.
        """
        pass

    def get_annunci(self):
        """
        Ottiene un DataFrame degli annunci utilizzando il dizionario di annunci fornito dal metodo _get_annunci_dict.
        Questo metodo utilizza il Template Method Pattern, poiché definisce la struttura dell'algoritmo
        permettendo alle sottoclassi di implementare i dettagli specifici dell'estrazione degli annunci,
        come definito dal metodo astratto _get_annunci_dict.

        :return: DataFrame degli annunci con 'riferimento' come indice.
        """
        annunci_dict = self._get_annunci_dict()

        annunci_df = pd.DataFrame(annunci_dict)
        return annunci_df.set_index("riferimento")
