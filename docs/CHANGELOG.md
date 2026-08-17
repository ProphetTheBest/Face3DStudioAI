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
