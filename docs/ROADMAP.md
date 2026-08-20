# Face3D Studio AI

## Roadmap Ufficiale del Progetto

---

Autore:
Marco Cantù

Technical Lead AI:
ChatGPT

Versione documento:
2.9

Ultimo aggiornamento:
20/08/2026

Stato:
Roadmap riallineato allo stato verificato del progetto dopo
la chiusura completa dello Sprint 26 — Local Deformation.

---

# 1. Visione del Progetto

Face3D Studio AI nasce con l'obiettivo di realizzare una piattaforma
professionale per la ricostruzione tridimensionale del volto umano
mediante Intelligenza Artificiale.

Il progetto utilizza attualmente MediaPipe Face Landmarker come motore
di rilevamento dei landmark facciali, ma l'architettura è stata progettata
per consentire in futuro l'integrazione di provider differenti senza
modificare la struttura principale dell'applicazione.

L'obiettivo del progetto non è semplicemente generare una FaceMesh
tridimensionale a partire da una fotografia.

L'obiettivo evolutivo è costruire una piattaforma capace di
ricostruire un modello 3D a partire, progressivamente, da:

    fotografia singola
    oppure
    video a 360°
    oppure
    più fotografie a 360° e da diverse angolazioni

attraverso una pipeline nella quale:

    input reale
          ↓
    rilevamento / estrazione delle informazioni geometriche
          ↓
    interpretazione anatomica o geometrica
          ↓
    registrazione rispetto a una mesh canonica
          ↓
    deformazione / ricostruzione
          ↓
    modello 3D completo
          ↓
    validazione
          ↓
    export
          ↓
    OBJ / STL / PLY / GLTF / FBX
          ↓
    stampa 3D

La componente fondamentale di questa nuova strategia è la costruzione
di una Canonical Mesh proprietaria di Face3D Studio.

---

# 2. Obiettivo strategico: Canonical Mesh

La principale evoluzione architetturale del progetto consiste nella
costruzione di una mesh canonica della testa umana.

La mesh canonica sarà basata sul modello MakeHuman selezionato come
template anatomico di riferimento.

Attualmente il progetto utilizza il template:

    male1591

e dispone di una variante specifica della testa:

    male1591_head.obj

Il template della testa contiene attualmente:

    1604 vertici
    3064 triangoli

La mesh MakeHuman non deve essere considerata semplicemente come un
modello 3D da visualizzare.

Deve diventare il riferimento geometrico stabile sul quale costruire
la corrispondenza anatomica con MediaPipe.

La sequenza prevista è:

    MakeHuman Head Mesh
             ↓
    selezione di punti anatomici
             ↓
    associazione manuale MediaPipe → Vertex
             ↓
    25 punti di controllo
             ↓
    registrazione geometrica
             ↓
    Canonical MakeHuman Mesh
             ↓
    deformazione guidata dai dati di un volto reale

La Canonical Mesh rappresenterà quindi la base geometrica comune
utilizzata dalle future procedure di ricostruzione.

---

# 3. MediaPipe e i 25 Landmark di controllo

MediaPipe Face Mesh dispone di una topologia molto più ampia rispetto
ai punti che è realistico associare manualmente alla mesh MakeHuman.

Il modello MediaPipe utilizzato dal progetto contiene 468 landmark
principali.

Il progetto non tenterà di associare manualmente tutti i 468 landmark
alla mesh MakeHuman.

Questa scelta sarebbe:

- eccessivamente onerosa;
- difficile da verificare manualmente;
- soggetta a errori;
- poco manutenibile;
- non necessaria per la registrazione iniziale.

Il progetto utilizzerà invece un insieme ridotto di landmark anatomici
di controllo.

Attualmente sono stati definiti 25 landmark standard.

I 25 landmark rappresentano punti anatomici strategici distribuiti tra:

- fronte;
- naso;
- occhi;
- bocca;
- sopracciglia;
- estremità e riferimenti principali del volto.

I 25 landmark NON rappresentano una riduzione dei 468 landmark.

Sono invece considerati:

    CONTROL POINTS

cioè punti di riferimento anatomici utilizzati per registrare
geometricamente la mesh MakeHuman rispetto al sistema MediaPipe.

---

# 4. Principio fondamentale della registrazione

Il sistema non dovrà interpretare i 25 punti come una mesh completa.

La funzione dei 25 punti sarà:

    25 landmark MediaPipe
             ↕
    25 vertici MakeHuman
             ↓
    vincoli geometrici
             ↓
    registrazione della mesh
             ↓
    deformazione/interpolazione
             ↓
    mesh completa

Il risultato finale dovrà essere una mesh MakeHuman completa della quale
sono conosciuti tutti i vertici originali e le loro coordinate.

I 25 punti costituiscono quindi una rete di controllo.

La geometria completa della mesh viene mantenuta.

---

# 5. MediaPipe Canonical Mesh e MakeHuman Canonical Mesh

Nel progetto devono essere mantenuti distinti due concetti.

## 5.1 MediaPipe Canonical Mesh

Il progetto contiene:

    source/resources/mediapipe/canonical_face_model.obj

Questo modello rappresenta il riferimento geometrico canonico
associato alla topologia MediaPipe.

Attualmente contiene:

    468 vertici
    898 facce

Questa mesh non deve essere confusa con la Canonical Mesh proprietaria
basata sul modello MakeHuman.

---

## 5.2 MakeHuman Canonical Mesh

La Canonical Mesh di Face3D Studio è stata costruita
sulla base del template MakeHuman.

Il suo riferimento iniziale è:

    male1591_head.obj

La mesh manterrà:

- tutti i vertici;
- tutte le facce;
- la topologia originale;
- l'identità dei vertici;
- le coordinate geometriche;
- la struttura necessaria alla successiva deformazione.

La registrazione MediaPipe → MakeHuman servirà a stabilire come
interpretare anatomicamente questa mesh.

---

# 6. Obiettivo della registrazione

La registrazione dovrà determinare una relazione geometrica stabile
tra:

    sistema MediaPipe

e:

    sistema MakeHuman

utilizzando i 25 punti di controllo.

Il primo livello previsto sarà una registrazione globale comprendente,
se necessario:

- traslazione;
- rotazione;
- scala.

Concettualmente:

    P_makehuman ≈ s · R · P_mediapipe + T

dove:

    P = punto 3D
    R = rotazione
    s = scala
    T = traslazione

Questa trasformazione costituirà il primo livello della registrazione.

---

# 7. Deformazione non rigida

Una semplice trasformazione rigida non sarà considerata sufficiente
come soluzione finale.

Un volto reale presenta differenze morfologiche rispetto al template
MakeHuman.

Tra queste:

- larghezza del volto;
- altezza del volto;
- forma della mandibola;
- posizione e dimensione del naso;
- distanza interpupillare;
- posizione degli occhi;
- forma della fronte;
- posizione del mento;
- proporzioni della bocca;
- profondità del volto.

I 25 landmark dovranno quindi essere utilizzati anche come vincoli
per una futura deformazione non rigida della mesh.

L'algoritmo definitivo di deformazione non viene considerato ancora
congelato.

Dovrà essere selezionato e validato sperimentalmente.

Tra le possibili famiglie di algoritmi da valutare:

- RBF;
- Thin Plate Spline;
- Laplacian deformation;
- ARAP;
- altre tecniche di mesh deformation compatibili con il progetto.

La scelta definitiva dovrà essere effettuata sulla base di:

- accuratezza;
- stabilità;
- preservazione della topologia;
- assenza di deformazioni patologiche;
- qualità del risultato;
- prestazioni;
- semplicità di integrazione nell'architettura.

---

# 8. Propagazione dei 25 punti alla mesh completa

Il risultato fondamentale della registrazione dovrà essere una
trasformazione applicabile all'intera mesh.

Il sistema dovrà quindi passare concettualmente da:

    25 vincoli

a:

    N vertici della mesh MakeHuman

dove N è il numero completo dei vertici del template.

Il sistema dovrà mantenere l'identità di ogni vertice.

Esempio:

    Vertex 0
    Vertex 1
    Vertex 2
    ...
    Vertex 1603

dovranno rimanere identificabili anche dopo la deformazione.

La deformazione modificherà le coordinate dei vertici, non la loro
identità.

---

# 9. Landmark MediaPipe completi

I 468 landmark MediaPipe continueranno a essere disponibili.

Non sarà necessario creare manualmente 468 associazioni.

Una volta costruita e registrata la Canonical Mesh, il sistema dovrà
poter determinare automaticamente la posizione dei landmark aggiuntivi
rispetto alla superficie della mesh.

La soluzione potrà utilizzare:

- ricerca del vertice più vicino;
- proiezione sulla superficie;
- faccia più vicina;
- coordinate baricentriche;
- altre rappresentazioni geometriche più accurate.

La soluzione definitiva dovrà essere scelta durante lo sviluppo
dell'algoritmo di registrazione.

È preferibile, ove possibile, utilizzare una rappresentazione
superficiale robusta rispetto all'associazione forzata di ogni
landmark a un singolo vertice.

---

# 10. Ruolo del Vertex Mapper

Il Vertex Mapper non rappresenta il prodotto finale.

È lo strumento di preparazione della Canonical Mesh.

Il suo compito è permettere all'operatore di costruire manualmente
le 25 corrispondenze fondamentali:

    MediaPipe Landmark
             ↕
    MakeHuman Vertex

Il lavoro manuale viene quindi eseguito una sola volta sulla mesh
canonica.

Una volta completate e salvate le 25 associazioni, il sistema potrà
utilizzarle per la registrazione automatica.

Il Vertex Mapper deve quindi essere considerato uno strumento
di calibrazione del sistema.

---

# 11. Stato attuale del Vertex Mapper

Il Vertex Mapper dispone già di:

- selezione dei 25 landmark;
- caricamento del template MakeHuman;
- MeshViewer dedicato;
- MeshPicker;
- selezione dei vertici;
- marker rosso del vertice corrente;
- marker azzurro del vertice già associato;
- associazione landmark → vertex;
- dissociazione;
- controllo dei duplicati;
- persistenza delle associazioni durante la sessione;
- pannello informativo del landmark;
- informazioni del vertice;
- report delle associazioni;
- mappa grafica MediaPipe;
- gestione di Mesh / Wire / Points;
- zoom;
- PAN;
- rotazione;
- illuminazione dedicata;
- riapertura della finestra senza perdita delle associazioni correnti.

Il Vertex Mapper è considerato consolidato e disponibile come
strumento di calibrazione della Canonical Mesh.

---

# 12. Architettura del Progetto

L'architettura del progetto rimane congelata.

La struttura fondamentale è:

    GUI
      ↓
    ApplicationController
      ↓
    Controllers
      ↓
    Services
      ↓
    Managers / Algorithms / Exporters
      ↓
    Models

Nessun componente deve saltare arbitrariamente i livelli.

La nuova funzionalità Canonical Mesh / Registration deve integrarsi
nell'architettura esistente.

---

# 13. Regola fondamentale della nuova pipeline

La GUI non deve contenere l'algoritmo di registrazione.

La GUI deve:

- mostrare i landmark;
- mostrare la mesh;
- consentire il picking;
- permettere l'associazione;
- visualizzare lo stato;
- richiamare i servizi appropriati.

La logica di registrazione dovrà appartenere a componenti dedicati.

Il modello dovrà contenere esclusivamente i dati.

Gli algoritmi dovranno essere indipendenti dalla GUI.

---

# 14. Struttura concettuale della nuova pipeline

La nuova pipeline evolutiva sarà:

    Fotografia reale
          ↓
    MediaPipe Face Landmarker
          ↓
    Face Analysis
          ↓
    Landmark 3D
          ↓
    25 landmark di controllo
          ↓
    Canonical Mesh Registration
          ↓
    MakeHuman Canonical Mesh
          ↓
    Deformazione guidata
          ↓
    Mesh del soggetto reale
          ↓
    Texture
          ↓
    Materiale
          ↓
    Export
          ↓
    OBJ / STL / PLY / GLTF / FBX

    # 15. Stato reale del progetto

Questa sezione descrive lo stato effettivamente raggiunto dal codice.

Il presente documento non considera completata una funzionalità
semplicemente perché esiste la relativa classe o infrastruttura.

Una funzionalità è considerata COMPLETATA solamente quando:

- è implementata;
- è integrata nell'architettura;
- è stata eseguita;
- è stata verificata;
- non presenta regressioni note.

Le componenti ancora predisposte ma non operative devono essere indicate
come IN SVILUPPO o INFRASTRUTTURA PRONTA.

---

# 16. Stato della pipeline AI

## Face Detection

Stato:

    STABILE

La pipeline di rilevamento dei volti è già integrata nell'applicazione.

---

## MediaPipe Face Landmarker

Stato:

    STABILE

Il progetto utilizza il modello:

    face_landmarker.task

Il provider MediaPipe è integrato nell'architettura AI.

---

## FaceAnalysisService

Stato:

    STABILE

Responsabilità:

- analisi del volto;
- landmark;
- FaceMesh;
- pose;
- blendshapes;
- dati necessari alle fasi successive.

---

## FaceMeshBuilder

Stato:

    STABILE

Costruisce la rappresentazione geometrica runtime
della FaceMesh.

---

# 17. Stato della geometria 3D

## FaceMesh

Stato:

    STABILE

La FaceMesh runtime rappresenta la geometria tridimensionale
del volto rilevato.

Contiene:

- Vertex3D;
- Triangle;
- Edge.

La FaceMesh non deve contenere logica AI o logica grafica.

---

## MeshViewer

Stato:

    STABILE E VERIFICATO

Il MeshViewer dispone attualmente di:

- visualizzazione Mesh;
- visualizzazione Wireframe;
- visualizzazione Points;
- rotazione;
- zoom;
- PAN;
- viste camera;
- reset camera;
- picking;
- selezione del vertice;
- marker del vertice;
- gestione del rendering OpenGL;
- illuminazione dedicata per il Vertex Mapper.

La versione di riferimento attuale è:

    MeshViewer 3.2.6

Il viewer è stato inoltre verificato nel contesto del Vertex Mapper
per evitare la perdita dei marker durante il cambio:

    Mesh → Wire → Points → Mesh

---

# 18. Stato del MakeHuman Template

Il progetto dispone di un sistema dedicato al caricamento
dei template anatomici.

Componenti principali:

    HeadTemplate
    TemplateLoader
    ObjTemplateLoader
    TemplateAnalyzer

Il template MakeHuman utilizzato per la costruzione della Canonical Mesh
è:

    male1591

Il progetto dispone inoltre della geometria specifica della testa:

    male1591_head.obj

La testa MakeHuman costituisce il riferimento geometrico
per la futura Canonical Mesh.

---

# 19. Stato del Template Loader

## TemplateLoader

Stato:

    OPERATIVO

Il loader permette di caricare il template MakeHuman
all'interno della pipeline di ricostruzione.

Il Vertex Mapper utilizza il template:

    male1591
    part = head

per lavorare sulla geometria della testa.

---

# 20. Stato del Template Analyzer

## TemplateAnalyzer

Stato:

    INFRASTRUTTURA DISPONIBILE

Il componente è stato introdotto per permettere
l'analisi geometrica e topologica del template.

Le analisi future dovranno essere utilizzate per:

- individuazione delle regioni anatomiche;
- identificazione dei vertici;
- analisi dei boundary;
- supporto alla registrazione;
- supporto alla deformazione;
- validazione della mesh canonica.

Il TemplateAnalyzer non deve contenere la logica della GUI.

---

# 21. Stato dei Landmark

## LandmarkCatalog

Stato:

    OPERATIVO

Il catalogo rappresenta l'insieme dei landmark
utilizzati da Face3D Studio.

---

## Standard Landmarks

Stato:

    OPERATIVO

Il progetto dispone di:

    25 landmark standard

Questi landmark rappresentano i punti di controllo
utilizzati per la costruzione della Canonical Mesh.

Non rappresentano tutti i 468 landmark MediaPipe.

---

# 22. I 25 Control Points

I 25 landmark standard costituiscono il set iniziale
di punti anatomici utilizzati per la registrazione.

La loro funzione è:

    MediaPipe
        ↓
    landmark anatomico
        ↓
    associazione manuale
        ↓
    vertice MakeHuman

Il risultato dovrà essere una collezione di 25
corrispondenze affidabili.

La qualità di queste 25 associazioni è fondamentale.

Non devono essere scelti solamente perché facili da individuare.

Devono essere scelti perché:

- anatomicamente significativi;
- distribuiti sul volto;
- sufficientemente stabili;
- utili alla registrazione globale;
- utili alla deformazione locale.

---

# 23. Stato del Vertex Mapping

## VertexMapping

Stato:

    OPERATIVO

Il modello rappresenta una singola associazione:

    MediaPipe Landmark
             ↕
    MakeHuman Vertex

Il mapping contiene concettualmente:

- landmark_index;
- landmark_name;
- vertex_index;
- Vertex3D.

---

## VertexMappingCollection

Stato:

    OPERATIVO

La collection rappresenta l'insieme delle associazioni.

Responsabilità:

- aggiungere mapping;
- rimuovere mapping;
- cercare mapping;
- verificare duplicazioni;
- contare mapping;
- gestire la relazione landmark → vertex.

La collection deve impedire:

    stesso landmark → due vertici

e:

    stesso vertice → due landmark

Questa regola è fondamentale per la costruzione
della Canonical Mesh.

---

# 24. Vertex Mapper

Il Vertex Mapper è lo strumento utilizzato per costruire
manualmente le associazioni tra i Control Points MediaPipe
e i vertici della Canonical Mesh MakeHuman.

Il suo scopo è limitare il lavoro manuale ai 25 Control Points
selezionati, evitando l'associazione manuale di tutti i
landmark MediaPipe.

La relazione fondamentale è:

    MediaPipe Control Point
            ↕
    MakeHuman Vertex

Il mapping prodotto dal Vertex Mapper costituisce la base
per la successiva costruzione del Canonical Mapping.

---

## Versione di riferimento

Versione corrente:

    VertexMapperDialog 1.8.0

La versione 1.8.0 comprende l'integrazione con la
mappa grafica interattiva dei landmark MediaPipe e
la visualizzazione dei mapping tramite filtri anatomici.

---

## Funzionalità implementate

Il Vertex Mapper attualmente supporta:

- selezione del landmark dalla ComboBox;
- visualizzazione delle informazioni del landmark corrente;
- selezione manuale del vertice sulla mesh;
- associazione landmark → vertice;
- dissociazione di un'associazione esistente;
- protezione dalle associazioni duplicate;
- visualizzazione del vertice associato;
- evidenziazione del vertice associato;
- distinzione visuale tra selezione temporanea e associazione;
- marker azzurro per i vertici associati;
- marker rosso per la selezione temporanea;
- mantenimento delle associazioni durante la sessione;
- mantenimento delle associazioni alla chiusura e riapertura
  della finestra del Vertex Mapper;
- compatibilità con le modalità Mesh, Wireframe e Point;
- gestione della rotazione del modello;
- gestione dello zoom;
- gestione del PAN;
- gestione della camera;
- gestione dell'illuminazione;
- report delle associazioni;
- visualizzazione della mappa MediaPipe;
- selezione interattiva dei Control Points dalla mappa;
- filtro di visualizzazione per landmark corrente;
- visualizzazione di tutti i landmark associati;
- visualizzazione dei mapping per gruppo anatomico;
- gruppi anatomici: Volto, Naso, Occhio destro, Occhio sinistro,
  Bocca, Sopracciglio destro e Sopracciglio sinistro;
- aggiornamento dinamico dei marker in base al filtro selezionato.

---

## Workflow di associazione

Il workflow previsto è:

    selezione Control Point
            ↓
    visualizzazione informazioni
            ↓
    selezione vertice MakeHuman
            ↓
    verifica visiva
            ↓
    Associa
            ↓
    mapping creato

Quando il Control Point è già associato:

    selezione Control Point
            ↓
    visualizzazione del vertice associato
            ↓
    Associa = DISABILITATO
    Dissocia = ABILITATO

