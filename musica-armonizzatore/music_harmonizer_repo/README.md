# Music Harmonizer

Repository standalone contenente solo `music_harmonizer.py`.

## Requisiti

- Python 3.13+
- pygame
- mido

Nella scheda **Note Musicali**, il pulsante **Analizza** mostra per ogni accordo i rivolti possibili (con sigle slash, ad esempio `C/E`) e una stima della funzione/tendenza armonica. Le funzioni sono indicate per le scale maggiori, minori naturali e minori armoniche; per le altre scale viene descritta la sonorita dell'accordo, la cui direzione dipende dal contesto.

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
