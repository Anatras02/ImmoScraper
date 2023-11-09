import argparse

import numpy
import numpy as np
import pandas as pd
from geopy.distance import geodesic

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
    annunci = annunci.join(tipologie, on="tipologia", how="inner", rsuffix="_tipologia", validate="many_to_one")
    annunci = annunci.join(agenzie, on="agenzia", how="inner", rsuffix="_agenzia", validate="many_to_one")

    annunci["data_ultima_modifica_prezzo"] = pd.to_datetime(annunci["data_ultima_modifica_prezzo"])

    return annunci


def _get_id_agenzie():
    """
    Estrae gli ID univoci delle agenzie da un file CSV.

    Legge il file 'agenzie.csv', che si presuppone contenga una colonna chiamata 'id' con gli ID delle agenzie, 
    e restituisce una lista di tali ID univoci.

    :return: Una lista degli ID univoci delle agenzie.
    :rtype: List[str]
    """
    df = pd.read_csv('files/agenzie.csv')
    return df['id'].unique().tolist()


def _get_args():
    """
    Analizza e restituisce gli argomenti passati dall'utente via riga di comando.

    Questa funzione permette all'utente di specificare vari filtri sugli annunci come prezzo minimo, prezzo massimo,
    latitudine, longitudine, raggio e numero dell'agenzia.

    :raises argparse.ArgumentError: Se vengono forniti valori non validi o mancanti per alcuni argomenti correlati
    (ad esempio, se si fornisce la latitudine ma non la longitudine o il raggio,
     o se il prezzo minimo è maggiore del prezzo massimo).

    :return: Un oggetto contenente tutti gli argomenti passati.
    :rtype: argparse.Namespace

    """
    parser = argparse.ArgumentParser(description='Fornisce impostazioni sui filtri da applicare agli annunci.')
    parser.add_argument('-pm', '--prezzo_minimo', type=int, help='Prezzo minimo', required=False)
    parser.add_argument('-pM', '--prezzo_massimo', type=int, help='Prezzo massimo', required=False)
    parser.add_argument('-lat', '--latitudine', type=float, help='Latitudine (Google Maps)', required=False)
    parser.add_argument('-lon', '--longitudine', type=float, help='Longitudine (Google Maps)', required=False)
    parser.add_argument('-r', '--raggio', type=float, help='Raggio (in km)', required=False)
    parser.add_argument('-a', '--agenzia', type=str, help='Numero dell\'agenzia', required=False,
                        choices=_get_id_agenzie())

    args = parser.parse_args()

    if any([args.latitudine, args.longitudine, args.raggio]) and not all(
            [args.latitudine, args.longitudine, args.raggio]):
        parser.error("Se specifichi uno tra latitudine, longitudine o raggio, devi specificare anche gli altri.")

    if args.prezzo_minimo and args.prezzo_massimo and args.prezzo_minimo > args.prezzo_massimo:
        parser.error("Il prezzo minimo deve essere minore del prezzo massimo.")

    return args


def _edita_date_annunci(annunci):
    """
    Modifica la data di ultima modifica prezzo per ogni annuncio in modo casuale.

    :param annunci: DataFrame contenente gli annunci.
    """
    for i in range(len(annunci)):
        # Crea un nuovo generatore di numeri casuali
        rng = np.random.default_rng(seed=i)

        # Genera un intervallo di date
        date_range = pd.date_range(start="2023-01-01", end="2023-12-31")

        # Seleziona casualmente una data dall'intervallo
        random_date = rng.choice(date_range)

        annunci.at[i, "data_ultima_modifica_prezzo"] = random_date


def _filtra_per_raggio(df, lat_centrale, lon_centrale, raggio):
    """
    Filtra il DataFrame in base alla distanza dal punto centrale specificato usando geopy.

    :param df: DataFrame originale con colonne 'lat' e 'lon'.
    :param lat_centrale: Latitudine del punto centrale.
    :param lon_centrale: Longitudine del punto centrale.
    :param raggio: Raggio in km entro il quale filtrare.
    :return: DataFrame filtrato.
    """

    # Definire il punto centrale come una tupla di latitudine e longitudine
    centro = (lat_centrale, lon_centrale)

    # Applica una funzione a ciascuna riga del DataFrame.
    # Per ogni riga, calcola la distanza tra le coordinate dell'annuncio e il punto centrale.
    # Se la distanza è minore o uguale al raggio specificato, restituisce True (l'annuncio è entro il raggio).
    # Altrimenti, restituisce False (l'annuncio è fuori dal raggio).
    maschera = df.apply(
        lambda riga: geodesic((riga['latitudine'], riga['longitudine']), centro).km <= raggio, axis=1
    )

    # Usa la maschera booleana per filtrare il DataFrame e restituire solo gli annunci entro il raggio specificato.
    return df[maschera]


def main():
    """
    Funzione principale che esegue l'analisi sugli annunci e mostra vari grafici.
    """
    args = _get_args()
    annunci = _get_annunci_join_tipologie()
    _edita_date_annunci(annunci)

    if args.prezzo_minimo:
        annunci = annunci[annunci["prezzo"] >= args.prezzo_minimo]
    if args.prezzo_massimo:
        annunci = annunci[annunci["prezzo"] <= args.prezzo_massimo]

    if all([args.latitudine, args.longitudine, args.raggio]):
        annunci = _filtra_per_raggio(annunci, args.latitudine, args.longitudine, args.raggio)

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
