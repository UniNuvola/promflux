# Promflux
Questo tool è creato per far da tramite tra Prometheus e Influx.
Il suo scopo è quello di salvare informazione specifiche dall'aggregatore Prometheus a un database Influx per conservare nel tempo informazioni chiave.

> In questo readme spiegherò la logica del progetto dato che la descrizione del comportamento del codice è scritto come commento nel codice stesso - questa guida si propone come uno strumento per poter mettere in piedi il sistema e si occupa di spiegare funzionalità o pecularietà ma non spiega il funzionamento del codice.

## Installazione
Il progetto è composto da vari file python il file principale è **promflux.py**.
La divisione del comportamento, richiedere a prometheus i dati, la scrittura su influx e il parsing sulle regole è diviso nelle classi contenute nella cartella **Wrappers**.
Per installare il progetto è presente nella cartella il comodissimo *requirements.txt*, quindi per installare le dipendenze lanciare il comando.

```sh
pip install -r requirements.txt
```
Lo script contiene anche l'help per il settaggio infatti lanciando:
```sh 
python3 promflux.py -h
```
Verranno stampate a schermo le configurazioni che è possibile passagli da riga di comando.
Esiste in più la possibilità di passare i  parametri necessari anche tramite variabili d'ambiente descritte nel file **.env.sample**.
> Si noti che i parametri passati allo script da riga di comando hanno la precedente sulle variabili d'ambiente settate.
>> Si noti che lo script si aspetta il file .env nella cartella dove è contenuto lo script.

```sh
cp .env.sample .env
```
per poi modificare le variabili d'ambiente con quelle corrette.

## Regole
Lo script si aspetta un file di tipo yaml che contenga le regole, una serie di query che fara è salverà sul database. Questo file deve essere leggibile dallo script.
Esiste una versione di esempio **example.yaml** che puo essere copiata e aggiornata con le query che sono necessarie da salvare.
```sh
cp example.yaml rule.yaml
```
### Specifiche
```yaml
rules:
    - name: "Rule Name" # Name of the rule that will be saved
      query: "<query>"  # Query that will generate data
      start: "1970-01-01 00:00:00 UTC" #[OPZIONALE]
      end: "1970-01-01 00:00:00 UTC" #[OPZIONALE]
      step: 1200 | "1d" #[OPZIONALE] https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries
```
Nello specifico vanno pero menzionate dei dettagli.
Si possono avere un numero infinito di regole
```yaml
rules:
    - name: "Rule Name"
      query: "<query>"
    - name: "Rule Name"
      query: "<query>"

    ...

    - name: "Rule Name"
      query: "<query>"
    - name: "Rule Name"
      query: "<query>"
```

Ma si consideri che se è richiesta una query a range tutti i campi opzionali vanno inseriti

```yaml
rules:
    - name: "Rule Name" # Name of the rule that will be saved
      query: "<query>"  # Query that will generate data
      start: "1970-01-01 00:00:00 UTC" #[OPZIONALE]
      end: "1970-01-01 00:00:00 UTC" #[OPZIONALE]
      step: 1200 | "1d" #[OPZIONALE] https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries
```
> **start** e **end** sono campi speciali, che richiedono una data, dato ciò è inutile che abbiano dei valori temporali fissi.
Ho quindi aggiunto la possibilità di ricercare temporalmente tramite testo quindi testualmente valori come '1d ago' e 'today' sono validi per i campi rispettivamente **start** e **end**

Esempio:
```yaml
rules:
    - name: "Rule Name" # Name of the rule that will be saved
      query: "<query>"  # Query that will generate data
      start: "1d ago" #[OPZIONALE]
      end: "today" #[OPZIONALE]
      step: "1d" #[OPZIONALE] https://prometheus.io/docs/prometheus/latest/querying/api/#range-queries
```

Il campo step significa la granularità tra i vari dati. Utilizzo in maniera identica quella richiesta da Prometheus. In caso di confusione fare riferimento al link delle API per chiarimenti.

---
Il campo **name** della regola sara il nome della tabella influx su cui verranno scritte le informazioni.
Le queri possono essere anche di tipo differente e avere lo stesso nome influx non richiede che le informazioni siano strutturalmente uguali.

## Influx
Per quanto riguarda influx le informazioni vengono scritte nel database **uninuvola** sotto la organizzazione **uninuvola**.
Queste informazioni sono codificate nel file **Wrappers/Influx.py** nella funzione **write**.