from matplotlib import pyplot as plt

from grafici.functions import get_nome_agenzia


def plot_grafico_a_torta_numero_annunci(annunci):
    grouped_by_agenzia = annunci.groupby("agenzia")
    plt.figure(figsize=(10, 6))
    labels = [get_nome_agenzia(key) for key in grouped_by_agenzia.groups.keys()]
    plt.pie(grouped_by_agenzia["riferimento"].count(), autopct='%1.1f%%', labels=labels)
    plt.tight_layout()
    plt.show()
