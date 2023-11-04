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
    if cinque_anni_dopo > end_date or dieci_anni_dopo > end_date:
        probabilita_5_10_anni = 0
    else:
        probabilita_5_10_anni = 0.9

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
    for lista in dizionario.values():
        if elemento in lista:
            return True

    return False


def _sono_case_tutte_assegnate(case, case_utenti):
    for casa in case:
        if not _cerca_elemento_in_sottoliste(case_utenti, casa):
            return False

    return True


def _scegli_venditore_e_casa(case, case_utenti, utenti):
    casa = None

    if _sono_case_tutte_assegnate(case, case_utenti) or random.random() < 0.8 or len(case) == 0:
        while True:
            venditore, case_utente = random.choice(list(case_utenti.items()))
            if case_utente:
                casa = random.choice(case_utente)
                break
    else:
        venditore = random.choice(utenti)
        MAX_TENTATIVI = 10
        for _ in range(MAX_TENTATIVI):
            casa = random.choice(case)
            if not _cerca_elemento_in_sottoliste(case_utenti, casa):
                break

    return venditore, casa


def _scegli_acquirente(venditore, utenti):
    while True:
        acquirente = random.choice(utenti)
        if acquirente != venditore:
            return acquirente


def _calcola_prezzo_e_data(transazioni, casa):
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

    NUM_RECORDS = int(args.numero_record)
    NUM_UTENTI = int(args.numero_utenti)
    NUM_AGENZIE = int(args.numero_agenzie)
    NUM_CASE = int(args.numero_case)

    # Generazione case
    case = [_genera_id_immobile() for _ in range(NUM_CASE)]

    # Generazione utenti
    utenti = [_genera_cf() for _ in range(NUM_UTENTI)]
    case_univoche = random.sample(case, NUM_UTENTI // 2)
    case_utenti = {utenti[i]: [case_univoche[i]] for i in range(NUM_UTENTI // 2)}

    # Generazione agenzie
    agenzie = [_genera_id_agenzia() for _ in range(NUM_AGENZIE)]

    transazioni = pd.DataFrame(
        columns=['id_transazione', 'acquirente', 'venditore', 'agenzia', 'immobile', 'prezzo', 'data']
    )

    for i in range(NUM_RECORDS):
        venditore, casa = _scegli_venditore_e_casa(case, case_utenti, utenti)
        if casa is None:
            logging.warning("Non ci sono case disponibili")
            break

        acquirente = _scegli_acquirente(venditore, utenti)
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
