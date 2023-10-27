# ImmoScraper

Questo progetto contiene strumenti per effettuare scraping di annunci e analizzarli, mostrando statistiche e generando grafici.

## Prerequisiti

- **Python**: Questo progetto richiede Python 3.10. Assicurati di averlo installato. Se non hai Python o non sei sicuro della versione, puoi scaricarlo da [qui](https://www.python.org/downloads/).

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
