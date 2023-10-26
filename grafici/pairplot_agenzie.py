import matplotlib.pyplot as plt
import seaborn as sb


def pairplot_agenzie(annunci):
    sb.pairplot(annunci, hue="agenzia", vars=["prezzo", "mq", "locali"])
    plt.show()
