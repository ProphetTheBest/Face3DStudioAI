# Face3D Studio AI

## Roadmap Ufficiale del Progetto

Autore:
Marco Cantù

Technical Lead AI:
ChatGPT

Versione documento:
1.1

Ultimo aggiornamento:
Sprint 17.1

---

# 1. Visione del Progetto

Face3D Studio AI nasce con l'obiettivo di realizzare una piattaforma professionale
per la ricostruzione tridimensionale del volto umano mediante Intelligenza Artificiale.

Il progetto utilizza MediaPipe Face Landmarker come motore di rilevamento,
ma è stato progettato per poter integrare in futuro provider differenti
senza modificare l'architettura dell'applicazione.

L'obiettivo non è solamente visualizzare una mesh 3D, ma costruire una pipeline
completa che permetta di:

- acquisire immagini;
- acquisire video;
- utilizzare webcam;
- rilevare automaticamente uno o più volti;
- costruire una mesh tridimensionale runtime;
- generare coordinate UV;
- applicare texture fotografiche;
- esportare modelli tridimensionali;
- effettuare misurazioni antropometriche;
- integrare algoritmi di Intelligenza Artificiale;
- integrare Blender;
- integrare la stampa 3D;
- costituire la base per future applicazioni mediche e scientifiche.

L'intero progetto viene sviluppato seguendo una architettura modulare,
estendibile e facilmente manutenibile.

Ogni componente deve avere una sola responsabilità.

---

# 2. Missione del Progetto

Face3D Studio AI ha come obiettivo principale la ricostruzione tridimensionale
di persone, volti e oggetti partendo da dati bidimensionali.

Le sorgenti di acquisizione previste sono:

• una singola fotografia;

• più fotografie dello stesso soggetto;

• fotografie provenienti da diverse angolazioni;

• video;

• video a 360°;

• webcam;

• flussi video in tempo reale.

Il sistema dovrà ricostruire automaticamente un modello tridimensionale
accurato, modificabile ed esportabile nei principali formati 3D.

L'obiettivo finale è ottenere modelli utilizzabili per:

- stampa 3D;
- Blender;
- CAD;
- realtà aumentata;
- realtà virtuale;
- videogiochi;
- analisi antropometrica;
- medicina;
- odontoiatria;
- chirurgia estetica;
- ricerca scientifica.

Il progetto dovrà evolversi fino a diventare una piattaforma completa
per l'analisi tridimensionale del volto umano.

---

# 3. Filosofia del Progetto

Ogni componente deve avere una sola responsabilità.

L'architettura deve essere semplice da comprendere.

Ogni Sprint deve produrre un risultato verificabile.

Ogni modifica deve essere accompagnata da un commit Git.

Ogni Sprint aggiorna la documentazione.

Mai introdurre nuove funzionalità lasciando regressioni aperte.

Prima si stabilizza il codice.

Poi si aggiungono nuove funzionalità.

Le decisioni architetturali consolidate non devono essere modificate
senza una reale necessità tecnica.

Ogni nuova funzionalità deve integrarsi nell'architettura esistente,
non sostituirla.

---

# 4. Obiettivi Finali

Il software dovrà consentire:

✔ caricamento immagini

✔ caricamento video

✔ acquisizione webcam

✔ rilevamento automatico dei volti

✔ gestione contemporanea di più volti

✔ mesh tridimensionale completa

✔ rendering OpenGL

✔ viewer professionale

✔ esportazione OBJ

✔ esportazione STL

✔ esportazione PLY

✔ esportazione GLTF

✔ esportazione FBX

✔ UV Mapping

✔ texture mapping

✔ materiali

✔ illuminazione

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

✔ ricostruzione tridimensionale da fotografia singola

✔ ricostruzione tridimensionale da fotografie multiple

✔ ricostruzione tridimensionale da video

✔ fusione automatica di più punti di vista

✔ generazione di mesh watertight per stampa 3D

✔ ottimizzazione automatica della mesh

✔ esportazione per stampanti 3D

✔ pipeline completa Blender

✔ materiali PBR (futuro)

✔ rigging

✔ animazione

---

# 5. Obiettivi NON previsti

Il progetto non nasce come software CAD.

Non nasce come software di modellazione artistica.

La modellazione sarà sempre derivata dai dati AI.

L'editing manuale sarà limitato alle funzionalità realmente utili
all'analisi tridimensionale.

