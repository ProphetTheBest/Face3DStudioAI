# Face3D Studio AI

# PROJECT MASTER PLAN

**Autore:** Marco Cantù

**Versione documento:** 1.1

**Ultimo aggiornamento:** 29 Luglio 2026

---

# 1. Visione del Progetto

Face3D Studio AI è un'applicazione desktop professionale sviluppata in Python
per la ricostruzione tridimensionale del volto umano a partire da fotografie
e video.

L'obiettivo è ottenere mesh 3D di alta qualità utilizzando esclusivamente
software open source e gratuito.

Il progetto è orientato alla modularità, all'estendibilità e alla manutenibilità
del codice.

---

# 2. Obiettivi Principali

- Gestione di progetti Face3D
- Importazione fotografie
- Importazione video
- Estrazione frame
- Face Detection
- Landmark Detection
- Camera Calibration
- Ricostruzione 3D
- Pulizia Mesh
- Texture Mapping
- Esportazione STL
- Esportazione OBJ
- Esportazione PLY
- AI Enhancement

---

# 3. Architettura

Il progetto adotta un'architettura MVC estesa.

```
GUI
│
▼
ApplicationController
│
├── ProjectController
├── PhotoController
├── VideoController
└── ...

│
▼

Manager
│
├── ProjectManager
├── PhotoManager
├── VideoManager
└── ...

│
▼

Model
```

### Regole architetturali

- La GUI non contiene logica di business.
- La GUI comunica esclusivamente con i Controller.
- I Controller coordinano i Manager.
- I Manager operano sui Model.
- Nessun Widget conosce direttamente Manager o Model.

---

# 4. Struttura del Progetto

```
source/

controllers/
models/
managers/
widgets/
services/
utils/
resources/
```

---

# 5. Tecnologie

## Linguaggio

- Python

## GUI

- PySide6

## Computer Vision

- OpenCV

## AI

- MediaPipe
- InsightFace
- ONNX Runtime
- PyTorch (se necessario)

## 3D

- Open3D
- Trimesh

## File

- JSON

## Versionamento

- Git
- GitHub

---

# 6. Convenzioni di sviluppo

- MVC rigoroso
- Nessuna logica nella GUI
- Una classe per file
- Type Hint obbligatori
- Dataclass per i Model
- Dependency Injection
- Codice modulare
- Nessuna duplicazione
- Un solo step di sviluppo alla volta
- Test al termine di ogni modifica
- Chiusura formale di ogni milestone
- Aggiornamento della documentazione prima del commit

---

# 7. Stato delle Milestone

## M0.1

✔ Architettura iniziale

---

## M0.2

✔ Interfaccia grafica di base

---

## M0.3

✔ MVC
✔ ApplicationController
✔ Project Explorer

---

## M0.4

✔ Gestione progetti

- Nuovo progetto
- Apertura progetto
- Salvataggio progetto
- Struttura cartelle

---

## M0.5

✔ Gestione fotografie

- Importazione multipla
- Copia nella cartella del progetto
- Persistenza completa
- Apertura corretta del progetto

---

## M0.6 (Corrente)

□ Project Explorer avanzato

Obiettivi:

- Espandere il nodo Photos
- Elencare le fotografie
- Selezionare una fotografia
- Mostrare l'immagine nel Viewer
- Aggiornare il Properties Panel

---

## M0.7

□ Gestione Video

---

## M0.8

□ Face Detection

---

## M0.9

□ Landmark Detection

---

## M1.0

□ Camera Calibration

---

## M1.1

□ Ricostruzione Mesh

---

## M1.2

□ Mesh Cleaning

---

## M1.3

□ Texture Mapping

---

## M1.4

□ Esportazione modelli 3D

---

## M2.0

□ Professional Edition

---

# 8. Architecture Decision Records (ADR)

## ADR-001

Introduzione di ApplicationController.

**Motivazione**

Centralizzare la gestione dell'applicazione.

---

## ADR-002

I Widget non conoscono Controller, Manager o Model diversi da quelli strettamente necessari.

**Motivazione**

Separazione tra GUI e logica applicativa.

---

## ADR-003

Pattern architetturale

GUI → Controller → Manager → Model

**Motivazione**

Massima separazione delle responsabilità.

---

# 9. Milestone Corrente

## M0.6

### Project Explorer avanzato

Obiettivo:

Trasformare il Project Explorer da semplice riepilogo del progetto
a browser completo delle risorse.

Attività previste:

- Espansione nodo Photos
- Visualizzazione miniature/elenco
- Selezione fotografia
- Viewer sincronizzato
- Properties Panel sincronizzato

---

# 10. Registro Versioni

## v0.5.0

- M0.5 completata
- Gestione fotografie completata
- Persistenza del progetto completata
- Refactoring Controller/Manager completato

---

## v0.3.1

- Introduzione ApplicationController
- Refactoring CentralWidget
- MVC completato
- Dependency Injection
- Repository GitHub