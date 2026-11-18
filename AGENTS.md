---
permissions:
  edit: ask
  bash: ask
---

# STATO DEL PROGETTO E MEMORIA MULTI-AGENTE

## 📌 Regole di Ingaggio (Global Rules)
- Ogni agente deve leggere questo file prima di iniziare qualsiasi operazione.
- Non sovrascrivere il codice scritto da un altro agente senza il consenso del @Critic.
- Ogni modifica strutturale deve essere registrata nella sezione "Cronologia delle Modifiche".

## 🎯 Obiettivo Corrente
- Sviluppare un'applicazione che riceve in input una scala musicale, ne calcola l'armonizzazione (triadi/quadriadi) e l'analisi armonica, ed esporta il risultato in un file binario .mid (MIDI).

## 🗺️ Architettura e Stack Tecnologico
- **Linguaggio/Framework:** Python 3.10+
- **Librerie Chiave:** `mido` (per la generazione e scrittura fisica del file MIDI)
- **Standard Musicale:** Mappatura note con MIDI Note Numbers standard (es. Do Centrale / C4 = 60).

## 📋 Task Board (Stato dei Lavori)
- [ ] **Task 1: Core Musicale** - Creare la logica per ricevere la scala e calcolare l'armonizzazione sui gradi. - *Assegnato a: @Planner & @Implementer* - Stato: In Coda
- [ ] **Task 2: Esportazione MIDI** - Integrare la libreria `mido` per convertire gli accordi in messaggi MIDI Note On/Off e salvare il file .mid. - *Assegnato a: @Implementer* - Stato: In Coda
- [ ] **Task 3: Code Review e Validazione** - Analisi teorico-musicale degli intervalli e verifica della chiusura dei file binari. - *Assegnato a: @Critic & @Security* - Stato: In Coda

## 🕒 Cronologia delle Modifiche (Long-term Memory)
- *Struttura inizializzata. Pronto per la catena di montaggio degli agenti.*
- 2026-11-02: resa la mappa degli intervalli la fonte unica delle scale predefinite, aggiunta la validazione della scala/armonizzazione e corretto il feedback di riproduzione MIDI.
- 2026-11-02: aggiunta una scheda sequencer per progressioni di quattro battute, composizione melodica a sedicesimi e esportazione MIDI multitraccia.
- 2026-11-04: ripristinati gli agenti personalizzati per GitHub Copilot in `.github/agents`, corretti i tool non validi, aggiunto il revisore UX al formato `.agent.md` e reso esplicito il passaggio Implementer-Critic.
- 2026-11-04: aggiunti i suggerimenti VS Code per le estensioni Python mantenute e le esclusioni Git per cache e ambienti virtuali.
- 2026-11-04: rinnovato il report Analizza con triadi diatoniche, numeri romani e funzioni modali, esclusione dell'ottava duplicata e impaginazione a sezioni.
- 2026-11-07: aggiunti Gate e Micro-shift del sequencer basati su cicli interi per quarto, con fondamentale equitemperata A4=440 Hz, armonizzazioni configurabili da tre a cinque voci e metadati temporali per traccia.
- 2026-11-07: aggiunta la modifica della scala personale direttamente nel sequencer e la gestione di progressioni fino a 32 battute, navigabili in pagine da quattro battute.
- 2026-11-07: limitata la griglia del sequencer a due ottave selezionabili, aggiunta la distinzione cromatica tra scala e accordi e la selezione/copia/incolla di gruppi di note.
- 2026-11-07: aggiunti eventi MIDI di metatesto per nome e grado dell'accordo, sincronizzati al Note-On e verificati con la durata Gate in tick.
- 2026-11-07: aggiunti loop continuo della battuta selezionata e durate melodiche da nota intera a sedicesimo, con Gate e micro-shift per frequenza e durata.
- 2026-11-07: aggiunta la licenza GNU GPL-3.0-or-later con titolare Mikiwolf e copyright 2026.
- 2026-11-07: uniformata la denominazione degli accordi alla notazione internazionale standard, anche per voicing estesi e sospesi.
- 2026-11-08: le note melodiche del sequencer ora mantengono durata individuale da intera a biscroma, visibile nella griglia e rispettata nell'esportazione Gate/micro-shift.
- 2026-11-08: aggiunto selettore di metro musicale e adeguati griglia, progressione, loop, esportazione MIDI e Gate accordali alla durata effettiva della battuta.
- 2026-11-15: aggiunti al sequencer preset di giri armonici per pop, rock, metal, darkwave, reggae, reggaeton, blues e jazz, con applicazione singola e preservazione delle battute successive.
- 2026-11-15: aggiunti controlli per battuta della durata accordale (intero–ottavo) e della pausa prima dell'accordo (nessuna–metà), con validazione metrica e integrazione nella generazione MIDI.
- 2026-11-15: aggiunto il comando per applicare un giro armonico da una battuta selezionata, con controllo dello spazio disponibile e preservazione delle altre battute.
- 2026-11-08: aggiunta una configurazione Run and Debug di VS Code per avviare Music Harmonizer dal workspace e rimossi due avvisi Pylance per variabili inutilizzate.
- 2026-11-16: aggiunta una timeline interattiva degli accordi per battuta con snap a 1/16, spostamento e trim dei bordi, sincronizzata con i controlli e l'esportazione MIDI.
- 2026-11-16: compattata la timeline degli accordi e riposizionati i comandi di registrazione/copia/incolla/loop sopra il piano roll per mantenerli visibili.
- 2026-11-16: integrata la timeline accordale nella griglia del piano roll per recuperare spazio verticale; mantenuta la regolazione da menu e via mouse fino a 1/16.
- 2026-11-18: aggiunti fino a quattro accordi sequenziali per battuta, con durata e pausa indipendenti, timeline interattiva e MIDI/loop multaccordo.