Face3D Studio AI non vuole sostituire Blender.

Face3D Studio AI vuole produrre automaticamente modelli tridimensionali
di alta qualità destinati ad essere utilizzati anche all'interno di Blender,
CAD e software professionali.
---

# 6. Architettura del Progetto

Face3D Studio AI è stato progettato seguendo un'architettura modulare,
fortemente disaccoppiata e facilmente estendibile.

Ogni componente deve avere una responsabilità ben definita.

L'obiettivo è consentire l'aggiunta di nuove funzionalità senza modificare
le parti già consolidate.

L'architettura segue rigorosamente il seguente schema:

GUI

↓

ApplicationController

↓

Controllers

↓

Services

↓

Managers / Exporters

↓

Models

Nessun componente può saltare uno dei livelli superiori.

Questa regola costituisce una delle fondamenta del progetto.

---

## Pipeline principale

La pipeline completa attualmente implementata è la seguente.

Immagine

↓

MediaPipe Face Landmarker

↓

FaceAnalysisService

↓

Face

├── Detection

├── Landmarks

├── FaceMesh

├── Pose Matrix

├── BlendShapes

└── UV Coordinates

↓

ProjectController

↓

Current Face

↓

FaceExportService

├── ObjExporter

├── TextureExporter

└── MaterialExporter

↓

OBJ

↓

MTL

↓

Texture Fotografica

↓

Blender

Questa pipeline rappresenta la prima versione completa
dell'esportazione tridimensionale del progetto.

---

## Pipeline 2D

FaceLandmarks

↓

ImageScene

↓

Overlay sulla fotografia

↓

Bounding Box

↓

Wireframe 2D

La pipeline 2D lavora esclusivamente sulle coordinate immagine.

Non utilizza mai la FaceMesh.

---

## Pipeline 3D

FaceMesh

↓

MeshViewer

↓

Rendering OpenGL

↓

UV Mapping

↓

OBJ Export

↓

Texture Mapping

↓

Blender

La pipeline 3D utilizza esclusivamente dati tridimensionali.

Non conosce le coordinate della fotografia.

---

## Pipeline Export

Current Face

↓

FaceExportService

↓

ObjExporter

↓

TextureExporter

↓

MaterialExporter

↓

OBJ + MTL + Texture

Il FaceExportService coordina tutti gli exporter.

Ogni exporter ha una sola responsabilità.

---

# 7. Struttura generale del Progetto

Attualmente il progetto è organizzato nelle seguenti aree.

app.py

Punto di ingresso dell'applicazione.

------------------------------------------------------------

source/

Contiene tutto il codice del progetto.

------------------------------------------------------------

source/ai

Responsabilità:

- Face Detection
- Face Landmarker
- AI Providers
- FaceAnalysisService

------------------------------------------------------------

source/controllers

Responsabilità:

- ProjectController
- ApplicationController
- Controller applicativi

------------------------------------------------------------

source/services

Responsabilità:

- servizi applicativi
- diagnostica
- esportazione

Attualmente comprende:

services/

diagnostics/

exporting/

FaceExportService

------------------------------------------------------------

source/exporters

Responsabilità:

esportazione dei formati supportati.

Attualmente comprende:

ObjExporter

TextureExporter

MaterialExporter

In futuro:

StlExporter

PlyExporter

GltfExporter

FbxExporter

------------------------------------------------------------

source/builders

Responsabilità:

costruzione degli oggetti runtime.

Tra i principali:

FaceMeshBuilder

------------------------------------------------------------

source/mapping

Responsabilità:

generazione delle coordinate UV.

Attualmente:

UVMapper

------------------------------------------------------------

source/models

Contiene tutti i modelli dati.

Tra i principali:

Asset

ImageAsset

Face

FaceMesh

Vertex3D

Triangle

Edge

------------------------------------------------------------

source/gui

Finestre principali.

------------------------------------------------------------

source/widgets

Componenti grafici.

Tra i principali:

ImageViewer

ImageScene

MeshViewer

ViewerPanel

CentralWidget

------------------------------------------------------------

docs

Documentazione del progetto.

ROADMAP.md

CHANGELOG.md

Guide tecniche

---

# 8. Componenti principali

## Face

Rappresenta un volto rilevato.

Contiene:

