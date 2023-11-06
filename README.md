# ImmoScraper

Questo progetto contiene strumenti per effettuare scraping di annunci e analizzarli, mostrando statistiche e generando grafici.

## Prerequisiti

- **Python**: Questo progetto richiede Python 3.10. Assicurati di averlo installato. Se non hai Python o non sei sicuro della versione, puoi scaricarlo da [qui](https://www.python.org/downloads/).
- **Graphviz**: È necessario avere Graphviz installato per generare alcuni dei grafici. Puoi installarlo da [qui](https://www.graphviz.org/download/).

## Installazione

1. Clona il repository:
   ```
   git clone https://github.com/Anatras02/ImmoScraper.git
   ```

2. Entra nella directory del progetto:
   ```
   cd ImmoScraper
   ```

3. (Opzionale) È consigliato utilizzare un ambiente virtuale per isolare le dipendenze. Puoi crearne uno ed attivarlo con:
   ```
   python -m venv env
   source env/bin/activate  # Su Windows, usa `env\Scripts\activate`
   ```

4. Installa le dipendenze del progetto:
   ```
   pip install -r requirements.txt
   ```

## Utilizzo

Il progetto contiene due principali script:

### 1. `scraper.py`

Questo script effettua lo scraping degli annunci e salva i risultati in `files/annunci.csv`.

Esegui lo script con:
```
python scraper.py
```

### 2. `analyzer.py`

Questo script prende gli annunci salvati, mostra diverse statistiche e genera grafici.

Esegui lo script con:
```
python analyzer.py
```

### 3. `generatore_csv_transazioni.py`

Questo script genera un file CSV con un insieme di record di transazioni. Devi fornire alcuni parametri obbligatori che definiscono il numero di record, utenti, agenzie e case da generare. Ecco una spiegazione dei parametri e i relativi vincoli:

- `-n` / `--numero_record`: Il numero totale di record da generare (obbligatorio).
- `-u` / `--numero_utenti`: Il numero di utenti da includere. Non può superare il numero di record (obbligatorio).
- `-a` / `--numero_agenzie`: Il numero di agenzie da includere. Non può superare il numero di record (obbligatorio).
- `-nC` / `--numero_case`: Il numero di case da includere. Non può superare né il numero di record né il numero di utenti (obbligatorio).

Per eseguire lo script con i parametri richiesti:

```
python generatore_csv_transazioni.py -n 100 -u 10 -a 5 -nC 50
```

Assicurati di sostituire i valori `100`, `10`, `5`, e `50` con i numeri desiderati per i tuoi record, utenti, agenzie e case, rispettando i vincoli imposti.


### 4. `transaction_analyzer.py`

Questo script analizza le transazioni. Esegui lo script con il seguente comando:

```
python transaction_analyzer.py
```

Assicurati che il file transazioni.csv sia presente nella directory `files/` affinché lo script possa funzionare correttamente.
