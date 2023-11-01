from matplotlib import pyplot as plt


# Funzione per preparare i dati
def prepara_dati(annunci):
    """
    Prepara i dati degli annunci immobiliari eliminando le righe con prezzo NaN, calcolando la media mobile
    settimanale e interpolando i dati mancanti.

    La funzione elimina gli annunci senza prezzo e ordina gli annunci in base alla data di ultima modifica
    del prezzo. Calcola poi la media mobile settimanale e gestisce eventuali valori NaN attraverso un'interpolazione
    lineare. Viene infine filtrato il dataset per mantenere solo le righe con una media settimanale maggiore di 0.

    :param annunci: DataFrame degli annunci immobiliari.
                    Deve contenere le colonne "prezzo" e "data_ultima_modifica_prezzo".
    :return: DataFrame degli annunci preparato.
    """
    annunci_preparati = annunci.dropna(subset=["prezzo"]).copy()
    annunci_preparati.sort_values(by="data_ultima_modifica_prezzo", inplace=True)
    annunci_preparati["media_settimanale"] = annunci_preparati["prezzo"].rolling(window=7, min_periods=1).mean()
    annunci_preparati["media_settimanale"].interpolate(method="linear", inplace=True)
    annunci_preparati = annunci_preparati[annunci_preparati["media_settimanale"] > 0]

    return annunci_preparati


# Funzione per plottare il grafico per una singola categoria
def plot_categoria(ax, dati_categoria, nome_categoria):
    """
    Plotta il grafico della media mobile dei prezzi per una singola categoria di annunci immobiliari.

    La funzione prende un subset di dati relativi a una specifica categoria e plotta la media mobile dei prezzi
    nel tempo.

    :param ax: AxesSubplot su cui plottare il grafico.
    :param dati_categoria: DataFrame contenente i dati della categoria specifica.
    :param nome_categoria: Stringa rappresentante il nome della categoria.
    """
    ax.plot(
        dati_categoria["data_ultima_modifica_prezzo"],
        dati_categoria["media_settimanale"],
        label=nome_categoria
    )
    ax.set_xlabel("Data")
    ax.set_ylabel("Prezzo")
    ax.set_title(f"Media prezzi nel tempo per {nome_categoria}")
    ax.legend()


def _get_categorie_con_abbastanza_dati(categorie, dati_preparati, soglia=5):
    """
    Restituisce una lista delle categorie che hanno un numero di dati superiore alla soglia specificata.

    Questa funzione serve a filtrare le categorie che hanno pochi dati, dato che plottare un grafico con pochi
    punti potrebbe non fornire informazioni significative.

    :param categorie: Lista delle categorie da controllare.
    :param dati_preparati: DataFrame contenente i dati preparati.
    :param soglia: Numero minimo di dati che una categoria deve avere per essere considerata (default è 5).
    :return: Lista delle categorie che soddisfano la soglia.
    """
    return [
        categoria for categoria in categorie if
        len(dati_preparati[dati_preparati['nome_tipologia'] == categoria]) > soglia
    ]


def plot_grafico_media_prezzi_nel_tempo_per_categoria(annunci):
    """
    Plotta un set di grafici rappresentanti la media mobile dei prezzi nel tempo per ciascuna categoria
    di annunci immobiliari.

    La funzione prepara prima i dati e poi determina quali categorie hanno un numero sufficiente di punti dati
    per essere plottate. Ogni categoria viene poi visualizzata in un subplot dedicato.

    :param annunci: DataFrame degli annunci immobiliari.
                    Deve contenere le colonne "prezzo", "data_ultima_modifica_prezzo" e "nome_tipologia".
    """
    dati_preparati = prepara_dati(annunci)
    categorie = _get_categorie_con_abbastanza_dati(dati_preparati['nome_tipologia'].unique(), dati_preparati)

    _, axs = plt.subplots(len(categorie), 1, figsize=(10, 3 * len(categorie)))

    # Se c'è solo una categoria, assicurarsi che axs sia una lista
    if len(categorie) == 1:
        axs = [axs]

    for i, categoria in enumerate(categorie):
        dati_categoria = dati_preparati[dati_preparati['nome_tipologia'] == categoria]
        plot_categoria(axs[i], dati_categoria, categoria)

    plt.tight_layout()
    plt.show()