- Detection
- Landmarks
- FaceMesh
- Pose Matrix
- BlendShapes

Il Face rappresenta l'intero stato di un volto.

Tutti i moduli del progetto dovranno utilizzare questo oggetto.

---

## FaceMesh

Rappresenta esclusivamente la geometria tridimensionale.

Contiene:

- Vertex3D
- Triangle
- Edge

Non contiene dati AI.

Non contiene dati grafici.

Non contiene dati della fotografia.

Ha la sola responsabilità di rappresentare la geometria.

---

## UVMapper

Genera automaticamente le coordinate UV della mesh.

Utilizza i landmark restituiti da MediaPipe.

Le coordinate UV vengono esportate
direttamente all'interno del file OBJ.

---

## FaceExportService

Coordina l'intera esportazione.

Non scrive alcun file.

Coordina esclusivamente:

- ObjExporter
- TextureExporter
- MaterialExporter

Rappresenta il punto unico di accesso
per tutte le future esportazioni.

---

## ObjExporter

Responsabile esclusivamente
della generazione del file OBJ.

Non conosce la GUI.

Non conosce MediaPipe.

Non conosce la fotografia.

---

## TextureExporter

Responsabile della generazione
della texture fotografica.

Versione corrente:

copia della fotografia originale.

Versioni future:

- correzione illuminazione

- rimozione riflessi

- miglioramento AI

- texture ad alta qualità

---

## MaterialExporter

Responsabile esclusivamente
della generazione del file MTL.

Non conosce la mesh.

Non conosce la GUI.

---

# 9. Decisioni Architetturali

Durante lo sviluppo sono state consolidate
le seguenti regole.

• Overlay 2D e Rendering 3D sono completamente separati.

• La FaceMesh non deve mai essere utilizzata
per il rendering 2D.

• Il Current Face rappresenta il punto unico
di accesso al volto selezionato.

• Tutte le esportazioni passano esclusivamente
attraverso il FaceExportService.

• Ogni Exporter scrive un solo formato.

• Nessun componente grafico
può accedere direttamente agli exporter.

• Le coordinate UV vengono generate
una sola volta durante l'analisi.

• L'architettura è considerata congelata
a partire dalla Milestone 0.7.0.

Ogni futura evoluzione dovrà rispettare
questa organizzazione.
---

# 10. Stato di avanzamento del Progetto

## Sprint completati

---

### Sprint 1 → Sprint 10

Durante i primi Sprint sono state costruite le fondamenta del progetto.

Risultati ottenuti:

✔ Definizione dell'architettura generale

✔ Struttura delle cartelle

✔ Modelli dati

✔ Caricamento immagini

✔ Gestione degli Asset

✔ Viewer immagini

✔ Face Detection

✔ Prima integrazione di MediaPipe

✔ Base dell'applicazione

---

### Sprint 11

Sprint fondamentale del progetto.

Risultati ottenuti:

✔ Integrazione completa del nuovo MediaPipe Face Landmarker

✔ Introduzione del FaceAnalysisService

✔ Costruzione runtime della FaceMesh

✔ Mesh triangolata

✔ Viewer OpenGL

✔ Overlay 2D corretto

✔ Separazione definitiva tra rendering 2D e rendering 3D

✔ Correzione del disallineamento della mesh

Questo Sprint rappresenta la prima versione stabile
della pipeline AI.

---

### Sprint 12

Viewer 3D professionale.

Risultati ottenuti:

✔ Miglioramento MeshViewer

✔ Introduzione dei controlli di navigazione

✔ Ottimizzazione del rendering

✔ Miglioramenti strutturali dell'interfaccia

---

### Sprint 13

Esportazione OBJ.

Risultati ottenuti:

✔ Implementazione ObjExporter

✔ Esportazione Wavefront OBJ

✔ Verifica della geometria esportata

✔ Importazione corretta in Blender

✔ Consolidamento del formato OBJ

---

### Sprint 14

Gestione Multi Face.

Risultati ottenuti:

✔ Introduzione del Current Face

✔ Selezione interattiva del volto

✔ Click sui Bounding Box

✔ Aggiornamento automatico di:

- Landmarks

- Wireframe 2D

- MeshViewer

✔ Preparazione architetturale per i futuri exporter

---

### Sprint 15

Consolidamento dell'architettura.

Risultati ottenuti:

✔ Introduzione dei Diagnostics