Questo impedisce di creare accidentalmente
una seconda associazione per lo stesso landmark.

---

## Dissociazione

La dissociazione è una funzionalità esplicita.

Workflow:

    Control Point associato
            ↓
    selezione
            ↓
    visualizzazione vertice associato
            ↓
    Dissocia
            ↓
    Control Point non associato

Dopo la dissociazione il Control Point torna
disponibile per una nuova associazione.

---

## Visualizzazione dello stato

Il Vertex Mapper distingue visualmente:

    selezione temporanea
            ↓
        marker rosso

    associazione esistente
            ↓
        marker azzurro

Questo permette di evitare che la selezione utilizzata
durante il picking venga confusa con un'associazione
già presente.

Il marker dell'associazione deve inoltre poter essere
ripristinato quando il landmark viene nuovamente selezionato.

---

## Mappa MediaPipe

Il Vertex Mapper dispone di una mappa grafica dei
landmark MediaPipe.

La mappa rappresenta visivamente la distribuzione
dei landmark MediaPipe e viene utilizzata come supporto
durante la costruzione delle 25 associazioni.

La mappa non sostituisce la selezione del vertice
sulla Canonical Mesh.

Il suo scopo è aiutare l'operatore a identificare
correttamente il Control Point MediaPipe da associare.

---

## Mappa MediaPipe interattiva

La mappa è stata resa interattiva.

Sono interattivi esclusivamente i 25 Control Points
utilizzati dal Canonical Mapping.

Il comportamento è:

    click sulla mappa
            ↓
    coordinate immagine
            ↓
    ricerca Control Point più vicino
            ↓
    landmark identificato
            ↓
    evidenziazione del punto

La selezione utilizza le coordinate dell'immagine
originale, indipendentemente dalle dimensioni
della finestra.

Questo permette di mantenere corretta la selezione
anche quando la finestra viene ridimensionata.

---

## Filtri anatomici dei mapping

La versione 1.8.0 introduce una modalità di visualizzazione
filtrata dei mapping già presenti nella VertexMappingCollection.

La ComboBox di visualizzazione supporta ora:

    Nessuno
    Solo landmark corrente
    Tutti i landmark associati
    Volto
    Naso
    Occhio destro
    Occhio sinistro
    Bocca
    Sopracciglio destro
    Sopracciglio sinistro

I filtri anatomici non modificano le associazioni e non introducono
una seconda sorgente dei dati. Il filtro opera esclusivamente
sulla visualizzazione dei marker già presenti nella collection.

La classificazione anatomica utilizza i nomi semantici dei
LandmarkDefinition già definiti dal progetto. In questo modo
la GUI non duplica gli indici MediaPipe e rimane coerente
con il LandmarkCatalog.

Il filtro è particolarmente utile durante la costruzione
e la verifica progressiva delle 25 associazioni, perché permette
di isolare una regione anatomica senza nascondere o modificare
i mapping esistenti.

### Gruppi attualmente disponibili

    Volto
        forehead_center
        chin

    Naso
        nose_tip
        nose_bridge
        nose_lower_center
        nose_left_base
        nose_right_base

    Occhio destro
        right_eye_outer
        right_eye_inner
        right_eye_upper
        right_eye_lower

    Occhio sinistro
        left_eye_outer
        left_eye_inner
        left_eye_upper
        left_eye_lower

    Bocca
        mouth_left
        mouth_right
        upper_lip_center
        lower_lip_center
        upper_lip_left
        upper_lip_right

    Sopracciglio destro
        right_eyebrow_inner
        right_eyebrow_outer

    Sopracciglio sinistro
        left_eyebrow_inner
        left_eyebrow_outer

Il filtro deve essere considerato uno strumento di verifica
visiva e non una modifica del modello di mapping.

---

## Sincronizzazione Mappa ↔ ComboBox

La mappa e la ComboBox del Vertex Mapper
sono sincronizzate.

### ComboBox → Mappa

Quando viene selezionato un Control Point
dalla ComboBox:

    ComboBox
        ↓
    landmark corrente
        ↓
    mappa
        ↓
    evidenziazione del landmark

### Mappa → ComboBox

Quando viene selezionato un Control Point
direttamente dalla mappa:

    click mappa
        ↓
    landmark identificato
        ↓
    ComboBox aggiornata
        ↓
    normale gestione del landmark corrente

La selezione dalla mappa utilizza quindi
lo stesso workflow già utilizzato dalla ComboBox.

---

## Control Points

Il Vertex Mapper lavora esclusivamente sui
25 Control Points definiti dal catalogo standard
del progetto.

Non è previsto che l'operatore associ manualmente
tutti i 468/478 landmark MediaPipe.

I 25 Control Points costituiscono una rete
di vincoli geometrici iniziali.

---

## Obiettivo del Vertex Mapper

Il risultato finale del Vertex Mapper non è
la Personalized Mesh.

Il risultato è:

    25 associazioni validate

tra:

    MediaPipe
        ↕
    Canonical Mesh MakeHuman

Queste associazioni saranno successivamente
utilizzate dal Canonical Mapping e dal
Registration Engine.

---

## Stato

Vertex Mapper:

    COMPLETATO

Mappa MediaPipe interattiva:

    COMPLETATA

Sincronizzazione Mappa ↔ ComboBox:

    COMPLETATA

Associazione:

    COMPLETATA

Dissociazione:

    COMPLETATA

Visualizzazione dei punti associati:

    COMPLETATA

Workflow Mesh / Wireframe / Point:

    COMPLETATO

Zoom / PAN / Camera:

    COMPLETATO

Report:

    COMPLETATO

Persistenza del Canonical Mapping su file:

    COMPLETATA E VERIFICATA

---

## Prossimo obiettivo

Il prossimo lavoro non consiste più
nel migliorare il meccanismo di selezione
del Vertex Mapper.

Il prossimo obiettivo è completare la fase
di costruzione del Canonical Mapping:

    Vertex Mapper
          ↓
    25 associazioni
          ↓
    Canonical Mapping
          ↓
    validazione
          ↓
    persistenza
          ↓
    utilizzo nel Registration Engine

## VertexMapperDialog

Stato:

    COMPLETATO

Versione di riferimento:

    VertexMapperDialog 1.6.4

Il Vertex Mapper rappresenta lo strumento manuale
di calibrazione della Canonical Mesh.

La GUI deve occuparsi esclusivamente di:

- interazione;
- visualizzazione;
- selezione landmark;
- selezione vertice;
- visualizzazione informazioni;
- richiesta di associazione;
- richiesta di dissociazione;
- interazione con la mappa MediaPipe.

La logica dei dati deve rimanere nei Models.

La versione 1.6.4 comprende inoltre
la sincronizzazione bidirezionale tra:

    Vertex Mapper
          ↕
    Mappa MediaPipe

La mappa permette di identificare
i 25 Control Points e di sincronizzare
la selezione del landmark con il Vertex Mapper.

---

# 25. Funzionalità già verificate del Vertex Mapper

Sono state verificate:

- caricamento del template MakeHuman;
- visualizzazione della testa;
- picking dei vertici;
- selezione del vertice;
- marker rosso;
- associazione;
- dissociazione;
- controllo delle associazioni duplicate;
- stato del pulsante Associa;
- stato del pulsante Dissocia;
- marker azzurro dei vertici associati;
- persistenza delle associazioni durante il lavoro;
- selezione di landmark già associati;
- visualizzazione del vertice associato;
- cambio Mesh / Wire / Points;
- mantenimento del marker associato durante il cambio modalità;
- zoom;
- PAN;
- rotazione;
- riapertura della finestra;
- illuminazione della mesh;
- report delle associazioni.

---

# 26. Mappa grafica MediaPipe

Il progetto dispone ora di una finestra separata:

    MediaPipeLandmarkMapDialog

Stato:

    OPERATIVA E INTERATTIVA

La mappa grafica viene utilizzata come riferimento visivo
per comprendere la distribuzione dei landmark MediaPipe
e per facilitare l'identificazione dei 25 Control Points
utilizzati dal Vertex Mapper.

La mappa non modifica direttamente:

- mesh;
- VertexMappingCollection;
- picking della mesh;
- camera;
- associazioni landmark → vertice.

La mappa comunica invece con il Vertex Mapper
attraverso la selezione del Control Point.

---

## Interazione con la mappa

La mappa consente di selezionare direttamente
i 25 Control Points utilizzati dal progetto.

Il workflow è:

    click sulla mappa
            ↓
    coordinate dell'immagine
            ↓
    ricerca del Control Point più vicino
            ↓
    landmark identificato
            ↓
    evidenziazione del punto

La selezione utilizza le coordinate dell'immagine
originale e rimane corretta anche quando
la finestra viene ridimensionata.

---

## Control Points interattivi

Non tutti i landmark rappresentati nella mappa
sono utilizzabili direttamente nel Vertex Mapper.

Sono interattivi esclusivamente i 25 Control Points
definiti dal catalogo standard del progetto.

Gli altri landmark rimangono disponibili
come riferimento grafico e anatomico.

Questo mantiene distinta la rappresentazione
completa dei landmark MediaPipe dal sottoinsieme
di Control Points utilizzato per la costruzione
del Canonical Mapping.

---

## Evidenziazione

Quando un Control Point viene selezionato,
il punto corrispondente viene evidenziato
sulla mappa.

L'evidenziazione viene mantenuta correttamente
anche dopo il ridimensionamento della finestra.

Il punto selezionato rimane quindi coerente
con le coordinate dell'immagine originale,
indipendentemente dalle dimensioni con cui
la mappa viene visualizzata.

---

## Sincronizzazione con il Vertex Mapper

La mappa e la ComboBox del Vertex Mapper
sono sincronizzate in entrambe le direzioni.

### ComboBox → Mappa

Quando l'utente seleziona un Control Point
dalla ComboBox:

    ComboBox
        ↓
    landmark corrente
        ↓
    mappa
        ↓
    Control Point evidenziato

La mappa viene quindi aggiornata
in base al landmark attualmente selezionato
nel Vertex Mapper.

### Mappa → ComboBox

Quando l'utente seleziona un Control Point
direttamente dalla mappa:

    click sulla mappa
            ↓
    Control Point identificato
            ↓
    ComboBox aggiornata
            ↓
    normale workflow del Vertex Mapper

La selezione effettuata dalla mappa utilizza
quindi la stessa gestione del landmark già
presente nel Vertex Mapper.

Non viene introdotta una seconda logica
indipendente per la gestione del landmark.

---

## Funzione della mappa nel workflow

La mappa non sostituisce il MeshViewer.

Il suo compito è aiutare l'operatore a identificare
correttamente il Control Point MediaPipe da associare.

Il MeshViewer rimane invece lo strumento utilizzato
per individuare il vertice corrispondente
sulla Canonical Mesh MakeHuman.

Il workflow complessivo diventa:

    Mappa MediaPipe
           ↓
    Control Point
           ↓
    Vertex Mapper
           ↓
    MeshViewer
           ↓
    Vertice MakeHuman
           ↓
    Associazione

La separazione dei due strumenti consente di mantenere
distinte:

- identificazione del landmark MediaPipe;
- selezione del vertice MakeHuman;
- creazione dell'associazione.

---

## Selezione tramite coordinate

Il widget interattivo della mappa converte
le coordinate del click dalla superficie
visualizzata alle coordinate dell'immagine originale.

Questo permette di mantenere corretta
l'identificazione del Control Point anche quando:

- la finestra viene ridimensionata;
- l'immagine viene scalata;
- vengono modificate le dimensioni dell'area grafica.

Il riconoscimento del Control Point utilizza
una tolleranza spaziale che facilita il click
dell'operatore senza richiedere una precisione
al singolo pixel.

---

## Verifica della funzionalità

La mappa interattiva è stata verificata mediante:

- selezione di diversi Control Points;
- verifica dell'indice MediaPipe;
- verifica dell'evidenziazione;
- click leggermente decentrati rispetto al punto;
- click in aree prive di Control Points;
- ridimensionamento della finestra;
- ripetizione della selezione dopo il resize;
- verifica della corretta posizione del marker;
- selezione dalla ComboBox;
- selezione direttamente dalla mappa;
- sincronizzazione Mappa → ComboBox;
- sincronizzazione ComboBox → Mappa.

Tutti i test previsti sono stati superati.

---

## Stato

Mappa grafica:

    COMPLETATA

Interazione:

    COMPLETATA

Selezione dei 25 Control Points:

    COMPLETATA

Evidenziazione:

    COMPLETATA

Sincronizzazione Mappa → ComboBox:

    COMPLETATA

Sincronizzazione ComboBox → Mappa:

    COMPLETATA

Verifica del ridimensionamento:

    COMPLETATA

Verifica della tolleranza di selezione:

    COMPLETATA

---

# 27. Evoluzione della mappa MediaPipe

La mappa MediaPipe è stata inizialmente introdotta
come componente puramente informativo per consentire
all'operatore di comprendere la distribuzione dei
landmark MediaPipe.

L'evoluzione successiva ha trasformato la mappa
in uno strumento interattivo integrato nel workflow
del Vertex Mapper.

---

## Funzionalità implementate

La mappa supporta ora:

- selezione interattiva dei 25 Control Points;
- riconoscimento del Control Point più vicino
  alla posizione del click;
- evidenziazione del Control Point selezionato;
- conversione corretta delle coordinate tra
  immagine originale e immagine visualizzata;
- mantenimento della posizione del marker
  durante il ridimensionamento della finestra;
- sincronizzazione con la ComboBox del Vertex Mapper.

---

## Sincronizzazione bidirezionale

La sincronizzazione è stata implementata
in entrambe le direzioni.

### ComboBox → Mappa

La selezione di un Control Point nella ComboBox
aggiorna la mappa e ne evidenzia il punto
corrispondente.

### Mappa → ComboBox

La selezione di un Control Point direttamente
sulla mappa aggiorna la ComboBox del Vertex Mapper.

La modifica utilizza il normale workflow
di gestione del landmark già presente
nel Vertex Mapper.

Non viene quindi introdotta una seconda
gestione indipendente dello stato del landmark.

---

## Limitazione ai 25 Control Points

La mappa grafica continua a rappresentare
la distribuzione completa dei landmark MediaPipe.

Tuttavia, ai fini dell'interazione con il
Vertex Mapper, vengono utilizzati esclusivamente
i 25 Control Points definiti dal catalogo standard
del progetto.

Questa scelta mantiene separati:

- rappresentazione completa dei landmark;
- Control Points utilizzati per il Canonical Mapping;
- vertici MakeHuman della Canonical Mesh.

---

## Obiettivo raggiunto

La mappa non è più soltanto una documentazione
grafica.

È diventata uno strumento operativo del
Vertex Mapper che permette all'utente di passare
direttamente da:

    riferimento anatomico MediaPipe

a:

    Control Point MediaPipe

e successivamente:

    vertice corrispondente sulla Canonical Mesh.

Il workflow completo è quindi:

    Mappa MediaPipe
          ↓
    Control Point
          ↓
    Vertex Mapper
          ↓
    MeshViewer
          ↓
    Vertice MakeHuman
          ↓
    Associazione

---

## Stato

Mappa MediaPipe:

    COMPLETATA

Interazione:

    COMPLETATA

Selezione dei 25 Control Points:

    COMPLETATA

Sincronizzazione bidirezionale:

    COMPLETATA

Test funzionali:

    COMPLETATI

La mappa è pertanto considerata parte
integrata del workflow del Vertex Mapper.

La mappa attualmente viene visualizzata
in una finestra separata.

---

# 28. Stato della persistenza

Le associazioni create nel Vertex Mapper devono essere
mantenute anche quando l'operatore chiude e riapre
la finestra di lavoro.

La persistenza temporanea della sessione è stata verificata.

La persistenza definitiva su file del Canonical Mapping
è stata implementata e verificata.

Il mapping viene integrato nel Project e viene salvato
nel project.json tramite la normale pipeline di persistenza
del progetto.

È stata inoltre verificata la ricostruzione del mapping
alla riapertura del progetto.

---

# 29. Salvataggio della Canonical Mapping

Il sistema permette di salvare il Canonical Mapping
all'interno della persistenza del progetto.

Il formato utilizzato è JSON, integrato nel file
project.json del progetto.

Il modello CanonicalMapping è indipendente dalla GUI
e viene serializzato tramite ProjectSerializer.

Il file contiene almeno:

- identificativo del template;
- versione del template;
- identificativo della mesh;
- indice MediaPipe;
- nome landmark;
- indice del vertice MakeHuman;
- coordinate del vertice;
- informazioni necessarie alla validazione.

Concettualmente:

    Canonical Mesh
          +
    Vertex Mapping
          ↓
    Canonical Mapping File

Il file dovrà poter essere ricaricato
senza ripetere il lavoro manuale.

---

# 30. Stato della Registration Architecture

Il progetto dispone già di una prima infrastruttura
per la registrazione.

Componenti concettuali:

    RegistrationPoint
    TemplateRegistration
    RegistrationLoader

Questi componenti rappresentano la base futura
del sistema di registrazione.

Stato:

    INFRASTRUTTURA PRONTA
    ALGORITMO NON ANCORA IMPLEMENTATO

Non deve essere considerata completata
la registrazione anatomica.

---

# 31. Stato della Head Reconstruction Pipeline

Il progetto dispone già di:

    HeadReconstructionPipeline

e:

    HeadReconstructionBuilder

La pipeline carica il template MakeHuman
e delega la ricostruzione al builder.

Stato:

    INFRASTRUTTURA OPERATIVA
    RICOSTRUZIONE NON ANCORA IMPLEMENTATA

Il builder attuale esegue principalmente
le prime analisi topologiche.

Non costituisce ancora l'algoritmo definitivo
di ricostruzione della testa.

---

# 32. Distinzione fondamentale

Il progetto deve mantenere separati:

    A. preparazione della Canonical Mesh

e:

    B. ricostruzione del volto reale

La preparazione consiste in:

    MakeHuman
       ↓
    25 landmark
       ↓
    25 vertex mapping
       ↓
    Canonical Mesh

La ricostruzione consiste in:

    fotografia reale
       ↓
    MediaPipe
       ↓
    landmark reali
       ↓
    registrazione
       ↓
    deformazione della Canonical Mesh
       ↓
    testa reale

Non bisogna anticipare la fase B
prima di aver stabilizzato la fase A.

---

# 33. Stato della ricostruzione completa della testa

La ricostruzione completa della testa MakeHuman
non è ancora completata.

Sono previste future operazioni per:

- lati della testa;
- cranio;
- nuca;
- orecchie;
- collo;
- chiusura dei boundary;
- eventuale simmetria;
- generazione di una mesh watertight.

Lo sviluppo di queste funzionalità dovrà essere
coordinato con la costruzione della Canonical Mesh.

---

# 34. Stato della pipeline di registrazione

La pipeline futura dovrà essere:

    25 MediaPipe Control Points
                 ↓
    25 MakeHuman Vertex
                 ↓
          Registration
                 ↓
        Global Alignment
                 ↓
       Local Deformation
                 ↓
        Complete Mesh
                 ↓
      Canonical Subject Mesh

L'algoritmo non è ancora stato implementato.

La scelta definitiva dell'algoritmo deve essere effettuata
dopo il completamento e la validazione dei 25 mapping.

---

# 35. Stato dell'esportazione

## FaceExportService

Stato:

    STABILE

Coordina l'esportazione dei dati 3D.

---

## ObjExporter

Stato:

    STABILE

Verificato con Blender.

---

## TextureExporter

Stato:

    STABILE

Versione attuale:

    copia della fotografia originale

---

## MaterialExporter

Stato:

    STABILE

Produce il materiale MTL associato all'OBJ.

---

# 36. Formati futuri

Sono previsti:

    STL
    PLY
    GLTF
    FBX

Questi formati saranno implementati
dopo la stabilizzazione della Canonical Mesh
e della pipeline di ricostruzione.

