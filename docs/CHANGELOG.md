# Face3D Studio AI

# CHANGELOG

Tutte le modifiche rilevanti del progetto vengono registrate in questo documento.

---

## Versione 0.3.1

Data: 28/07/2026

### Nuove funzionalità

- Introduzione di ApplicationController.
- Refactoring completo di CentralWidget.
- Dependency Injection dei Controller.
- Project Explorer completato.

### Miglioramenti

- Architettura MVC completata.
- Separazione tra GUI e Controller.
- ProjectTreeWidget indipendente dal Controller.

### Correzioni

- Eliminata la duplicazione di CentralWidget.
- Corretto il flusso di inizializzazione della GUI.

### Repository

- Repository GitHub configurato.
- Push iniziale completato.
---

## Versione 0.5.0

Data: 29/07/2026

### Nuove funzionalità

- Implementata l'importazione multipla delle fotografie.
- Le fotografie vengono copiate automaticamente nella cartella del progetto.
- Introdotto il modello `Photo`.
- Implementato `PhotoController`.
- Implementato `PhotoManager`.
- Aggiunto il comando **File → Import Photos...**.
- Introdotta la persistenza delle fotografie nel progetto.

### Miglioramenti

- Refactoring completo dell'architettura Controller → Manager.
- MainWindow comunica esclusivamente con i Controller.
- Separazione delle responsabilità tra `ProjectController` e `PhotoController`.
- Introdotto `ProjectSerializer`.
- Aggiunti i metodi `to_dict()` e `from_dict()` al modello `Photo`.
- Aggiornato `ProjectLoader` per la ricostruzione degli oggetti `Photo`.

### Correzioni

- Corretto il salvataggio del percorso del progetto.
- Corretta la serializzazione degli oggetti `Photo`.
- Corretta la deserializzazione delle fotografie all'apertura del progetto.

### Stato della milestone

✅ M0.5 completata e verificata.

### Test eseguiti

- Creazione progetto.
- Apertura progetto.
- Importazione multipla fotografie.
- Copia automatica delle fotografie.
- Salvataggio del progetto.
- Chiusura e riapertura dell'applicazione.
- Riapertura del progetto con ricostruzione delle fotografie.

---

## Vertex Mapper - Interactive MediaPipe Mapping

Data: 12/08/2026

### Nuove funzionalita

- Completata la fase di selezione e associazione dei Control Points MediaPipe.
- Implementata la mappa grafica interattiva dei landmark MediaPipe.
- Limitata l'interazione della mappa ai 25 Control Points utilizzati dal Vertex Mapper.
- Implementata la selezione dei Control Points direttamente dalla mappa.
- Implementata l'evidenziazione grafica del landmark selezionato.
- Implementata la sincronizzazione tra mappa MediaPipe e ComboBox del Vertex Mapper.
- Selezionando un landmark dalla ComboBox, il corrispondente punto viene evidenziato sulla mappa.
- Selezionando un punto dalla mappa, il corrispondente landmark viene selezionato automaticamente nella ComboBox.
- Mantenuta la gestione esistente delle associazioni landmark -> vertice MakeHuman.
- Mantenuta la gestione esistente della selezione e della visualizzazione dei vertici associati.
- Mantenuta la gestione della mappa indipendente dal MeshViewer.

### Miglioramenti

- La mappa MediaPipe mantiene correttamente le coordinate dei landmark anche durante il ridimensionamento della finestra.
- La selezione dei punti utilizza una tolleranza per facilitare il click dell'utente.
- Separata la logica grafica della mappa dalla logica di mapping dei vertici.
- Preparata l'interfaccia per le successive funzionalita del Vertex Mapper.

### Test

- Apertura della mappa MediaPipe.
- Click sui Control Points.
- Riconoscimento dei landmark.
- Evidenziazione del landmark selezionato.
- Click leggermente distante dal punto.
- Click in aree prive di Control Points.
- Ridimensionamento della finestra.
- Verifica della stabilita delle coordinate.
- Sincronizzazione mappa -> ComboBox.
- Sincronizzazione ComboBox -> mappa.
- Verifica dei landmark gia associati.
- Verifica della conservazione delle associazioni esistenti.

### Stato della milestone

[x] Vertex Mapper - Interactive MediaPipe Mapping completato e verificato.

---

## Vertex Mapper - Anatomical Mapping Filters

Data: 13/08/2026

