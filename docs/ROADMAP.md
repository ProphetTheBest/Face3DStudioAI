# Face3D Studio AI

## Roadmap Ufficiale del Progetto

Autore:
Marco Cantù

Technical Lead AI:
ChatGPT

Versione documento:
1.0

Ultimo aggiornamento:
Sprint 12

---

# 1. Visione del Progetto

Face3D Studio AI nasce con l'obiettivo di realizzare una piattaforma professionale per
l'analisi tridimensionale del volto umano mediante Intelligenza Artificiale.

Il progetto utilizza MediaPipe Face Landmarker come motore di rilevamento e costruisce
una rappresentazione tridimensionale completamente manipolabile del volto.

L'obiettivo non è solamente visualizzare una mesh, ma creare una pipeline completa
che permetta di:

- acquisire immagini
- rilevare automaticamente uno o più volti
- costruire una mesh 3D runtime
- modificare la mesh
- applicare texture
- esportare modelli 3D
- effettuare misurazioni
- utilizzare algoritmi AI
- integrare Blender
- integrare stampa 3D

Il progetto viene sviluppato seguendo un'architettura modulare,
estendibile e facilmente manutenibile.

---

# 2. Filosofia del progetto

Ogni componente deve avere una sola responsabilità.

L'architettura deve essere semplice da comprendere.

Ogni Sprint deve produrre un risultato verificabile.

Ogni modifica deve essere accompagnata da un commit Git.

Ogni Sprint aggiorna la documentazione.

Mai introdurre nuove funzionalità lasciando regressioni aperte.

Prima si stabilizza il codice.

Poi si aggiungono nuove funzionalità.

---

# 3. Obiettivi finali

Il software dovrà consentire:

✔ caricamento immagini

✔ caricamento video

✔ acquisizione webcam

✔ rilevamento automatico dei volti

✔ gestione di più volti contemporaneamente

✔ mesh tridimensionale completa

✔ rendering OpenGL

✔ viewer professionale

✔ esportazione OBJ

✔ esportazione STL

✔ texture mapping

✔ UV Mapping

✔ materiali

✔ illuminazione

✔ animazioni

✔ BlendShapes

✔ Morph Targets

✔ editing della mesh

✔ misura distanze

✔ misura angoli

✔ confronto tra due volti

✔ AI per analisi morfologica

✔ AI per chirurgia estetica

✔ AI per odontoiatria

✔ AI per medicina

✔ AI per antropometria

✔ AI per riconoscimento automatico

✔ plugin futuri

---

# 4. Obiettivi NON previsti

Il progetto non nasce come software CAD.

Non nasce come software di modellazione artistica.

La modellazione sarà sempre derivata dai dati AI.

L'editing manuale sarà limitato.
---

# 5. Architettura del progetto

Face3D Studio AI è stato progettato seguendo un'architettura modulare.

Ogni componente deve avere una responsabilità ben definita.

L'obiettivo è rendere il software facilmente estendibile senza dover modificare
le parti già consolidate.

La pipeline principale è la seguente:

Immagine
↓
MediaPipe Face Landmarker
↓
FaceAnalysisService
↓
Face
├── Detection
├── Landmarks
├── Mesh
├── Pose Matrix
├── BlendShapes
└── Texture (futuro)
↓
Rendering

Da questo punto la pipeline viene divisa definitivamente in due rami indipendenti.

------------------------------------------------------------

Pipeline 2D

FaceLandmarks
↓
ImageScene
↓
Overlay sulla fotografia

------------------------------------------------------------

Pipeline 3D

FaceMesh
↓
MeshViewer
↓
Rendering OpenGL

Questa separazione è stata introdotta durante lo Sprint 11.

È una delle decisioni architetturali più importanti del progetto.

Da questo momento il rendering 2D e quello 3D sono completamente indipendenti.

---

# 6. Struttura generale del progetto

Attualmente il progetto è organizzato nelle seguenti aree principali.

app.py

Punto di ingresso dell'applicazione.

------------------------------------------------------------

source/

Contiene tutto il codice del progetto.

