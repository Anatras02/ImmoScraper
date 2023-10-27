import abc
import concurrent.futures
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame


class AbstractScraper(abc.ABC):
    """
    Classe astratta che rappresenta un estrattore di annunci.
    Le sottoclassi devono sovrascrivere i metodi astratti per fornire una specifica implementazione
    in base alle loro esigenze.
    """

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
        Proprietà astratta URL. Questa proprietà deve essere sovrascritta nelle sottoclassi
        per fornire l'URL specifico da utilizzare nella scraping.
        """
        pass

    @property
    def NUMERO_PAGINA_INIZIALE(self):
        """
        Proprietà che ritorna il numero della pagina iniziale.
        Può essere sovrascritto nelle sottoclassi se necessario.

        :return: Int rappresentante il numero della prima pagina.
        """
        return 1

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
        Di default, restituisce sempre False. Può essere sovrascritto nelle sottoclassi
        per gestire la logica specifica.

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

    @staticmethod
    def _get_tipo_from_dataframe(tipo: str, df: DataFrame) -> int:
        """
        Estrae l'identificatore numerico di un tipo di proprietà specificato dalla DataFrame delle tipologie.

        Questo metodo viene utilizzato per convertire una descrizione testuale della tipologia di proprietà
        (es. "appartamento", "attico", ecc.) nel suo corrispondente ID numerico, come definito nel file CSV
        delle tipologie.

        :param tipo: Una stringa che rappresenta il tipo di proprietà.
        :param df: La DataFrame delle tipologie caricate dal file CSV.
        :return: L'ID numerico corrispondente al tipo di proprietà specificato.
        """
        return df[df["nome"] == tipo].index[0]

    def _clean_tipologia(self, tipologia: str) -> int:
        """
        Pulisce e mappa una stringa di tipologia in un corrispondente identificativo intero.
        Utilizza un file CSV per effettuare la corrispondenza.

        :param tipologia: Stringa della tipologia da mappare.
        :return: ID della tipologia come int.
        """
        tipologie = pd.read_csv("files/tipologie.csv", index_col="id")
        tipologia = tipologia.strip().lower()

        match tipologia:
            case "appartamento":
                return self._get_tipo_from_dataframe("appartamento", tipologie)
            case "attico":
                return self._get_tipo_from_dataframe("attico", tipologie)
            case "box":
                return self._get_tipo_from_dataframe("box", tipologie)
            case "garage":
                return self._get_tipo_from_dataframe("garage", tipologie)
            case "casa indipendente":
                return self._get_tipo_from_dataframe("casa indipendente", tipologie)
            case "palazzina":
                return self._get_tipo_from_dataframe("palazzina", tipologie)
            case "villa":
                return self._get_tipo_from_dataframe("villa", tipologie)
            case "rustico":
                return self._get_tipo_from_dataframe("rustico", tipologie)
            case "cascina":
                return self._get_tipo_from_dataframe("cascina", tipologie)
            case _:
                return self._get_tipo_from_dataframe("altro", tipologie)

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
    def _get_annunci_pagina_concurrent(self, pagina: BeautifulSoup, max_workers=1):
        """
        Metodo astratto per ottenere un dizionario di annunci. Da sovrascrivere nelle sottoclassi.

        :return: Dizionario degli annunci.
        """
        pass

    def get_annunci_concurrent(self, max_workers=3, max_annunci_pagina_workers=2):
        """
        Estrae gli annunci in modo concorrente.

        Questo metodo utilizza esecutori di thread per eseguire il web scraping in modo concorrente,
        permettendo una raccolta di dati più veloce. Il numero massimo di thread per l'estrazione
        di pagine e annunci può essere specificato attraverso i parametri.

        Nota: Aumentare il numero di thread potrebbe aumentare il rischio di essere bloccati dal sito web
        o causare altri problemi. Usare con cautela.

        :param max_workers: Numero massimo di thread per l'estrazione delle pagine.
        :param max_annunci_pagina_workers: Numero massimo di thread per l'estrazione degli annunci in una pagina.
        :return: DataFrame degli annunci con 'riferimento' come indice.
        """
        numero_pagina = self.NUMERO_PAGINA_INIZIALE
        annunci_totali = []
        futures = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            while page := self._get_pagina(numero_pagina):
                futures.append(executor.submit(self._get_annunci_pagina_concurrent, page, max_annunci_pagina_workers))
                numero_pagina += 1

        for future in concurrent.futures.as_completed(futures):
            annunci_totali.extend(future.result())

        annunci_df = pd.DataFrame(annunci_totali)
        return annunci_df.set_index("riferimento")
