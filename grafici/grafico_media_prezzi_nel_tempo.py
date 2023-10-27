from matplotlib import pyplot as plt


def plot_grafico_media_prezzi_nel_tempo(annunci):
    """
    Plotta un grafico che rappresenta la media mobile settimanale dei prezzi degli annunci nel tempo.

    Questa funzione prende in input un DataFrame di annunci immobiliari, calcola la media mobile settimanale
    dei prezzi, e plotta la media nel tempo. Si assicura anche che non vi siano valori NaN nel prezzo e li
    sostituisce interpolando linearmente i dati.

    La media mobile è utilizzata per smussare le fluttuazioni a breve termine e evidenziare le tendenze
    generali. In questo contesto, si utilizza una finestra di 7 giorni per catturare le tendenze settimanali
    nei prezzi, riducendo il rumore causato da variazioni giornaliere.

    L'interpolazione lineare viene applicata per gestire eventuali valori NaN nella serie temporale,
    assicurando che il grafico sia continuo e che le tendenze siano facilmente visibili.

    :param annunci: DataFrame degli annunci immobiliari. Deve contenere le colonne "prezzo" e
                    "data_ultima_modifica_prezzo".
    """
    annunci_senza_prezzi_nan = annunci.dropna(subset=["prezzo"], inplace=False).copy()
    annunci_senza_prezzi_nan.sort_values(by="data_ultima_modifica_prezzo", inplace=True)
    annunci_senza_prezzi_nan["media_settimanale"] = annunci_senza_prezzi_nan["prezzo"].rolling(window=7,
                                                                                               min_periods=1).mean()
    annunci_senza_prezzi_nan["media_settimanale"].interpolate(method="linear", inplace=True)
    annunci_senza_prezzi_nan.plot(x='data_ultima_modifica_prezzo', y='media_settimanale')
    plt.title("Media prezzi nel tempo")
    plt.tight_layout()
    plt.show()

