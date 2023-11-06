from typing import Tuple, Dict, List, Callable

import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt


def genera_grafo(transazioni) -> Tuple[nx.MultiDiGraph, Dict[str, str]]:
    """
    Genera un grafo diretto multi-arco (MultiDiGraph) che rappresenta le transazioni immobiliari.

    Crea un grafo basato sui dati di un DataFrame che rappresenta le transazioni immobiliari. Ogni transazione
    è rappresentata come un arco in un grafo, e ogni arco è colorato in base all'immobile a cui si riferisce.

    :param transazioni: Il DataFrame che contiene i dati delle transazioni immobiliari.
    :return: Una tupla contenente il grafo delle transazioni e la mappa dei colori per ogni immobile.
    :rtype: Tuple[nx.MultiDiGraph, Dict[str, str]]
    :type transazioni: pandas.DataFrame
    """
    grafo_transazioni = nx.MultiDiGraph()
    mappa_colori = get_mappa_colori(transazioni)
    aggiungi_archi(grafo_transazioni, transazioni, mappa_colori)

    return grafo_transazioni, mappa_colori


def get_immobili_unici(transazioni: pd.DataFrame) -> List[str]:
    """
    Estrae una lista di identificativi unici di immobili da un DataFrame di transazioni.
    Questa funzione passa attraverso un DataFrame che contiene transazioni immobiliari, ognuna
    con un identificativo di immobile, e raccoglie un insieme unico di questi identificativi.
    Questo può essere particolarmente utile per analizzare i dati delle transazioni immobiliari,
    per identificare gli immobili coinvolti, o per preparare i dati per ulteriori analisi o
    visualizzazioni dove ogni immobile deve essere rappresentato una sola volta.

    :param transazioni: Un DataFrame contenente le transazioni immobiliari. Si aspetta che una colonna
                        di questo DataFrame contenga gli identificativi degli immobili.
    :type transazioni: DataFrame
    :return: Una lista contenente gli identificativi unici degli immobili.
    :rtype: List[str]
    """
    return list(set(transazioni['immobile']))


def get_mappa_colori(transazioni: pd.DataFrame) -> Dict[str, str]:
    """
    Crea una mappa che associa ogni immobile presente nel DataFrame delle transazioni a un colore unico.
    Questo permette di avere una rappresentazione visiva consistente degli immobili quando vengono
    visualizzati nel grafico delle transazioni. Quindi ogni transazione riguardante un immobile avrà
    lo stesso colore, e questo colore sarà diverso per ogni immobile.

    :param transazioni: Un DataFrame pandas con almeno una colonna che identifica gli immobili.

    :return: Un dizionario dove le chiavi sono gli identificatori degli immobili e i valori sono stringhe che
    rappresentano colori. I colori sono scelti da una mappa di colore 'nipy_spectral' per avere una gamma ampia e
    distinta di colori.
    """

    def rgba_to_hex(rgba):
        return "#{:02x}{:02x}{:02x}".format(
            int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
        )

    immobili_unici = get_immobili_unici(transazioni)
    return {immobile: rgba_to_hex(plt.get_cmap('nipy_spectral')(i / len(immobili_unici))) for i, immobile in
            enumerate(immobili_unici)}


def get_calcolatore_aumento_prezzo(transazioni: pd.DataFrame) -> Callable[[str, float, int], str]:
    ultime_transazioni_per_immobile = {}

    def get_aumento_prezzo(immobile, prezzo_transazione, id_transazione):
        ultima_transazione_immobile_id = ultime_transazioni_per_immobile.get(immobile, None)
        if ultima_transazione_immobile_id is not None:
            ultima_transazione_immobile = transazioni[(transazioni['id_transazione'] == ultima_transazione_immobile_id)]
            aumento_prezzo = (prezzo_transazione - ultima_transazione_immobile['prezzo']).iloc[0]
        else:
            aumento_prezzo = prezzo_transazione

        if aumento_prezzo > 0:
            aumento_prezzo = f"+{aumento_prezzo} €"
        else:
            aumento_prezzo = f"{aumento_prezzo} €"

        ultime_transazioni_per_immobile[immobile] = id_transazione

        return aumento_prezzo

    return get_aumento_prezzo


def aggiungi_archi(grafo: nx.MultiDiGraph, transazioni: pd.DataFrame, mappa_colori: Dict[str, str]) -> None:
    """
    Aggiunge gli archi al grafo basandosi sulle transazioni fornite. Ogni arco è colorato secondo la mappa dei colori
    fornita e rappresenta una transazione tra due parti.
    Gli archi vengono ordinati in base alla data delle transazioni, e ogni arco contiene attributi come l'identificatore
    dell'immobile, l'agenzia, la data e il prezzo della transazione.

    :param grafo: Grafo diretto di NetworkX sul quale aggiungere gli archi.
    :type grafo: MultiDiGraph
    :param transazioni: DataFrame di pandas che contiene le transazioni con colonne per l'acquirente,
                        il venditore, l'immobile, l'agenzia, la data e il prezzo.
    :type transazioni: DataFrame
    :param mappa_colori: Dizionario che associa ogni immobile a un colore specifico per la rappresentazione degli archi.
    :type mappa_colori: Dict[str, str]

    :return: None
    """
    transazioni = transazioni.sort_values(by='data')
    prime_transazioni_per_immobile = transazioni.groupby('immobile').first()
    counter_immobili = {immobile: 1 for immobile in transazioni['immobile']}
    funzione_calcolo_aumento_prezzo = get_calcolatore_aumento_prezzo(transazioni)

    for _, transazione in transazioni.iterrows():
        immobile = transazione['immobile']
        id_transazione = transazione['id_transazione']
        prima_transazione_immobile = prime_transazioni_per_immobile.loc[immobile]['id_transazione']
        aumento_prezzo = funzione_calcolo_aumento_prezzo(immobile, transazione['prezzo'], id_transazione)

        grafo.add_edge(
            transazione['venditore'],
            transazione['acquirente'],
            key=id_transazione,
            immobile=transazione['immobile'],
            agenzia=transazione['agenzia'],
            data=transazione['data'],
            prezzo=transazione['prezzo'],
            color=mappa_colori[transazione['immobile']],  # Assegna il colore qui,
            prima_transazione_immobile=id_transazione == prima_transazione_immobile,
            label=f"{counter_immobili[immobile]}. {transazione['data'].strftime('%d/%m/%Y')}\n{aumento_prezzo}"
        )

        counter_immobili[immobile] += 1