---

# 37. Stato generale

Alla data di questo aggiornamento:

    PIPELINE AI
        STABILE

    FACE MESH
        STABILE

    MESH VIEWER
        STABILE

    MAKEHUMAN TEMPLATE
        OPERATIVO

    LANDMARK CATALOG
        OPERATIVO

    25 CONTROL POINTS
        DEFINITI

    VERTEX MAPPING
        OPERATIVO

    VERTEX MAPPER
        COMPLETATO

    MEDIAPIPE LANDMARK MAP
        OPERATIVA E INTERATTIVA

    REGISTRATION
        INFRASTRUTTURA PRONTA
        ALGORITMO DA IMPLEMENTARE

    CANONICAL MESH
        COMPLETATA — Sprint 22
        1604 vertici / 3064 triangoli

    HEAD RECONSTRUCTION
        INFRASTRUTTURA PRONTA
        ALGORITMO DA IMPLEMENTARE

    TEXTURE / OBJ EXPORT
        STABILE

    RICOSTRUZIONE DA FOTOGRAFIA
        NON ANCORA COMPLETATA

---

# 38. Regola di avanzamento della nuova fase

Prima di implementare la registrazione automatica:

    1. completare e validare i 25 mapping;
    2. salvare i mapping;
    3. costruire il formato Canonical Mapping;
    4. testare il caricamento;
    5. solo successivamente implementare Registration;
    6. validare l'allineamento;
    7. implementare la deformazione;
    8. generare la prima Canonical Mesh completa.

La sequenza non deve essere invertita.

---

# 39. ROADMAP OPERATIVA — NUOVA FASE

A partire dallo stato raggiunto con lo Sprint 17.1,
il progetto entra nella fase di costruzione della
Canonical Mesh e della pipeline di ricostruzione.

La nuova fase non deve essere considerata una semplice
continuazione lineare degli Sprint precedenti.

Rappresenta il passaggio da:

    visualizzazione / analisi / mapping

a:

    ricostruzione geometrica reale.

---

# 40. Obiettivo della nuova fase

L'obiettivo principale è costruire una pipeline capace di trasformare:

    Face reale
        ↓
    MediaPipe Landmarks
        ↓
    Landmark anatomici
        ↓
    Canonical Mesh
        ↓
    Registrazione
        ↓
    Deformazione
        ↓
    Mesh 3D personalizzata

Il primo risultato concreto da ottenere non sarà
la ricostruzione automatica da fotografia.

Sarà invece:

    una Canonical Mesh MakeHuman
    correttamente associata ai 25 landmark.

Solo dopo questo risultato sarà possibile
sviluppare la registrazione automatica.

---

# 41. Nuova sequenza degli Sprint

La sequenza prevista è:

    Sprint 18
        Stabilizzazione definitiva del Vertex Mapper

    Sprint 19
        Completamento dei 25 Control Points

    Sprint 20
        Canonical Mapping Model

    Sprint 21
        Salvataggio e caricamento del Mapping

    Sprint 22
        Canonical Mesh Builder

    Sprint 23
        Validazione geometrica della Canonical Mesh — COMPLETATO

    Sprint 24
        Registration Engine

    Sprint 25
        Global Alignment

    Sprint 26
        Local Deformation

    Sprint 27
        Head Reconstruction

    Sprint 28
        Complete Head Mesh

    Sprint 29
        Texture Projection

    Sprint 30
        Reconstruction Pipeline

    Sprint 31
        Ricostruzione da fotografia singola

    Sprint 32
        Validazione e confronto

Questa sequenza potrà essere modificata solamente
se durante l'implementazione emerge una reale
necessità tecnica.

---

# 42. Sprint 18 — Vertex Mapper Stabilization

## Obiettivo

Portare il Vertex Mapper a una versione definitiva
e utilizzabile come strumento di calibrazione manuale
per la costruzione del mapping tra i Control Points
MediaPipe e i vertici della Canonical Mesh MakeHuman.

Lo Sprint comprende sia la stabilizzazione del workflow
di associazione sia gli strumenti visivi necessari
per facilitare l'identificazione dei 25 Control Points.

---

## Attività

Sono state verificate e consolidate le seguenti funzionalità:

- selezione landmark;
- selezione vertice;
- picking;
- associazione;
- dissociazione;
- prevenzione delle associazioni duplicate;
- sostituzione controllata dell'associazione;
- marker;
- distinzione tra selezione temporanea e associazione;
- visualizzazione del vertice associato;
- report;
- gestione della VertexMappingCollection;
- apertura;
- chiusura;
- riapertura;
- mantenimento delle associazioni durante le sessioni;
- cambio modalità rendering;
- Mesh;
- Wireframe;
- Point;
- camera;
- reset della camera;
- zoom;
- PAN;
- rotazione;
- gestione dell'illuminazione;
- visualizzazione corretta del modello dopo la riapertura;
- mantenimento della selezione dei punti associati;
- visualizzazione del punto associato durante la revisione;
- mappa grafica MediaPipe;
- interazione con la mappa MediaPipe;
- selezione dei 25 Control Points dalla mappa;
- evidenziazione del Control Point selezionato;
- sincronizzazione ComboBox → Mappa;
- sincronizzazione Mappa → ComboBox;
- mantenimento della corretta posizione dei marker
  durante il ridimensionamento della finestra;
- verifica della tolleranza di selezione sulla mappa;
- filtro di visualizzazione del mapping corrente;
- visualizzazione di tutti i mapping associati;
- filtri anatomici dei mapping;
- verifica dei gruppi Volto, Naso, Occhio destro, Occhio sinistro,
  Bocca, Sopracciglio destro e Sopracciglio sinistro;
- verifica che i filtri modifichino esclusivamente la visualizzazione
  senza modificare la VertexMappingCollection.

---

## Mappa MediaPipe

Durante lo Sprint è stata completata l'integrazione
della mappa grafica MediaPipe nel workflow
del Vertex Mapper.

La mappa è disponibile in una finestra separata:

    MediaPipeLandmarkMapDialog

e rappresenta un supporto visivo per l'identificazione
dei Control Points MediaPipe.

La mappa non modifica direttamente:

- mesh;
- picking della mesh;
- camera;
- VertexMappingCollection;
- associazioni landmark → vertice.

La mappa comunica invece con il Vertex Mapper
attraverso la selezione del landmark.

---

## Interazione con la mappa

Sono stati resi interattivi esclusivamente
i 25 Control Points utilizzati dal progetto.

Il workflow è:

    click sulla mappa
            ↓
    coordinate immagine originale
            ↓
    ricerca del Control Point più vicino
            ↓
    landmark identificato
            ↓
    evidenziazione
            ↓
    selezione del landmark nel Vertex Mapper

La selezione utilizza una tolleranza spaziale
per facilitare il click dell'operatore.

---

## Sincronizzazione Mappa ↔ ComboBox

La sincronizzazione è bidirezionale.

### ComboBox → Mappa

La selezione di un Control Point dalla ComboBox
aggiorna la mappa e ne evidenzia il punto
corrispondente.

### Mappa → ComboBox

La selezione di un Control Point dalla mappa
aggiorna automaticamente la ComboBox
del Vertex Mapper.

La selezione utilizza il normale workflow
di gestione del landmark già presente
nel Vertex Mapper.

---

## Verifica del comportamento dopo riapertura

È stato verificato che la chiusura e la successiva
riapertura della finestra del Vertex Mapper
non comportano la perdita delle associazioni
effettuate durante il lavoro.

Le associazioni già presenti rimangono disponibili
per la successiva revisione.

Quando viene selezionato nuovamente un Control Point
già associato, il vertice corrispondente viene
visualizzato e identificato come associazione esistente.

---

## Verifica delle modalità di rendering

È stato verificato il comportamento della selezione
e dei marker durante il passaggio tra:

    Mesh
    Wireframe
    Point

La selezione del landmark associato rimane coerente
anche dopo il cambio della modalità di visualizzazione.

---

## Verifica camera, zoom e PAN

È stato verificato il comportamento del Vertex Mapper
durante:

- rotazione del modello;
- zoom;
- PAN;
- reset della camera;
- modifica delle dimensioni della finestra.

Il sistema mantiene la corretta visualizzazione
del modello e dei punti selezionati.

---

## Risultato

Il Vertex Mapper è ora sufficientemente stabile
per essere utilizzato come strumento di calibrazione
manuale.

La versione di riferimento consolidata è la 1.8.0.
Oltre al workflow di associazione e alla mappa MediaPipe
interattiva, il Vertex Mapper dispone ora di filtri anatomici
per la revisione progressiva dei mapping.

Il workflow completo è:

    selezione Control Point
            ↓
    verifica anatomica tramite mappa MediaPipe
            ↓
    selezione del vertice MakeHuman
            ↓
    verifica visiva
            ↓
    associazione
            ↓
    eventuale revisione
            ↓
    eventuale dissociazione
            ↓
    associazione definitiva

---

## Criterio di completamento

Lo Sprint è completato quando:

    Vertex Mapper
        +
    MeshViewer
        +
    VertexMappingCollection
        +
    MediaPipeLandmarkMapDialog

funzionano senza regressioni e consentono
di costruire e verificare manualmente
le associazioni dei 25 Control Points.

---

## Stato

    COMPLETATO

Tutte le funzionalità previste per lo Sprint
sono state implementate e verificate.

I test funzionali eseguiti non hanno evidenziato
regressioni nelle funzionalità già operative.

Il Vertex Mapper può quindi essere utilizzato
per la fase successiva di costruzione delle
25 associazioni definitive.

---

## Prossimo Sprint

Il prossimo obiettivo è:

    Sprint 19 — Complete 25 Control Points

Lo Sprint 19 sarà dedicato alla costruzione
effettiva e alla validazione delle 25 associazioni:

    MediaPipe Control Point
              ↕
    MakeHuman Vertex

con verifica dell'univocità dei landmark
e dei vertici associati.


---

# 43. Sprint 19 — Complete 25 Control Points

## Obiettivo

Completare le associazioni:

    MediaPipe
        ↔
    MakeHuman

per tutti i 25 Control Points.

---

## Attività

Per ogni landmark:

1. selezionare il landmark;
2. individuare il punto anatomico corrispondente;
3. selezionare il vertice MakeHuman;
4. verificare la posizione;
5. creare il mapping;
6. controllare eventuali duplicazioni.

---

## Regola

Non procedere automaticamente al successivo
se il mapping corrente non è stato verificato.

---

## Risultato

Devono esistere:

    25 landmark
        ↓
    25 vertex mapping

con:

    25 landmark univoci

e:

    25 vertici univoci.

---

# 44. Sprint 20 — Canonical Mapping Model

## Obiettivo

Creare il modello dati ufficiale che rappresenta
la relazione tra MediaPipe e Canonical Mesh.

---

## Stato

    COMPLETATO

Il modello `CanonicalMapping` è stato implementato
nel layer Models e integrato nel modello Project.

Il modello è indipendente dalla GUI e rappresenta
le associazioni tra i Control Points MediaPipe
e i vertici della Canonical Mesh MakeHuman.

---

## Nuova responsabilità

Il modello rappresenta:

    Canonical Mapping

senza dipendere dalla GUI.

---

## Struttura concettuale

    CanonicalMapping
        ├── mapping_version
        ├── canonical_mesh_id
        ├── canonical_mesh_version
        ├── template_id
        ├── template_version
        └── control_points

Ogni associazione contiene i dati necessari
a identificare il Control Point e il vertice MakeHuman
associato.

---

## Regola architetturale

Il Mapping Model appartiene ai Models.

Non appartiene a:

- Dialog;
- Widget;
- Viewer;
- Controller GUI.

La GUI utilizza il modello tramite i livelli architetturali
previsti dal progetto.

---

# 45. Sprint 21 — Mapping Persistence

## Obiettivo

Salvare e ricaricare il Canonical Mapping.

---

## Stato

    COMPLETATO

La persistenza del Canonical Mapping è stata implementata
e verificata attraverso la persistenza standard del progetto.

Il mapping viene salvato nel `project.json` e viene
ricostruito automaticamente durante il caricamento
del progetto.

---

## Funzionalità implementate

Sono operative:

    Save Canonical Mapping

e:

    Load Canonical Mapping

attraverso:

    Project
        ↓
    ProjectSerializer
        ↓
    project.json

e:

    project.json
        ↓
    ProjectLoader
        ↓
    CanonicalMapping

È inoltre operativo il comando:

    File → Save

tramite:

    MainWindow
        ↓
    ApplicationController
        ↓
    ProjectController
        ↓
    ProjectManager
        ↓
    ProjectSaver

---

## Informazioni minime

Il file contiene:

- identificativo template;
- versione template;
- nome mesh;
- landmark index;
- landmark name;
- vertex index;
- coordinate del vertice;
- eventuali metadati.

---

## Validazione

Durante il caricamento devono essere verificati:

- template compatibile;
- numero mapping corretto;
- landmark validi;
- vertici esistenti;
- assenza di duplicati;
- coordinate coerenti.

---

## Risultato

Il mapping creato manualmente una sola volta
deve poter essere riutilizzato.

---

# 46. Sprint 22 — Canonical Mesh Builder

## Stato

    COMPLETATO E VERIFICATO

Data completamento:

    18/08/2026

---

## Obiettivo

Creare il primo vero:

    CanonicalMeshBuilder

con il compito di costruire la Canonical Mesh
derivata dal template MakeHuman della testa.

---

## Template utilizzato

Template:

    male1591

Mesh specifica della testa:

    male1591_head.obj

Il modello completo `male1591.obj` rimane disponibile
nel progetto, ma non viene utilizzato per la Canonical Mesh
della testa.

La scelta della mesh specifica della testa è coerente
con l'obiettivo della pipeline attuale.

---

## Responsabilità

Il builder costruisce la geometria canonica
partendo dal template MakeHuman.

La pipeline verificata è:

    MakeHuman Template
            ↓
    TemplateLoader
            ↓
    HeadTemplate
            ↓
    CanonicalMeshBuilder
            ↓
    Canonical Mesh

---

## Geometria prodotta

La Canonical Mesh contiene:

    1604 vertici
    3064 triangoli

Il Builder mantiene:

- identità dei vertici;
- ordine dei vertici;
- coordinate geometriche;
- indici dei triangoli;
- triangolazione;
- topologia della mesh.

La Canonical Mesh è una rappresentazione derivata
e indipendente dal template sorgente.

Il template originale non viene modificato.

---

## Validazione minima del Builder

Il `CanonicalMeshBuilder` esegue una validazione minima
dei prerequisiti del template prima della costruzione.

Sono verificati:

- tipo corretto di `HeadTemplate`;
- presenza dei vertici;
- validità degli indici dei triangoli;
- assenza di riferimenti a vertici inesistenti;
- coerenza dei metadati identificativi.

La validazione geometrica completa della Canonical Mesh
rimane responsabilità dello Sprint 23.

---

## Compatibilità con Canonical Mapping

La Canonical Mesh è stata verificata rispetto
al Canonical Mapping definitivo.

Risultato:

    Mapping: 25/25
    Mapping status: COMPLETE

Sono state verificate per tutti i 25 Control Points:

- esistenza del vertice;
- validità dell'indice;
- corrispondenza delle coordinate;
- compatibilità dei metadati;
- unicità dei vertici associati.

---

## Test eseguiti

Sono stati superati:

- test del template reale;
- test della copia delle coordinate;
- test della copia degli indici;
- test dell'indipendenza degli oggetti Vertex3D;
- test dell'indipendenza degli oggetti Triangle;
- test del template privo di vertici;
- test di un triangolo con indice fuori range;
- test di compatibilità Canonical Mapping ↔ Canonical Mesh;
- test finale integrato dello Sprint 22.

---

## Test finale integrato

Risultato:

    Template vertices: 1604
    Template triangles: 3064
    Canonical vertices: 1604
    Canonical triangles: 3064

    Counts: OK
    Geometry: OK
    Object independence: OK
    Template unchanged: OK
    Canonical Mapping: OK

    FINAL RESULT: SPRINT 22 OK

---

## Regola architetturale

Il CanonicalMeshBuilder non deve occuparsi di:

- GUI;
- MediaPipe;
- fotografia;
- rendering;
- texture;
- esportazione;
- Registration Engine;
- deformazione.

Deve occuparsi esclusivamente
della costruzione della geometria canonica.

La Registration Engine rimane successiva
e non viene anticipata.

---

# 47. Sprint 23 — Canonical Mesh Validation

## Stato

    COMPLETATO E VERIFICATO

Data completamento:

    19/08/2026

Lo Sprint 23 ha completato la validazione della Canonical Mesh
necessaria come prerequisito per la Registration Engine.

---

## Obiettivo

Validare geometricamente e topologicamente la Canonical Mesh
prima del suo utilizzo nella fase di Registration Engine.

---

## Controlli completati

Sono stati implementati e verificati:

- numero dei vertici;
- numero dei triangoli;
- validità degli indici;
- assenza di riferimenti a vertici inesistenti;
- coordinate finite;
- rilevamento di NaN;
- rilevamento di Inf;
- bounding box;
- dimensioni della mesh;
- centro geometrico derivato dalla bounding box;
- boundary edges;
- boundary vertices;
- edge non-manifold;
- triangoli degeneri per indici duplicati;
- triangoli degeneri per area geometrica nulla;
- calcolo delle normali delle facce;
- validazione delle normali;
- rilevamento delle normali di lunghezza nulla;
- rilevamento di normali non finite;
- controllo dell'orientamento / winding;
- verifica della distribuzione dei 25 Control Points;
- verifica delle coordinate normalizzate dei Control Points;
- verifica della simmetria bilaterale dei Control Points;
- verifica del sistema di coordinate della Canonical Mesh;
- serializzazione dei report diagnostici;
- integrazione dei controlli nella validazione della Canonical Mesh.

---

## Risultato sulla Canonical Mesh reale

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

Il boundary viene mantenuto come warning diagnostico e non
come errore bloccante.

Gli edge non-manifold e i triangoli degeneri rimangono invece
condizioni di errore.

---

## Validazione delle normali

È stato introdotto il componente dedicato:

    MeshNormalAnalyzer

con relativo report:

    MeshNormalAnalysisReport

La validazione finale ha verificato:

    Normal count:
        3064

    Valid normals:
        3064

    Zero-length normals:
        0

    Non-finite normals:
        0

La Canonical Mesh dispone quindi di una normale valida per
ogni triangolo della geometria verificata.

---

## Orientamento / Winding

L'orientamento delle facce è stato verificato come parte
della validazione delle normali e della coerenza geometrica.

Il controllo non modifica la topologia della mesh e non
introduce una nuova geometria.

---

## Control Points

È stata verificata la distribuzione dei 25 Control Points
sulla Canonical Mesh.

Sono state mantenute le associazioni definitive:

    25 / 25
    COMPLETE

Sono inoltre state verificate:

- presenza dei vertici associati;
- validità degli indici;
- coerenza delle coordinate;
- normalizzazione rispetto alla componente principale;
- simmetria bilaterale delle coppie previste.

L'unica asimmetria locale già documentata rimane:

    right_eye_outer ↔ left_eye_outer
    errore normalizzato = 0.0117

Il valore non invalida il mapping e viene mantenuto come
caratteristica geometrica locale da monitorare.

---

## Sistema di coordinate

Il sistema di coordinate della Canonical Mesh è stato
verificato sul template realmente utilizzato.

Convenzione Face3D Studio:

    X = asse laterale
        +X = destra anatomica
        -X = sinistra anatomica

    Y = asse verticale
        +Y = alto
        -Y = basso

    Z = asse di profondità
        +Z = anteriore / fronte
        -Z = posteriore / nuca

Le coordinate originali della Canonical Mesh vengono
preservate.

L'eventuale centratura effettuata dal viewer è considerata
una trasformazione di visualizzazione e non modifica
le coordinate canoniche.

