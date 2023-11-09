# ImmoScraper - Documentazione

## Introduzione

Questa applicazione avanzata si distingue per la sua doppia competenza nell'acquisizione dinamica di dati immobiliari e
nella simulazione e analisi di transazioni immobiliari. Dotata di strumenti di scraping intelligenti e una suite
analitica multifunzionale, l'applicazione estrae dati dalle agenzie immobiliari per poi elaborarli, consentendo agli
utenti di ottenere preziose intuizioni sul mercato immobiliare.

## Funzionalità Core

### 1. Scraping e Analisi dei Dati Immobiliari

#### Scraping Dei Dati

Attraverso un sofisticato sistema di scraper, il modulo di recupero annunci interroga e aggrega dati da
multiple agenzie immobiliari. Implementando un ThreadPool, l'acquisizione delle pagine avviene in modo concorrente,
massimizzando l'efficienza mentre si presta attenzione a non sovraccaricare i server delle agenzie.

#### Analisi Dati Personalizzata

L'applicazione consente analisi personalizzate con la possibilità di aggiungere filtri specifici passati via linea di
comando, offrendo agli utenti la libertà di esaminare i dataset secondo parametri selezionati. Ciò aggiunge un livello
di personalizzazione all'analisi dei dati, rendendo gli insight rilevanti per esigenze specifiche.

### 2. Generazione e Analisi delle Transazioni

#### Generazione File Transazioni

Mediante un algoritmo di generazione casuale, vengono simulate transazioni immobiliari, producendo un file di
transazioni che serve da base per l'analisi delle dinamiche di mercato.

#### Analisi Delle Transazioni Con Grafi

I dati simulati vengono visualizzati in grafi di rete che illustrano le transazioni tra le parti, offrendo una
rappresentazione dettagliata e intuitiva delle relazioni e delle tendenze di mercato.

## Architettura dei Dati

La struttura dati su cui si basa l'app include file CSV essenziali per l'operatività dello scraping e per le analisi
effettuate:

- `agenzie.csv`: elenco delle agenzie e degli scraper associati.
- `annunci.csv`: annunci immobiliari con dettagli come prezzo e localizzazione.
- `tipologie.csv`: classificazione degli immobili.
- `transazioni.csv`: registro delle transazioni simulate.

## Innovazioni di Design

- **Modularità**: L'app è strutturata in moduli per facilitare l'espansione e la manutenzione.
- **Scalabilità**: La piattaforma è costruita per adattarsi a un volume crescente di dati senza perdere in prestazioni.
- **Interfaccia Comandi**: L'utente può filtrare i dati direttamente da linea di comando, per un'analisi mirata e
  flessibile.
- **Analisi Integrata**: L'app offre un'esperienza olistica che spazia dall'acquisizione dei dati fino alla loro
  interpretazione e visualizzazione.
