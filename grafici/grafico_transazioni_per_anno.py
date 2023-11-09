
from matplotlib import pyplot as plt


def plot_grafico_transazioni_per_anno(transazioni):
    """
    Genera un grafico a barre del numero di transazioni immobiliari per anno.

    Questa funzione prende un DataFrame di transazioni immobiliari, raggruppa i dati per anno,
    e poi plotta il numero di transazioni per ciascun anno in un grafico a barre.

    :param transazioni: DataFrame contenente le transazioni immobiliari. Deve avere una colonna 'data'
                        con la data della transazione.
    :return: Non ritorna nulla poiché il risultato è la visualizzazione di un grafico.

    Side effects:
        - Apre una finestra di matplotlib con il grafico a barre delle transazioni per anno.
        - Plotta il numero di transazioni per anno in un grafico a barre.
        - Mostra titoli degli assi e del grafico.
    """
    transazioni_per_anno = transazioni.groupby(transazioni['data'].dt.year).size()
    plt.figure(figsize=(20, 5))
    transazioni_per_anno.plot(kind='bar', title='Transazioni per anno')
    plt.xlabel('Anno')
    plt.ylabel('Numero transazioni')
    plt.tight_layout()
    plt.show()
