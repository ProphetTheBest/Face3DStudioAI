# Face3D Studio AI

## PROJECT MASTER PLAN

**Autore:** Marco Cantù

**Versione documento:** 1.0

**Ultimo aggiornamento:** 28 Luglio 2026

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

Il progetto utilizza il pattern MVC.

```
                app.py
                   │
                   ▼
       ApplicationController
                   │
                   ▼
              MainWindow
                   │
                   ▼
            CentralWidget
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 ProjectPanel  ViewerPanel  PropertiesPanel
      │
      ▼
ProjectController
      │
      ▼
 Project Model
```

---

# 4. Struttura del Progetto

```
source/

controllers/
models/
widgets/
services/
utils/
resources/
```

---

# 5. Tecnologie

Linguaggio

- Python

GUI

- PySide6

Computer Vision

- OpenCV

AI

- MediaPipe
- ONNX Runtime
- InsightFace
- PyTorch (se necessario)

3D

- Open3D
- Trimesh

File

- JSON

Versionamento

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
- Test ad ogni milestone

---

# 7. Stato delle Milestone

## M0.1

✔ Architettura iniziale

---

## M0.2

✔ BasePanel

✔ MainWindow

✔ CentralWidget

---

## M0.3

✔ MVC

✔ ApplicationController

✔ ProjectController

✔ Project Explorer

✔ GitHub

---

## M0.4

⏳ Project Manager

---

## M0.5

□ Import immagini

---

## M0.6

□ Import video

---

## M0.7

□ Face Detection

---

## M0.8

□ Landmark Detection

---

## M0.9

□ Camera Calibration

---

## M1.0

□ Ricostruzione Mesh

---

## M1.1

□ Mesh Cleaning

---

## M1.2

□ Texture Mapping

---

## M1.3

□ Export STL OBJ PLY

---

## M1.4

□ AI Enhancement

---

## M2.0

□ Professional Edition

---

# 8. Architecture Decision Records (ADR)

## ADR-001

Introduzione di ApplicationController.

Motivazione:

Centralizzare la gestione dei controller evitando dipendenze dirette tra View
e Model.

---

## ADR-002

ProjectTreeWidget non conosce ProjectController.

Motivazione:

Separazione tra interfaccia grafica e logica applicativa.

---

# 9. Milestone Corrente

M0.4

Project Manager

Attività:

- Nuovo progetto
- Apri progetto
- Salva progetto
- Salva con nome
- Chiudi progetto
- Recent Projects

---

# 10. Registro Versioni

## v0.3.1

- Introduzione ApplicationController
- Refactoring CentralWidget
- MVC completato
- Dependency Injection
- Project Explorer completato
- Repository GitHub configurato