✔ Miglioramento della separazione dei componenti

✔ Consolidamento del ProjectController

✔ Preparazione dell'infrastruttura Export

---

### Sprint 16

Preparazione della pipeline Texture.

Risultati ottenuti:

✔ Introduzione del FaceExportService

✔ Separazione definitiva tra GUI ed Export

✔ Coordinamento centralizzato dell'esportazione

✔ Preparazione degli exporter dedicati

---

### Sprint 17

Texture Mapping.

Milestone fondamentale del progetto.

Risultati ottenuti:

✔ Introduzione UVMapper

✔ Generazione automatica delle coordinate UV

✔ Esportazione delle coordinate UV nel formato OBJ

✔ Introduzione TextureExporter

✔ Introduzione MaterialExporter

✔ Completamento FaceExportService

✔ Esportazione automatica:

- OBJ

- MTL

- Texture fotografica

✔ Collegamento automatico tra OBJ e MTL

✔ Importazione corretta in Blender

✔ Primo modello 3D con texture fotografica

✔ Pipeline completa Blender funzionante

---

## Milestone raggiunte

### Milestone 0.5

✔ Prima Mesh 3D runtime

---

### Milestone 0.6

✔ Primo Export OBJ corretto

✔ Importazione Blender

---

### Milestone 0.7

✔ UV Mapping

✔ Texture Mapping

✔ Materiali

✔ Pipeline Export completa

✔ Blender completamente operativo

Questa rappresenta la prima versione realmente utilizzabile
di Face3D Studio AI.

---

# 11. Stato dei componenti

## AI

Face Detection

Stato:

STABILE

---

Face Landmarker

Stato:

STABILE

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

## Mapping

UVMapper

Stato:

STABILE

Coordinate UV verificate mediante Blender.

---

## Export

FaceExportService

Stato:

STABILE

---

ObjExporter

Stato:

STABILE

Verificato mediante Blender.

---

TextureExporter

Stato:

STABILE

Versione 1:

copia della fotografia originale.

---

MaterialExporter

Stato:

STABILE

Compatibile con Blender.

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

Miglioramenti futuri:

- assi XYZ

- griglia

- illuminazione

- materiali PBR

- controllo camera

- reset camera

---

# 12. Bug aperti

Ogni bug deve essere registrato in questa sezione.

Formato:

ID

Descrizione

Priorità

Stato

Data

Responsabile

---

## Bug aperti

Attualmente non sono presenti bug bloccanti.

---

## Miglioramenti pianificati

• eliminazione dei warning Qt relativi alla QGraphicsScene;

• miglioramento della gestione della memoria;

• consolidamento della pipeline Export;

• ottimizzazione delle prestazioni del MeshViewer.

---

# 13. Sprint Pianificati

La roadmap seguente rappresenta la pianificazione attuale del progetto.

Gli Sprint futuri potranno essere modificati solo se emergeranno nuove
esigenze tecniche durante lo sviluppo.

---

## Sprint 18

Texture Enhancement

Obiettivi:

□ Correzione automatica dell'illuminazione

□ Riduzione dei riflessi

□ Uniformazione del colore della pelle

□ Miglioramento della texture mediante AI

□ Texture ad alta risoluzione

□ Primo sistema di baking della texture

---

## Sprint 19

Ricostruzione della Testa

Obiettivi:

□ completamento della testa

□ ricostruzione dei lati

□ ricostruzione della nuca

□ ricostruzione delle orecchie

□ simmetria automatica

---

## Sprint 20

Hair Reconstruction

Obiettivi:

□ ricostruzione automatica dei capelli

□ volume dei capelli

□ gestione capelli lunghi

□ gestione barba e baffi

---

## Sprint 21

Mesh Editing

Obiettivi:

□ selezione dei vertici

□ modifica locale della mesh

□ smoothing

□ sculpting leggero

□ undo / redo

---

## Sprint 22

Esportazione Professionale

Obiettivi:

□ STL Exporter

□ PLY Exporter

□ GLTF Exporter

□ FBX Exporter

□ verifica MeshLab

□ verifica Blender

□ verifica stampa 3D

---

## Sprint 23

Rendering Professionale

Obiettivi:

□ materiali PBR

□ HDRI

□ illuminazione avanzata

□ ombre

□ controllo camera

□ screenshot HD

---

## Sprint 24

Analisi Antropometrica

