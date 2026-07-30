# Face3D Studio AI

# DEVELOPMENT GUIDELINES

**Versione:** 1.0

**Ultimo aggiornamento:** 30 Luglio 2026

---

# Obiettivo

Questo documento definisce le regole di sviluppo del progetto Face3D Studio AI.

Tutte le modifiche al codice devono rispettare queste linee guida.

---

# Workflow di sviluppo

Ogni sessione segue sempre questa sequenza:

1. Leggere `PROJECT_STATE.md`
2. Verificare lo stato del repository Git
3. Individuare la milestone corrente
4. Analizzare i file coinvolti
5. Implementare una sola modifica
6. Testare la modifica
7. Aggiornare la documentazione
8. Eseguire il commit
9. Eseguire il push su GitHub

---

# Regole architetturali

- La GUI non contiene logica di business.
- La GUI comunica esclusivamente con i Controller.
- I Controller coordinano i Manager.
- I Manager operano sui Model.
- I Model non conoscono la GUI.
- Ogni classe ha una singola responsabilità.

Architettura:

GUI

↓

Controller

↓

Manager

↓

Model

---

# Regole di sviluppo

- Analizzare sempre il codice prima di modificarlo.
- Non modificare file che non sono stati letti.
- Una modifica alla volta.
- Un test dopo ogni modifica.
- Non introdurre refactoring durante lo sviluppo di una funzionalità, salvo necessità.
- Preferire modifiche piccole e verificabili.

---

# Gestione delle milestone

Una milestone può essere considerata conclusa solo se:

- la funzionalità è completa;
- tutti i test sono superati;
- `CHANGELOG.md` è aggiornato;
- `PROJECT_MASTER_PLAN.md` è aggiornato;
- `PROJECT_STATE.md` è aggiornato;
- è stato eseguito il commit Git.

---

# Convenzioni

- Una classe per file.
- Type Hint obbligatori.
- Dataclass per i Model.
- Dependency Injection.
- Nessuna duplicazione di codice.
- Codice leggibile prima di essere "intelligente".

---

# Filosofia del progetto

L'obiettivo non è soltanto sviluppare Face3D Studio AI.

L'obiettivo è costruire un progetto ordinato, documentato, facilmente manutenibile e comprensibile anche a distanza di anni.