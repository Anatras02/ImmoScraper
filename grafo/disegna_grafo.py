from typing import Dict, List, Tuple, Any

import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from grafo.genera_grafo import genera_grafo


def disegna_grafico_grafi_per_immobile(transazioni: pd.DataFrame):
    """
    Genera una serie di grafici delle transazioni per ogni immobile presente nel DataFrame.

    Ogni immobile verrà rappresentato da un grafo in un subplot separato all'interno di una griglia di grafici.
    La griglia è dimensionata in base al numero totale di immobili per ottimizzare la visualizzazione.

    :param transazioni: DataFrame che contiene le transazioni, con almeno una colonna chiamata 'immobile'.
    :type transazioni: pd.DataFrame
    :return: None. La funzione produce un grafico come output e non restituisce alcun valore.

    """
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


def disegna_grafo(grafo, mappa_colori, title=None, ax=None, fig=None, disegna_legenda=True, show=True):
    """
    Disegna un grafo completo con nodi, etichette, e archi multipli con stili e colori corrispondenti
    ai diversi immobili.

    La funzione assembla le varie parti del grafo, organizzando nodi, etichette e archi con la possibilità di
    aggiungere una legenda e un titolo. Può anche mostrare immediatamente il grafico.

    :param grafo: Il grafo di NetworkX da disegnare.
    :param mappa_colori: Un dizionario che mappa ogni immobile a un colore specifico per gli archi.
    :param title: Il titolo da mostrare sopra il grafico.
    :param ax: L'oggetto Axes su cui disegnare il grafo. Se None, ne verrà creato uno nuovo.
    :param fig: L'oggetto Figure su cui è basato il grafico. Se None, ne verrà creato uno nuovo.
    :param disegna_legenda: Se True, disegna una legenda sul grafico.
    :param show: Se True, mostra il grafico immediatamente dopo averlo generato.
    :type grafo: nx.MultiDiGraph
    :type mappa_colori: Dict[str, str]
    :type title: str or None
    :type ax: matplotlib.axes._axes.Axes or None
    :type fig: matplotlib.figure.Figure or None
    :type disegna_legenda: bool
    :type show: bool
    """
    if ax is None or fig is None:
        fig, ax = plt.subplots(figsize=(15, 15))

    # layout è un dict che mappa ogni nodo a una coppia di coordinate (x, y)
    layout = nx.shell_layout(grafo)
    disegna_nodi_e_etichette(grafo, layout, ax=ax)
    disegna_archi_multipli(grafo, layout, mappa_colori, ax=ax)

    if disegna_legenda:
        genera_legenda(mappa_colori)

    if title is not None:
        ax.set_title(title, fontsize=20)

    # Imposta un bordo attorno al plot per assicurarsi che la legenda non sovrapponga il grafo
    if show:
        fig.tight_layout()
        fig.show()


def disegna_archi_multipli(grafo: nx.MultiDiGraph, layout: dict, mappa_colori: Dict[str, str], ax=None):
    """
    Disegna archi multipli tra le coppie di nodi in un grafo, con colori specifici e stili per evitare sovrapposizioni.

    Questa funzione gestisce il rendering degli archi in un grafo dove possono esistere connessioni multiple tra
    la stessa coppia di nodi. Ogni arco viene disegnato con un colore che corrisponde all'immobile che rappresenta
    e con una curvatura tale da evitare sovrapposizioni con altri archi simili.

    :param grafo: Il grafo da visualizzare.
    :param layout: Un dizionario che assegna a ogni nodo del grafo una posizione (x, y) sul piano del grafico.
    :param mappa_colori: Un dizionario che associa ogni immobile a un colore.
    :param ax: L'asse matplotlib su cui verranno disegnati gli archi. Se None, verrà utilizzato l'asse corrente.
    :type grafo: MultiDiGraph
    :type layout: Dict
    :type mappa_colori: Dict[str, str]
    :type ax: matplotlib.axes._axes.Axes or None
    """
    numero_cerchi_per_nodo = {}

    for immobile, color in mappa_colori.items():
        archi_immobile = get_archi_immobile(grafo, immobile)
        for indice_arco, (u, v, data) in enumerate(archi_immobile):
            archi_specifici = [(u, v, k) for k in grafo[u][v]]
            style = calcola_stile_arco(indice_arco, archi_specifici)

            if data['prima_transazione_immobile']:
                disegna_cerchio_prima_transazione_immobile(u, color, layout, numero_cerchi_per_nodo, ax)

            nx.draw_networkx_edges(
                grafo, layout,
                edgelist=[(u, v)],
                edge_color=color,
                connectionstyle=style,
                arrowsize=20,
                ax=ax,
            )


