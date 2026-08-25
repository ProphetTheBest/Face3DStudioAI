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

---

## Sprint 25 — Global Alignment

Data: 20/08/2026

### Stato

[x] Sprint 25 completato e verificato.

### Obiettivo

È stato completato il primo livello della registrazione geometrica
globale della Canonical Mesh rispetto ai Control Points del volto reale.

Il Global Alignment determina una trasformazione composta da:

    translation
    rotation
    scale

e la rappresenta tramite una matrice omogenea 4×4.

### RegistrationTransformation

È stato introdotto il modello:

    source/models/registration_transformation.py

Il modello rappresenta la trasformazione geometrica globale attraverso
una matrice NumPy 4×4.

La trasformazione espone:

- matrice omogenea 4×4;
- componente di traslazione;
- sottomatrice 3×3 di rotazione / scala;
- costruzione della trasformazione identità.

Sono stati inoltre introdotti controlli per:

- dimensione obbligatoria 4×4;
- valori esclusivamente finiti;
- rifiuto di matrici non valide.

### RegistrationResult

Il modello `RegistrationResult` è stato esteso per rappresentare
anche il risultato del Global Alignment.

Sono ora disponibili:

- `transformation`;
- `mean_error`;
- `rms_error`;
- `max_error`.

È stata mantenuta la compatibilità con il precedente contratto
del Registration Engine.

Il test di backward compatibility ha confermato che un risultato
di registrazione precedente continua a essere utilizzabile senza
una trasformazione globale valorizzata.

### Global Alignment con Umeyama

Il `RegistrationEngine` è stato esteso con la stima della
trasformazione globale mediante algoritmo di Umeyama.

La procedura utilizza:

    Canonical Control Points
            +
    Real Control Points
            ↓
    stima della trasformazione
            ↓
    scale
    rotation
    translation
            ↓
    matrice omogenea 4×4

La trasformazione viene applicata concettualmente all'intera
Canonical Mesh, mantenendo separata la fase di Global Alignment
dalla successiva Local Deformation.

### Test matematico

È stato eseguito un test deterministico con trasformazione nota.

Risultati:

    Expected scale:       1.75
    Recovered scale:      1.75
    Scale error:          0.0

    Rotation error:
        1.1102230246251565e-16

    Translation error:
        4.440892098500626e-16

    Mean point error:
        4.440892098500626e-16

    RMS point error:
        4.440892098500626e-16

    Max point error:
        4.440892098500626e-16

    RESULT: OK

### Test integrato

È stato eseguito il test completo:

    test_global_alignment.py

Il test ha verificato:

    Canonical Control Points: 25
    Real Control Points:      25
    Mapping entries:          25
    Mapping complete:         True
    Canonical mesh vertices:  25
    Face landmarks:           25

Risultato della registrazione:

    Status: RegistrationStatus.SUCCESS
    Success: True
    Used landmarks: 25
    Expected landmarks: 25
    Registration error:
        2.936915022422793e-16

    Mean error:
        2.739988667247874e-16

    RMS error:
        2.936915022422793e-16

    Max error:
        5.23691153334427e-16

    Errors: []
    Warnings: []

### Trasformazione verificata

La trasformazione recuperata nel test integrato è risultata
coerente con i parametri attesi:

    Expected scale:    1.35
    Recovered scale:  1.35
    Scale error:      0.0

    Expected translation:
        [ 0.1  -0.05  0.2 ]

    Recovered translation:
        [ 0.1  -0.05  0.2 ]

    Translation error:
        5.967448757360216e-16

    Rotation error:
        5.599433397402341e-16

    RESULT: OK

### Regression Test dello Sprint 24

Dopo l'introduzione del Global Alignment è stato rieseguito
il test di integrazione della Registration Engine dello
Sprint 24.

Il test ha confermato:

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

Il comportamento precedente della Registration Engine è quindi
rimasto compatibile e non sono state rilevate regressioni.

### Test del modello di trasformazione

Sono stati verificati:

- costruzione della trasformazione identità;
- matrice 4×4;
- estrazione della traslazione;
- estrazione della sottomatrice 3×3;
- rifiuto di una matrice 3×3;
- rifiuto di una matrice 5×5;
- rifiuto di valori NaN.

Tutti i test hanno prodotto il risultato atteso.

### File introdotti o modificati

Sono stati introdotti:

    source/models/registration_transformation.py
    test_global_alignment.py

Sono stati modificati:

    source/models/registration_result.py
    source/reconstruction/registration/registration_engine.py

### Risultato finale

    SPRINT 25 — COMPLETATO E VERIFICATO

