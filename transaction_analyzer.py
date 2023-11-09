"""
Modulo per analizzare le transazioni
"""
import networkx as nx
import pandas as pd

from grafici import plot_grafico_transazioni_per_anno, plot_grafico_funzione_prezzo_transazioni_immobili, \
    plot_grafico_frequenza_gradi
from grafo.disegna_grafo import disegna_grafo
from grafo.genera_grafo import genera_grafo


def main():
    """
    Funzione principale eseguita quando lo script è avviato.

    Legge un file CSV contenente transazioni immobiliari, lo converte in un DataFrame, e genera e visualizza
    un grafo delle transazioni. Inoltre, genera immagini del grafo e grafici delle transazioni per ogni immobile.
    """
    transazioni = pd.read_csv('files/transazioni.csv')
    transazioni['data'] = pd.to_datetime(transazioni['data'])

    plot_grafico_transazioni_per_anno(transazioni)
    plot_grafico_funzione_prezzo_transazioni_immobili(transazioni)
    grafo_transazioni, mappa_colori = genera_grafo(transazioni)
    disegna_grafo(grafo_transazioni, mappa_colori)

    disegnatore_grafo = nx.nx_agraph.to_agraph(grafo_transazioni)
    disegnatore_grafo.layout('dot')
    disegnatore_grafo.draw('output/multidigraph.png')

    # disegna_grafico_grafi_per_immobile(transazioni)

    plot_grafico_frequenza_gradi(grafo_transazioni)


if __name__ == '__main__':
    main()