La scala relativa tra MediaPipe e Canonical Mesh non viene
fissata arbitrariamente in questo Sprint: sarà stimata
nel successivo Global Alignment.

---

## Test negativi

Sono stati verificati con successo:

- vertice con NaN;
- vertice con +Inf;
- vertice con -Inf;
- triangolo con indice duplicato;
- triangolo con tre indici distinti ma area nulla;
- edge condiviso da più di due triangoli;
- gestione delle normali non valide.

È stata inoltre verificata l'indipendenza delle diagnostiche,
evitando che un triangolo degenere generi artificialmente
errori non-manifold secondari.

---

## Visualizzazione

La Canonical Mesh e i relativi Control Points possono essere
utilizzati nel contesto del MeshViewer esistente senza spostare
la responsabilità della validazione geometrica nella GUI.

La visualizzazione rimane quindi un supporto operativo e
diagnostico; gli algoritmi di validazione restano nei componenti
dedicati del layer di ricostruzione.

---

## Regola architetturale

Lo Sprint 23 non modifica l'architettura congelata.

La struttura rimane:

    GUI
      ↓
    ApplicationController
      ↓
    Controllers
      ↓
    Services
      ↓
    Managers / Algorithms / Exporters
      ↓
    Models

La validazione geometrica rimane indipendente dalla GUI.

---

## Risultato finale

La Canonical Mesh è ora considerata:

    VALIDATA
    STABILE
    PRONTA PER LA REGISTRATION ENGINE

Il progetto può quindi passare allo:

    Sprint 24 — Registration Engine

La Registration Engine non viene anticipata nello Sprint 23.

---

# 48. Sprint 24 — Registration Engine

## Obiettivo

Creare il motore di registrazione.

---

## Input

Il Registration Engine riceverà:

    Canonical Mesh

e:

    25 landmark reali

---

## Output

Produrrà:

    trasformazione geometrica

necessaria ad allineare la Canonical Mesh
al volto reale.

---

## Pipeline

    Canonical Mesh
          +
    Real Face Landmarks
          ↓
    Registration Engine
          ↓
    Aligned Canonical Mesh

---

## Regola

La registrazione non deve modificare
il template originale.

Deve produrre una nuova geometria.

---

# 49. Sprint 25 — Global Alignment

## Stato

    [x] COMPLETATO E VERIFICATO

## Obiettivo

Implementare il primo livello della registrazione:

    Global Alignment

---

## Funzione

Allineare globalmente:

- posizione;
- scala;
- orientamento.

---

## Sequenza

    Landmark Canonici
            ↓
    Landmark Reali
            ↓
    stima trasformazione
            ↓
    translation
            ↓
    rotation
            ↓
    scale

---

## Risultato

La Canonical Mesh deve assumere
la posizione e l'orientamento generale
del volto reale.

---

## Importante

In questa fase NON deve essere eseguita
la deformazione locale della mesh.

Il risultato deve essere esclusivamente:

    allineamento globale.

---

# 50. Sprint 26 — Local Deformation

## Obiettivo

Implementare la deformazione locale
della Canonical Mesh.

---

## Problema

L'allineamento globale non è sufficiente.

Due volti possono avere:

- stessa posizione;
- stessa scala;
- stesso orientamento;

ma:

- naso diverso;
- mandibola diversa;
- fronte diversa;
- zigomi diversi;
- bocca diversa;
- occhi diversi.

---

## Soluzione

Applicare una deformazione controllata
della mesh utilizzando i Control Points.

---

## Principio

    Canonical Vertex
          ↓
    influenza dei landmark vicini
          ↓
    spostamento ponderato
          ↓
    Personalized Vertex

---

## Vincoli

La deformazione deve:

- mantenere la topologia;
- evitare artefatti;
- evitare discontinuità;
- mantenere la stabilità delle zone non interessate;
- preservare i Control Points.

---

# 51. Sprint 27 — Head Reconstruction

## Obiettivo

Completare la ricostruzione della testa.

---

## Componenti previste

Il processo dovrà gestire:

- volto;
- lati della testa;
- cranio;
- nuca;
- orecchie;
- collo.

---

## Pipeline

    Face Mesh
        ↓
    Canonical Face
        ↓
    Head Reconstruction
        ↓
    Complete Head

---

## Boundary

Il BoundaryDetector dovrà individuare
le zone aperte della mesh.

Successivamente:

    Boundary
       ↓
    reconstruction
       ↓
    closed geometry

---

# 52. Sprint 28 — Complete Head Mesh

## Obiettivo

Produrre una mesh completa e coerente
della testa.

---

## Controlli

La mesh dovrà essere verificata per:

- buchi;
- triangoli degenerati;
- normali invertite;
- boundary inattesi;
- intersezioni;
- continuità;
- manifoldness.

---

## Risultato

Output:

    Complete Head Mesh

utilizzabile dalle fasi successive.

---

# 53. Sprint 29 — Texture Projection

## Obiettivo

Proiettare la fotografia sulla mesh ricostruita.

---

## Input

    fotografia originale
        +
    Complete Head Mesh

---

## Output

    texture map

---

## Pipeline prevista

    fotografia
        ↓
    camera projection
        ↓
    UV coordinates
        ↓
    texture
        ↓
    material

---

## Regola

La texture deve essere separata dalla geometria.

La mesh non deve contenere direttamente
la logica della texture.

---

# 54. Sprint 30 — Reconstruction Pipeline

## Obiettivo

Unificare le componenti precedenti
in una pipeline completa.

---

## Pipeline

    Input Image
        ↓
    Face Detection
        ↓
    Face Analysis
        ↓
    MediaPipe Landmarks
        ↓
    Canonical Mesh
        ↓
    Registration
        ↓
    Global Alignment
        ↓
    Local Deformation
        ↓
    Head Reconstruction
        ↓
    Complete Head Mesh
        ↓
    Texture Projection
        ↓
    Final 3D Model

---

## Responsabilità

La pipeline deve coordinare i componenti.

Non deve contenere direttamente
gli algoritmi geometrici.

---

# 55. Sprint 31 — Single Photo Reconstruction

## Obiettivo

Ottenere la prima ricostruzione completa
partendo da una singola fotografia.

---

## Input

    JPEG / PNG

---

## Output

    Face3D Project
        +
    Complete 3D Head
        +
    Texture

---

## Risultato minimo

L'applicazione deve essere in grado di:

1. caricare una fotografia;
2. rilevare il volto;
3. estrarre i landmark;
4. caricare la Canonical Mesh;
5. registrarla;
6. deformarla;
7. completare la testa;
8. applicare la texture;
9. visualizzare il risultato.

---

# 56. Sprint 32 — Reconstruction Validation

## Obiettivo

Validare la qualità della ricostruzione.

---

## Test

Utilizzare fotografie di prova
con caratteristiche differenti.

Devono essere testati:

- volto frontale;
- volto leggermente ruotato;
- volto inclinato;
- differenti condizioni di luce;
- differenti distanze dalla camera;
- differenti proporzioni del volto.

---

## Metriche future

Dovranno essere introdotte metriche
per valutare:

- errore landmark;
- errore medio;
- errore massimo;
- deviazione geometrica;
- stabilità della deformazione.

---

# 57. Criterio generale di completamento

La nuova fase non sarà considerata completata
quando semplicemente:

    "la mesh si vede"

ma quando sarà possibile dimostrare:

    fotografia
        ↓
    landmark
        ↓
    mapping
        ↓
    registrazione
        ↓
    deformazione
        ↓
    testa 3D

con un risultato:

- ripetibile;
- verificabile;
- stabile;
- esportabile.

---

# 58. Regola fondamentale per gli Sprint 18–32

Ogni Sprint deve modificare una sola responsabilità principale.

Non è consentito:

    Sprint 24
        Registration
        +
        Texture
        +
        GUI redesign
        +
        Export

Lo Sprint deve essere invece:

    Sprint 24
        Registration Engine

e solamente dopo la verifica:

    Sprint 25
        Global Alignment

---

# 59. Regola "prima il modello, poi la GUI"

Quando viene introdotta una nuova funzionalità:

    1. Model
    2. Service / Manager
    3. Controller
    4. GUI
    5. Test

La GUI non deve diventare il luogo
dove viene implementata la logica applicativa.

---

# 60. Regola "una modifica alla volta"

Per ogni Sprint:

    modifica
        ↓
    esecuzione
        ↓
    test
        ↓
    verifica
        ↓
    documentazione
        ↓
    commit

Solo successivamente:

    modifica successiva.

---

# 61. Definition of Done

Uno Sprint può essere marcato:

    COMPLETATO

solamente quando:

- il codice funziona;
- il test è stato eseguito;
- eventuali bug sono stati corretti;
- non ci sono regressioni;
- il codice temporaneo è stato rimosso;
- ROADMAP.md è aggiornato;
- CHANGELOG.md è aggiornato;
- la documentazione tecnica è aggiornata;
- il commit Git è stato effettuato;
- il push GitHub è stato effettuato.

Questa procedura è coerente con le regole già presenti
nel ROADMAP storico. :contentReference[oaicite:1]{index=1}

---

# 62. Stato della roadmap

Alla data del 20/08/2026:

    Sprint 17.1
        COMPLETATO

    Sprint 18
        COMPLETATO

    Sprint 19
        COMPLETATO

    Sprint 20
        COMPLETATO

    Sprint 21
        COMPLETATO

    Sprint 22
        COMPLETATO

    Sprint 23
        COMPLETATO

    Sprint 24
        COMPLETATO

    Sprint 25
        COMPLETATO

    Sprint 26
        COMPLETATO

    Sprint 27
        PIANIFICATO

    Sprint 28
        PIANIFICATO

    Sprint 29
        PIANIFICATO

    Sprint 30
        PIANIFICATO

    Sprint 31
        PIANIFICATO

    Sprint 32
        PIANIFICATO

Lo Sprint 18 ha portato il Vertex Mapper
a uno stato stabile e utilizzabile come
strumento di calibrazione manuale.

Lo Sprint 19 ha completato e validato
le 25 associazioni MediaPipe ↔ MakeHuman.

Sono state inoltre eseguite verifiche
geometriche e topologiche sul template
male1591/head utilizzato come base
della Canonical Mesh.

Il progetto è quindi pronto per la fase
successiva di costruzione e validazione
della Canonical Mesh.

---

# 63. Milestone principali

## MILESTONE A

    Vertex Mapper definitivo

    Sprint 18–19

---

## MILESTONE B

    Canonical Mapping persistente

    Sprint 20–21

---

## MILESTONE C

    Canonical Mesh

    Sprint 22–23

---

## MILESTONE D

    Registration Engine

    Sprint 24–25

---

## MILESTONE E

    Personalized Mesh

    Sprint 26

---

## MILESTONE F

    Complete Head

    Sprint 27–28

---

## MILESTONE G

    Textured 3D Head

    Sprint 29–30

---

## MILESTONE H

    Single Photo 3D Reconstruction

    Sprint 31–32

---

# 64. Obiettivo tecnico della fase

Il vero obiettivo degli Sprint 18–32 è arrivare
a questa trasformazione:

    2D
     │
     ▼
    MediaPipe
     │
     ▼
    25 Control Points
     │
     ▼
    Canonical Mesh
     │
     ▼
    Registration
     │
     ▼
    Deformation
     │
     ▼
    Complete Head
     │
     ▼
    Texture
     │
     ▼
    3D Person

Questa pipeline costituisce il nucleo
della futura Face3D Studio AI.

---

# 65. ARCHITETTURA DELLA CANONICAL MESH

La Canonical Mesh rappresenta il modello geometrico
di riferimento sul quale verranno successivamente
registrati e deformati i volti reali.

La Canonical Mesh non deve essere considerata
semplicemente come una mesh MakeHuman caricata
nel programma.

Deve diventare un modello geometrico identificabile,
versionabile e riproducibile.

---

# 66. Origine della Canonical Mesh

La prima Canonical Mesh di Face3D Studio AI
sarà derivata dal modello MakeHuman utilizzato
come template anatomico.

Pipeline:

    MakeHuman OBJ
         ↓
    TemplateLoader
         ↓
    Template Mesh
         ↓
    Canonical Mesh

Il modello MakeHuman originale deve rimanere
immutato.

La Canonical Mesh sarà una rappresentazione
derivata del template.

---

# 67. Identità della Canonical Mesh

Ogni Canonical Mesh dovrà avere almeno:

- identificativo;
- nome;
- versione;
- origine;
- numero di vertici;
- numero di facce;
- numero di edge;
- bounding box;
- scala;
- sistema di coordinate;
- versione del mapping;
- elenco dei Control Points.

Esempio concettuale:

    CanonicalMesh
        ├── id
        ├── name
        ├── version
        ├── source_template
        ├── vertices
        ├── faces
        ├── edges
        ├── bounds
        ├── coordinate_system
        └── control_points

---

# 68. Separazione tra Template e Canonical Mesh

Il progetto deve mantenere una distinzione
tra:

    Template Mesh

e:

    Canonical Mesh

Il Template Mesh rappresenta il modello sorgente.

La Canonical Mesh rappresenta il modello
geometrico normalizzato utilizzato dalla pipeline
di ricostruzione.

Questa distinzione è importante perché in futuro
potranno esistere più template.

Esempio:

    MakeHuman Template
          ↓
    Canonical Mesh v1

oppure:

    altro Template
          ↓
    Canonical Mesh v2

---

# 69. Control Points

I 25 landmark MediaPipe selezionati costituiscono
i Control Points della Canonical Mesh.

Ogni Control Point rappresenta una corrispondenza:

    MediaPipe Landmark
            ↕
    Canonical Vertex

Esempio:

    landmark 4
        ↕
    vertex 18342

---

# 70. Proprietà di un Control Point

Ogni Control Point dovrà contenere
almeno:

- landmark index;
- landmark name;
- vertex index;
- coordinate del vertex;
- posizione anatomica;
- eventuale descrizione;
- stato del mapping.

Esempio:

    ControlPoint
        ├── landmark_index
        ├── landmark_name
        ├── vertex_index
        ├── vertex_position
        ├── anatomical_region
        └── status

---

# 71. Unicità dei Control Points

Il mapping deve rispettare due vincoli.

## Vincolo 1

Un landmark può essere associato
ad un solo vertice.

    landmark → 1 vertex

## Vincolo 2

Un vertice non deve essere associato
a più landmark differenti.

    vertex → 1 landmark

Pertanto il mapping deve essere
biunivoco.

---

# 72. Validazione del Mapping

Prima che un mapping venga considerato valido
devono essere verificati:

- landmark esistente;
- vertex esistente;
- landmark non duplicato;
- vertex non duplicato;
- coordinate valide;
- template compatibile;
- numero minimo di Control Points raggiunto.

Il Vertex Mapper deve occuparsi dell'interazione
con l'utente.

La validazione definitiva deve invece appartenere
al Model / Service competente.

---

# 73. Mapping come asset del progetto

Il mapping dei 25 punti non deve rimanere
unicamente nella memoria del Vertex Mapper.

Deve diventare un asset persistente.

Concettualmente:

    resources/
        canonical/
            mappings/
                makehuman_v1.json

Il formato definitivo potrà essere stabilito
quando verrà implementata la persistenza.

---

# 74. Versionamento

Il mapping deve essere associato alla versione
della Canonical Mesh.

Esempio:

    Canonical Mesh:
        makehuman_v1

    Mapping:
        makehuman_v1_mapping_v1

Se la mesh cambia significativamente,
il mapping precedente non deve essere utilizzato
automaticamente.

---

# 75. Separazione tra Mapping e Mesh

Il mapping non deve contenere una copia
della mesh completa.

Deve contenere solamente le informazioni necessarie
a identificare i Control Points.

Quindi:

    Canonical Mesh
          +
    Canonical Mapping
          ↓
    Canonical Model

---

# 76. Canonical Model

A livello concettuale la pipeline dovrà poter
lavorare con un oggetto composto da:

    CanonicalModel
        ├── mesh
        └── mapping

Questo oggetto rappresenterà il riferimento
geometrico completo.

---

# 77. Flusso di caricamento

Quando il sistema dovrà utilizzare
la Canonical Mesh:

    Load Canonical Mesh
            ↓
    Load Canonical Mapping
            ↓
    Validate compatibility
            ↓
    Build Canonical Model
            ↓
    Ready

Se il mapping non è compatibile,
la pipeline deve fermarsi con un errore esplicito.

Non deve tentare una correzione automatica
silenziosa.

---

# 78. Registrazione della Canonical Mesh

La registrazione rappresenta il processo
attraverso il quale la Canonical Mesh viene
allineata al volto reale.

Input:

    Canonical Model
          +
    Real Face Landmarks

Output:

    Registered Canonical Mesh

---

# 79. Landmark reali

I landmark reali saranno prodotti
dal provider MediaPipe.

La pipeline dovrà quindi avere:

    MediaPipe Provider
          ↓
    Face Landmarks
          ↓
    Registration Engine

Il Registration Engine non deve conoscere
i dettagli interni del provider MediaPipe.

---

# 80. Normalizzazione dei landmark

Prima della registrazione sarà necessario
portare i dati in uno spazio geometrico coerente.

I dati MediaPipe e quelli della Canonical Mesh
potrebbero utilizzare:

- scale differenti;
- orientamenti differenti;
- origini differenti;
- sistemi di coordinate differenti.

Pertanto sarà necessario definire
un sistema di coordinate canonico.

---

# 81. Coordinate System

Il progetto dovrà definire esplicitamente:

- asse X;
- asse Y;
- asse Z;
- origine;
- unità di misura;
- orientamento del volto.

La conversione dovrà avvenire in un solo punto
della pipeline.

Non devono essere presenti conversioni
coordinate sparse nei vari componenti.

---

# 82. Global Registration

La prima fase della registrazione sarà:

    Global Registration

Il suo compito sarà determinare:

- traslazione;
- rotazione;
- scala.

Input:

    Canonical Control Points
            +
    Real Control Points

Output:

    Global Transform

---

# 83. Global Transform

La trasformazione globale potrà essere
rappresentata concettualmente come:

    T_global

e applicata alla Canonical Mesh:

    V' = T_global(V)

dove:

    V

è il vertice originale e:

    V'

è il vertice dopo l'allineamento.

---

# 84. Separazione tra Alignment e Deformation

Il sistema deve distinguere chiaramente:

    Alignment

da:

    Deformation

Alignment:

    sposta e orienta la mesh.

Deformation:

    modifica localmente la forma.

Non devono essere implementati
come un unico algoritmo monolitico.

---

# 85. Local Deformation

Dopo l'allineamento globale:

    Canonical Mesh
          ↓
    Global Transform
          ↓
    Aligned Mesh
          ↓
    Local Deformation
          ↓
    Personalized Mesh

La deformazione utilizzerà i 25 Control Points
come vincoli.

---

# 86. Control Point Constraints

Per ogni Control Point:

    C_i

dovrà esistere una posizione target:

    T_i

Il sistema dovrà quindi cercare una deformazione
tale che:

    D(C_i) ≈ T_i

per tutti i Control Points.

---

# 87. Distribuzione della deformazione

La deformazione non deve essere applicata
uniformemente a tutta la testa.

L'influenza di ciascun Control Point dovrà
diminuire con la distanza.

Concettualmente:

    Control Point
          ↓
    influenza locale
          ↓
    vertici vicini

e:

    distanza maggiore
          ↓
    influenza minore

---

# 88. Deformazione e Topologia

La deformazione deve modificare
le coordinate dei vertici.

Non deve modificare:

- numero dei vertici;
- indici dei vertici;
- triangolazione;
- topologia.

Quindi:

    Canonical Topology
            ↓
    invariata
            ↓
    Personalized Geometry

Questo permetterà di mantenere una topologia
comune tra modelli differenti.

---

# 89. Vantaggio della Topologia Canonica

Una topologia comune permetterà in futuro
di confrontare direttamente due modelli.

Esempio:

    Person A
       ↓
    Canonical Topology

    Person B
       ↓
    Canonical Topology