Versione: VertexMapperDialog 1.8.0

### Nuove funzionalita

- Aggiunta la visualizzazione dei mapping tramite filtro anatomico.
- Aggiunta la modalità di visualizzazione "Nessuno".
- Aggiunta la modalità "Solo landmark corrente".
- Aggiunta la modalità "Tutti i landmark associati".
- Aggiunti i gruppi anatomici Volto, Naso, Occhio destro,
  Occhio sinistro, Bocca, Sopracciglio destro e Sopracciglio sinistro.
- I gruppi anatomici vengono derivati dai nomi semantici
  dei LandmarkDefinition già presenti nel LandmarkCatalog.

### Miglioramenti

- La revisione delle associazioni può ora essere effettuata
  isolando una singola regione anatomica.
- I filtri operano esclusivamente sulla visualizzazione
  dei marker e non modificano la VertexMappingCollection.
- Non vengono duplicati nella GUI gli indici MediaPipe già
  definiti nel catalogo dei landmark.
- Il workflow esistente di associazione, dissociazione, picking,
  report e mappa MediaPipe interattiva rimane invariato.

### Test

- Verifica modalità Nessuno.
- Verifica modalità Solo landmark corrente.
- Verifica modalità Tutti i landmark associati.
- Verifica filtro Volto.
- Verifica filtro Naso.
- Verifica filtro Occhio destro.
- Verifica filtro Occhio sinistro.
- Verifica filtro Bocca.
- Verifica filtro Sopracciglio destro.
- Verifica filtro Sopracciglio sinistro.
- Verifica del cambio ripetuto tra i diversi filtri.
- Verifica che i filtri non modifichino le associazioni esistenti.
- Verifica completa del Vertex Mapper dopo l'integrazione dei filtri.

### Stato della milestone

[x] Vertex Mapper 1.8.0 - Filtri anatomici dei mapping completati e verificati.

Il Vertex Mapper è ora pronto per la prosecuzione dello Sprint 19,
con il completamento progressivo delle 25 associazioni MediaPipe ↔ MakeHuman.

---

## Sprint 19 — Canonical Mapping Validation

Data: 17/08/2026

### Stato

[x] Sprint 19 completato e verificato.

### Canonical Mapping

Il set definitivo dei Control Points MediaPipe è stato
completato.

Risultato:

    Mapping: 25/25
    Mapping status: COMPLETE

Sono state verificate l'univocità dei landmark e dei
vertici associati e la coerenza della convenzione
anatomica destra/sinistra.

La convenzione utilizzata è anatomica:

    right_* = lato destro anatomico del modello
    left_*  = lato sinistro anatomico del modello

La posizione del punto sulla bitmap visualizzata non
deve essere utilizzata per reinterpretare il lato anatomico.

### Mapping definitivo

- nose_bridge → vertex 216
- nose_lower_center → vertex 531
- nose_tip → vertex 537
- forehead_center → vertex 534
- upper_lip_center → vertex 536
- lower_lip_center → vertex 259
- right_eye_outer → vertex 211
- right_eyebrow_inner → vertex 85
- right_eyebrow_outer → vertex 82
- mouth_right → vertex 62
- upper_lip_right → vertex 55
- nose_right_base → vertex 92
- right_eye_inner → vertex 26
- right_eye_lower → vertex 1323
- chin → vertex 487
- right_eye_upper → vertex 1379
- left_eye_outer → vertex 303
- left_eyebrow_inner → vertex 357
- left_eyebrow_outer → vertex 354
- mouth_left → vertex 333
- upper_lip_left → vertex 326
- nose_left_base → vertex 364
- left_eye_inner → vertex 298
- left_eye_lower → vertex 791
- left_eye_upper → vertex 590

### Validazione del template MakeHuman

Template:

    male1591
    part = head

Verifiche eseguite:

- 1604 vertici;
- 3064 triangoli;
- nessun indice triangolare non valido;
- nessun triangolo degenerato;
- nessun vertice duplicato;
- 4812 coordinate finite;
- NaN = 0;
- Inf = 0.

### Componenti connesse

La mesh presenta 6 componenti connesse:

- Componente 1: 490 vertici
- Componente 2: 276 vertici
- Componente 3: 276 vertici
- Componente 4: 256 vertici
- Componente 5: 256 vertici
- Componente 6: 50 vertici

