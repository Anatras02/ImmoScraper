from matplotlib import pyplot as plt


def plot_grafico_a_torta_numero_annunci(annunci):
    """
    Visualizza un grafico a torta che mostra la distribuzione percentuale degli annunci immobiliari per agenzia.

    La funzione raggruppa gli annunci in base al nome dell'agenzia e calcola il conteggio degli annunci per ogni agenzia.
    Il grafico a torta risultante visualizza la percentuale degli annunci di ciascuna agenzia rispetto al totale.

    :param annunci: DataFrame contenente gli annunci immobiliari, con le colonne 'agenzia' e 'nome_agenzia'.
    :type annunci: pd.DataFrame
    :return: None. La funzione genera un grafico a torta come output e non restituisce alcun valore.
    """
    grouped_by_agenzia = annunci.groupby("agenzia")
    plt.figure(figsize=(10, 6))

    labels = [group[1]['nome_agenzia'].iloc[0] for group in grouped_by_agenzia]
    plt.pie(grouped_by_agenzia["riferimento"].count(), autopct='%1.1f%%', labels=labels)

    plt.show()