Sarà quindi possibile confrontare:

- distanza tra vertici;
- curvature;
- proporzioni;
- aree;
- volumi;
- deformazioni.

---

# 90. Canonical Vertex Correspondence

Questo è uno dei motivi principali per cui
la Canonical Mesh è fondamentale.

Ogni vertice della mesh canonica rappresenta
una posizione topologica coerente.

Dopo la deformazione:

    vertex 18342
          ↓
    stesso vertex semantico
          ↓
    soggetto A

e:

    vertex 18342
          ↓
    stesso vertex semantico
          ↓
    soggetto B

La posizione cambia.

L'identità topologica rimane.

---

# 91. Perché non associare 468 landmark

Il Vertex Mapper utilizza intenzionalmente
un numero limitato di Control Points.

Associare manualmente tutti i landmark MediaPipe
non è necessario per costruire il mapping iniziale.

I 25 Control Points costituiscono
i punti di riferimento principali.

Successivamente il sistema dovrà utilizzare
questi punti per determinare la trasformazione
dell'intera Canonical Mesh.

---

# 92. Espansione dai 25 punti

La pipeline futura sarà:

    25 Control Points
          ↓
    stima trasformazione
          ↓
    trasformazione della mesh
          ↓
    tutti i vertici Canonical Mesh

Quindi:

    25 punti manuali

non significano:

    25 vertici finali.

Significano:

    25 vincoli geometrici

utilizzati per determinare
la posizione degli altri vertici.

---

# 93. MediaPipe 468 → Canonical Mesh

In una fase successiva sarà possibile utilizzare
anche i landmark MediaPipe non inclusi
nei 25 Control Points.

La strategia prevista sarà:

    468 MediaPipe Landmarks
             ↓
    25 Control Points
             ↓
    Canonical Registration
             ↓
    Canonical Mesh
             ↓
    eventuali landmark intermediari
             ↓
    Personalized Mesh

I 25 punti costituiscono quindi
la struttura di calibrazione iniziale.

---

# 94. Non assumere una corrispondenza 1:1 automatica

Non deve essere assunto automaticamente
che:

    MediaPipe Landmark N
            =
    Canonical Vertex N

I numeri dei landmark MediaPipe
e gli indici dei vertici MakeHuman
appartengono a sistemi completamente differenti.

La corrispondenza deve essere esplicita
nel Canonical Mapping.

---

# 95. Registration Engine — responsabilità

Il Registration Engine dovrà occuparsi
esclusivamente della registrazione geometrica.

Non deve occuparsi di:

- GUI;
- caricamento immagini;
- MediaPipe;
- rendering;
- texture;
- esportazione.

Input:

    Canonical Model
        +
    Target Landmarks

Output:

    Registered Mesh

---

# 96. Possibile struttura futura

La struttura concettuale potrà essere:

    source/
        models/
            canonical/
                canonical_mesh.py
                canonical_mapping.py
                canonical_model.py

        reconstruction/
            registration/
                registration_engine.py
                global_alignment.py
                local_deformation.py

Questa struttura è indicativa.

I nomi definitivi dovranno essere scelti
solo dopo aver verificato la struttura
effettiva del progetto.

---

# 97. Principio di non duplicazione

Prima di creare una nuova classe:

    verificare se esiste già
    una responsabilità equivalente.

Non devono essere create classi duplicate
con nomi differenti.

Esempio da evitare:

    MeshRegistration
    MeshRegistrar
    RegistrationManager
    RegistrationService

se svolgono sostanzialmente
la stessa responsabilità.

---

# 98. Utilizzo dei componenti esistenti

La nuova pipeline dovrà riutilizzare
i componenti già presenti quando possibile.

In particolare:

- TemplateLoader;
- FaceMesh;
- Vertex3D;
- VertexMapping;
- VertexMappingCollection;
- LandmarkCatalog;
- MeshViewer;
- provider MediaPipe;
- componenti di reconstruction già presenti.

Il fatto che esistano già componenti per la mesh
e per i landmark deve essere considerato
prima di introdurre nuovi Model.

---

# 99. Vertex Mapper e Canonical Pipeline

Il Vertex Mapper non deve diventare
il Registration Engine.

Il suo compito termina con:

    creazione / modifica del mapping.

Quindi:

    Vertex Mapper
          ↓
    Canonical Mapping
          ↓
    Registration Engine

Il Vertex Mapper è uno strumento
di calibrazione.

---

# 100. Stato del Mapping

Il sistema dovrà distinguere almeno:

    UNMAPPED

    MAPPED

    INVALID

Esempio:

    Landmark 4
        → MAPPED

    Landmark 5
        → UNMAPPED

    Landmark 6
        → INVALID

---

# 101. Mapping Completo

Il Canonical Mapping potrà essere considerato
completo quando tutti i Control Points
previsti saranno associati.

Per il mapping previsto:

    expected = 25

Il mapping sarà completo solamente quando:

    mapped = 25

e:

    complete = True

Lo stato:

    mapped = 25
    complete = True

rappresenta quindi la condizione di validità
finale prevista per il Canonical Mapping,
non lo stato corrente dello Sprint 19.

---

# 102. Mapping Incompleto

Se:

    mapped < expected

la Canonical Mesh non deve essere considerata
pronta per la registrazione definitiva.

Il sistema dovrà poter indicare:

    Canonical Mapping incomplete

specificando:

    mapped / expected

Esempio:

    18 / 25

---

# 103. Validazione prima della Registration

Prima di avviare la registrazione:

    Canonical Mapping
            ↓
        validation
            ↓
        complete?
          /   \
        NO     YES
        ↓       ↓
      STOP    Registration

La validazione deve essere esplicita.

---

# 104. Errore di registrazione

Gli errori della Registration Engine
non devono essere nascosti.

Devono essere rappresentati
attraverso risultati strutturati.

Concettualmente:

    RegistrationResult
        ├── success
        ├── transform
        ├── error
        └── diagnostics

---

# 105. Diagnostica

Il sistema dovrà poter fornire
informazioni utili per capire
perché una registrazione non è riuscita.

Esempi:

- Control Point mancante;
- landmark non disponibile;
- mapping incompatibile;
- coordinate invalide;
- errore di trasformazione;
- errore geometrico.

---

# 106. Test della Canonical Pipeline

Ogni componente dovrà essere testato
indipendentemente.

---

## Test Mapping

Verificare:

    25 landmark
       ↕
    25 vertex

---

## Test Canonical Mesh

Verificare:

    mesh valida

---

## Test Registration

Utilizzare una trasformazione artificiale
conosciuta.

Esempio:

    Canonical Mesh
          ↓
    rotazione nota
          +
    traslazione nota
          +
    scala nota

Il Registration Engine dovrà recuperare
una trasformazione compatibile.

---

## Test Deformation

Applicare spostamenti artificiali
ai Control Points e verificare
la risposta della mesh.

---

# 107. Test di regressione

Ogni modifica alla pipeline geometrica
deve essere verificata contro:

- caricamento template;
- rendering;
- Vertex Mapper;
- mapping;
- apertura/chiusura;
- salvataggio;
- caricamento;
- viewer.

Una modifica al sistema geometrico
non deve rompere il Vertex Mapper
o il MeshViewer.

---

# 108. Regola fondamentale della Canonical Mesh

Una volta validata la Canonical Mesh:

    NON MODIFICARLA MANUALMENTE

senza generare una nuova versione.

Esempio:

    Canonical Mesh v1
          ↓
       stabile

Se viene modificata:

    Canonical Mesh v2

Il mapping dovrà essere rivalidato.

---

# 109. Versioning della geometria

La versione della Canonical Mesh
deve essere indipendente
dalla versione del software.

Esempio:

    Face3D Studio 0.15.0

può utilizzare:

    Canonical Mesh 1.0

Successivamente:

    Face3D Studio 0.20.0

potrà continuare a utilizzare:

    Canonical Mesh 1.0

oppure:

    Canonical Mesh 2.0

---

# 110. Obiettivo della fase Canonical

La fase sarà considerata completata quando
sarà possibile eseguire:

    Load Canonical Mesh
            ↓
    Load Canonical Mapping
            ↓
    Validate
            ↓
    Receive 25 Real Landmarks
            ↓
    Global Alignment
            ↓
    Local Deformation
            ↓
    Output Personalized Mesh

senza dipendere dal Vertex Mapper.

---

# 111. Principio architetturale definitivo

Il Vertex Mapper serve a costruire
la conoscenza.

Il Canonical Mapping conserva
la conoscenza.

Il Registration Engine utilizza
la conoscenza.

La Canonical Mesh costituisce
il riferimento geometrico.

La Personalized Mesh costituisce
il risultato.

Quindi:

    Vertex Mapper
          ↓
    Mapping
          ↓
    Canonical Mesh
          ↓
    Registration
          ↓
    Personalized Mesh

---

# 112. Obiettivo finale della pipeline

L'architettura dovrà arrivare a:

                ┌──────────────────┐
                │  Real Photograph │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │     MediaPipe    │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Real Landmarks   │
                └────────┬─────────┘
                         ↓
          ┌──────────────────────────────┐
          │     Registration Engine      │
          └──────────────┬───────────────┘
                         ↑
             ┌───────────┴───────────┐
             │                       │
    ┌────────────────┐     ┌──────────────────┐
    │ Canonical Mesh │     │ Canonical Mapping│
    └────────────────┘     └──────────────────┘
                         ↓
                ┌──────────────────┐
                │ Personalized Mesh│
                └──────────────────┘

Questa rappresenta la struttura concettuale
centrale della futura ricostruzione 3D.

---

# 113. Limite della fase attuale

Non implementare ancora:

- registrazione automatica;
- deformazione;
- ricostruzione completa;
- texture projection;
- ricostruzione da fotografia.

Prima deve essere completato e validato
il Canonical Mapping.

---

# 114. Stato operativo dopo la validazione dei 25 Control Points

Il Vertex Mapper è stato completato e stabilizzato
durante lo Sprint 18.

Il Canonical Mapping Model e la sua persistenza
sono stati implementati e verificati durante
gli Sprint 20 e 21.

Lo Sprint 19 è stato completato con la costruzione
e la validazione del set definitivo dei 25 Control Points.

La relazione risultante è:

    MediaPipe Control Point
            ↕
    MakeHuman Vertex

---

## Risultato dello Sprint 19

Sono presenti:

    25 Control Points
            ↕
    25 associazioni
            ↕
    25 vertici MakeHuman univoci

Il mapping risulta:

    Mapping: 25/25
    Mapping status: COMPLETE

La corrispondenza è stata verificata anche
rispetto alla convenzione anatomica destra/sinistra.
I nomi `right_*` e `left_*` rappresentano il lato
anatomico del modello e non la posizione grafica
sullo schermo.

---

## Validazione geometrica eseguita

Il template:

    male1591
    part = head

è stato verificato con:

    1604 vertici
    3064 triangoli

Controlli eseguiti:

    coordinate finite:
        NaN = 0
        Inf = 0

    indici triangolari:
        non validi = 0

    triangoli degenerati:
        0

    vertici duplicati:
        0

    componenti connesse:
        6

Dimensioni delle componenti:

    Componente 1: 490 vertici
    Componente 2: 276 vertici
    Componente 3: 276 vertici
    Componente 4: 256 vertici
    Componente 5: 256 vertici
    Componente 6: 50 vertici

La componente principale contiene 21 Control Points.
Le restanti componenti interessate dai Control Points
sono le componenti associate alle geometrie degli occhi.

---

## Bounding Box della componente principale

    X: -0.081100 → 0.081100
    Y:  1.387100 → 1.659500
    Z: -0.048500 → 0.159300

Dimensioni:

    X = 0.162200
    Y = 0.272400
    Z = 0.207800

Centro:

    (0.000000, 1.523300, 0.055400)

---

## Control Points normalizzati

È stata verificata la normalizzazione dei 25 Control Points
rispetto al bounding box della componente principale.

Sono state inoltre verificate le coppie bilaterali:

    right_eye_outer       ↔ left_eye_outer
    right_eye_inner       ↔ left_eye_inner
    right_eyebrow_inner   ↔ left_eyebrow_inner
    right_eyebrow_outer   ↔ left_eyebrow_outer
    mouth_right           ↔ mouth_left
    upper_lip_right       ↔ upper_lip_left
    nose_right_base       ↔ nose_left_base

Tutte le coppie risultano coerenti entro la tolleranza
utilizzata, ad eccezione di `eye_outer`, che presenta
un piccolo errore normalizzato:

    errore = 0.0117

Questo valore non è stato considerato sufficiente
per invalidare il mapping e viene mantenuto come
caratteristica geometrica locale da monitorare.

---

## Stato

    VERTEX MAPPER
        COMPLETATO

    25 CONTROL POINTS
        COMPLETATI E VALIDATI

    CANONICAL MAPPING
        IMPLEMENTATO

    CANONICAL MAPPING
        25/25 - COMPLETE

    PERSISTENZA CANONICAL MAPPING
        IMPLEMENTATA E VERIFICATA

    CANONICAL MESH BUILDER
        COMPLETATO E VERIFICATO

    CANONICAL MESH VALIDATION
        IN CORSO — FASE STRUTTURALE, NUMERICA,
        GEOMETRICA E TOPOLOGICA COMPLETATA

    NORMALI / ORIENTAMENTO
        DA IMPLEMENTARE E VERIFICARE

    REGISTRATION
        DA IMPLEMENTARE

    PERSONALIZED MESH
        DA IMPLEMENTARE

---

## Prossima fase

Il prossimo obiettivo operativo è completare lo Sprint 23
con i controlli ancora mancanti sulla Canonical Mesh:

    - normali;
    - orientamento / winding;
    - scala e sistema di coordinate;
    - distribuzione dei Control Points;
    - eventuali controlli topologici residui necessari;
    - visualizzazione Canonical Mesh + 25 Control Points.

Solo dopo la chiusura completa dello Sprint 23 verrà avviato:

    Sprint 24 — Registration Engine

Non implementare ancora:

- Registration Engine;
- Global Alignment;
- Local Deformation;
- ricostruzione completa;
- texture projection;
- ricostruzione da fotografia.

Queste funzionalità rimangono successive secondo la sequenza
prevista dalla roadmap.

---

# 115. ARCHITETTURA MATEMATICA DELLA REGISTRAZIONE

La registrazione costituisce il cuore matematico
della futura Canonical Mesh.

Il suo compito è determinare come trasformare
la geometria della Canonical Mesh MakeHuman
per adattarla ai landmark rilevati su un soggetto reale.

Il problema può essere rappresentato come:

    Canonical Control Points
            ↓
    Real Control Points
            ↓
    stima trasformazione
            ↓
    Canonical Mesh registrata
            ↓
    deformazione locale
            ↓
    Personalized Mesh

---

# 116. Definizione dei dati

Sia:

    C = {c₁, c₂, ..., c₂₅}

l'insieme dei 25 Control Points della Canonical Mesh.

Sia:

    R = {r₁, r₂, ..., r₂₅}

l'insieme dei corrispondenti Control Points
rilevati sul volto reale.

Ogni coppia rappresenta:

    cᵢ ↔ rᵢ

dove:

    cᵢ = posizione del Control Point
        sulla Canonical Mesh

    rᵢ = posizione del landmark
        rilevato sul soggetto reale

---

# 117. Corrispondenza esplicita

La corrispondenza non deve essere determinata
dal numero del vertice.

Esempio:

    MediaPipe landmark 4
            ↓
    Canonical vertex 1234

deve essere esplicitamente presente
nel Canonical Mapping.

Non deve essere assunto:

    landmark 4 = vertex 4

perché MediaPipe e MakeHuman utilizzano
sistemi di indicizzazione completamente differenti.

---

# 118. Costruzione dei Control Point Set

Il Registration Engine riceverà:

    Canonical Mapping
          +
    Real MediaPipe Landmarks

e costruirà:

    Canonical Point Set

e:

    Target Point Set

Esempio:

    canonical_mapping:
        landmark 4 → vertex 1234

    real_landmarks:
        landmark 4 → (x, y, z)

Il sistema potrà quindi costruire:

    C₄ = Vertex[1234]

    R₄ = MediaPipe[4]

---

# 119. Validazione dei Control Points

Prima della registrazione:

    C = Control Points Canonical
    R = Control Points Real

devono essere verificati.

Controlli:

- stesso numero di punti;
- stessi landmark;
- nessun landmark duplicato;
- nessun punto mancante;
- coordinate finite;
- coordinate valide;
- nessun NaN;
- nessun infinito;
- compatibilità del sistema di coordinate.

Se un Control Point fondamentale manca:

    Registration = NOT VALID

---

# 120. Qualità dei Control Points

Non tutti i Control Points hanno necessariamente
la stessa affidabilità.

In futuro il sistema potrà associare
un peso:

    wᵢ

a ogni punto.

Esempio concettuale:

    w₁ = 1.0
    w₂ = 1.0
    w₃ = 0.8
    ...

Questo permetterà di ridurre l'influenza
di landmark meno affidabili.

La gestione dei pesi non deve essere introdotta
prima di aver validato la registrazione base.

---

# 121. Prima fase: Global Alignment

La prima trasformazione da implementare
sarà una trasformazione globale.

Obiettivo:

    sovrapporre globalmente
    Canonical Mesh
    e
    volto reale.

La trasformazione comprenderà:

- traslazione;
- rotazione;
- scala.

---

# 122. Trasformazione similare

La trasformazione globale può essere rappresentata
come:

    rᵢ ≈ s R cᵢ + t

dove:

    cᵢ = Control Point canonico

    rᵢ = Control Point reale

    R = matrice di rotazione

    s = fattore di scala

    t = vettore di traslazione

---

# 123. Obiettivo matematico

Il sistema deve minimizzare:

    Σ wᵢ ||s R cᵢ + t - rᵢ||²

rispetto a:

    R
    s
    t

La prima implementazione dovrà preferire
un metodo numericamente stabile e ben noto
per la stima di una trasformazione similare 3D.

Una possibile soluzione è una variante
dell'allineamento Procrustes / Umeyama.

Questa scelta è una proposta progettuale
e dovrà essere validata durante l'implementazione.

---

# 124. Perché partire dalla trasformazione globale

La trasformazione globale permette di separare
due problemi differenti.

Problema 1:

    Dove si trova il volto?

Problema 2:

    Che forma ha il volto?

La prima fase risolve:

    posizione
    orientamento
    scala

La seconda fase risolverà:

    forma.

Questa separazione semplifica notevolmente
la validazione dell'algoritmo.

---

# 125. Test della Global Registration

Prima di utilizzare fotografie reali,
il sistema dovrà essere testato con una trasformazione
conosciuta artificialmente.

Procedura:

    Canonical Mesh
          ↓
    rotazione nota
          ↓
    scala nota
          ↓
    traslazione nota
          ↓
    Target Points

Il Registration Engine dovrà recuperare
una trasformazione equivalente entro
una tolleranza definita.

---

# 126. Errore di registrazione

Dopo la trasformazione globale deve essere
calcolato l'errore dei Control Points.

Per ogni punto:

    eᵢ = ||s R cᵢ + t - rᵢ||

Devono essere disponibili almeno:

    errore medio

    errore massimo

    errore RMS

Questi valori saranno fondamentali
per la diagnostica.

---

# 127. Registration Result

Il risultato della registrazione
non deve essere solamente una mesh.

Dovrà essere possibile rappresentare:

    RegistrationResult

contenente concettualmente:

    success
    transformation
    registered_mesh
    mean_error
    rms_error
    max_error
    diagnostics

Questo permetterà alla GUI futura
di mostrare informazioni comprensibili.

---

# 128. Seconda fase: Local Deformation

Dopo il Global Alignment
verrà applicata la deformazione locale.

Input:

    Global Aligned Canonical Mesh

e:

    Real Control Points

Output:

    Personalized Mesh

---

# 129. Problema della deformazione

Dopo l'allineamento globale:

    cᵢ'

non coinciderà necessariamente con:

    rᵢ

