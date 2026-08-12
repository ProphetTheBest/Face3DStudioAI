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