Obiettivi:

□ misure lineari

□ misure angolari

□ proporzioni facciali

□ confronto tra due soggetti

□ report PDF

---

## Sprint 25

AI Analysis

Obiettivi:

□ classificazione morfologica

□ analisi automatica

□ suggerimenti estetici

□ confronto temporale

□ modelli AI dedicati

---

# 14. Regole di sviluppo

Durante lo sviluppo dovranno essere rispettate le seguenti regole.

✔ Ogni componente deve avere una sola responsabilità.

✔ L'architettura GUI → Controller → Services → Exporters → Models
non deve essere modificata senza una reale necessità tecnica.

✔ Ogni Sprint affronta un solo obiettivo principale.

✔ Ogni nuova funzionalità deve essere testata prima del commit.

✔ Ogni commit deve rappresentare una milestone funzionante.

✔ Mai introdurre regressioni.

✔ Ogni nuova architettura deve essere documentata.

✔ Mai duplicare codice.

✔ Preferire sempre componenti riutilizzabili.

✔ Tutte le funzionalità che operano su un volto
devono utilizzare il Current Face del ProjectController.

✔ I widget grafici non devono essere utilizzati
come sorgente dei dati dell'applicazione.

✔ Ogni nuova classe deve avere una responsabilità chiaramente definita.

✔ Ogni nuovo exporter deve scrivere un solo formato.

✔ Ogni nuova funzionalità deve integrarsi
nell'architettura esistente.

---

# 15. Procedura di apertura Sprint

Ogni Sprint dovrà iniziare seguendo la stessa procedura.

1.

Aprire una nuova chat ChatGPT.

2.

Allegare il progetto aggiornato.

3.

Leggere ROADMAP.md.

4.

Leggere CHANGELOG.md.

5.

Definire l'obiettivo dello Sprint.

6.

Verificare lo stato dell'architettura.

7.

Implementare una modifica alla volta.

8.

Testare ogni modifica.

---

# 16. Procedura di chiusura Sprint

Ogni Sprint termina seguendo sempre gli stessi passaggi.

1.

Verifica funzionale completa.

2.

Correzione dei bug.

3.

Pulizia del codice.

4.

Eliminazione del codice temporaneo.

5.

Aggiornamento ROADMAP.md.

6.

Aggiornamento CHANGELOG.md.

7.

Aggiornamento della documentazione tecnica.

8.

Commit Git.

9.

Push GitHub.

Uno Sprint può considerarsi concluso solamente
quando tutti questi passaggi sono stati completati.

---

# 17. Convenzioni Git

Ogni commit deve descrivere chiaramente
il risultato ottenuto.

Formato consigliato:

Sprint XX: descrizione

Esempi:

Sprint 17: complete texture export pipeline

Sprint 18: AI texture enhancement

Sprint 19: complete head reconstruction

Mai utilizzare commit come:

update

fix

test

prova

pippo

Ogni commit deve rappresentare
uno stato stabile del progetto.

---

# 18. Visione a lungo termine

Face3D Studio AI dovrà evolversi fino a diventare
una piattaforma professionale dedicata
alla ricostruzione tridimensionale del volto umano.

Gli ambiti di utilizzo previsti comprendono:

• medicina;

• odontoiatria;

• chirurgia estetica;

• antropometria;

• stampa 3D;

• Blender;

• CAD;

• realtà aumentata;

• realtà virtuale;

• ricerca scientifica;

• Intelligenza Artificiale.

L'obiettivo finale non è semplicemente generare
una mesh tridimensionale.

L'obiettivo è costruire un framework completo
capace di trasformare fotografie e video
in modelli tridimensionali accurati,
modificabili, analizzabili ed esportabili
nei principali formati professionali.

La Milestone 0.7.0 rappresenta il punto in cui
Face3D Studio AI dispone della prima pipeline completa:

Fotografia

↓

MediaPipe Face Landmarker

↓

Face Analysis

↓

Mesh 3D

↓

UV Mapping

↓

Texture

↓

Materiale

↓

OBJ

↓

Blender

Da questa versione in avanti,
gli sviluppi futuri saranno dedicati principalmente
al miglioramento della qualità dei modelli,
all'incremento del realismo
e all'introduzione di nuove funzionalità AI,
mantenendo invariata l'architettura fondamentale del progetto.

---

# Fine documento
