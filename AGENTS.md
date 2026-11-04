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
