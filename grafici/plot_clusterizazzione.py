import locale

from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def _genera_clusters(appartamenti):
    """
    Genera clusters utilizzando KMeans basato su prezzo e metri quadrati.

    :param appartamenti: DataFrame con le informazioni sugli appartamenti.
    :return: Tuple (modello KMeans, oggetto StandardScaler).
    """
    scaler = StandardScaler()
    appartamenti_standardizzati = scaler.fit_transform(appartamenti[["prezzo", "mq"]])

    kmeans = KMeans(n_clusters=6, n_init=10)
    kmeans.fit(appartamenti_standardizzati)
    appartamenti["cluster"] = kmeans.labels_

    return kmeans, scaler


def _stampa_media_prezzi_per_mq(centri, scaler, media_prezzo_per_cluster):
    """
    Annota la media dei prezzi per mq vicino ai centroidi nel grafico.

    :param centri: Centroidi dei cluster.
    :param scaler: StandardScaler utilizzato per invertire la scalatura.
    :param media_prezzo_per_cluster: Serie contenente il prezzo medio per mq per cluster.
    """
    centri_scala_originale = scaler.inverse_transform(centri)
    for i, (x, y) in enumerate(centri_scala_originale):
        numero_formattato = locale.format_string('%.2f', media_prezzo_per_cluster[i], grouping=True)

        # Annota la media del prezzo vicino al centroide con una freccetta e un box
        plt.annotate(
            f"€ {numero_formattato} al mq",
            (x, y),
            textcoords="offset points",
            xytext=(125, -30),
            ha='center',
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5')
        )


def _get_label(cluster_id, media_prezzo_per_cluster, media_rapporto_prezzo_mq_per_cluster):
    """
    Restituisce una descrizione del cluster in base al rapporto qualità-prezzo,
    al prezzo medio e ai metri quadrati medi del cluster.

    :param cluster_id: ID del cluster di cui si vuole ottenere la descrizione.
    :param media_prezzo_per_cluster: Serie contenente il prezzo medio per ogni cluster.
    :param media_rapporto_prezzo_mq_per_cluster: Serie contenente il rapporto qualità-prezzo medio per ogni cluster.
    :return: Stringa descrizione del cluster.
    """
    # Questo ci dà una comprensione di quali cluster hanno un buon valore rispetto al prezzo (basso prezzo per mq)
    # e quali sono costosi rispetto alla loro superficie (alto prezzo per mq).
    cluster_ordinati_rapporto = media_rapporto_prezzo_mq_per_cluster.sort_values().index.tolist()
    print(cluster_ordinati_rapporto)

    # Si considera che i primi tre cluster abbiano un basso prezzo per mq, mentre gli ultimi due abbiano un alto prezzo
    # per mq.
    cluster_basso_prezzo_mq = cluster_ordinati_rapporto[:3]
    cluster_alto_prezzo_mq = cluster_ordinati_rapporto[3:]

    print(cluster_basso_prezzo_mq)
    print(cluster_alto_prezzo_mq)

    # Ogni gruppo di cluster (basso o alto prezzo per mq) viene ulteriormente ordinato in base al prezzo totale.
    # Questo permette di determinare, ad esempio, quali "case economiche" sono effettivamente le più economiche in
    # termini di prezzo totale.
    cluster_basso_prezzo_mq = sorted(cluster_basso_prezzo_mq, key=lambda x: media_prezzo_per_cluster[x])
    cluster_alto_prezzo_mq = sorted(cluster_alto_prezzo_mq, key=lambda x: media_prezzo_per_cluster[x])

    # Una volta che i cluster sono stati ordinati in questo modo, la funzione assegna una descrizione in base al
    # cluster_id fornito, basandosi sulla sua posizione tra i cluster ordinati.
    if cluster_id == cluster_basso_prezzo_mq[0]:
        label = "Case Economiche di Piccola Dimensione"
    elif cluster_id == cluster_basso_prezzo_mq[1]:
        label = "Case Economiche di Media Dimensione"
    elif cluster_id == cluster_basso_prezzo_mq[2]:
        label = "Case Economiche di Grande Dimensione"
    elif cluster_id == cluster_alto_prezzo_mq[0]:
        label = "Case di Lusso di Piccola Dimensione"
    elif cluster_id == cluster_alto_prezzo_mq[1]:
        label = "Case di Lusso di Media Dimensione"
    elif cluster_id == cluster_alto_prezzo_mq[2]:
        label = "Case di Lusso di Grande Dimensione"
    else:
        label = "Cluster sconosciuto"

    return label