------------------------------------------------------------

source/ai

Motore di Intelligenza Artificiale.

Responsabilità:

- Face Detection
- Face Landmarker
- AI Providers
- FaceAnalysisService
- modelli dati AI

------------------------------------------------------------

source/gui

Finestre principali dell'applicazione.

Responsabilità:

- MainWindow
- Controller GUI

------------------------------------------------------------

source/widgets

Tutti i componenti grafici.

Tra i principali:

ImageViewer

ImageScene

MeshViewer

ViewerPanel

CentralWidget

------------------------------------------------------------

source/models

Contiene i modelli dati del progetto.

Tra i principali:

Face

FaceMesh

Vertex3D

Triangle

Edge

Asset

------------------------------------------------------------

source/resources

Contiene:

modelli MediaPipe

icone

texture

risorse future

------------------------------------------------------------

docs

Documentazione del progetto.

---

# 7. Componenti principali

## Face

Rappresenta un volto rilevato.

È il contenitore principale di tutte le informazioni.

Contiene:

Detection

Landmarks

Mesh

Pose Matrix

BlendShapes

Texture (futura)

Il Face rappresenta l'intero stato di un volto.

Tutti i moduli del progetto dovranno lavorare utilizzando questo oggetto.

---

## FaceMesh

Rappresenta esclusivamente la mesh tridimensionale.

Contiene:

Vertex3D

Triangle

Edge

La FaceMesh NON contiene informazioni di rendering.

La FaceMesh NON contiene informazioni AI.

Ha il solo compito di rappresentare la geometria.

---

## FaceLandmark

Rappresenta un landmark restituito da MediaPipe.

Coordinate:

x

y

z

visibility

presence

Questi dati sono utilizzati esclusivamente dalla pipeline 2D.

---

## FaceAnalysisService

È il cuore della pipeline AI.

Responsabilità:

ricevere i dati da MediaPipe

costruire gli oggetti Face

costruire la FaceMesh

associare Detection

associare Landmarks

associare Pose Matrix

associare BlendShapes

restituire il risultato finale

Nessun componente grafico deve eseguire elaborazioni AI.

---

## ImageScene

Responsabile del rendering 2D.

Visualizza:

immagine

rettangoli dei volti

landmarks

wireframe 2D

Non deve conoscere la mesh tridimensionale.

Utilizza direttamente i FaceLandmarks.

---

## MeshViewer

Responsabile esclusivamente del rendering tridimensionale.

Visualizza:

Point Cloud

Wireframe

Mesh triangolata

Non utilizza coordinate immagine.

Lavora esclusivamente nello spazio tridimensionale.

---

# 8. Decisioni architetturali

Durante lo Sprint 11 è stata presa una decisione fondamentale.

La mesh 3D NON deve essere utilizzata per disegnare l'overlay 2D.

Motivazione:

La mesh utilizza coordinate tridimensionali normalizzate.

L'overlay utilizza coordinate della fotografia.

Sono due sistemi di riferimento differenti.

La conversione continua tra i due sistemi introduce errori.

Per questo motivo:

Overlay 2D → FaceLandmarks

Rendering 3D → FaceMesh

Questa regola non dovrà più essere modificata.
---

# 9. Stato di avanzamento del progetto

## Sprint completati

### Sprint 1 → Sprint 10

Durante i primi Sprint sono state costruite le fondamenta del progetto:

- struttura delle cartelle
- architettura MVC
- modelli dati
- caricamento immagini
- gestione Asset
- Viewer immagini
- Face Detection
- integrazione iniziale MediaPipe

---

### Sprint 11

Sprint fondamentale del progetto.

Risultati ottenuti:

✔ Integrazione completa del nuovo MediaPipe Face Landmarker

✔ FaceAnalysisService aggiornato

✔ Costruzione della FaceMesh runtime

✔ Mesh triangolata

✔ Viewer OpenGL

✔ Overlay 2D corretto

✔ Separazione definitiva tra rendering 2D e rendering 3D

✔ Correzione del disallineamento della mesh sull'immagine

