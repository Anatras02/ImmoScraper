from matplotlib import pyplot as plt


def plot_grafico_a_torta_numero_annunci(annunci):
    grouped_by_agenzia = annunci.groupby("agenzia")
    plt.figure(figsize=(10, 6))

    labels = [group[1]['nome_agenzia'].iloc[0] for group in grouped_by_agenzia]
    plt.pie(grouped_by_agenzia["riferimento"].count(), autopct='%1.1f%%', labels=labels)

    plt.show()