La componente principale contiene 21 Control Points.
Le componenti relative alle geometrie degli occhi
contengono i restanti Control Points oculari.

### Bounding Box componente principale

    X: -0.081100 → 0.081100
    Y:  1.387100 → 1.659500
    Z: -0.048500 → 0.159300

    sizeX = 0.162200
    sizeY = 0.272400
    sizeZ = 0.207800

    center = (0.000000, 1.523300, 0.055400)

### Coordinate normalizzate

È stata verificata la normalizzazione dei Control Points
rispetto al bounding box della componente principale.

Sono state verificate le coppie bilaterali:

- right_eye_outer ↔ left_eye_outer
- right_eye_inner ↔ left_eye_inner
- right_eyebrow_inner ↔ left_eyebrow_inner
- right_eyebrow_outer ↔ left_eyebrow_outer
- mouth_right ↔ mouth_left
- upper_lip_right ↔ upper_lip_left
- nose_right_base ↔ nose_left_base

Tutte le coppie risultano coerenti entro la tolleranza
utilizzata, con una sola piccola asimmetria locale:

    right_eye_outer ↔ left_eye_outer
    errore normalizzato = 0.0117

Il valore non è stato considerato sufficiente per invalidare
il mapping. Viene registrato come caratteristica geometrica
locale da monitorare.

### Test superati

- Catalogo Control Points: OK
- Convenzione anatomica dei lati: OK
- Associazione dei 25 Control Points: OK
- Mapping 25/25: OK
- Stato COMPLETE: OK
- Validazione coordinate: OK
- Validazione triangoli: OK
- Triangoli degenerati: 0
- Vertici duplicati: 0
- Componenti connesse: verificata
- Bounding box: verificata
- Normalizzazione Control Points: OK
- Simmetria bilaterale: OK con l'asimmetria locale documentata

### Risultato

Il Canonical Mapping è ora considerato il set definitivo
di 25 associazioni per il template `male1591/head`.

La fase di associazione manuale è conclusa.

### Prossimo obiettivo

Il prossimo lavoro sarà la costruzione della Canonical Mesh
derivata dal template MakeHuman, mantenendo:

- identità dei vertici;
- triangolazione;
- topologia;
- coordinate;
- compatibilità con il Canonical Mapping.

La Registration Engine non viene ancora implementata.
---

## Sprint 22 — Canonical Mesh Builder

Data: 18/08/2026

### Stato

[x] Sprint 22 completato e verificato.

### Canonical Mesh

È stata completata la costruzione della Canonical Mesh
derivata dal template MakeHuman della testa.

Template utilizzato:

    male1591

Mesh sorgente:

    male1591_head.obj

La scelta della mesh specifica della testa è intenzionale:
il modello completo `male1591.obj` rimane disponibile nel progetto,
ma non viene utilizzato per la costruzione della Canonical Mesh
della testa.

### Implementazione

È stato implementato il:

    CanonicalMeshBuilder

La pipeline verificata è:

    MakeHuman Template
            ↓
    TemplateLoader
            ↓
    HeadTemplate
            ↓
    CanonicalMeshBuilder
            ↓
    CanonicalMesh

Il Builder costruisce una rappresentazione derivata e indipendente
dal template sorgente.

Sono mantenuti:

- identità e ordine dei vertici;
- coordinate geometriche;
- indici dei triangoli;
- triangolazione;
- topologia della mesh.

Il template sorgente non viene modificato.

### Validazione minima del Builder

Il `CanonicalMeshBuilder` verifica i prerequisiti minimi
necessari alla costruzione della Canonical Mesh.

Sono stati implementati controlli per:

- tipo corretto di `HeadTemplate`;
- presenza dei vertici;
- validità degli indici dei triangoli;
- assenza di riferimenti a vertici inesistenti;
- coerenza dei metadati identificativi.

La validazione geometrica completa della Canonical Mesh
rimane responsabilità dello Sprint 23.

### Risultato geometrico

La Canonical Mesh costruita dal template `male1591_head.obj`
contiene:

    1604 vertici
    3064 triangoli

È stata verificata la corrispondenza completa con la geometria
del template originale.

### Compatibilità con Canonical Mapping

La Canonical Mesh è stata verificata rispetto al
Canonical Mapping definitivo.

Risultato:

    Mapping: 25/25
    Mapping status: COMPLETE

Per tutti i 25 Control Points è stata verificata:

- esistenza del vertice indicato;
- validità dell'indice;
- corrispondenza delle coordinate;
- compatibilità dei metadati;
- unicità dei vertici associati.

### Test eseguiti

Sono stati superati i seguenti test:

- caricamento del template reale `male1591/head`;
- costruzione della Canonical Mesh;
- verifica di 1604 vertici;
- verifica di 3064 triangoli;
- verifica delle coordinate;
- verifica degli indici dei triangoli;
- verifica della triangolazione;
- verifica dell'indipendenza degli oggetti Vertex3D;
- verifica dell'indipendenza degli oggetti Triangle;
- verifica che il template originale rimanga invariato;
- verifica del template privo di vertici;
- verifica di un triangolo con indice fuori range;
- verifica della compatibilità Canonical Mapping ↔ Canonical Mesh;
- test finale integrato dello Sprint 22.

### Test finale integrato

Risultato:

    Counts: OK
    Geometry: OK
    Object independence: OK
    Template unchanged: OK
    Canonical Mapping: OK

    FINAL RESULT: SPRINT 22 OK
---

## Sprint 23 — Canonical Mesh Validation

Data: 19/08/2026

### Stato

[x] Sprint 23 completato e verificato.

Lo Sprint 23 ha completato la validazione della Canonical Mesh
necessaria come prerequisito per la Registration Engine.

### Validazione completata

È stato completato e integrato il sistema di validazione della
Canonical Mesh.

Sono stati verificati:

- numero dei vertici;
- numero dei triangoli;
- validità degli indici triangolari;
- coordinate finite;
- NaN / Inf;
- bounding box;
- dimensioni;
- centro geometrico;
- boundary edges;
- boundary vertices;
- edge non-manifold;
- triangoli degeneri;
- normali delle facce;
- normali zero-length;
- normali non finite;
- orientamento / winding;
- distribuzione dei 25 Control Points;
- coordinate normalizzate;
- simmetria bilaterale;
- sistema di coordinate;
- serializzazione dei report diagnostici.

### Componenti introdotti

È stato integrato:

    MeshNormalAnalyzer

con relativo:

    MeshNormalAnalysisReport

Il componente analizza le normali della mesh e produce
le informazioni necessarie alla validazione finale.

### Risultato sulla Canonical Mesh reale

Template:

    male1591/head

Source:

    male1591_head.obj

Risultati finali:

    Template vertices:       1604
    Template triangles:      3064
    Canonical vertices:      1604
    Canonical triangles:     3064

    Valid:                    True

    Normal count:             3064
    Valid normals:            3064
    Zero-length normals:      0
    Non-finite normals:       0

    Boundary edges:           138
    Boundary vertices:        138
    Non-manifold edges:       0
    Degenerate triangles:     0
    Non-finite vertices:      0
    Bounds available:         True

    Warnings:                 1
    Errors:                   0

    RESULT: SPRINT 23 FINAL OK

### Control Points

Sono stati verificati i 25 Control Points sulla Canonical Mesh.

Risultato:

    Mapping: 25/25
    Status: COMPLETE

È stata inoltre verificata la distribuzione dei Control Points,
la normalizzazione rispetto alla componente principale e la
simmetria delle coppie bilaterali.

Rimane documentata la sola asimmetria locale:

    right_eye_outer ↔ left_eye_outer
    errore normalizzato = 0.0117

Il valore non invalida il mapping e viene mantenuto come
caratteristica geometrica locale da monitorare.

### Sistema di coordinate

È stata verificata la convenzione del sistema di coordinate
della Canonical Mesh:

    X:
        +X = destra anatomica
        -X = sinistra anatomica

    Y:
        +Y = alto
        -Y = basso

    Z:
        +Z = anteriore / fronte
        -Z = posteriore / nuca

Le coordinate canoniche originali vengono preservate.

La scala tra MediaPipe e Canonical Mesh non viene fissata
arbitrariamente nello Sprint 23 e sarà stimata durante
il Global Alignment.

### Test negativi

Sono stati verificati con successo:

- vertice con NaN;
- vertice con +Inf;
- vertice con -Inf;
- triangolo con indice duplicato;
- triangolo con area nulla;
- edge non-manifold;
- condizioni di normale non valida.

È stata verificata anche l'indipendenza delle diagnostiche.

### Commit

Commit di chiusura dello Sprint:

    8928164 feat: integrate canonical mesh normal analysis

### Repository