Lo Sprint 11 rappresenta la prima versione stabile della pipeline AI.

---

# 10. Stato dei componenti

## AI

Face Detection

Stato:

COMPLETATO

---

Face Landmarker

Stato:

COMPLETATO

---

FaceAnalysisService

Stato:

STABILE

---

FaceMeshBuilder

Stato:

STABILE

---

MediaPipe Provider

Stato:

STABILE

---

## Rendering 2D

ImageViewer

Stato:

STABILE

---

ImageScene

Stato:

STABILE

---

Overlay Landmark

Stato:

COMPLETATO

---

Wireframe 2D

Stato:

COMPLETATO

---

## Rendering 3D

MeshViewer

Stato:

FUNZIONANTE

Da migliorare:

- assi XYZ
- griglia
- illuminazione
- materiali
- controllo camera
- reset camera

---

# 11. Sprint pianificati

## Sprint 12

Viewer 3D Professional

Obiettivi:

- assi XYZ
- griglia
- reset camera
- gestione camera
- modalità Point Cloud
- modalità Wireframe
- modalità Mesh
- miglioramento illuminazione
- colori materiali

---

## Sprint 13

Esportazione OBJ

Obiettivi:

- esportazione mesh runtime
- apertura Blender
- verifica geometria

---

## Sprint 14

Texture Mapping

Obiettivi:

- UV Mapping
- texture fotografica
- materiali

---

## Sprint 15

Esportazione STL

Obiettivi:

- stampa 3D

---

## Sprint 16

Misure antropometriche

---

## Sprint 17

Confronto tra due volti

---

## Sprint 18

Editing Mesh

---

## Sprint 19

AI Morphing

---

## Sprint 20

Plugin

---

# 12. Bug aperti

Ogni bug deve essere registrato qui.

Formato:

ID

Descrizione

Priorità

Stato

Data

Responsabile

Attualmente:

Nessun bug bloccante.

---

# 13. Regole di sviluppo

Durante lo sviluppo dovranno essere rispettate le seguenti regole.

Mai modificare un componente stabile senza motivo.

Ogni Sprint affronta un solo obiettivo principale.

Ogni nuova funzionalità deve essere testata prima del commit.

Ogni commit deve rappresentare una milestone funzionante.

Mai introdurre regressioni.

Ogni nuova architettura deve essere documentata.

Mai duplicare codice.

Preferire sempre componenti riutilizzabili.

---

# 14. Procedura di apertura Sprint

Ogni Sprint inizia sempre nello stesso modo.

1.

Aprire una nuova chat ChatGPT.

2.

Allegare il progetto completo aggiornato.

3.

Leggere ROADMAP.md.

4.

Leggere CHANGELOG.md.

5.

Definire l'obiettivo dello Sprint.

6.

Implementazione.

---

# 15. Procedura di chiusura Sprint

Ogni Sprint termina sempre nello stesso modo.

1.

Verifica funzionale.

2.

Correzione bug.

3.

Pulizia codice.

4.

Aggiornamento ROADMAP.md.

5.

Aggiornamento CHANGELOG.md.

6.

Commit Git.

7.

Push GitHub.

Solo dopo questi passaggi lo Sprint può essere considerato concluso.

---

# 16. Convenzioni Git

Ogni commit deve descrivere chiaramente il risultato ottenuto.

Formato consigliato:

Sprint XX: descrizione

Esempi:

Sprint 11: separate 2D overlay from 3D rendering

Sprint 12: professional MeshViewer

Sprint 13: runtime OBJ exporter

Mai utilizzare commit come:

update

fix

test

prova

pippo

---

# 17. Visione a lungo termine

Face3D Studio AI dovrà evolversi fino a diventare una piattaforma professionale per:

- analisi facciale

- medicina

- odontoiatria

- chirurgia estetica

- antropometria

- stampa 3D

- Blender

- realtà aumentata

- ricerca scientifica

L'obiettivo principale non è solamente generare una mesh, ma costruire un framework completo per l'analisi tridimensionale del volto umano.

---

# Fine documento