per tutti i punti.

Il sistema deve quindi determinare
uno spostamento:

    dᵢ = rᵢ - cᵢ'

per ogni Control Point.

Questi vettori rappresentano
i vincoli della deformazione.

---

# 130. Deformation Field

L'obiettivo è costruire una funzione:

    D(x)

che determini lo spostamento
di un qualsiasi punto della mesh.

Per un Control Point:

    D(cᵢ') ≈ dᵢ

Per un vertice generico:

    v'

diventa:

    v'' = v' + D(v')

---

# 131. Interpolazione della deformazione

Il campo di deformazione dovrà essere
interpolato dai 25 Control Points.

Il principio generale sarà:

    25 displacement constraints
              ↓
       deformation field
              ↓
        N mesh vertices

dove:

    N = tutti i vertici della Canonical Mesh.

---

# 132. Possibili algoritmi

Le famiglie di algoritmi da valutare
comprendono almeno:

    1. Radial Basis Functions
    2. Thin Plate Spline
    3. Laplacian Deformation
    4. ARAP
    5. altre tecniche di deformation
       compatibili con una mesh 3D.

La scelta non deve essere fatta
solamente sulla base della semplicità.

Devono essere confrontati:

- accuratezza;
- stabilità;
- deformazione globale;
- deformazione locale;
- comportamento fuori dai Control Points;
- preservazione della forma;
- prestazioni;
- robustezza.

---

# 133. Prima candidata: RBF / TPS

Una prima famiglia da testare sarà
quella delle interpolazioni radiali.

Il principio è:

    Control Point
          ↓
    displacement
          ↓
    radial influence
          ↓
    mesh vertices

Questa famiglia è interessante perché permette
di definire direttamente la posizione target
dei Control Points e interpolare la deformazione
sull'intera geometria.

La scelta definitiva non è ancora congelata.

---

# 134. Seconda candidata: Laplacian Deformation

Una seconda famiglia da valutare
è la deformazione Laplaciana.

Il vantaggio potenziale è la capacità
di preservare caratteristiche locali
della mesh durante la deformazione.

Potrebbe essere particolarmente interessante
per deformazioni anatomiche dove è importante
evitare che la superficie perda localmente
la propria struttura.

La sua complessità e il suo comportamento
dovranno essere valutati sul template MakeHuman.

---

# 135. Terza candidata: ARAP

ARAP:

    As-Rigid-As-Possible

potrà essere valutato per mantenere
localmente una forma il più possibile rigida
durante la deformazione.

Potrebbe risultare utile per zone
dove una deformazione eccessivamente liscia
produrrebbe perdita di dettaglio geometrico.

Anche questa soluzione non deve essere
considerata già scelta.

---

# 136. Criterio di scelta dell'algoritmo

Non verrà scelto un algoritmo
solo perché matematicamente elegante.

Dovrà essere costruito un test comparativo.

Input:

    stessa Canonical Mesh
    stesso set di 25 Control Points
    stessi displacement

Output:

    RBF/TPS
    Laplacian
    ARAP

Confrontare:

- errore Control Points;
- deviazione dei vertici;
- qualità della superficie;
- stabilità;
- tempo di esecuzione.

---

# 137. Test sintetico

Prima delle fotografie reali
verrà costruito un dataset artificiale.

Esempio:

    Canonical Mesh
          ↓
    deformazione nota
          ↓
    Target Control Points

Il sistema tenterà di ricostruire
la deformazione.

Questo permette di sapere
in anticipo quanto l'algoritmo
si discosta dal risultato atteso.

---

# 138. Test anatomico

Dopo il test sintetico:

    Canonical Mesh
          ↓
    25 Control Points reali
          ↓
    Registration
          ↓
    Personalized Mesh

Il risultato dovrà essere verificato
visivamente e numericamente.

---

# 139. Controllo delle deformazioni patologiche

L'algoritmo non deve solamente
far coincidere i 25 punti.

Potrebbe infatti produrre
una mesh geometricamente errata
pur rispettando perfettamente
i Control Points.

Devono quindi essere controllati:

- triangoli troppo deformati;
- inversione delle normali;
- self-intersections;
- collasso locale;
- stretching eccessivo;
- compressione eccessiva;
- curvature anomale.

---

# 140. Vincoli di deformazione

La deformazione potrà essere soggetta
a vincoli.

Esempi:

    distanza massima
    per vertice

    variazione massima
    di scala locale

    preservazione delle normali

    preservazione della topologia

Questi vincoli saranno introdotti
solo se i test dimostreranno
che sono necessari.

---

# 141. Preservazione della topologia

La deformazione non deve creare
una nuova topologia.

Deve essere:

    geometria modificata

su:

    topologia invariata.

Pertanto:

    vertices[i]

rimane:

    vertices[i]

anche dopo la deformazione.

Le facce continueranno
a utilizzare gli stessi indici.

---

# 142. Corrispondenza semantica dei vertici

Il vantaggio fondamentale della Canonical Mesh
sarà mantenere la corrispondenza topologica
tra soggetti differenti.

Esempio:

    Canonical Vertex 1000

può rappresentare una determinata zona
anatomica.

Dopo la deformazione:

    Subject A Vertex 1000

e:

    Subject B Vertex 1000

continueranno a rappresentare
la stessa posizione topologica.

Le coordinate saranno differenti.

---

# 143. Landmark non appartenenti ai 25 Control Points

I 25 punti non devono essere confusi
con tutti i landmark MediaPipe.

Una volta ottenuta la trasformazione
della Canonical Mesh sarà possibile
utilizzare anche gli altri landmark.

Per un landmark MediaPipe:

    Lⱼ

si potrà determinare
la posizione corrispondente
sulla mesh registrata.

Le strategie possibili comprendono:

    nearest vertex

oppure:

    nearest surface point

oppure:

    triangle + barycentric coordinates

---

# 144. Preferenza per la superficie

Quando sarà possibile, il sistema dovrebbe
preferire una rappresentazione sulla superficie
della mesh rispetto alla semplice associazione
al vertice più vicino.

Questo evita che:

    Landmark → Vertex

introduca un errore inutile
quando il landmark si trova
naturalmente all'interno di una faccia.

La scelta definitiva sarà effettuata
dopo i primi test della Canonical Mesh.

---

# 145. 468 Landmark dopo la registrazione

La pipeline futura potrà quindi essere:

    468 MediaPipe Landmarks
              ↓
       25 Control Points
              ↓
        Registration
              ↓
      Personalized Mesh
              ↓
    remaining landmarks
              ↓
    surface correspondence

Questo evita il lavoro manuale
di associare 468 punti.

---

# 146. Importante limite dei 25 Control Points

I 25 Control Points sono sufficienti
come struttura di controllo iniziale
per la registrazione del volto.

Non devono però essere considerati
sufficienti da soli per ricostruire
informazioni che non sono osservabili
nella fotografia.

In particolare:

- nuca;
- parte posteriore del cranio;
- retro delle orecchie;
- eventuali zone completamente nascoste.

non possono essere ricavate
direttamente da una fotografia frontale
solamente attraverso 25 landmark.

---

# 147. Ruolo del MakeHuman Prior

Per le regioni non osservabili
la mesh MakeHuman fungerà da prior geometrico.

Quindi:

    dati osservati
          +
    Canonical Mesh prior
          ↓
    Complete Head

La parte osservata dalla fotografia
potrà essere deformata maggiormente.

Le parti non osservate
dovranno mantenere maggiormente
la struttura canonica.

---

# 148. Confidence Map futura

In una fase avanzata potrà essere introdotta
una confidence map geometrica.

Ogni regione della mesh potrà avere
un livello di affidabilità:

    observed
    partially_observed
    inferred

Esempio:

    volto frontale
        → observed

    lato volto
        → partially_observed

    nuca
        → inferred

Questo permetterà di distinguere
la geometria misurata dalla geometria
derivata dal template.

---

# 149. Simmetria

Per le regioni non direttamente osservabili
potrà essere utilizzata la simmetria facciale
come informazione aggiuntiva.

La simmetria non deve però essere applicata
automaticamente a tutto il volto.

Un volto reale presenta asimmetrie.

La simmetria deve quindi essere utilizzata
come:

    prior

e non come:

    vincolo assoluto.

---

# 150. Complete Head Reconstruction

Dopo la deformazione del volto:

    Personalized Face Mesh
             ↓
    Head Reconstruction
             ↓
    Complete Head

Il processo dovrà utilizzare
la struttura MakeHuman come prior.

Le parti mancanti non devono essere
inventate arbitrariamente.

---

# 151. Boundary Reconstruction

La ricostruzione delle parti mancanti
dovrà partire dall'analisi dei boundary.

Il progetto dispone già di:

    MeshBoundaryAnalyzer

e il:

    HeadReconstructionBuilder

è predisposto per utilizzare
questa informazione.

Attualmente il builder analizza
i boundary ma non completa ancora
la geometria. :contentReference[oaicite:2]{index=2}

---

# 152. Evoluzione del HeadReconstructionBuilder

La futura evoluzione potrà essere:

    BoundaryDetector
          ↓
    Region Classifier
          ↓
    Head Reconstruction
          ↓
    Ear Reconstruction
          ↓
    Neck Reconstruction
          ↓
    Hole Filling
          ↓
    Validation

La struttura esatta dovrà essere
definita durante gli Sprint dedicati.

---

# 153. Non modificare prematuramente il Builder

Il HeadReconstructionBuilder
non deve essere trasformato immediatamente
nel contenitore di tutti gli algoritmi.

Quando verranno introdotti nuovi algoritmi
dovranno essere verificati:

    responsabilità

    dipendenze

    riutilizzabilità

    posizione architetturale.

Se una responsabilità diventa autonoma,
deve essere estratta in un componente dedicato.

---

# 154. Ricostruzione della testa e fotografia

La fotografia reale fornisce
informazioni principalmente sul lato osservabile.

Il sistema dovrà quindi distinguere:

    geometria osservata

da:

    geometria inferita.

La Canonical Mesh permette di completare
la parte non osservabile senza creare
una mesh priva di struttura.

---

# 155. Texture Projection

La texture verrà applicata
solo dopo la stabilizzazione
della geometria.

Sequenza:

    Personalized Mesh
          ↓
    Camera Model
          ↓
    UV Projection
          ↓
    Texture
          ↓
    Material

Non deve essere utilizzata la texture
per correggere errori geometrici.

---

# 156. Geometria prima della texture

Una mesh geometricamente corretta
con texture imperfetta può essere migliorata.

Una mesh geometricamente errata
con una texture perfetta rimane errata.

Pertanto:

    Geometry
        >
    Texture

nelle priorità di sviluppo.

---

# 157. Validazione finale della Personalized Mesh

La mesh personalizzata dovrà essere
validata prima della texture.

Controlli:

- numero vertici;
- numero facce;
- topologia;
- normali;
- self-intersections;
- Control Point error;
- bounding box;
- dimensioni;
- continuità.

---

# 158. Metriche della ricostruzione

Il sistema dovrà progressivamente introdurre
metriche quantitative.

Almeno:

    Control Point RMS Error

    Control Point Mean Error

    Control Point Max Error

In futuro:

    Surface Distance

    Hausdorff Distance

    Curvature Error

    Local Deformation Error

---

# 159. Visualizzazione diagnostica

Il MeshViewer dovrà poter visualizzare
in futuro:

    Canonical Mesh
          +
    Target Points
          +
    Registered Points
          +
    Error vectors

Esempio concettuale:

        ● target
        ↑
        │ error
        │
        ● registered

Questo permetterà di individuare
immediatamente i punti problematici.

---

# 160. Error Heatmap

In una fase avanzata potrà essere realizzata
una heatmap sulla mesh.

Ogni vertice potrà essere associato
a un valore di errore.

Esempio concettuale:

    errore basso
        ↓
    mesh corretta

    errore alto
        ↓
    regione problematica

La heatmap sarà uno strumento diagnostico,
non un elemento necessario
alla prima implementazione.

---

# 161. Validazione visuale

Ogni versione dell'algoritmo di deformazione
dovrà essere verificata almeno con:

    3D Mesh
        +
    Control Points
        +
    Wireframe

La modalità Wireframe sarà particolarmente utile
per individuare:

- stretching;
- collassi;
- deformazioni irregolari;
- triangoli distorti.

---

# 162. Benchmark degli algoritmi

Prima di congelare
il Local Deformation Engine:

    RBF/TPS
       vs
    Laplacian
       vs
    ARAP

devono essere confrontati
su un dataset controllato.

Il benchmark deve essere ripetibile.

---

# 163. Decisione dell'algoritmo

Il risultato del benchmark dovrà produrre
una decisione documentata.

Esempio:

    Selected Algorithm:
        Thin Plate Spline

    Reason:
        migliore accuratezza
        con 25 Control Points

oppure:

    Selected Algorithm:
        ARAP

    Reason:
        migliore preservazione
        della geometria locale.

La decisione dovrà essere documentata
nel CHANGELOG / ADR / documentazione tecnica.

---

# 164. Algoritmo non congelato prematuramente

Fino alla conclusione del benchmark:

    Registration Algorithm
        = NOT FROZEN

Questo è intenzionale.

La struttura del progetto deve essere preparata
per permettere la sostituzione dell'algoritmo
senza modificare:

- GUI;
- Canonical Mapping;
- Vertex Mapper;
- MediaPipe Provider.

---

# 165. Interfaccia dell'algoritmo

La futura interfaccia concettuale potrà essere:

    RegistrationEngine.register(
        canonical_model,
        target_landmarks
    )

con risultato:

    RegistrationResult

La specifica definitiva dovrà essere verificata
contro le classi già presenti nel progetto
prima della creazione di nuovi file.

---

# 166. Pipeline matematica completa

La pipeline prevista sarà:

    Canonical Mapping
          ↓
    Canonical Control Points
          ↓
    Real MediaPipe Control Points
          ↓
    Coordinate Normalization
          ↓
    Global Alignment
          ↓
    Alignment Error
          ↓
    Local Displacement
          ↓
    Deformation Field
          ↓
    Personalized Mesh
          ↓
    Geometry Validation
          ↓
    Complete Head Reconstruction

---

# 167. Principio fondamentale

I 25 Control Points non "creano"
direttamente tutti i vertici.

Creano i vincoli necessari
a determinare come deformare
una mesh che possiede già
tutti i vertici.

Quindi:

    25 punti
       ↓
    vincoli
       ↓
    algoritmo geometrico
       ↓
    N vertici

e non:

    25 punti
       ↓
    468 punti
       ↓
    N vertici

---

# 168. Obiettivo finale della registrazione

Il risultato ideale sarà:

    Canonical Mesh
         ↓
    Global Alignment
         ↓
    Local Deformation
         ↓
    Personalized Mesh

dove:

    topology = Canonical topology

e:

    geometry = Subject geometry

Questa distinzione è fondamentale
per tutta l'evoluzione futura
di Face3D Studio AI.

---

# 169. Condizione per procedere alla fotografia reale

Non utilizzare fotografie reali
come test principale finché non saranno
superati:

    Test Mapping
        ↓
    Test Canonical Mesh
        ↓
    Test Global Alignment
        ↓
    Test Synthetic Deformation
        ↓
    Test Local Deformation
        ↓
    Test Geometry Validation

Solo dopo:

    Real Photograph Test

---

# 170. Milestone tecnica

La milestone più importante della fase
sarà:

    "Canonical Mesh Registration v1"

La milestone sarà raggiunta quando
sarà possibile:

    caricare Canonical Mesh
          ↓
    caricare Canonical Mapping
          ↓
    ricevere 25 target points
          ↓
    allineare la mesh
          ↓
    deformarla
          ↓
    ottenere Personalized Mesh
          ↓
    calcolare errore
          ↓
    validare la geometria

senza intervento manuale del Vertex Mapper.

---

# 171. Milestone successiva

La seconda grande milestone sarà:

    "Complete Head Reconstruction v1"

con:

    Personalized Face
          ↓
    Head Extension
          ↓
    Cranial Geometry
          ↓
    Ears
          ↓
    Neck
          ↓
    Closed Head

---

# 172. Milestone finale della prima pipeline

La prima pipeline completa sarà:

    Single Photograph
          ↓
    MediaPipe
          ↓
    25 Control Points
          ↓
    Canonical Mesh
          ↓
    Registration
          ↓
    Deformation
          ↓
    Complete Head
          ↓
    Texture
          ↓
    Export

Il risultato costituirà la prima versione
funzionale della ricostruzione 3D
da fotografia singola.

---

# 173. VERTEX MAPPER — COMPLETATO

Il Vertex Mapper è stato completato durante
lo Sprint 18 ed è ora lo strumento operativo
per la costruzione manuale del Canonical Mapping.

Il lavoro manuale è limitato ai Control Points
selezionati dal catalogo standard del progetto.

Obiettivo del workflow:

    MediaPipe Landmark
            ↕
    MakeHuman Vertex

Il Vertex Mapper consente di:

- selezionare il Control Point;
- utilizzare la mappa MediaPipe come riferimento anatomico;
- selezionare il vertice MakeHuman;
- creare l'associazione;
- verificare un'associazione esistente;
- dissociare un'associazione;
- correggere un'associazione errata;
- visualizzare il punto associato;
- mantenere le associazioni durante la sessione;
- mantenere le associazioni dopo la chiusura e riapertura
  della finestra;
- utilizzare Mesh, Wireframe e Point;
- utilizzare zoom, PAN e rotazione;
- verificare il modello attraverso il MeshViewer.

La mappa MediaPipe interattiva consente inoltre
di identificare i 25 Control Points e di sincronizzare
la selezione con il Vertex Mapper.

Il Vertex Mapper rappresenta quindi lo strumento
di calibrazione manuale necessario alla costruzione
del Canonical Mapping.

La persistenza definitiva del Canonical Mapping
su file è stata implementata e verificata.

La validazione anatomica e geometrica completa
delle 25 associazioni rimane una attività da completare
prima dell'utilizzo del mapping nel Registration Engine.

---

# 174. Stato persistente del Vertex Mapper

La VertexMappingCollection non deve essere considerata
solamente uno stato temporaneo della finestra.

Le associazioni devono poter sopravvivere
alla chiusura e riapertura del Vertex Mapper.

Questo è necessario perché la costruzione
della Canonical Mesh può richiedere più sessioni.

---

# 175. Salvataggio del Canonical Mapping

Il mapping può essere serializzato attraverso
la persistenza del progetto.

Il formato utilizzato è:

    JSON

integrato nel:

    project.json

Il file contiene almeno:

    landmark_index
    landmark_name
    vertex_index
    vertex_coordinates

ed eventualmente:

    confidence
    notes
    mapping_version

---

# 176. Caricamento del Canonical Mapping

All'apertura del progetto:

    project.json
          ↓
    ProjectLoader
          ↓
    CanonicalMapping
          ↓
    Project
          ↓
    Vertex Mapper
          ↓
    GUI

Le associazioni precedenti vengono ricaricate
automaticamente quando disponibili.

Il sistema non richiede di ripetere associazioni
già effettuate e salvate nel progetto.

La persistenza è stata verificata con chiusura
completa dell'applicazione e successiva riapertura
del progetto.

---

# 177. Validazione del Mapping

Prima di considerare valido il Canonical Mapping:

- ogni landmark deve essere univoco;
- ogni vertex deve essere valido;
- il vertex deve esistere nella mesh;
- non devono esistere associazioni duplicate;
- il template deve essere quello previsto;
- la versione del mapping deve essere compatibile.

---

# 178. Versionamento del Mapping

Il Canonical Mapping deve essere associato
alla versione della Canonical Mesh.

Esempio:

    canonical_mesh_version = 1.0
    mapping_version = 1.0

Se cambia la topologia della Canonical Mesh,
il mapping potrebbe non essere più valido.

In quel caso il sistema deve rilevare
l'incompatibilità invece di utilizzare
silenziosamente dati errati.

---

# 179. Report del Mapping

