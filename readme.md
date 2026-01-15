***

# Data Quality Dashboard

Ein interaktives Dashboard zur Analyse, Überwachung und Validierung von Datenqualität in Auftrags- und Positionsdaten. Das Projekt nutzt **Streamlit** für das Frontend, **DuckDB** als performante In-Memory-Datenbank und **Evidently** zur Analyse von Data Drift. Zusätzlich kommen NLP-Modelle (**Sentence Transformers**) zum Einsatz, um semantische Auffälligkeiten in Textfeldern zu erkennen.

## 📋 Features

Das Dashboard ist in fünf Hauptbereiche unterteilt:

1.  **Startseite (Overview):**
    *   Zentrale KPIs (Zeilenanzahl, Null-Werte-Quoten, Eindeutigkeit der IDs).
    *   Visualisierung von Fehlerschwerpunkten nach Wochentag und Uhrzeit (Heatmap).
    *   Trendanalyse der Positionen pro Auftrag.
2.  **Numerische Daten:**
    *   Validierung von Zeitwert-Berechnungen.
    *   Erkennung von Ausreißern (z.B. Aufträge > 50.000 €).
    *   Abgleich von Auftragssummen gegen die Summe der Positionen.
3.  **Textuelle Daten:**
    *   Erkennung von Testdatensätzen.
    *   **NLP-Analyse:** Semantischer Abgleich zwischen "Handwerker" und "Gewerk" (nutzt `paraphrase-multilingual-MiniLM-L12-v2`), um falsche Zuordnungen zu finden.
4.  **Plausibilitätscheck:**
    *   Logik-Prüfungen: Ist die Einigung höher als die Forderung?
    *   Rabatt-Validierung: Sind Rabatte korrekt als Abzug gekennzeichnet?
    *   Erkennung von Proforma-Belegen.
    *   Vorzeichen-Logik (Tripel-Check: Forderung, Empfehlung, Einigung).
5.  **Data Drift:**
    *   Integration von **Evidently AI** zur Erkennung von Verteilungsänderungen in den Daten über verschiedene Zeiträume.

## 🛠 Technologie-Stack

*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Datenbank:** [DuckDB](https://duckdb.org/)
*   **Data Science & Manipulation:** Pandas, NumPy
*   **Visualisierung:** Altair
*   **Machine Learning / NLP:** PyTorch, SentenceTransformers
*   **Monitoring:** Evidently

## 📂 Projektstruktur

```text
.
├── app_pages/                  # Enthält die Logik für die einzelnen Dashboard-Seiten
│   ├── page1.py                # Startseite
│   ├── page2.py                # Numerische Daten
│   ├── page3.py                # Textuelle Daten
│   ├── page4.py                # Plausibilitätscheck
│   └── page5.py                # Data Drift
├── assets/                     # Bilder (Logo, Favicon)
├── resources/                  # Datenordner
│   ├── Auftragsdaten           # Input Parquet
│   ├── Positionsdaten          # Input Parquet
│   ├── dashboard_data.duckdb   # Generierte Datenbank (durch build_db.py)
│   └── reports/                # HTML-Reports von Evidently
├── build_db.py                 # ETL-Skript: Liest Parquet, berechnet Metriken, erstellt DB
├── data_drift_metrics.py       # Wrapper für Evidently-Reports
├── db_dashboard.py             # Hauptanwendung (Entry Point)
├── metrics.py                  # Bibliothek für Berechnungslogik & ML-Modelle
└── requirements.txt            # Python Abhängigkeiten
```

## 🚀 Installation & Setup

### 1. Repository klonen und Umgebung einrichten
Es wird empfohlen, eine virtuelle Umgebung (venv oder conda) zu nutzen.

```bash
git clone <repository-url>
cd <projekt-ordner>
python -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```
*Hinweis: Da `torch` und `sentence-transformers` genutzt werden, kann die Installation je nach System einige Minuten dauern.*

### 3. Daten bereitstellen
Stelle sicher, dass die Quell-Dateien (Parquet-Format) im Ordner `resources/` liegen:
*   `resources/Auftragsdaten`
*   `resources/Positionsdaten`
*   `resources/Auftragsdaten_Zeit`

### 4. Datenbank aufbauen (ETL)
Bevor das Dashboard gestartet werden kann, müssen die Daten verarbeitet und die Metriken berechnet werden. Dies geschieht einmalig (oder bei Datenupdates) über das Build-Skript.

```bash
python build_db.py
```
*Das Skript führt Data Cleaning durch, berechnet Embeddings auf der GPU (falls verfügbar) und speichert alles in `resources/dashboard_data.duckdb`.*

### 5. Dashboard starten
```bash
streamlit run db_dashboard.py
```

## 🧠 Besonderheiten der Logik

### NLP & Vektorisierung (`metrics.py`)
Das Projekt nutzt das Modell `paraphrase-multilingual-MiniLM-L12-v2`, um zu prüfen, ob der Name eines Handwerkers semantisch zum angegebenen Gewerk passt.
*   **Performance:** Das Skript prüft auf CUDA-Verfügbarkeit. Auf einer CPU kann dieser Schritt bei großen Datensätzen Zeit in Anspruch nehmen.
*   **Outlier-Detection:** Einträge mit einem Similarity-Score < 0.2 werden als potenzielle Mismatches markiert.

### Datenbank-Rotation
Das `build_db.py` Skript implementiert eine einfache Rotation. Die vorherige Datenbank wird als `dashboard_data_old.duckdb` gespeichert, um Delta-Vergleiche (Veränderung der KPIs zum vorherigen Lauf) im Dashboard zu ermöglichen.

## 📊 Verwendung der Data Drift Reports
Auf Seite 5 ("Data Drift") können Zeiträume für Referenz- und Vergleichsdaten ausgewählt werden.
*   Wird ein Report angefordert, der noch nicht existiert, wird dieser *on-the-fly* berechnet und im Ordner `resources/reports/` als HTML gespeichert.
*   Bereits erstellte Reports werden gecached und direkt geladen.