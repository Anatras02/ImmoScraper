from matplotlib import pyplot as plt


# Funzione per preparare i dati
def prepara_dati(annunci):
    annunci_preparati = annunci.dropna(subset=["prezzo"]).copy()
    annunci_preparati.sort_values(by="data_ultima_modifica_prezzo", inplace=True)
    annunci_preparati["media_settimanale"] = annunci_preparati["prezzo"].rolling(window=7, min_periods=1).mean()
    annunci_preparati["media_settimanale"].interpolate(method="linear", inplace=True)
    annunci_preparati = annunci_preparati[annunci_preparati["media_settimanale"] > 0]

    return annunci_preparati


# Funzione per plottare il grafico per una singola categoria
def plot_categoria(ax, dati_categoria, nome_categoria):
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
    return [
        categoria for categoria in categorie if
        len(dati_preparati[dati_preparati['nome_tipologia'] == categoria]) > soglia
    ]


# Funzione principale per plottare il grafico per tutte le categorie
def plot_grafico_media_prezzi_nel_tempo_per_categoria(annunci):
    dati_preparati = prepara_dati(annunci)
    categorie = _get_categorie_con_abbastanza_dati(dati_preparati['nome_tipologia'].unique(), dati_preparati)

    fig, axs = plt.subplots(len(categorie), 1, figsize=(10, 3 * len(categorie)))

    # Se c'è solo una categoria, assicurarsi che axs sia una lista
    if len(categorie) == 1:
        axs = [axs]

    for i, categoria in enumerate(categorie):
        dati_categoria = dati_preparati[dati_preparati['nome_tipologia'] == categoria]
        plot_categoria(axs[i], dati_categoria, categoria)

    plt.tight_layout()
    plt.show()