def disegna_cerchio_prima_transazione_immobile(nodo, color, layout, numero_cerchi_per_nodo, ax=None):
    """
    Disegna un cerchio attorno al nodo che rappresenta la prima transazione per un dato immobile.

    La funzione è pensata per evidenziare i nodi che hanno effettuato la prima transazione per un immobile,
    disegnando attorno a essi un cerchio il cui raggio è proporzionale al numero di transazioni del nodo.

    :param nodo: Il nodo attorno al quale disegnare il cerchio.
    :param color: Il colore del cerchio.
    :param layout: Il layout dei nodi nel grafico.
    :param numero_cerchi_per_nodo: Un dizionario che tiene traccia del numero di cerchi già disegnati per nodo.
    :param ax: L'asse di matplotlib su cui disegnare il cerchio. Se None, usa l'asse corrente.
    :type nodo: Any
    :type color: str
    :type layout: Dict
    :type numero_cerchi_per_nodo: Dict
    :type ax: matplotlib.axes._axes.Axes or None
    """
    contatore_cerchi = numero_cerchi_per_nodo.get(nodo, 0)
    offset = 1000 * contatore_cerchi
    size = 1000 + offset

    if ax is None:
        ax = plt.gca()

    ax.scatter(layout[nodo][0], layout[nodo][1], s=size, facecolors='none', edgecolors=color, linewidths=2)

    numero_cerchi_per_nodo[nodo] = numero_cerchi_per_nodo.get(nodo, 0) + 1


def calcola_stile_arco(indice_arco: int, archi_specifici: List[Tuple[Any, Any, int]]) -> str:
    """
    Determina lo stile di connessione per gli archi di un grafo, gestendo la sovrapposizione di archi multipli.

    Questa funzione è utile quando si disegnano grafi con connessioni multiple tra gli stessi nodi,
    permettendo di visualizzare chiaramente ogni transazione senza sovrapposizioni grafiche.
    Lo stile di connessione è definito in modo da differenziare visivamente gli archi in base alla loro
    posizione nella lista degli archi connessi tra due nodi.

    :param indice_arco: Posizione dell'arco corrente nella sequenza di archi tra due nodi.
    :type indice_arco: Int
    :param archi_specifici: Lista di tuple rappresentanti gli archi tra due nodi.
    :type archi_specifici: List[Tuple[Any, Any, int]]
    :return: Una stringa che definisce lo stile di connessione per matplotlib.
             Ad esempio, 'arc3,rad=0.2' indica uno stile di arco curvato con raggio 0.2.
    :rtype: String
    """
    if len(archi_specifici) > 1:
        # Lo spostamento radiale è calcolato per distanziare gli archi multipli in modo visibile.
        rad_offset = 0.1 + 0.1 * (indice_arco - len(archi_specifici) / 2)
        style = f'arc3,rad={rad_offset}'
    else:
        style = 'arc3,rad=0.1'

    return style


def disegna_nodi_e_etichette(grafo: nx.MultiDiGraph, layout, ax=None) -> None:
    """
    Disegna i nodi e le etichette del grafo utilizzando il layout specificato per determinare la posizione dei nodi
    nel grafico.

    :param grafo: Grafo NetworkX da cui disegnare nodi ed etichette.
    :type grafo: MultiDiGraph
    :param layout: Dizionario che mappa ogni nodo a una coppia di coordinate (x, y).
    :type layout: Dict
    :param ax: Oggetto matplotlib Axes su cui disegnare. Se None, utilizza l'asse corrente.
    :type ax: Axes, optional

    :return: None
    """
    nx.draw_networkx_nodes(grafo, layout, ax=ax, node_size=500, node_color='skyblue', alpha=0.9)
    nx.draw_networkx_labels(grafo, layout, ax=ax)


