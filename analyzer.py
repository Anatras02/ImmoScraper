import numpy
import pandas as pd

from grafici import plot_grafico_a_torta_numero_annunci, plot_grafico_media_prezzi_nel_tempo, pairplot_agenzie, \
    plot_grafico_media_prezzi_nel_tempo_per_categoria
from grafici.plot_clusterizazzione import plot_clusterizazzione


def _get_annunci_join_tipologie():
    """
    Carica i dati relativi agli annunci e le loro tipologie da file CSV.

    :return: Un DataFrame contenente gli annunci uniti alle loro tipologie e agenzie.
    """
    tipologie = pd.read_csv("files/tipologie.csv", index_col="id")
    tipologie = tipologie.add_suffix('_tipologia')
    agenzie = pd.read_csv("files/agenzie.csv", index_col="id")
    agenzie = agenzie.add_suffix('_agenzia')

    annunci = pd.read_csv("files/annunci.csv")
    annunci = annunci.join(tipologie, on="tipologia", how="inner", rsuffix="_tipologia")
    annunci = annunci.join(agenzie, on="agenzia", how="inner", rsuffix="_agenzia")

    annunci["data_ultima_modifica_prezzo"] = pd.to_datetime(annunci["data_ultima_modifica_prezzo"])

    return annunci


def _edita_date_annunci(annunci):
    """
    Modifica la data di ultima modifica prezzo per ogni annuncio in modo casuale.

    :param annunci: DataFrame contenente gli annunci.
    """
    for i in range(len(annunci)):
        annunci.at[i, "data_ultima_modifica_prezzo"] = numpy.random.choice(
            pd.date_range(start="2023-01-01", end="2023-12-31"))


def main():
    """
    Funzione principale che esegue l'analisi sugli annunci e mostra vari grafici.
    """
    annunci = _get_annunci_join_tipologie()
    _edita_date_annunci(annunci)

    media_prezzo = annunci["prezzo"].mean()
    print(f"Media prezzo: € {media_prezzo:.2f}")

    mediana_prezzo = annunci["prezzo"].median()
    print(f"Mediana prezzo: € {mediana_prezzo:.2f}")

    derivazione_standard_prezzo = annunci["prezzo"].std()
    print(f"Derivazione standard prezzo: € {derivazione_standard_prezzo:.2f}")

    prezzo_minimo = annunci["prezzo"].min()
    print(f"Prezzo minimo: € {prezzo_minimo:.2f}")

    prezzo_massimo = annunci["prezzo"].max()
    print(f"Prezzo massimo: € {prezzo_massimo:.2f}")

    plot_grafico_a_torta_numero_annunci(annunci)
    plot_grafico_media_prezzi_nel_tempo(annunci)
    plot_grafico_media_prezzi_nel_tempo_per_categoria(annunci)
    pairplot_agenzie(annunci)
    plot_clusterizazzione(annunci)


if __name__ == '__main__':
    main()