Il Vertex Mapper dovrà poter produrre
un report completo.

Il report dovrà contenere:

    landmark
    index
    vertex
    coordinate
    stato

Esempio:

    NOSE_TIP (4)
        Vertex: 12345
        X: ...
        Y: ...
        Z: ...
        Status: ASSOCIATED

Il report potrà essere visualizzato
in una finestra separata oppure esportato.

---

# 180. Interfaccia diagnostica del Vertex Mapper

La GUI definitiva deve mantenere
una distinzione tra:

    punto corrente

e:

    storico completo.

Il punto corrente deve essere sempre
immediatamente leggibile.

Lo storico completo deve essere accessibile
separatamente.

Questo evita che una lunga lista di operazioni
renda difficile comprendere lo stato corrente.

---

# 181. Stato visuale dei punti

La visualizzazione deve distinguere almeno:

    punto selezionato
    punto associato
    punto da associare
    punto selezionato per dissociazione

Il colore azzurro utilizzato per i punti
già associati deve rimanere parte
della semantica visuale del Vertex Mapper.

---

# 182. Dissociazione

La dissociazione deve essere una operazione
esplicita.

Procedura:

    landmark associato
          ↓
    selezione landmark
          ↓
    visualizzazione vertex associato
          ↓
    Dissocia
          ↓
    mapping rimosso

Dopo la dissociazione:

    landmark = NON ASSOCIATO

e il Vertex Mapper deve tornare
nello stato corretto per una nuova associazione.

---

# 183. Protezione dalle associazioni duplicate

Se un landmark è già associato:

    Associa = DISABLED

    Dissocia = ENABLED

Il sistema non deve consentire
una nuova associazione sullo stesso landmark.

Questo evita che l'utente scopra l'errore
solamente dopo aver premuto "Associa".

---

# 184. Selezione di un landmark già associato

Quando l'utente seleziona dalla combo
un landmark già associato:

    recuperare vertex associato

    visualizzarlo

    evidenziarlo

    mostrare le sue informazioni

    abilitare Dissocia

    disabilitare Associa

Questo permette di verificare
visivamente l'associazione prima
di modificarla.

---

# 185. Controllo finale dei 25 punti

Prima di congelare il Canonical Mapping:

    25 / 25

devono risultare associati.

Il sistema dovrà mostrare:

    Associated:
        25

    Missing:
        0

---

# 186. Canonical Mapping v1

Milestone:

    CANONICAL MAPPING v1

Condizioni:

- tutti i Control Points definiti;
- tutte le associazioni validate;
- nessun duplicato;
- mapping salvabile;
- mapping ricaricabile;
- template identificato;
- report disponibile.

Da questo momento il mapping diventa
un asset del progetto.

---

# 187. CANONICAL MESH

La Canonical Mesh sarà il modello MakeHuman
utilizzato come riferimento geometrico.

Deve essere trattata come un asset fondamentale.

Dovranno essere documentati:

    nome
    origine
    versione
    numero vertici
    numero facce
    coordinate system
    scala
    unità di misura
    topologia

---

# 188. Canonical Mesh Integrity

Prima dell'utilizzo nel Reconstruction Engine
devono essere verificati:

- vertici validi;
- triangoli validi;
- indici validi;
- assenza di NaN;
- assenza di Inf;
- normali;
- winding;
- componenti connesse;
- bounding box.

---

# 189. Canonical Mesh Analyzer

Il progetto dispone già di una struttura
di analisi del template.

Il TemplateAnalyzer dovrà progressivamente
diventare il punto di raccolta
delle informazioni diagnostiche
sulla Canonical Mesh.

Non deve diventare però
un contenitore generico di algoritmi.

---

# 190. Coordinate System

Il sistema di coordinate della Canonical Mesh è stato verificato
sul modello realmente utilizzato dal progetto.

Convenzione Face3D Studio:

    X = asse laterale
        +X = destra anatomica
        -X = sinistra anatomica

    Y = asse verticale
        +Y = alto
        -Y = basso

    Z = asse di profondità
        +Z = anteriore / fronte
        -Z = posteriore / nuca

La Canonical Mesh mantiene le coordinate originali del template.

Il centraggio effettuato dal MeshViewer, quando presente,
è considerato esclusivamente una trasformazione di visualizzazione
e non modifica il sistema di coordinate canonico.

Stato:

    VERIFIED

# 191. MediaPipe Coordinate Conversion

Le coordinate MediaPipe
non devono essere utilizzate direttamente
come coordinate MakeHuman.

Dovrà essere presente
una fase esplicita di conversione:

    MediaPipe Coordinates
             ↓
    Coordinate Normalization
             ↓
    Face3D Coordinate System

La conversione deve essere documentata
e testata durante l'implementazione della Registration Engine
e del Global Alignment.

Non viene introdotta una conversione arbitraria nello Sprint 23.

---

# 192. Scale Normalization

MediaPipe fornisce coordinate
in un sistema differente dalla mesh.

Sarà quindi necessario determinare
una relazione di scala.

La scala globale dovrà essere stimata
durante il Global Alignment
e non codificata arbitrariamente.

---

# 193. REGISTRATION ENGINE

Il Registration Engine sarà responsabile
della trasformazione della Canonical Mesh.

Responsabilità:

- preparazione Control Points;
- validazione;
- Global Alignment;
- calcolo errore;
- Local Deformation;
- produzione RegistrationResult.

La GUI non deve contenere
la matematica della registrazione.

---

# 194. Separazione GUI / Engine

La struttura deve rimanere:

    GUI
      ↓
    ApplicationController
      ↓
    Controllers
      ↓
    Managers / Services
      ↓
    Reconstruction / Registration Engine
      ↓
    Models

Il Vertex Mapper deve quindi rimanere
uno strumento GUI.

Non deve diventare
il contenitore del Registration Engine.

---

# 195. Registration Controller

Quando la registrazione verrà integrata
nell'applicazione principale:

    GUI
      ↓
    ReconstructionController
      ↓
    RegistrationEngine
      ↓
    CanonicalMesh
      +
    MediaPipe Landmarks
      ↓
    PersonalizedMesh

---

# 196. RegistrationResult

Il risultato dovrà essere indipendente
dalla GUI.

Dovrà poter essere utilizzato da:

- GUI;
- test;
- export;
- diagnostica;
- pipeline automatica.

---

# 197. Test Registration Engine

Test obbligatori:

    test_identity_registration

    test_translation

    test_rotation

    test_scale

    test_combined_transform

    test_known_deformation

    test_invalid_control_points

    test_duplicate_control_points

    test_missing_control_points

---

# 198. Tolleranze

I test numerici devono utilizzare
tolleranze esplicite.

Non:

    result == expected

ma:

    abs(result - expected) < tolerance

Le tolleranze dovranno essere documentate.

---

# 199. Synthetic Dataset

Dovrà essere creato un piccolo dataset
di test sintetico.

Il dataset deve permettere
di verificare la pipeline senza
dipendere da fotografie reali.

Questo permetterà di distinguere:

    bug dell'algoritmo

da:

    problemi del rilevamento MediaPipe.

---

# 200. LOCAL DEFORMATION ENGINE

Dopo il Global Alignment:

    canonical aligned mesh
             +
    displacement constraints
             ↓
    Local Deformation Engine
             ↓
    personalized mesh

L'algoritmo definitivo verrà scelto
sulla base dei benchmark definiti
negli Sprint precedenti.

---

# 201. Deformation Safety

Ogni deformazione deve essere controllata.

Il sistema deve poter rilevare:

- vertici fuori scala;
- triangoli degenerati;
- inversione delle facce;
- self-intersection;
- deformazione eccessiva.

Una deformazione non valida
non deve essere esportata
come risultato corretto.

---

# 202. COMPLETE HEAD RECONSTRUCTION

Dopo la personalizzazione del volto:

    Personalized Face
          ↓
    Head Reconstruction Builder
          ↓
    Complete Head

La ricostruzione utilizzerà
la Canonical Mesh MakeHuman
come struttura di riferimento.

---

# 203. Cranial Reconstruction

La parte cranica dovrà essere
ricostruita preservando la struttura
del modello canonico.

Le informazioni del volto reale
modificheranno la regione osservata.

La parte non osservata
sarà maggiormente vincolata
alla Canonical Mesh.

---

# 204. Ear Reconstruction

Le orecchie dovranno essere
trattate come regioni anatomiche
specifiche.

Dovranno essere valutate:

- posizione;
- scala;
- inclinazione;
- simmetria;
- collegamento con il cranio.

Non devono essere semplicemente
estruse dal volto.

---

# 205. Neck Reconstruction

Il collo dovrà essere
ricostruito utilizzando
la struttura MakeHuman come prior.

La transizione:

    testa → collo

deve essere continua.

Devono essere evitati:

- buchi;
- intersezioni;
- discontinuità;
- triangoli degenerati.

---

# 206. Hole Filling

Qualunque boundary residuo
deve essere rilevato.

Il sistema deve distinguere:

    boundary previsto

da:

    boundary patologico.

Non tutti i boundary rappresentano
un errore.

---

# 207. Complete Head Validation

La testa completa deve essere
validata con:

- topologia;
- normali;
- boundary;
- self-intersection;
- manifoldness;
- continuità;
- dimensioni.

---

# 208. TEXTURE PIPELINE

La texture sarà sviluppata
solamente dopo la stabilizzazione
della geometria.

Pipeline:

    Image
      ↓
    Face Detection
      ↓
    MediaPipe
      ↓
    Registration
      ↓
    Personalized Mesh
      ↓
    UV Mapping
      ↓
    Texture Projection
      ↓
    Material
      ↓
    Export

---

# 209. UV Mapping

La Canonical Mesh dovrà avere
un sistema UV coerente.

Quando la topologia rimane invariata:

    Canonical UV
          ↓
    Personalized Mesh

potrà essere mantenuto.

Questo rappresenta uno dei principali
vantaggi della Canonical Mesh.

---

# 210. Texture Projection

La fotografia reale dovrà essere
proiettata sulla mesh.

Dovranno essere valutati:

- camera model;
- projection;
- occlusioni;
- stretching;
- aree non visibili;
- blending.

---

# 211. Texture Confidence

Come per la geometria,
la texture potrà avere
una confidence.

Zone osservate:

    alta confidence

Zone non osservate:

    bassa confidence

Per queste ultime potrà essere utilizzata
una strategia di completamento.

---

# 212. MULTI-VIEW FUTURO

L'architettura dovrà possibilmente
permettere in futuro:

    fotografia frontale
          +
    fotografia laterale
          +
    fotografia posteriore

Questo non deve essere implementato
nella prima versione.

La pipeline però non deve essere progettata
in modo da impedirlo.

---

# 213. Multi-view Registration

In una futura evoluzione:

    Image 1
       ↓
    Landmarks 1

    Image 2
       ↓
    Landmarks 2

    Image 3
       ↓
    Landmarks 3

            ↓

    Combined Constraints

            ↓

    Personalized Mesh

Questo permetterà di ridurre
la quantità di geometria inferita.

---

# 214. EXPORT

La pipeline dovrà poter esportare
la Personalized Mesh.

Formati iniziali da valutare:

    OBJ
    STL

e successivamente:

    GLB / GLTF

se necessario.

---

# 215. OBJ Export

L'OBJ dovrà contenere
almeno:

- vertices;
- faces;
- normals;
- UV quando disponibili;
- material reference quando disponibile.

---

# 216. STL Export

Lo STL sarà destinato
principalmente alla geometria.

Non conserva:

- texture;
- UV;
- materiali complessi.

Dovrà quindi essere considerato
un formato geometrico.

---

# 217. GLTF / GLB

In una fase successiva,
GLTF/GLB potrà diventare
il formato preferenziale
per visualizzazione moderna.

Potrà contenere:

- mesh;
- materiali;
- texture;
- UV;
- informazioni necessarie
  al rendering.

---

# 218. PROJECT VALIDATION

Prima della prima release
dovrà essere eseguita
una validazione completa.

Pipeline:

    application startup
          ↓
    MediaPipe
          ↓
    Canonical Mesh
          ↓
    Mapping
          ↓
    Registration
          ↓
    Deformation
          ↓
    Head Reconstruction
          ↓
    Texture
          ↓
    Export

---

# 219. Regression Tests

Ogni modifica significativa
dovrà essere verificata contro
le funzionalità già funzionanti.

Particolare attenzione a:

- MeshViewer;
- VertexPicker;
- Vertex Mapper;
- mapping persistence;
- mesh modes;
- camera;
- lighting;
- pan;
- zoom;
- selection;
- dissociation.

---

# 220. OpenGL Regression

Il problema già riscontrato
con la riapertura della finestra
e la perdita della mesh
deve essere considerato
un caso di regression test.

Test:

    open
      ↓
    visualize
      ↓
    close
      ↓
    reopen
      ↓
    visualize again

Ripetere più volte.

---

# 221. Mesh Mode Regression

Verificare:

    Mesh
    Wireframe
    Point

e tutte le transizioni:

    Mesh → Wire → Point → Mesh

senza perdere:

- mesh;
- camera;
- selected point;
- highlighted point.

---

# 222. Selection Regression

Verificare:

    select landmark
        ↓
    highlight vertex
        ↓
    switch mode
        ↓
    highlight remains

Il punto associato deve rimanere
visualmente identificabile.

---

# 223. Mapping Persistence Regression

Verificare:

    associazione
        ↓
    chiusura finestra
        ↓
    riapertura
        ↓
    associazione ancora presente

Questo deve funzionare
anche dopo più sessioni.

---

# 224. Final Vertex Mapper Test

Scenario completo:

    25 landmark
       ↓
    associazione progressiva
       ↓
    chiusura
       ↓
    riapertura
       ↓
    controllo
       ↓
    dissociazione
       ↓
    nuova associazione
       ↓
    salvataggio
       ↓
    reload
       ↓
    verifica finale

---

# 225. Performance

La pipeline dovrà essere misurata
su almeno una Canonical Mesh reale.

Metriche:

    load time
    mapping load time
    registration time
    deformation time
    reconstruction time
    export time

---

# 226. Logging

Il logging deve essere utile
alla diagnosi ma non invadente.

Devono essere distinguibili:

    INFO
    WARNING
    ERROR

I messaggi diagnostici temporanei
utilizzati durante lo sviluppo
dovranno essere progressivamente
rimossi o trasformati in logging strutturato.

---

# 227. Error Handling

Gli errori prevedibili
devono produrre messaggi comprensibili.

Esempi:

    Canonical Mesh non trovata

    Mapping non trovato

    Mapping incompatibile

    Landmark mancante

    Control Point duplicato

    Registration fallita

    Mesh non valida

L'applicazione non deve terminare
con traceback non gestiti
per errori prevedibili.

---

# 228. DOCUMENTAZIONE TECNICA

Dovranno essere mantenuti aggiornati:

    README.md

    ROADMAP.md

    CHANGELOG.md

    documentazione architetturale

    documentazione del Canonical Mapping

    documentazione degli algoritmi

---

# 229. Architecture Decision Records

Le decisioni architetturali importanti
dovranno essere documentate.

In particolare:

- scelta dei 25 Control Points;
- scelta Canonical Mesh;
- algoritmo Global Registration;
- algoritmo Local Deformation;
- strategia Complete Head;
- strategia Texture;
- formato Canonical Mapping.

---

# 230. Frozen Architecture

L'architettura generale rimane:

    GUI
      ↓
    ApplicationController
      ↓
    Controllers
      ↓
    Managers / Services
      ↓
    Models

Non introdurre redesign architetturali
senza una reale necessità tecnica.

---

# 231. PRINCIPIO DI SVILUPPO

Una modifica alla volta.

Dopo ogni modifica:

    modifica
       ↓
    test
       ↓
    verifica
       ↓
    commit

Non accumulare numerose modifiche
non testate.

---

# 232. FULL FILE POLICY

Quando viene modificato un file:

    fornire il file completo

e non una patch parziale,

salvo quando una modifica limitata
sia esplicitamente richiesta
e non rischi di compromettere
le funzionalità esistenti.

---

# 233. Regression First

Prima di aggiungere
una nuova funzionalità:

    verificare stato attuale.

Dopo la modifica:

    ripetere i test precedenti.

La nuova funzionalità non deve
rompere una funzionalità già validata.

---

# 234. VERSIONING

Ogni milestone importante
deve produrre una versione identificabile.

Esempio:

    0.x
        sviluppo

    1.0
        prima pipeline funzionante

Successivamente:

    1.1
    1.2
    ...

con versioning documentato.

---

# 235. GIT WORKFLOW

Ogni milestone significativa
deve essere accompagnata da commit.

Formato consigliato:

    feat:
    fix:
    refactor:
    test:
    docs:

Esempio:

    feat: implement canonical registration

---

# 236. RELEASE CHECKLIST

Prima di una release:

    [ ] application startup
    [ ] MediaPipe
    [ ] Canonical Mesh
    [ ] Vertex Mapper
    [ ] Mapping persistence
    [ ] Global Registration
    [ ] Local Deformation
    [ ] Geometry Validation
    [ ] Head Reconstruction
    [ ] Texture
    [ ] OBJ Export
    [ ] STL Export
    [ ] Regression tests
    [ ] Documentation
    [ ] Git commit/tag

---

# 237. ROADMAP FINALE DEL PROGETTO

La sequenza complessiva diventa:

    PHASE 1
    Foundation
        ↓

    PHASE 2
    MediaPipe
        ↓

    PHASE 3
    MakeHuman / Canonical Mesh
        ↓

    PHASE 4
    Vertex Mapper
        ↓

    PHASE 5
    Canonical Mapping
        ↓

    PHASE 6
    Global Registration
        ↓

    PHASE 7
    Local Deformation
        ↓

    PHASE 8
    Complete Head Reconstruction
        ↓

    PHASE 9
    Texture
        ↓

    PHASE 10
    Export
        ↓

    PHASE 11
    Validation
        ↓

    PHASE 12
    Release

---

# 238. OBIETTIVO FINALE DI FACE3D STUDIO AI

L'obiettivo finale del progetto è:

    FOTO REALE
        ↓
    MediaPipe
        ↓
    468 LANDMARKS
        ↓
    25 CONTROL POINTS
        ↓
    CANONICAL MAPPING
        ↓
    MAKEHUMAN CANONICAL MESH
        ↓
    GLOBAL REGISTRATION
        ↓
    LOCAL DEFORMATION
        ↓
    PERSONALIZED FACE
        ↓
    COMPLETE HEAD
        ↓
    TEXTURE
        ↓
    3D MODEL
        ↓
    OBJ / STL / GLB

---

# 239. CONCETTO FONDAMENTALE DEL PROGETTO

Face3D Studio AI non deve essere considerato
semplicemente un convertitore:

    fotografia → mesh.

Il progetto deve essere considerato
un sistema di:

    osservazione
        +
    corrispondenza
        +
    registrazione
        +
    deformazione
        +
    ricostruzione.

La Canonical Mesh rappresenta
il riferimento geometrico.

I MediaPipe Landmarks rappresentano
le osservazioni.

I 25 Control Points rappresentano
i vincoli manuali iniziali.

Il Registration Engine rappresenta
il collegamento matematico tra
osservazione e geometria.

---

# 240. RISULTATO ATTESO

Il risultato finale dovrà essere
una mesh 3D completa che:

- mantiene la topologia Canonical;
- rappresenta la forma del soggetto;
- utilizza i landmark MediaPipe;
- utilizza i 25 Control Points come vincoli;
- ricostruisce le regioni non osservabili
  utilizzando il modello canonico;
- può essere texturizzata;
- può essere esportata;
- può essere riutilizzata
  per successive elaborazioni.

---

# 241. DEFINIZIONE DELLA CANONICAL MESH

La Canonical Mesh non è semplicemente
il modello MakeHuman originale.

È:

    MakeHuman
        +
    Canonical Mapping
        +
    coordinate validation
        +
    topology validation
        +
    landmark correspondence

