import numpy
import pandas as pd
import matplotlib.pyplot as plt

from config.definitions import AGENZIE
from grafici import plot_grafico_a_torta_numero_annunci, plot_grafico_media_prezzi_nel_tempo


def get_annunci_join_tipologie():
    tipologie = pd.read_csv("tipologie.csv", index_col="id")
    annunci = pd.read_csv("annunci.csv")
    return pd.merge(annunci, tipologie, left_on="tipologia", right_on="id")


def edita_date_annunci(annunci):
    for i in range(len(annunci)):
        annunci.at[i, "data_ultima_modifica_prezzo"] = numpy.random.choice(
            pd.date_range(start="2023-01-01", end="2023-12-31"))


def main():
    annunci = get_annunci_join_tipologie()
    edita_date_annunci(annunci)

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


if __name__ == '__main__':
    main()