Il Registration Engine dispone ora del primo livello di
registrazione geometrica globale mediante trasformazione
omogenea 4×4 e stima Umeyama.

La pipeline è pronta per il successivo:

    Sprint 26 — Local Deformation

La Local Deformation non viene anticipata nello Sprint 25.

---

## Sprint 26 — Local Deformation

Data: 20/08/2026

### Stato

[x] Sprint 26 completato e verificato.

### Obiettivo

È stata completata l'implementazione della deformazione locale
della Canonical Mesh dopo il Global Alignment.

La pipeline raggiunta è:

    Canonical Mesh
          +
    Real Face Landmarks
          ↓
    Registration Engine
          ↓
    Global Alignment
          ↓
    Aligned Canonical Mesh
          ↓
    Local Deformation
          ↓
    Personalized Mesh

La topologia della Canonical Mesh viene preservata durante la
deformazione.

### LocalDeformationEngine

È stato introdotto il componente:

    source/reconstruction/algorithms/local_deformation.py

Il motore riceve:

- source control points;
- target control points;
- smoothing opzionale.

Il componente espone:

- `source_points`;
- `target_points`;
- `displacements`;
- `displacement()`;
- `deform()`;
- `control_point_count`;
- `smoothing`.

### Algoritmo

Per lo Sprint 26 è stata utilizzata una interpolazione RBF
con kernel Thin Plate Spline tramite `scipy.interpolate.RBFInterpolator`.

La scelta è stata validata sul dataset sintetico utilizzato
durante lo sviluppo.

La deformazione è calcolata a partire dagli spostamenti dei
25 Control Points e viene propagata all'intera geometria.

### Ambiente numerico verificato

Sono state verificate le dipendenze disponibili nell'ambiente
di sviluppo:

    NumPy: 1.26.4
    SciPy: 1.17.1

È stata inoltre verificata la disponibilità di:

    scipy.interpolate.RBFInterpolator

con risultato:

    RESULT: OK

### Test dei Control Points

È stato eseguito un test con 25 Control Points e deformazione
artificiale nota.

Risultati:

    Control Points: 25
    Source shape: (25, 3)
    Target shape: (25, 3)
    Displacement shape: (25, 3)
    Smoothing: 0.0

    Mean error:
        3.203803786809599e-17

    RMS error:
        4.082882857376341e-17

    Max error:
        7.850462293418876e-17

    RESULT: OK

Il test conferma la corretta interpolazione dei Control Points.

### Test dei punti intermedi

È stata verificata la capacità del motore di deformare punti
non coincidenti con i Control Points.

Risultati:

    Intermediate points: 5
    Input shape: (5, 3)
    Output shape: (5, 3)
    Displacement shape: (5, 3)
    Finite output: True
    Finite displacement: True

    Displacement norm:
        [0.08719264 0.02798869 0.02809725
         0.08715859 0.0252629 ]

    RESULT: OK

### Test sulla mesh completa

Il motore è stato verificato su una geometria contenente:

    1604 vertices
    3064 triangles

Risultati:

    Control Points: 25
    Original vertices: 1604
    Deformed vertices: 1604

    Shape unchanged: True
    Vertex count unchanged: True
    Input vertices unchanged: True
    Source Control Points unchanged: True
    Target Control Points unchanged: True
    Finite output: True

    Moved vertices:
        1604 / 1604

    Mean displacement:
        0.09187980028230278

    Max displacement:
        0.13124467965624315

    Control Point max error:
        7.850462293418876e-17

    RESULT: OK

Il test conferma inoltre che il motore non modifica in-place
né i vertici di input né i Control Points sorgente e destinazione.

### Integrazione Global Alignment + Local Deformation

È stato eseguito il test integrato:

    test_global_alignment_local_deformation.py

Sono stati verificati:

    Canonical vertices: 1604
    Canonical triangles: 3064
    Canonical Control Points: 25
    Real Control Points: 25
    Mapping entries: 25
    Mapping complete: True

    Global Alignment:
        Status: RegistrationStatus.SUCCESS
        Success: True
        Used landmarks: 25
        Expected landmarks: 25
        Transformation shape: (4, 4)

    Aligned vertices: 1604
    Aligned shape: (1604, 3)

    Deformed vertices: 1604
    Deformed shape: (1604, 3)

    Control Points mean error:
        1.0852430065710906e-16

    Control Points RMS error:
        1.3475753576563817e-16

    Control Points max error:
        3.3306690738754696e-16

È stata verificata anche l'integrità della Canonical Mesh:

    Canonical vertices unchanged: True
    Canonical topology unchanged: True

    RESULT: OK

### HeadReconstructionBuilder

La deformazione locale è stata integrata nel:

    HeadReconstructionBuilder

