"""
Genera un file CSV contenente informazioni sulle transazioni.
"""
import argparse
import logging
import random
import string
from datetime import datetime, timedelta

import pandas as pd


def _genera_cf():
    """
    Genera un Codice Fiscale (CF) casuale.

    :return: str Il Codice Fiscale generato casualmente.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


def _genera_id_agenzia():
    """
    Genera un ID casuale per un'agenzia.

    :return: str L'ID dell'agenzia generato casualmente.
    """
    return ''.join(random.choices(string.ascii_uppercase, k=3))


def _genera_id_immobile():
    """
    Genera un ID casuale per un immobile.

    :return: str L'ID dell'immobile generato casualmente.
    """
    return f"Casa_{random.randint(0, 1000)}"


def _genera_data(data_ultima_transazione=None):
    """
    Genera una data casuale, dando priorità alle date comprese tra 5 e 10 anni
    dalla data data_ultima_transazione fornita.

    Se `data_ultima_transazione` è fornita, la data generata sarà successiva
    a questa data e antecedente o uguale alla data odierna.

    Se `data_ultima_transazione` non è fornita, la data generata sarà
    compresa tra il 1 gennaio 1900 e il 31 dicembre 1920. Questa scelta è motivata
    dal desiderio di iniziare con case che sono state tutte inizialmente vendute
    nello stesso periodo storico.

    La funzione ha una probabilità del 90% di scegliere una data nell'intervallo
    compreso tra 5 e 10 anni dalla `data_ultima_transazione`. In caso contrario,
    sceglie una data casuale nel range disponibile.

    :param datetime data_ultima_transazione: La data dell'ultima transazione
                                             registrata. Se None, verrà scelto un intervallo iniziale.

    :return: datetime Una data generata in base ai criteri sopra descritti.
    """
    if data_ultima_transazione is not None:
        start_date = data_ultima_transazione
        end_date = datetime.now()
    else:
        start_date = datetime(1900, 1, 1)
        end_date = datetime(1920, 12, 31)

    # Intervallo di date compreso tra 5 e 10 anni dalla data_ultima_transazione
    cinque_anni_dopo = start_date + timedelta(days=5 * 365)  # approssimazione di 5 anni
    dieci_anni_dopo = start_date + timedelta(days=10 * 365)  # approssimazione di 10 anni

    # Probabilità di scegliere una data nell'intervallo 5-10 anni
    probabilita_5_10_anni = 0.9
    if cinque_anni_dopo > end_date or dieci_anni_dopo > end_date:
        probabilita_5_10_anni = 0

    if random.random() < probabilita_5_10_anni:
        delta_5_10 = dieci_anni_dopo - cinque_anni_dopo
        giorni_casuali_5_10 = random.randint(0, delta_5_10.days)
        return cinque_anni_dopo + timedelta(days=giorni_casuali_5_10)
    else:
        delta_totale = end_date - start_date
        giorni_casuali_totali = random.randint(0, delta_totale.days)
        return start_date + timedelta(days=giorni_casuali_totali)


def _get_args():
    """
    Ottiene gli argomenti dalla linea di comando usando argparse.

    Controlla la validità degli argomenti forniti e restituisce un oggetto che contiene
    tutti gli argomenti parsati.

    :return: Namespace L'oggetto contenente tutti gli argomenti della riga di comando parsati.
    """
    parser = argparse.ArgumentParser(description="Impostazioni generazione CSV transazioni")
    parser.add_argument('-n', '--numero_record', type=int, help='Numero di record da generare', required=True)
    parser.add_argument('-u', '--numero_utenti', type=int, help='Numero di utenti da generare', required=True)
    parser.add_argument('-a', '--numero_agenzie', type=int, help='Numero di agenzie da generare', required=True)
    parser.add_argument('-nC', '--numero_case', type=int, help='Numero di case da generare', required=True)

    args = parser.parse_args()

    if args.numero_utenti > args.numero_record:
        parser.error("Il numero di utenti non può essere maggiore del numero di record")
    if args.numero_agenzie > args.numero_record:
        parser.error("Il numero di agenzie non può essere maggiore del numero di record")
    if args.numero_case > args.numero_record:
        parser.error("Il numero di case non può essere maggiore del numero di record")
    if args.numero_case > args.numero_utenti:
        parser.error("Il numero di case non può essere maggiore del numero di utenti")

    return args


def _cerca_elemento_in_sottoliste(dizionario, elemento):
    """
    Cerca un elemento all'interno delle sottoliste di un dizionario.

    :param dizionario: Un dizionario le cui sottoliste verranno esaminate alla ricerca dell'elemento.
    :type dizionario: dict
    :param elemento: L'elemento da cercare all'interno delle sottoliste del dizionario.
    :type elemento: Any
    :return: True se l'elemento è presente in almeno una delle sottoliste, altrimenti False.
    :rtype: bool
    """
    for lista in dizionario.values():
        if elemento in lista:
            return True

    return False


def _sono_case_tutte_assegnate(case, case_utenti):
    """
    Verifica se tutte le case nella lista sono state assegnate agli utenti.

    :param case: Una lista di case da controllare.
    :type case: list
    :param case_utenti: Un dizionario che associa ogni venditore alle case che ha in vendita.
    :type case_utenti: dict
    :return: True se tutte le case sono assegnate, altrimenti False.
    :rtype: bool
    """
    for casa in case:
        if not _cerca_elemento_in_sottoliste(case_utenti, casa):
            return False

    return True


def _scegli_venditore_e_casa(case, case_utenti, utenti):
    """
    Seleziona un venditore e una casa, basandosi sulle assegnazioni attuali e una probabilità casuale.

    :param case: Una lista di case disponibili.
    :type case: list
    :param case_utenti: Un dizionario che associa ogni venditore alle case che ha in vendita.
    :type case_utenti: dict
    :param utenti: Una lista di utenti tra cui scegliere il venditore.
    :type utenti: list
    :return: Una tupla contenente il venditore selezionato e la casa corrispondente.
    :rtype: tuple
    """
    if _sono_case_tutte_assegnate(case, case_utenti) or random.random() < 0.8 or len(case) == 0:
        while True:
            venditore, case_utente = random.choice(list(case_utenti.items()))
            if case_utente:
                casa = random.choice(case_utente)
                break
    else:
        venditore = random.choice(utenti)
        while True:
            casa = random.choice(case)
            if not _cerca_elemento_in_sottoliste(case_utenti, casa):
                break

        print(f"Venditore: {venditore}, casa: {casa}")

    return venditore, casa


def _scegli_acquirente(venditore, utenti, transazioni_casa):
    """
    Seleziona un acquirente diverso dal venditore, che non sia l'ultimo venditore della casa.

    :param venditore: Il venditore attuale della casa.
    :type venditore: str
    :param utenti: Una lista di utenti tra cui scegliere l'acquirente.
    :type utenti: list
    :param transazioni_casa: DataFrame delle transazioni per una specifica casa.
    :type transazioni_casa: pd.DataFrame
    :return: L'acquirente selezionato per la transazione.
    :rtype: str
    """
    ultima_transazione = transazioni_casa.groupby('immobile').last()
    if ultima_transazione.empty:
        ultimo_venditore = None
    else:
        ultimo_venditore = ultima_transazione['venditore'].iloc[0]

    while True:
        acquirente = random.choice(utenti)
        if acquirente != venditore:
            if len(ultima_transazione) == 0 or ultimo_venditore != acquirente:
                return acquirente


def _calcola_prezzo_e_data(transazioni, casa):
    """
    Calcola il prezzo e la data dell'ultima transazione per una determinata casa.

    :param transazioni: DataFrame contenente le transazioni immobiliari.
    :type transazioni: pd.DataFrame
    :param casa: La casa per cui calcolare il prezzo e la data dell'ultima transazione.
    :type casa: str
    :return: Il prezzo calcolato e la data dell'ultima transazione (se presente).
    :rtype: tuple
    """
    transazioni_casa = transazioni[transazioni['immobile'] == casa]
    if len(transazioni_casa) == 0:
        prezzo = random.randint(100000, 10000000)
        data_ultima_transazione = None
    else:
        ultima_transazione = transazioni_casa.groupby('immobile').last()
        prezzo_ultima_transazione = ultima_transazione['prezzo'].iloc[0]
        data_ultima_transazione = ultima_transazione['data'].iloc[0]
        variazione_percentuale = random.uniform(-0.30, 0.30)
        prezzo = round(prezzo_ultima_transazione * (1 + variazione_percentuale))

    return prezzo, data_ultima_transazione


def main():
    """
    Funzione principale per generare un file CSV contenente informazioni sulle transazioni.

    Questa funzione genera un numero specificato di record, utenti, agenzie e case e
    registra le transazioni in un DataFrame. Infine, salva il DataFrame in un file CSV.
    """
    args = _get_args()

    numero_record = int(args.numero_record)
    numero_utenti = int(args.numero_utenti)
    numero_agenzie = int(args.numero_agenzie)
    numero_case = int(args.numero_case)

    # Generazione case
    case = [_genera_id_immobile() for _ in range(numero_case)]

    # Generazione utenti
    utenti = [_genera_cf() for _ in range(numero_utenti)]
    case_univoche = random.sample(case, numero_utenti // 2)
    case_utenti = {utenti[i]: [case_univoche[i]] for i in range(numero_utenti // 2)}

    # Generazione agenzie
    agenzie = [_genera_id_agenzia() for _ in range(numero_agenzie)]

    transazioni = pd.DataFrame(
        columns=['id_transazione', 'acquirente', 'venditore', 'agenzia', 'immobile', 'prezzo', 'data']
    )

    for i in range(numero_record):
        venditore, casa = _scegli_venditore_e_casa(case, case_utenti, utenti)
        transazioni_casa = transazioni[transazioni['immobile'] == casa]
        if casa is None:
            logging.warning("Non ci sono case disponibili")
            break

        acquirente = _scegli_acquirente(venditore, utenti, transazioni_casa)
        prezzo, data_ultima_transazione = _calcola_prezzo_e_data(transazioni, casa)
        agenzia = random.choice(agenzie)

        case_utenti.setdefault(acquirente, []).append(casa)
        if venditore in case_utenti and casa in case_utenti[venditore]:
            case_utenti[venditore].remove(casa)

        transazioni.loc[i] = {
            'id_transazione': i,
            'acquirente': acquirente,
            'venditore': venditore,
            'agenzia': agenzia,
            'immobile': casa,
            'prezzo': prezzo,
            'data': _genera_data(data_ultima_transazione)
        }

    transazioni.to_csv('files/transazioni.csv', index=False)


if __name__ == '__main__':
    main()
