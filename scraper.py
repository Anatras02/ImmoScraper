import importlib
import logging

import numpy as np
import pandas as pd


def get_annunci() -> pd.DataFrame:
    """
    Recupera gli annunci da tutte le agenzie specificate nella costante AGENZIE. Per ogni agenzia, inizializza lo
    scraper corrispondente e ottiene gli annunci. Tutti gli annunci recuperati vengono poi concatenati in un unico
    DataFrame che viene restituito.

    :return: Un DataFrame contenente tutti gli annunci recuperati da tutte le agenzie.
    """
    annunci_nuovi = pd.DataFrame()
    agenzie = pd.read_csv("files/agenzie.csv")

    for index, agenzia in agenzie.iterrows():
        module_name, class_name = agenzia["scraper"].rsplit('.', 1)
        module = importlib.import_module(module_name)
        _scraper = getattr(module, class_name)

        scraper = _scraper(agenzia["id"])
        annunci = scraper.get_annunci_concurrent(3, 6)

        annunci_nuovi = pd.concat([annunci_nuovi, annunci])

    return annunci_nuovi


def merge_annunci(annunci_vecchi: pd.DataFrame, annunci_nuovi: pd.DataFrame) -> pd.DataFrame:
    """
    Unisce un DataFrame di annunci vecchi con uno di annunci nuovi. Se un annuncio nel DataFrame nuovo ha lo stesso
    indice di un annuncio nel DataFrame vecchio, l'annuncio vecchio viene aggiornato solo se il prezzo è cambiato.
    Altrimenti, l'annuncio nuovo viene aggiunto al DataFrame vecchio.

    :param annunci_vecchi: DataFrame contenente gli annunci vecchi, con l'indice impostato al riferimento dell'annuncio.
    :param annunci_nuovi: DataFrame contenente gli annunci nuovi, con l'indice impostato al riferimento dell'annuncio.
    :return: DataFrame contenente gli annunci vecchi aggiornati con le informazioni degli annunci nuovi.
    """
    for riferimento, annuncio_nuovo in annunci_nuovi.iterrows():
        try:
            annuncio_vecchio_relativo = annunci_vecchi.loc[riferimento]
        except KeyError:
            annunci_vecchi.loc[riferimento] = annuncio_nuovo
            logging.info(f"Nuovo annuncio {riferimento}")
            continue

        if not np.isnan(annuncio_vecchio_relativo["prezzo"]) and not np.isnan(annuncio_nuovo["prezzo"]):
            if not np.isclose(annuncio_vecchio_relativo["prezzo"], annuncio_nuovo["prezzo"]):
                logging.info(
                    f"Annuncio {riferimento} ha cambiato prezzo da {annuncio_vecchio_relativo['prezzo']} a {annuncio_nuovo['prezzo']}")
                annunci_vecchi.loc[riferimento] = annuncio_nuovo

    return annunci_vecchi


def main():
    """
    Carica annunci vecchi e nuovi, unisce i DataFrames, e salva il risultato se i DataFrame hanno le stesse colonne
    e il DataFrame degli annunci vecchi non è vuoto. Gli annunci vecchi vengono aggiornati solo se il prezzo è cambiato,
    riflettendo la data dell'ultimo cambiamento del prezzo.

    Gli altri campi non sono considerati per l'aggiornamento, poiché l'obiettivo è tracciare le variazioni di prezzo
    piuttosto che gli errori di inserimento o altre modifiche.
    """
    annunci_nuovi = get_annunci()
    annunci_vecchi = pd.read_csv("files/annunci.csv", index_col="riferimento")

    if not annunci_vecchi.empty:
        if annunci_vecchi.columns.equals(annunci_nuovi.columns):
            annunci_merge = merge_annunci(annunci_vecchi, annunci_nuovi)
            annunci_merge.to_csv("files/annunci.csv")

            logging.info("Annunci aggiornati")
        else:
            logging.error("Annunci vecchi e nuovi hanno colonne diverse")
    else:
        annunci_nuovi.to_csv("files/annunci.csv")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    main()