Versione verificata:

    3.0.1

Il builder produce una FaceMesh con:

    Vertices: 1604
    Triangles: 3064
    Shape: (1604, 3)

Sono risultati verificati:

    Finite geometry: True
    Vertex count OK: True
    Triangle count OK: True
    Shape OK: True
    Geometry changed: True
    Topology unchanged: True
    Canonical vertices unchanged: True
    Canonical topology unchanged: True

    RESULT: OK

### HeadReconstructionPipeline

La Local Deformation è stata verificata anche attraverso:

    HeadReconstructionPipeline

La pipeline ha prodotto:

    FaceMesh created: True
    Vertices: 1604
    Triangles: 3064
    Shape: (1604, 3)
    Finite geometry: True
    Triangle indices valid: True
    Boundary phase completed: True
    Geometry non-degenerate: True

Il test ha inoltre confermato:

    Returned same Face: True
    Pipeline completed: True

    RESULT: OK

### Regression Test della Registration Engine

Dopo l'integrazione della Local Deformation è stato rieseguito
il test:

    test_reconstruction_registration.py

Il test ha confermato:

    Registration status: RegistrationStatus.SUCCESS
    Registration success: True
    Used landmarks: 25
    Expected landmarks: 25
    Registration transformation: True
    RegistrationEngine calls: 1

La ricostruzione finale mantiene:

    Initial FaceMesh vertices: 3
    Reconstructed vertices: 1604

    Initial FaceMesh triangles: 1
    Reconstructed triangles: 3064

    Expected vertices: 1604
    Expected triangles: 3064

    Geometry finite: True
    Topology matches Canonical Mesh: True
    Canonical geometry unchanged: True
    Canonical topology unchanged: True

    RESULT: OK

### Regression Test Global Alignment

È stato inoltre rieseguito:

    test_global_alignment.py

Risultati:

    Status: RegistrationStatus.SUCCESS
    Success: True
    Used landmarks: 25
    Expected landmarks: 25

    Registration error:
        2.936915022422793e-16

    Mean error:
        2.739988667247874e-16

    RMS error:
        2.936915022422793e-16

    Max error:
        5.23691153334427e-16

    Errors: []
    Warnings: []

    Expected scale: 1.35
    Recovered scale: 1.35
    Scale error: 0.0

    Translation error:
        5.967448757360216e-16

    Rotation error:
        5.599433397402341e-16

    RESULT: OK

### Regression Test Head Reconstruction Builder

È stato rieseguito:

    test_head_reconstruction_builder.py

Risultato:

    FaceMesh created: True
    1604 vertices: True
    3064 triangles: True
    Geometry shape: True
    Finite geometry: True
    Geometry deformed: True
    Topology unchanged: True
    Canonical geometry unchanged: True
    Canonical topology unchanged: True

    RESULT: OK

### Regression Test Head Reconstruction Pipeline

È stato rieseguito:

    test_head_reconstruction_pipeline.py

Risultato:

    Pipeline completed: True
    FaceMesh created: True
    1604 vertices: True
    3064 triangles: True
    Finite geometry: True
    Triangle indices valid: True
    Boundary phase: True
    Geometry non-degenerate: True

    RESULT: OK

### Proprietà preservate

Lo Sprint 26 mantiene invariati:

- numero dei vertici;
- numero dei triangoli;
- indici dei triangoli;
- topologia;
- identità dei vertici;
- Canonical Mesh originale.

La deformazione modifica esclusivamente le coordinate della
geometria derivata.

### File introdotti o modificati

È stato introdotto:

    source/reconstruction/algorithms/local_deformation.py

Sono stati integrati/modificati i componenti necessari alla
ricostruzione locale e ai relativi test.

### Risultato finale

    SPRINT 26 — COMPLETATO E VERIFICATO

Il progetto dispone ora di una pipeline verificata:

    Registration
        ↓
    Global Alignment
        ↓
    Local Deformation
        ↓
    Personalized FaceMesh

con 1604 vertici e 3064 triangoli e preservazione della
topologia canonica.

Il prossimo obiettivo è:

    Sprint 27 — Head Reconstruction

La Local Deformation non viene ulteriormente estesa nello
Sprint 26 oltre le verifiche già completate.

---

## Milestone post-Sprint 26 — Project / Subject / Canonical Asset

Data: 25/08/2026

### Stato

[x] Stabilizzazione completata e verificata.

### Architettura

È stata consolidata la gestione delle elaborazioni tramite
`ReconstructionSubject`.

Il Project rimane il contenitore generale, mentre ogni Subject
rappresenta una specifica persona/elaborazione e mantiene
l'associazione alla propria Canonical Asset.

