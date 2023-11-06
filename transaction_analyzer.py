import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from grafici import plot_grafico_transazioni_per_anno, plot_grafico_funzione_prezzo_transazioni_immobili
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
    disegnatore_grafo.layout('dot')  # 'dot' è uno dei layout di Graphviz; puoi usarne altri come 'neato'
    disegnatore_grafo.draw('output/multidigraph.png')  # Salva il grafico come immagine PNG

    transazioni_per_immobile = transazioni.groupby('immobile')
    numero_immobili = len(transazioni_per_immobile)
    colonne = int(np.ceil(np.sqrt(numero_immobili)))
    righe = int(np.ceil(numero_immobili / colonne))

    fig, axs = plt.subplots(righe, colonne, figsize=(colonne * 12, righe * 12))  # Adjust the size as needed
    axs = axs.flatten()

    for index, (immobile, transazioni_per_immobile) in enumerate(transazioni_per_immobile):
        grafo_transazioni_immobile, mappa_colori_immobile = genera_grafo(transazioni_per_immobile)

        disegna_grafo(
            grafo_transazioni_immobile,
            mappa_colori_immobile,
            title=f'Transazioni per immobile: {immobile}',
            ax=axs[index],
            fig=fig,
            show=False,
            disegna_legenda=False
        )

    fig.tight_layout()
    fig.show()


if __name__ == '__main__':
    main()