Il commit è stato pubblicato su:

    origin/master

Repository verificato:

    working tree clean
    branch master
    up to date with origin/master

### Risultato

    SPRINT 23 — COMPLETATO

La Canonical Mesh è ora validata e pronta
per essere utilizzata dalla Registration Engine.

### Prossimo Sprint

    Sprint 24 — Registration Engine

La Registration Engine non viene anticipata nello Sprint 23.



---

## Sprint 24 — Registration Engine

Data: 19/08/2026

### Stato

[x] Sprint 24 completato e verificato.

### Obiettivo

È stato completato il Registration Engine previsto dalla
roadmap del progetto.

Il motore costituisce il punto di integrazione tra:

    Canonical Mesh
          +
    Real Face Landmarks
          ↓
    Registration Engine

senza anticipare il Global Alignment, la deformazione locale
o le successive fasi di ricostruzione.

### Integrazione nella pipeline

La Registration Engine è stata integrata nella pipeline:

    FaceAnalysisService
          ↓
    HeadReconstructionPipeline
          ↓
    HeadReconstructionBuilder
          ↓
    RegistrationEngine

Il Registration Engine riceve:

- Canonical Mesh;
- Canonical Mapping;
- Face con i landmark MediaPipe.

### Canonical Mesh reale

L'integrazione è stata verificata utilizzando la Canonical Mesh
reale derivata dal template:

    male1591/head

Risultato:

    Canonical vertices: 1604
    Canonical triangles: 3064

Il test integrato ha verificato che la Canonical Mesh passata
effettivamente al Registration Engine sia quella prevista.

### Canonical Mapping

È stato verificato l'utilizzo del Canonical Mapping definitivo:

    Mapping entries: 25
    Mapping complete: True

Il Registration Engine utilizza quindi tutti i 25 Control Points
previsti dal progetto.

### Test del Registration Engine

Sono stati eseguiti test positivi e negativi per verificare
la robustezza del motore.

#### Input valido

Risultato:

    Registration status: RegistrationStatus.SUCCESS
    Success: True
    Used landmarks: 25
    Expected landmarks: 25
    Errors: []

#### Landmark mancante

È stata verificata la corretta gestione di un landmark MediaPipe
mancante.

Risultato:

    RegistrationStatus.FAILED
    Missing MediaPipe landmark detected.

#### Coordinate non finite

Sono stati verificati:

- NaN su una coordinata;
- +Inf su una coordinata.

Il Registration Engine rileva correttamente entrambe le
condizioni e restituisce lo stato FAILED con diagnostica
esplicita.

#### Mapping incompleto

È stato verificato un Canonical Mapping contenente 24
associazioni invece delle 25 previste.

Il Registration Engine rileva correttamente:

    Canonical Mapping is not complete.

#### Mapping incompatibile

È stata verificata l'incompatibilità tra il numero di
Control Points atteso e quello dichiarato dal mapping.

Il motore rileva correttamente la configurazione incompatibile.

#### Landmark fuori range

È stato verificato un landmark MediaPipe con indice non valido.

Il Registration Engine rileva correttamente:

    Missing MediaPipe landmark at index 500.

### Test di regressione geometrica

È stato verificato che il Registration Engine non modifichi
la geometria della Canonical Mesh in questa fase.

Risultato:

    Geometry unchanged: True
    Topology unchanged: True
    Vertex count unchanged: True
    Triangle count unchanged: True

Questo comportamento è intenzionale e mantiene separata la
fase di registrazione dalla successiva fase di Global Alignment.

### Test finale di integrazione

Il test finale ha verificato l'intera catena:

    HeadReconstructionPipeline
            ↓
    HeadReconstructionBuilder
            ↓
    RegistrationEngine

Risultato:

    Registration status: RegistrationStatus.SUCCESS
    Registration success: True
    Used landmarks: 25
    Expected landmarks: 25
    RegistrationEngine calls: 1

    Canonical vertices passed: 1604
    Canonical triangles passed: 3064

    Face mesh vertices: 3
    Face mesh triangles: 1

    Geometry unchanged: True
    Topology unchanged: True

    RESULT: OK

### Risultato

    SPRINT 24 — COMPLETATO E VERIFICATO

La Registration Engine è ora integrata nella pipeline
di ricostruzione e pronta per il successivo:

    Sprint 25 — Global Alignment

Il Global Alignment non viene anticipato nello Sprint 24.
