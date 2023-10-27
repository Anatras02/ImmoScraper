import matplotlib.pyplot as plt
import seaborn as sb


def pairplot_agenzie(annunci):
    g = sb.pairplot(annunci, hue="agenzia", vars=["prezzo", "mq", "locali"])
    g.fig.suptitle("Pairplot per agenzia")
    plt.tight_layout()
    plt.show()
