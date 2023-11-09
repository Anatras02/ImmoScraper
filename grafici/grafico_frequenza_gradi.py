import pandas as pd
from matplotlib import pyplot as plt


def plot_grafico_frequenza_gradi(grafo):
    """
    Visualizza un grafico a barre rappresentante la frequenza dei gradi dei nodi di un grafo.

    Il grafico mostra il grado di ogni nodo all'interno del grafo fornito come parametro. Il grado di un nodo è
    definito come il numero di archi collegati a quel nodo. Questo tipo di visualizzazione è utile per analizzare
    la distribuzione dei collegamenti all'interno di una rete, come quella delle transazioni.

    :param grafo: Una struttura dati di grafo che contiene nodi e i loro gradi.
    :type grafo: networkx.Graph o altra struttura di grafo compatibile.
    :return: None. La funzione visualizza un grafico a barre e non restituisce alcun valore.
    """
    idx, values = zip(*grafo.degree())
    gradi_nodi = pd.Series(values, index=idx)

    gradi_nodi.plot.bar()
    plt.xlabel('Nodo')
    plt.ylabel('Grado')
    plt.title('Frequenza dei gradi dei nodi del grafo delle transazioni')

    plt.tight_layout()
    plt.show()
