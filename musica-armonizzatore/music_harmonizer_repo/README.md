# Music Harmonizer

Repository standalone contenente l'applicazione `music_harmonizer.py` e il modulo matematico `pitch_timing.py`.

## Requisiti

- Python 3.13+
- pygame
- mido

Nella scheda **Note Musicali**, il pulsante **Analizza** mostra le triadi costruite per terze sui gradi della scala. Per le scale di sette note indica qualità, numeri romani e funzione/tendenza armonica, comprese le scale modali; le scale con un diverso numero di note sono descritte senza attribuire loro funzioni tonali standard. La nota `8`, se presente, indica l'ottava e non viene contata come un grado aggiuntivo. Sotto l'analisi sono riportati anche gli accordi e i rivolti del voicing selezionato.

Le formule personalizzate devono iniziare da `1` e inserire i gradi in ordine crescente; `8` indica esplicitamente l'ottava superiore ed è facoltativo.

La scheda **Sequencer** consente di scegliere tonalità, scala, BPM, metro (`4/4`, `3/4`, `5/4`, `8/16` e altri comuni), armonizzazione per terze/quarte/quinte, voicing da tre a cinque note, ottava di lavoro e durata delle note melodiche: intera (`1/1`), minima (`1/2`), semiminima (`1/4`), croma (`1/8`), semicroma (`1/16`) o biscroma (`1/32`). Il menu **Giro armonico** offre preset pop, rock, heavy metal, darkwave, reggae, reggaeton, blues a 12 battute, jazz, turnaround e doo-wop. **Applica dall'inizio** inserisce un solo giro dalla prima battuta; con **Battuta** e **Applica qui** puoi scegliere il punto di inserimento. In entrambi i casi vengono modificate solo le battute occupate dal giro e le altre restano invariate; il preset non viene applicato se non c'è spazio per tutto il giro o se la scala non contiene i gradi necessari. Per esempio, per ottenere il ♭VII del giro rock mixolidio scegli una scala misolidia. I preset forniscono sequenze di accordi, non le caratteristiche ritmiche o di esecuzione dei generi (come il levare reggae o il dembow reggaeton). La durata selezionata determina sia la lunghezza visibile della nota nella griglia sia il Gate MIDI; il Note-On viene micro-shiftato per lasciare il Gate corrispondente a cicli interi della frequenza. Le frequenze sono temperate equabilmente con riferimento A4=440 Hz; a 100 BPM un quarto dura 600 ms. Gli accordi sono denominati con sigle internazionali standard (per esempio `Am`, `Dm9`, `Cmaj9`, `G7`); i voicing estesi e sospesi usano suffissi e alterazioni convenzionali. Il campo **Loop battuta** e il pulsante **Loop** ripetono continuamente la battuta selezionata finché non si preme **Ferma**; il loop è supportato dal mixer audio interno. La griglia mostra due ottave per volta, selezionabili da C2 a C7. Le note della scala sono blu scuro e quelle dell'accordo verde chiaro. Trascina il mouse sulla griglia per selezionare un gruppo di note; usa i pulsanti **Copia**/**Incolla** o `Ctrl+C`/`Ctrl+V` (dopo aver armato Incolla, clicca la cella iniziale della destinazione). La scala personale si può scrivere nel formato dei gradi (per esempio `1 2 3b 4 5 6b 7b 8`) e applicare dal sequencer; se non si specifica l'ottava, viene aggiunta automaticamente. La progressione e la melodia supportano fino a 32 battute, visualizzate in pagine da quattro battute con navigazione. Per ciascun accordo calcola la frequenza della fondamentale in temperamento equabile (A4=440 Hz), il Gate corrispondente a cicli interi per la durata della battuta e il Micro-shift che mantiene il Note-Off sul suo confine. Il MIDI Type 1 include nella traccia degli accordi un evento di testo sincronizzato a ogni attacco, con grado e nome dell'accordo; i Note-Off usano la durata Gate convertita in tick. I metadati temporali sono disponibili in `sequencer_channel_metadata`, per traccia. La sequenza può essere ascoltata o esportata come MIDI con tracce separate per accordi e melodia.

Per ogni battuta della progressione puoi impostare la **durata dell'accordo** (intero, metà, quarto o ottavo) e una **pausa prima dell'accordo** (nessuna, ottavo, quarto o metà). Le durate sono valori musicali standard; se pausa e accordo insieme superano la battuta nel metro selezionato, il sequencer segnala l'incompatibilità e non genera il MIDI. Il micro-shift di fase può posticipare leggermente l'attacco per mantenere il Gate dell'accordo sulla durata scelta.

Il preset armonico può essere applicato anche da una battuta specifica usando il campo **Battuta** e il pulsante **Applica qui**. Il giro viene inserito una sola volta e non viene troncato: se non ci sono abbastanza battute libere fino alla fine della sequenza, l'operazione viene rifiutata senza modificare la progressione.

I MIDI generati per ascolto o salvataggio vengono conservati in una cartella temporanea della sessione e rimossi alla chiusura dell'applicazione; anche il mixer audio viene rilasciato.

## Sincronizzazione pitch/timing

Il modulo `pitch_timing.py` espone `calculate_pitch_timing`, una funzione indipendente dalla GUI. Dato un offset di semitoni da La4 oppure un numero MIDI assoluto, collega frequenza e BPM con il temperamento equabile (default La4=440 Hz e tempo master=100.3 BPM), calcola le suddivisioni richieste e l'offset/deriva rispetto alla griglia master. Per esempio:

```python
from pitch_timing import calculate_pitch_timing

result = calculate_pitch_timing(-12, beats_without_realign=8)
print(result["frequenza_hz"], result["bpm"], result["deriva_totale_ms"])
```

Il risultato include le suddivisioni `1/4`, `1/8.`, `1/8`, `1/8T`, `1/16` e `1/32`, espresse in millisecondi. L'offset singolo è la durata del quarto della nota meno quella del quarto master; la deriva è l'offset moltiplicato per il numero di battiti senza riallineamento. La funzione rifiuta input non finiti, note MIDI fuori range e valori frazionari che non corrispondono a una nota MIDI intera. `validate_pitch_timing_reference_points()` verifica i riferimenti La3, La4 e La5.

## Cronologia delle Modifiche

- 2026-11-15: aggiunto il modulo indipendente per mappare semitoni/frequenze su BPM, suddivisioni ritmiche e deriva rispetto alla griglia master.
- 2026-11-15: aggiunti al sequencer preset di giri armonici per pop, rock, heavy metal, darkwave, reggae, reggaeton, blues, jazz, turnaround e doo-wop, applicabili una sola volta senza alterare le battute successive.
- 2026-11-15: aggiunti controlli per battuta della durata accordale (intero–ottavo) e della pausa precedente (nessuna–metà), con validazione sul metro e applicazione a riproduzione, loop ed esportazione MIDI.
- 2026-11-15: aggiunta l'applicazione dei giri armonici a partire da una battuta selezionata, preservando gli accordi fuori dal giro e verificando che il preset entri nella sequenza.

## Installazione

```bash
pip install -r requirements.txt
```

## Visual Studio Code

Il workspace consiglia le estensioni Microsoft **Python** e **Python Debugger**. Se hai installato **Python Preview**, puoi rimuoverla: è deprecata e non è necessaria per eseguire il progetto. Per avviare l'app dal pulsante di VS Code, apri **Run and Debug** e seleziona la configurazione **Music Harmonizer**. Se non hai ancora selezionato un interprete Python, scegli quello dell'ambiente virtuale del workspace o installa le dipendenze indicate sopra.

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
