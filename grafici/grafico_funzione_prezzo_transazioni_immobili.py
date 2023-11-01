from matplotlib import pyplot as plt


def plot_grafico_funzione_prezzo_transazioni_immobili(transazioni):
    """
    Genera un grafico a linee delle transazioni immobiliari.

    Questa funzione prende un DataFrame di transazioni immobiliari, raggruppa i dati per immobile,
    e poi plotta il prezzo di ogni immobile in funzione della data.

    :param transazioni: DataFrame contenente le transazioni immobiliari. Deve avere almeno tre colonne:
                        'immobile' con il nome dell'immobile, 'data' con la data della transazione,
                        e 'prezzo' con il prezzo di transazione.
    :return: Non ritorna nulla poiché il risultato è la visualizzazione di un grafico.

    Side effects:
        - Apre una finestra di matplotlib con il grafico delle transazioni.
        - Plotta i dati sul grafico.
        - Mostra una legenda al di fuori del grafico sulla destra.
    """
    _, ax = plt.subplots(figsize=(10, 5))

    for transazione in transazioni.groupby('immobile'):
        # Transazione è una tupla (nome_immobile, dataframe)
        transazione[1].plot(x='data', y='prezzo', label=transazione[0], ax=ax)

    plt.xlabel('Data')
    plt.ylabel('Prezzo')

    # Posiziona la legenda al di fuori del grafico sulla destra
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