def _get_cluster_e_label_ordinate(appartamenti, media_prezzo_per_cluster, media_rapporto_prezzo_mq_per_cluster):
    """
    Ordina i cluster di appartamenti in base alle etichette assegnate e alla priorità definita.

    Questa funzione prende in ingresso una serie di informazioni sugli appartamenti e le loro
    media di prezzo, metri quadri e il rapporto tra prezzo e metri quadri per cluster. Dopo aver
    assegnato un'etichetta a ciascun cluster utilizzando la funzione `_get_label`, la funzione ordina
    i cluster in base alla priorità delle etichette.

    Args:
    - appartamenti (pd.DataFrame): DataFrame contenente informazioni sugli appartamenti, inclusa una colonna 'cluster'
     per l'ID del cluster.
    - media_prezzo_per_cluster (pd.Series): Series con i cluster ID come indici e la media di prezzo come valore.
    - media_mq_per_cluster (pd.Series): Series con i cluster ID come indici e la media di metri quadri come valore.
    - media_rapporto_prezzo_mq_per_cluster (pd.Series): Series con i cluster ID come indici e la media del rapporto
    tra prezzo e metri quadri come valore.

    Returns:
    - list of tuple: Una lista di tuple, dove ogni tupla ha l'ID del cluster come primo elemento e l'etichetta come secondo elemento. La lista è ordinata in base alla priorità delle etichette.
    """
    priorita_etichette = {
        "Case Economiche di Piccola Dimensione": 1,
        "Case Economiche di Media Dimensione": 2,
        "Case Economiche di Grande Dimensione": 3,
        "Case di Lusso di Piccola Dimensione": 4,
        "Case di Lusso di Media Dimensione": 5,
        "Case di Lusso di Grande Dimensione": 6,
    }

    cluster_e_etichette = []

    for cluster_id in appartamenti["cluster"].unique():
        label = _get_label(cluster_id, media_prezzo_per_cluster, media_rapporto_prezzo_mq_per_cluster)
        cluster_e_etichette.append((cluster_id, label))

    return sorted(
        cluster_e_etichette,
        key=lambda x: priorita_etichette[x[1]]  # Ordina in base alla priorità delle etichette
    )


def _plot_cluster_data(appartamenti, cluster_e_etichette_ordinati):
    """
    Plotta i dati degli appartamenti per ogni cluster.

    :param appartamenti: DataFrame degli appartamenti.
    :param cluster_e_etichette_ordinati: Lista di tuple con ID del cluster e etichetta associata.
    """
    for cluster_id, label in cluster_e_etichette_ordinati:
        subset = appartamenti[appartamenti["cluster"] == cluster_id]
        plt.scatter(subset["prezzo"], subset["mq"], label=label, cmap='rainbow')


def plot_clusterizazzione(annunci):
    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

    appartamenti = annunci[annunci["nome_tipologia"] == "appartamento"].copy()
    appartamenti_senza_prezzi_nan = appartamenti.dropna(subset=["prezzo"]).copy()
    appartamenti_senza_prezzi_nan.sort_values(by="data_ultima_modifica_prezzo", inplace=True)

    kmeans, scaler = _genera_clusters(appartamenti_senza_prezzi_nan)

    media_prezzo_per_cluster = appartamenti_senza_prezzi_nan.groupby("cluster")["prezzo"].mean()
    media_mq_per_cluster = appartamenti_senza_prezzi_nan.groupby("cluster")["mq"].mean()
    media_rapporto_prezzo_mq_per_cluster = (media_prezzo_per_cluster / media_mq_per_cluster).sort_values()

    plt.figure(figsize=(12, 8))

    cluster_e_etichette_ordinati = _get_cluster_e_label_ordinate(appartamenti_senza_prezzi_nan,
                                                                 media_prezzo_per_cluster,
                                                                 media_rapporto_prezzo_mq_per_cluster)
    _plot_cluster_data(appartamenti_senza_prezzi_nan, cluster_e_etichette_ordinati)

    _stampa_media_prezzi_per_mq(kmeans.cluster_centers_, scaler, media_rapporto_prezzo_mq_per_cluster)

    plt.legend()
    plt.xlabel("Prezzo")
    plt.ylabel("Metri quadrati")
    plt.title("Clusterizzazione appartamenti per prezzo e metri quadrati")
    plt.show()
