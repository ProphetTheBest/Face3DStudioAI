# Face3D Studio AI

# DEVELOPMENT RULES

Versione documento: 1.0

Ultimo aggiornamento: 28/07/2026

---

# 1. Obiettivo

Questo documento definisce le regole di sviluppo del progetto Face3D Studio AI.

Ogni modifica al codice deve rispettare queste regole.

---

# 2. Architettura

- Pattern MVC rigoroso.
- Nessuna logica nella GUI.
- I Widget non conoscono i Model.
- I Controller coordinano la logica applicativa.
- I Model rappresentano esclusivamente i dati.
- Le operazioni sul filesystem sono delegate ai Manager o ai Service.

---

# 3. Organizzazione del codice

- Una classe principale per file.
- Un file = una responsabilità.
- Niente codice duplicato.
- Preferire classi piccole e coese.

---

# 4. Convenzioni Python

- Type Hint obbligatori.
- Utilizzare @dataclass quando appropriato.
- Docstring per classi e metodi pubblici.
- Nomi delle classi in PascalCase.
- Nomi di metodi e variabili in snake_case.

---

# 5. GUI

- Tutti i Widget derivano da BasePanel quando applicabile.
- Nessuna elaborazione dati nella GUI.
- La GUI mostra solamente informazioni.

---

# 6. Testing

Ogni modifica deve essere verificata prima di procedere.

Mai iniziare una nuova funzionalità con errori presenti.

---

# 7. Git

Ogni milestone termina con:

git status

git add .

git commit

git push

---

# 8. Documentazione

Alla fine di ogni milestone devono essere aggiornati:

- PROJECT_MASTER_PLAN.md
- CHANGELOG.md

---

# 9. Metodo di sviluppo

Per ogni nuova funzionalità:

1. Analisi
2. Progettazione
3. Implementazione
4. Test
5. Commit Git
6. Aggiornamento documentazione

---

# 10. Regola fondamentale

Il progetto deve essere sempre compilabile.

Non si procede mai alla milestone successiva finché quella corrente non è completamente conclusa.