Questa combinazione costituisce
il riferimento geometrico ufficiale
di Face3D Studio AI.

---

# 242. DEFINIZIONE DEL PERSONALIZED MESH

La Personalized Mesh è:

    Canonical Mesh
        +
    Global Alignment
        +
    Local Deformation

mantenendo:

    topology

e modificando:

    geometry.

---

# 243. DEFINIZIONE DELLA COMPLETE HEAD

La Complete Head è:

    Personalized Mesh
        +
    inferred geometry
        +
    cranial reconstruction
        +
    ears
        +
    neck
        +
    hole closure

utilizzando il modello canonico
come prior per le regioni
non direttamente osservate.

---

# 244. PRINCIPIO DI CONSERVAZIONE DELLA TOPOLOGIA

Finché tecnicamente possibile:

    non cambiare topology.

Questo permette di mantenere:

    vertex correspondence
    UV correspondence
    landmark correspondence
    semantic regions

tra Canonical Mesh
e Personalized Mesh.

---

# 245. POSSIBILE EVOLUZIONE FUTURA

Una volta completata la prima pipeline:

    Single View Reconstruction

potranno essere sviluppati:

    Multi View Reconstruction

    Automatic Canonical Mapping

    Statistical Face Model

    Automatic Control Point Refinement

    Texture Completion

    Expression Transfer

    Facial Animation

    Blendshape Generation

    3D Character Generation

Queste funzionalità non fanno parte
della prima release.

---

# 246. AUTOMATIC CANONICAL MAPPING — FUTURO

Il Vertex Mapper manuale serve a costruire
il primo mapping affidabile.

Una volta ottenuto un Canonical Mapping
validato, potrà essere utilizzato
come dataset di riferimento
per sviluppare una procedura
di mapping automatica.

Questa funzionalità sarà affrontata
solo dopo aver stabilizzato
la pipeline manuale.

---

# 247. MACHINE LEARNING — FUTURO

Un eventuale modello ML futuro
potrà imparare:

    MediaPipe Landmarks
          ↓
    Canonical Mesh deformation

ma non deve essere introdotto
prima di avere una pipeline
deterministica funzionante.

La pipeline deterministica
costituirà il baseline.

---

# 248. BASELINE DETERMINISTICO

Prima:

    deterministic registration

poi:

    automatic optimization

poi eventualmente:

    machine learning.

Questo ordine permette di avere
un riferimento verificabile
in ogni fase.

---

# 249. CRITERIO DI SUCCESSO DEL PROGETTO

Il progetto sarà considerato
funzionalmente riuscito quando
una fotografia reale potrà essere
trasformata automaticamente in:

    Personalized Complete Head

utilizzando:

    MediaPipe
    +
    Canonical Mapping
    +
    MakeHuman Canonical Mesh

con errori geometrici misurabili
e una pipeline ripetibile.

---

# 250. FINE ROADMAP

Il completamento della prima roadmap
non rappresenta la fine del progetto.

Rappresenta il completamento
della prima pipeline:

    PHOTO
      ↓
    LANDMARKS
      ↓
    CANONICAL REGISTRATION
      ↓
    DEFORMATION
      ↓
    COMPLETE HEAD
      ↓
    TEXTURE
      ↓
    EXPORT

Da questo punto il progetto potrà evolvere
verso sistemi più avanzati di:

    automatic reconstruction
    multi-view reconstruction
    statistical modeling
    animation
    expression transfer
    AI-based reconstruction.

---

# 251. REGOLA FINALE DI SVILUPPO

La priorità assoluta rimane:

    CORRETTEZZA
        >
    STABILITÀ
        >
    TESTABILITÀ
        >
    PRESTAZIONI
        >
    NUOVE FUNZIONALITÀ

Non sacrificare una funzionalità
già funzionante per introdurne una nuova
senza prima averne compreso
la reale necessità tecnica.

---

# 252. STATO DEL ROADMAP

Il presente documento rappresenta
la roadmap di riferimento del progetto.

Gli Sprint completati devono essere
marcati progressivamente come:

    [x] COMPLETATO

Gli Sprint in lavorazione:

    [>] IN CORSO

Gli Sprint futuri:

    [ ] DA FARE

Il ROADMAP.md deve essere aggiornato
al termine di ogni milestone significativa.

---

# 253. PROSSIMO STEP OPERATIVO

Lo Sprint 19 è stato completato.

Il Canonical Mapping definitivo contiene:

    25 / 25 Control Points
    status = COMPLETE

Sono state inoltre completate le verifiche
geometriche e topologiche preliminari sul template
`male1591/head`.

In particolare sono stati verificati:

    [x] 1604 vertici
    [x] 3064 triangoli
    [x] coordinate senza NaN
    [x] coordinate senza Inf
    [x] indici triangolari validi
    [x] triangoli non degenerati
    [x] assenza di vertici duplicati
    [x] 6 componenti connesse identificate
    [x] bounding box della componente principale
    [x] distribuzione dei Control Points
    [x] coordinate normalizzate
    [x] verifica della simmetria bilaterale

La verifica della simmetria ha evidenziato una sola
piccola asimmetria locale:

    right_eye_outer ↔ left_eye_outer
    errore normalizzato = 0.0117

Il valore è stato registrato come caratteristica
da monitorare e non come errore invalidante.

---

## Mapping definitivo

Le 25 associazioni definitive sono:

    1    nose_bridge           → vertex 216
    2    nose_lower_center    → vertex 531
    4    nose_tip             → vertex 537
    10   forehead_center      → vertex 534
    13   upper_lip_center     → vertex 536
    14   lower_lip_center     → vertex 259
    33   right_eye_outer      → vertex 211
    46   right_eyebrow_inner  → vertex 85
    55   right_eyebrow_outer  → vertex 82
    61   mouth_right          → vertex 62
    78   upper_lip_right      → vertex 55
    98   nose_right_base      → vertex 92
    133  right_eye_inner      → vertex 26
    145  right_eye_lower      → vertex 1323
    152  chin                 → vertex 487
    159  right_eye_upper      → vertex 1379
    263  left_eye_outer       → vertex 303
    276  left_eyebrow_inner   → vertex 357
    285  left_eyebrow_outer   → vertex 354
    291  mouth_left            → vertex 333
    308  upper_lip_left       → vertex 326
    327  nose_left_base       → vertex 364
    362  left_eye_inner       → vertex 298
    374  left_eye_lower       → vertex 791
    386  left_eye_upper       → vertex 590

La convenzione `right_*` / `left_*` è anatomica:
non deve essere reinterpretata in base alla posizione
del punto sulla bitmap visualizzata.

---

## Stato corrente

    [x] Vertex Mapper
    [x] Mappa MediaPipe interattiva
    [x] Filtri anatomici
    [x] CanonicalMapping Model
    [x] Mapping persistence
    [x] 25 Control Points associati
    [x] Mapping 25/25 COMPLETE
    [x] Validazione strutturale del mapping
    [x] Validazione geometrica preliminare del template
    [x] Normalizzazione dei Control Points
    [x] Verifica di simmetria bilaterale
    [x] CanonicalMeshBuilder
    [x] Canonical Mesh costruita da `male1591_head.obj`
    [x] 1604 vertici / 3064 triangoli
    [x] Verifica indipendenza della geometria
    [x] Verifica Canonical Mapping ↔ Canonical Mesh
    [x] Validazione Canonical Mesh
    [x] Validazione delle normali
    [x] Validazione orientamento / winding
    [x] Verifica distribuzione Control Points
    [x] Verifica sistema di coordinate
    [x] Test finale completo Sprint 23
    [x] Commit Sprint 23
    [x] Push Sprint 23

## Prossimo lavoro

Il prossimo obiettivo operativo è:

    Sprint 24 — Registration Engine

Lo Sprint 23 — Canonical Mesh Validation è stato completato,
verificato e chiuso.

Commit di chiusura dello Sprint 23:

    8928164 feat: integrate canonical mesh normal analysis

Stato repository verificato:

    branch:
        master

    upstream:
        origin/master

    working tree:
        clean

    sincronizzazione:
        up to date

---

## Checkpoint definitivo dello Sprint 23

    [x] CanonicalMesh
    [x] CanonicalMeshBuilder
    [x] Template `male1591/head`
    [x] Mesh sorgente `male1591_head.obj`
    [x] 1604 vertici
    [x] 3064 triangoli
    [x] Copia indipendente della geometria
    [x] Preservazione delle coordinate
    [x] Preservazione degli indici
    [x] Preservazione della triangolazione
    [x] Template sorgente invariato
    [x] Compatibilità Canonical Mapping
    [x] Mapping 25/25 COMPLETE
    [x] Validazione dei conteggi della Canonical Mesh
    [x] Validazione degli indici triangolari
    [x] Validazione coordinate finite
    [x] Rilevamento NaN / Inf
    [x] Bounding box e centro geometrico
    [x] Boundary edges / boundary vertices
    [x] Edge non-manifold
    [x] Triangoli degeneri
    [x] Test negativi della validazione
    [x] Serializzazione del Validation Report
    [x] Calcolo delle normali
    [x] Validazione delle normali
    [x] Verifica zero-length normals
    [x] Verifica non-finite normals
    [x] Verifica orientamento / winding
    [x] Verifica distribuzione Control Points
    [x] Verifica coordinate normalizzate
    [x] Verifica simmetria bilaterale
    [x] Verifica sistema di coordinate
    [x] Test finale integrato Sprint 23
    [x] Aggiornamento documentazione
    [x] Commit
    [x] Push

---


---

# 49A. Checkpoint Sprint 24 — Registration Engine

## Stato

    [x] Sprint 24 completato
    [x] Registration Engine implementato
    [x] Integrazione Pipeline → Builder → RegistrationEngine
    [x] Canonical Mesh reale verificata
    [x] Canonical Mapping 25/25 verificato
    [x] Validazione landmark mancanti
    [x] Validazione coordinate non finite
    [x] Validazione mapping incompleto
    [x] Validazione mapping incompatibile
    [x] Validazione landmark fuori range
    [x] Verifica regressione geometrica
    [x] Test finale di integrazione
    [x] Geometria preservata
    [x] Topologia preservata

## Canonical Mesh utilizzata

Il Registration Engine è stato verificato utilizzando la
Canonical Mesh reale derivata dal template:

    male1591
    part = head

La mesh contiene:

    1604 vertici
    3064 triangoli

Il test integrato ha verificato che la Canonical Mesh
effettivamente passata al Registration Engine sia quella
attesa.

## Canonical Mapping

Il Canonical Mapping utilizzato dal Registration Engine
contiene:

    25 mapping
    Status: COMPLETE

La corrispondenza tra i 25 Control Points MediaPipe e i
vertici della Canonical Mesh è stata verificata prima
dell'esecuzione della registrazione.

## Validazione degli input

Sono stati verificati con esito positivo i principali
casi di errore del Registration Engine:

- landmark mancante;
- coordinate NaN;
- coordinate +Inf;
- mapping incompleto;
- mapping incompatibile con il numero atteso di Control Points;
- landmark MediaPipe fuori range.

In tutti questi casi il Registration Engine restituisce
uno stato di errore coerente e produce il relativo messaggio
diagnostico.

## Registrazione valida

Con input validi il Registration Engine produce:

    RegistrationStatus.SUCCESS
    Success: True
    Used landmarks: 25
    Expected landmarks: 25
    Errors: []

Il test integrato ha inoltre verificato:

    RegistrationEngine calls: 1

e ha confermato che la Canonical Mesh reale viene passata
correttamente al Registration Engine:

    Canonical vertices passed: 1604
    Canonical triangles passed: 3064

## Preservazione della geometria

Lo Sprint 24 non deve ancora deformare la Canonical Mesh.

Il test di regressione e il test integrato hanno confermato:

    Geometry unchanged: True
    Topology unchanged: True

Questo comportamento è intenzionale.

Lo Sprint 24 realizza e verifica il motore di registrazione
e il relativo contratto di integrazione, mentre la stima
della trasformazione globale e la modifica effettiva della
geometria vengono affrontate nel successivo Sprint 25 —
Global Alignment.

## Risultato finale

    SPRINT 24 — COMPLETATO E VERIFICATO

La Registration Engine è ora integrata nella pipeline di
ricostruzione ed è pronta per essere utilizzata dal
successivo Global Alignment.

## Vincolo per lo Sprint 25

Il prossimo Sprint deve occuparsi esclusivamente di:

    Global Alignment

con:

    Canonical Control Points
            ↓
    Real Control Points
            ↓
    stima trasformazione globale
            ↓
    translation
            ↓
    rotation
            ↓
    scale
            ↓
    Global Aligned Canonical Mesh

Non anticipare nello Sprint 25:

- Local Deformation;
- Head Reconstruction;
- Complete Head Mesh;
- Texture Projection;
- ricostruzione completa da fotografia;
- ricostruzione da video;
- export finale.

## Regole operative per gli Sprint successivi

    1. verificare sempre la struttura reale del progetto;
    2. non duplicare classi, servizi o algoritmi già esistenti;
    3. non modificare ciò che è già funzionante senza necessità tecnica;
    4. una sola responsabilità principale per Sprint;
    5. una modifica principale alla volta;
    6. eseguire il test dopo ogni modifica;
    7. verificare le regressioni;
    8. aggiornare ROADMAP.md e CHANGELOG.md al termine dello Sprint;
    9. chiudere lo Sprint con commit e push;
   10. usare il ROADMAP come guida operativa per lo Sprint successivo.

---

## Vincolo fondamentale

Non ripetere il lavoro già completato a meno che
un test non dimostri una regressione reale.

La Registration Engine deve partire dallo stato verificato
del progetto e utilizzare le componenti già esistenti.

Non anticipare:

    - Global Alignment
    - Local Deformation
    - Head Reconstruction
    - Complete Head Mesh
    - Texture Projection
    - Reconstruction Pipeline
    - ricostruzione da fotografia singola
    - ricostruzione da video 360°
    - ricostruzione da più fotografie
    - export finale

prima degli Sprint previsti.

---

## Checkpoint Sprint 25 — Global Alignment

### Stato

    [x] Sprint 25 completato
    [x] Global Alignment implementato
    [x] RegistrationTransformation introdotto
    [x] matrice omogenea 4×4 verificata
    [x] validazione dimensione matrice verificata
    [x] validazione valori finiti verificata
    [x] RegistrationResult esteso
    [x] backward compatibility verificata
    [x] algoritmo Umeyama implementato
    [x] stima scala verificata
    [x] stima rotazione verificata
    [x] stima traslazione verificata
    [x] errori mean / RMS / max verificati
    [x] test matematico deterministico
    [x] test integrato Global Alignment
    [x] regression test Registration Engine
    [x] geometria della Canonical Mesh preservata
    [x] topologia preservata
    [x] test finale OK

### Trasformazione globale

Il Global Alignment utilizza i:

    25 Canonical Control Points
            +
    25 Real Control Points

per stimare una trasformazione globale composta da:

    translation
    rotation
    scale

La trasformazione viene rappresentata mediante:

    RegistrationTransformation

con matrice omogenea:

    4 × 4

### Algoritmo

La stima della trasformazione globale è stata implementata
mediante algoritmo di Umeyama.

Il test deterministico ha recuperato correttamente:

    scale = 1.75

con errore di scala:

    0.0

La rotazione e la traslazione sono state recuperate con errori
numerici dell'ordine della precisione floating point.

### Test integrato

Il test `test_global_alignment.py` ha verificato:

    Canonical Control Points: 25
    Real Control Points:      25
    Mapping entries:          25
    Mapping complete:         True

La registrazione ha prodotto:

    RegistrationStatus.SUCCESS
    Used landmarks: 25
    Expected landmarks: 25
    Errors: []
    Warnings: []

con errori:

    Registration error:
        2.936915022422793e-16

    Mean error:
        2.739988667247874e-16

    RMS error:
        2.936915022422793e-16

    Max error:
        5.23691153334427e-16

### Trasformazione verificata

Nel test integrato sono stati recuperati:

    scale = 1.35

    translation =
        [ 0.1  -0.05  0.2 ]

con:

    Scale error:
        0.0

    Rotation error:
        5.599433397402341e-16

    Translation error:
        5.967448757360216e-16

    RESULT: OK

### Regression Test

È stato rieseguito il test integrato della Registration Engine
dello Sprint 24.

Risultato:

    Registration status: RegistrationStatus.SUCCESS
    Registration success: True
    Used landmarks: 25
    Expected landmarks: 25
    RegistrationEngine calls: 1

    Canonical vertices passed: 1604
    Canonical triangles passed: 3064

    Geometry unchanged: True
    Topology unchanged: True

    RESULT: OK

La modifica dello Sprint 25 non ha introdotto regressioni
nel comportamento già verificato dello Sprint 24.

### Modello RegistrationTransformation

Il modello è stato validato anche con test negativi:

    3×3 → ValueError
    5×5 → ValueError
    NaN → ValueError

La matrice identità 4×4 è stata verificata correttamente.

### Stato della pipeline

La pipeline concettuale raggiunta è:

    Canonical Mesh
          +
    Real Face Landmarks
          ↓
    Registration Engine
          ↓
    Global Alignment
          ↓
    Aligned Canonical Mesh

La Local Deformation non viene anticipata nello Sprint 25.

### Repository

Checkpoint Git di implementazione dello Sprint 25:

    d55285a
    Sprint 25: implement Global Alignment

Il commit è stato pubblicato su:

    origin/master

Repository verificato:

    branch master
    working tree clean
    up to date with origin/master

La documentazione di chiusura dello Sprint 25 viene consolidata
con un commit separato prima dell'avvio dello Sprint 26.
---
## Chiusura Sprint 26 — Local Deformation

Lo Sprint 26 — Local Deformation è stato completato,
integrato e verificato.

### Risultato

La pipeline verificata è:

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

È stato introdotto il:

    LocalDeformationEngine

che utilizza una interpolazione RBF con kernel Thin Plate Spline
tramite `scipy.interpolate.RBFInterpolator`.

La scelta è stata verificata con test deterministici e con
una mesh reale di 1604 vertici e 3064 triangoli.

### Verifiche principali

Sono risultati verificati:

    Control Points: 25
    Mesh vertices: 1604
    Mesh triangles: 3064

    Control Point max error:
        7.850462293418876e-17

    Global Alignment:
        SUCCESS

    Local Deformation:
        SUCCESS

    Canonical geometry unchanged:
        True

    Canonical topology unchanged:
        True

La deformazione mantiene quindi l'identità dei vertici e la
topologia della Canonical Mesh, modificando le coordinate della
geometria derivata.

### Test finali dello Sprint 26

Sono stati superati:

    test_global_alignment.py
    test_global_alignment_local_deformation.py
    test_reconstruction_registration.py
    test_head_reconstruction_builder.py
    test_head_reconstruction_pipeline.py

Tutti hanno prodotto:

    RESULT: OK

### Milestone

La Milestone E:

    Personalized Mesh
    Sprint 26

è ora:

    COMPLETATA E VERIFICATA

### Regola di chiusura dello Sprint

La chiusura segue la procedura:

    sviluppo
       ↓
    test
       ↓
    integration test
       ↓
    regression test
       ↓
    aggiornamento ROADMAP.md
       ↓
    aggiornamento CHANGELOG.md
       ↓
    verifica Git
       ↓
    commit
       ↓
    push
       ↓
    repository clean
       ↓
    nuovo Sprint

### Prossimo Sprint

    Sprint 27 — Head Reconstruction

Lo Sprint 27 dovrà occuparsi della ricostruzione della testa
a partire dalla Personalized Mesh.

Non anticipare:

    - Complete Head Mesh oltre quanto previsto dallo Sprint 27;
    - Texture Projection;
    - ricostruzione completa da fotografia;
    - ricostruzione da video 360°;
    - ricostruzione da più fotografie;
    - export finale.

La nuova sessione deve ripartire dal presente checkpoint.

Non ripetere il lavoro già completato a meno che un test non
dimostri una regressione reale.
