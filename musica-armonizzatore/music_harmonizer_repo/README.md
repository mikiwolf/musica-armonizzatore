# Music Harmonizer

Repository standalone contenente solo `music_harmonizer.py`.

## Requisiti

- Python 3.13+
- pygame
- mido

Nella scheda **Note Musicali**, il pulsante **Analizza** mostra le triadi costruite per terze sui gradi della scala. Per le scale di sette note indica qualità, numeri romani e funzione/tendenza armonica, comprese le scale modali; le scale con un diverso numero di note sono descritte senza attribuire loro funzioni tonali standard. La nota `8`, se presente, indica l'ottava e non viene contata come un grado aggiuntivo. Sotto l'analisi sono riportati anche gli accordi e i rivolti del voicing selezionato.

Le formule personalizzate devono iniziare da `1` e inserire i gradi in ordine crescente; `8` indica esplicitamente l'ottava superiore ed è facoltativo.

La scheda **Sequencer** consente di scegliere tonalità, scala, BPM, metro (`4/4`, `3/4`, `5/4`, `8/16` e altri comuni), armonizzazione per terze/quarte/quinte, voicing da tre a cinque note, ottava di lavoro e durata delle note melodiche: intera (`1/1`), minima (`1/2`), semiminima (`1/4`), croma (`1/8`), semicroma (`1/16`) o biscroma (`1/32`). La durata selezionata determina sia la lunghezza visibile della nota nella griglia sia il Gate MIDI; il Note-On viene micro-shiftato per lasciare il Gate corrispondente a cicli interi della frequenza. Le frequenze sono temperate equabilmente con riferimento A4=440 Hz; a 100 BPM un quarto dura 600 ms. Gli accordi sono denominati con sigle internazionali standard (per esempio `Am`, `Dm9`, `Cmaj9`, `G7`); i voicing estesi e sospesi usano suffissi e alterazioni convenzionali. Il campo **Loop battuta** e il pulsante **Loop** ripetono continuamente la battuta selezionata finché non si preme **Ferma**; il loop è supportato dal mixer audio interno. La griglia mostra due ottave per volta, selezionabili da C2 a C7. Le note della scala sono blu scuro e quelle dell'accordo verde chiaro. Trascina il mouse sulla griglia per selezionare un gruppo di note; usa i pulsanti **Copia**/**Incolla** o `Ctrl+C`/`Ctrl+V` (dopo aver armato Incolla, clicca la cella iniziale della destinazione). La scala personale si può scrivere nel formato dei gradi (per esempio `1 2 3b 4 5 6b 7b 8`) e applicare dal sequencer; se non si specifica l'ottava, viene aggiunta automaticamente. La progressione e la melodia supportano fino a 32 battute, visualizzate in pagine da quattro battute con navigazione. Per ciascun accordo calcola la frequenza della fondamentale in temperamento equabile (A4=440 Hz), il Gate corrispondente a cicli interi per la durata della battuta e il Micro-shift che mantiene il Note-Off sul suo confine. Il MIDI Type 1 include nella traccia degli accordi un evento di testo sincronizzato a ogni attacco, con grado e nome dell'accordo; i Note-Off usano la durata Gate convertita in tick. I metadati temporali sono disponibili in `sequencer_channel_metadata`, per traccia. La sequenza può essere ascoltata o esportata come MIDI con tracce separate per accordi e melodia.

I MIDI generati per ascolto o salvataggio vengono conservati in una cartella temporanea della sessione e rimossi alla chiusura dell'applicazione; anche il mixer audio viene rilasciato.

## Installazione

```bash
pip install -r requirements.txt
```

## Visual Studio Code

Il workspace consiglia le estensioni Microsoft **Python** e **Python Debugger**. Se hai installato **Python Preview**, puoi rimuoverla: è deprecata e non è necessaria per eseguire il progetto.

## Licenza

Copyright (C) 2026 Mikiwolf. Questo progetto è distribuito secondo i termini della **GNU General Public License, versione 3 o successiva** (GPL-3.0-or-later). Consulta [LICENSE](./LICENSE) per il testo completo.

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
