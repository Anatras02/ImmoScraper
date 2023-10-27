import matplotlib.pyplot as plt
import seaborn as sb


def pairplot_agenzie(annunci):
    """
    Crea un pairplot delle variabili 'prezzo', 'mq', e 'locali' colorato per 'agenzia'.

    :param annunci: DataFrame con almeno le colonne 'agenzia', 'prezzo', 'mq', e 'locali'.
    """
    g = sb.pairplot(annunci, hue="agenzia", vars=["prezzo", "mq", "locali"])
    g.fig.suptitle("Pairplot per agenzia")
    plt.tight_layout()
    plt.show()