La struttura concettuale è:

    Project
       ↓
    ReconstructionSubject
       ├── source assets / fotografie
       └── Canonical Asset

Questo permette di mantenere nello stesso Project più soggetti
con Canonical Asset differenti.

### Canonical Asset Library

È stata integrata la selezione della Canonical Asset
durante la creazione di una nuova ricostruzione.

Il dialogo di nuova ricostruzione:

- carica le Canonical Asset disponibili;
- permette la selezione dell'asset;
- utilizza un asset di default se disponibile;
- conserva ID, tipo e versione dell'asset;
- permette di ricostruire l'associazione alla riapertura del Project.

### Persistenza

La relazione Subject → Canonical Asset viene serializzata
e ricostruita dal Project Loader.

Sono state verificate:

- creazione di una nuova ricostruzione;
- selezione della Canonical Asset;
- associazione al Subject;
- presenza delle fotografie del Subject;
- salvataggio del Project;
- chiusura dell'applicazione;
- riapertura del Project;
- conservazione dell'associazione;
- visualizzazione dell'associazione nel Project Panel;
- riapertura del Vertex Mapper;
- mantenimento del Canonical Mapping 25/25.

### Compatibilità

La modifica non altera il contratto geometrico esistente.

Restano invariati:

- Canonical Mesh;
- Canonical Mapping;
- Registration Engine;
- Global Alignment;
- Local Deformation;
- topologia;
- identità dei vertici.

---

## CONGELAMENTO — BASELINE 25/08/2026

Il progetto viene congelato nello stato corrente come baseline
prima dello Sprint 27.

La baseline comprende:

    Project
       ↓
    Subjects
       ↓
    Source Photos
       +
    Canonical Asset associata
       ↓
    Canonical Mapping 25/25
       ↓
    Registration
       ↓
    Global Alignment
       ↓
    Local Deformation
       ↓
    Personalized Mesh

Le migliorie residue dell'interfaccia utente non vengono affrontate
in questa milestone e saranno riprese successivamente senza
alterare l'architettura stabilizzata.

---

## Sprint 27 — DEVIAZIONE TECNICA

La roadmap originaria prevedeva Head Reconstruction.

Prima di procedere con la ricostruzione della testa completa,
è stata identificata una priorità geometrica:

    MediaPipe Face Surface
             ↕
    MakeHuman Canonical Face

La mesh MediaPipe viene mantenuta come riferimento facciale
geometrico.

La Canonical Mesh deve mantenere topologia e identità dei vertici,
adattando la propria geometria alla superficie facciale osservata.

Lo Sprint 27 viene quindi riallineato temporaneamente alla
correzione della geometria MediaPipe ↔ Canonical Mesh.

La Head Reconstruction viene posticipata fino alla stabilizzazione
di questo passaggio.

---

## Pulizia dei test sperimentali

I test utilizzati durante l'esplorazione della soluzione geometrica
sono stati classificati come diagnostici temporanei.

I seguenti file non fanno parte della baseline definitiva
e possono essere eliminati dal repository:

- test_mediapipe_to_canonical_surface_transfer.py
- test_mediapipe_to_canonical_surface_transfer_v2.py
- test_mediapipe_to_canonical_surface_transfer_v3.py
- test_mediapipe_to_canonical_surface_transfer_v4.py
- test_mediapipe_to_canonical_surface_transfer_v5.py
- test_mediapipe_to_canonical_surface_transfer_v6.py
- test_mediapipe_to_canonical_surface_transfer_v7.py
- test_mediapipe_canonical_face_surface_alignment.py
- test_mediapipe_canonical_surface_projection.py
- test_tps_components.py
- test_tps_displacement_field.py
- test_tps_distance_analysis.py
- test_tps_gaussian_influence_radius.py
- test_tps_influence_field.py
- test_tps_influence_radius.py
- test_tps_main_component.py
- test_real_local_deformation_sigma02.py

Questi test hanno avuto valore durante la ricerca e la diagnosi,
ma non rappresentano codice di produzione né una suite stabile
di regressione della baseline.

I test strutturali e di integrazione relativi a Canonical Asset,
Canonical Mapping, Registration, Global Alignment, Local Deformation
e Project/Canonical Asset vengono invece mantenuti.

---

## Stato finale della baseline

    BASELINE: 25/08/2026
    SPRINT 26: COMPLETATO
    ARCHITETTURA PROJECT/SUBJECT/CANONICAL ASSET: VERIFICATA
    CANONICAL MAPPING: 25/25 COMPLETE
    REGRESSIONI NOTE: NESSUNA
    SPRINT 27: DEVIAZIONE TECNICA PIANIFICATA