def genera_legenda(mappa_colori: Dict[str, str]) -> None:
    """
    Genera una legenda grafica basata su una mappa di colori data e la posiziona nel plot corrente.
    La funzione assume che un plot sia già stato creato tramite matplotlib, e utilizza la mappa
    dei colori fornita per costruire una legenda che associa ciascun colore a un identificativo di immobile.
    Questo è utile per grafici complessi dove diversi colori vengono utilizzati per distinguere tra diversi
    tipi di elementi o categorie, e una legenda chiara è necessaria per interpretare correttamente ciò che
    viene visualizzato nel grafico.

    :param mappa_colori: Un dizionario dove ogni chiave è un identificativo unico di un immobile e ogni valore
                         è una stringa che rappresenta il colore associato a quell'immobile nel plot.
    :type mappa_colori: Dict[str, str]
    :return: Non ritorna nulla.
    """
    # Crea una legenda per gli archi
    legenda_elementi = []
    for immobile, color in mappa_colori.items():
        legenda_elementi.append(Line2D([0], [0], color=color, lw=4, label=immobile))

    # Aggiungi la legenda al plot, posizionandola al di fuori del box del grafo
    plt.legend(handles=legenda_elementi, loc='upper left', bbox_to_anchor=(1, 1), title="Immobili")


def aggiungi_nodo_se_non_esistente(grafo: nx.Graph, nodo, tipo: str) -> None:
    """
    Questa funzione è progettata per aggiungere un nodo a un grafo NetworkX fornito come parametro,
    se e solo se il nodo non è già presente nel grafo. È utile per mantenere i grafi puliti senza duplicati,
    assicurando che ogni nodo sia unico e sia associato a un tipo specificato dall'utente.
    Questo metodo è particolarmente utile nell'ambito di grafi dove i nodi rappresentano entità come persone,
    luoghi od oggetti con attributi univoci, come nel caso di un nodo che rappresenta un acquirente o un venditore
    nel contesto di una rete di transazioni.

    :param grafo: Il grafo su cui operare. Il grafo deve essere una istanza di `nx.Graph`.
    :type grafo: nx.Graph
    :param nodo: Il nodo da aggiungere. Il tipo di questo parametro deve essere hashable,
                 cioè un tipo di dato che può essere utilizzato come chiave di un dizionario, come
                 una stringa o un numero.
    :type nodo: hashable
    :param tipo: Una stringa che descrive il tipo del nodo. Questo parametro viene usato per
                 assegnare attributi al nodo all'interno del grafo e dovrebbe essere una descrizione
                 come 'acquirente' o 'venditore'.
    :type tipo: str
    :return: Non ritorna nulla.
    """
    if not grafo.has_node(nodo):
        grafo.add_node(nodo, type=tipo)


def get_archi_immobile(grafo: nx.MultiDiGraph, immobile: str):
    """
    Ottiene tutti gli archi associati a un determinato immobile in un grafo di transazioni.

    Attraverso questa funzione è possibile estrarre gli archi che rappresentano le transazioni
    collegate a un singolo immobile. Gli archi vengono restituiti in una lista di tuple, dove ogni
    tupla rappresenta una connessione (arco) nel grafo con i dati relativi.

    :param grafo: Il grafo diretto multiarco da cui estrarre le informazioni.
    :type grafo: nMultiDiGraph
    :param immobile: Identificativo dell'immobile per cui si desiderano ottenere gli archi.
    :type immobile: String
    :return: Lista delle tuple che rappresentano gli archi e i loro attributi associati all'immobile.
             Ogni tupla contiene il nodo di partenza, il nodo di arrivo e un dizionario degli attributi.
    :rtype: List[Tuple[Any, Any, dict]]
    """
    archi_immobile = list(filter(lambda x: x[2]['immobile'] == immobile, grafo.edges(data=True)))

    return archi_immobile
