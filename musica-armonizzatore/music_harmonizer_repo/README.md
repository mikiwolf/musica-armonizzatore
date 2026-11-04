# Music Harmonizer

Repository standalone contenente solo `music_harmonizer.py`.

## Requisiti

- Python 3.13+
- pygame
- mido

Nella scheda **Note Musicali**, il pulsante **Analizza** mostra le triadi costruite per terze sui gradi della scala. Per le scale di sette note indica qualità, numeri romani e funzione/tendenza armonica, comprese le scale modali; le scale con un diverso numero di note sono descritte senza attribuire loro funzioni tonali standard. La nota `8`, se presente, indica l'ottava e non viene contata come un grado aggiuntivo. Sotto l'analisi sono riportati anche gli accordi e i rivolti del voicing selezionato.

Le formule personalizzate devono iniziare da `1` e inserire i gradi in ordine crescente; `8` indica esplicitamente l'ottava superiore ed è facoltativo.

La scheda **Sequencer** consente di scegliere tonalità, scala e una progressione di quattro accordi, quindi comporre una melodia cliccando una griglia di quattro battute. Le righe verdi chiare indicano note dell'accordo corrente; la sequenza può essere ascoltata o esportata come MIDI con tracce separate per accordi e melodia.

I MIDI generati per ascolto o salvataggio vengono conservati in una cartella temporanea della sessione e rimossi alla chiusura dell'applicazione; anche il mixer audio viene rilasciato.

## Installazione

```bash
pip install -r requirements.txt
```

## Visual Studio Code

Il workspace consiglia le estensioni Microsoft **Python** e **Python Debugger**. Se hai installato **Python Preview**, puoi rimuoverla: è deprecata e non è necessaria per eseguire il progetto.

## Uso

```bash
python music_harmonizer.py
```

## Creazione di un eseguibile Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed music_harmonizer.py
```

L'eseguibile verrà creato nella cartella `dist/`.
