# Data Quality Dashboard

Dieses Projekt ist ein umfassendes Tool zur Analyse und Überwachung der Datenqualität von Auftrags- und Positionsdaten. Es besteht aus einer ETL-Pipeline (Extract, Transform, Load), die Daten bereinigt und Metriken vorberechnet, sowie einem interaktiven Streamlit-Dashboard zur Visualisierung.

Das System nutzt **DuckDB** als performante Backend-Datenbank und **Evidently AI** für Data Drift Analysen. Zusätzlich kommen Machine Learning Komponenten (**Sentence Transformers**) zum Einsatz, um semantische Auffälligkeiten in Textdaten zu erkennen.

## Inhaltsverzeichnis

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Projektstruktur](#projektstruktur)
- [Voraussetzungen & Installation](#voraussetzungen--installation)
- [Datenvorbereitung](#datenvorbereitung)
- [Nutzung](#nutzung)
    - [1. Datenbank erstellen (ETL)](#1-datenbank-erstellen-etl)
    - [2. Dashboard starten](#2-dashboard-starten)
- [Dashboard-Bereiche](#dashboard-bereiche)

## Features

*   **Datenbereinigung:** Automatische Typkonvertierung, Behandlung von Null-Werten und Korrektur von Tippfehlern.
*   **Performance:** Vorberechnung komplexer Metriken und Speicherung in einer lokalen DuckDB-Datenbank für schnelles Laden im Dashboard.
*   **Plausibilitätsprüfungen:**
    *   Logik-Checks (z.B. *Forderung < Einigung*).
    *   Erkennung von Proforma-Belegen.
    *   Vorzeichen-Konsistenzprüfungen.
    *   Abgleich von Auftragssummen mit der Summe der Positionen.
*   **Semantische Analyse:** KI-gestützte Prüfung (mittels `SentenceTransformer`), ob das angegebene Gewerk zum Namen des Handwerkers passt.
*   **Data Drift:** Erkennung von Veränderungen in der Datenverteilung über die Zeit (Data Drift) mittels Evidently AI.
*   **Trendanalyse:** Vergleich aktueller Metriken mit dem vorherigen Datenbank-Stand (automatisches Backup/Rotation der DB).

## Tech Stack

Dieses Projekt setzt auf einen modernen, auf Data-Science ausgerichteten Technologie-Stack, um hohe Performance bei der Verarbeitung lokaler Daten zu gewährleisten.

### **Core & Data Processing**
*   **Python 3.12+**: Die Basisprogrammiersprache.
*   **Pandas & NumPy**: Für die grundlegende Datenmanipulation, Bereinigung und numerische Operationen (ETL-Prozess).
*   **Apache Parquet**: Als Speicherformat für die Rohdaten (hochkomprimiertes, spaltenbasiertes Format).

### **Datenbank & Storage**
*   **DuckDB**: Eine In-Process SQL OLAP-Datenbank.
    *   Dient als performanter Zwischenspeicher für die bereinigten Daten und vorberechneten Metriken.
    *   Ermöglicht extrem schnelle Aggregationen für das Dashboard, ohne dass ein externer Datenbank-Server benötigt wird.

### **Machine Learning & AI**
*   **Sentence Transformers (Hugging Face)**:
    *   Modell: `paraphrase-multilingual-MiniLM-L12-v2`.
    *   Wird genutzt, um semantische Ähnlichkeiten zwischen Handwerkernamen und Gewerken zu berechnen (Vektorisierung und Cosine-Similarity).
*   **PyTorch**: Backend für die Sentence Transformers (nutzt GPU/CUDA falls verfügbar, sonst CPU).

### **Data Quality & Monitoring**
*   **Evidently AI**: Framework zur Erkennung von Data Drift (Veränderung der Datenverteilung über die Zeit) und Generierung statischer HTML-Reports.

### **Frontend & Visualisierung**
*   **Streamlit**: Framework für das Dashboard. Ermöglicht Interaktivität und Caching (`@st.cache_data`) für eine flüssige User Experience.
*   **Altair**: Deklarative Bibliothek zur Erstellung der interaktiven Diagramme und Heatmaps im Dashboard.
*   **Streamlit Option Menu**: Für die moderne Navigation innerhalb der App.

## Projektstruktur

```text
.
├── Notizen/
│   └── Dokumentation AAD       # Dokumentaion zum Datensatz
├── resources/                  # Daten-Ordner
│   ├── Auftragsdaten           # Raw Parquet Datei
│   ├── Positionsdaten          # Raw Parquet Datei
│   ├── Auftragsdaten_Zeit      # Raw Parquet Datei
│   ├── dashboard_data.duckdb   # Generierte Datenbank (durch build_db.py)
│   └── reports/                # Generierte HTML Data Drift Reports
├── app_pages/                  # Streamlit Seiten-Logik
│   ├── page1.py                # Startseite (KPIs & Trends)
│   ├── page2.py                # Numerische Daten
│   ├── page3.py                # Textuelle Daten
│   ├── page4.py                # Plausibilitätscheck
│   └── page5.py                # Data Drift Reports
├── assets/                     # Bilder (Logos, Favicon)
├── build_db.py                 # ETL-Skript (MAIN: Führt Cleaning & Metriken aus)
├── data_cleaning.py            # Logik für Datenimport & Bereinigung
├── metrics.py                  # Bibliothek für alle Berechnungsfunktionen
├── data_drift_metrics.py       # Logik für Evidently AI Reports
├── db_dashboard.py             # Hauptanwendung (Streamlit App)
└── requirements.txt            # Python Abhängigkeiten
```

## Voraussetzungen & Installation

Es wird Python 3.12+ empfohlen.

1.  **Repository klonen / Dateien ablegen.**
2.  **Abhängigkeiten installieren:**

    Erstelle eine `requirements.txt` mit folgendem Inhalt (basierend auf den Imports):
    ```text
    pandas
    numpy
    duckdb
    streamlit
    streamlit-option-menu
    altair
    evidently
    sentence-transformers
    torch
    pyarrow
    fastparquet
    ```

    Installiere die Pakete:
    ```bash
    pip install -r requirements.txt
    ```

    *Hinweis: Für die semantische Analyse wird `torch` benötigt. Falls eine GPU verfügbar ist (CUDA), wird diese automatisch genutzt, um die Berechnung zu beschleunigen.*

## Datenvorbereitung

Das Skript erwartet drei `.parquet` Dateien im Ordner `resources/`:

1.  **`Auftragsdaten`**: Enthält die Kopfdaten der Aufträge (IDs, Beträge, Kundengruppe, etc.).
2.  **`Positionsdaten`**: Enthält die Detailpositionen zu den Aufträgen.
3.  **`Auftragsdaten_Zeit`**: Enthält Zeitstempel-Informationen (`KvaRechnung_ID`, `CRMEingangszeit`), die an die Aufträge gemerged werden.

Stelle sicher, dass diese Dateien vorhanden sind, bevor das ETL-Skript ausgeführt wird.

## Nutzung

### 1. Datenbank erstellen (ETL)

Bevor das Dashboard gestartet werden kann, müssen die Daten bereinigt und die Metriken berechnet werden. Dies übernimmt das Skript `build_db.py`.

```bash
python build_db.py
```

**Was passiert hier?**
*   Lädt die Raw-Daten.
*   Führt `data_cleaning.py` aus.
*   Berechnet alle Metriken aus `metrics.py` (inkl. aufwendiger KI-Berechnungen).
*   Erstellt/Ersetzt `resources/dashboard_data.duckdb`.
*   Rotiert die alte Datenbank zu `dashboard_data_old.duckdb`, um Trendvergleiche zu ermöglichen.

### 2. Dashboard starten

Nach erfolgreicher Erstellung der Datenbank kann das Dashboard gestartet werden. Nutze hierfür `db_dashboard.py`, da dieses für die Nutzung der Datenbank optimiert ist.

```bash
streamlit run db_dashboard.py
```

*(Hinweis: `Dashboard.py` ist eine Legacy-Variante, die Berechnungen On-The-Fly durchführt und weniger performant ist).*

## Dashboard-Bereiche

Das Dashboard ist in 5 Bereiche unterteilt:

1.  **Startseite:**
    *   Globale KPIs (Anzahl Zeilen, Null-Quoten, Unique-Checks).
    *   Übersicht der Fehlerhäufigkeit (Heatmap nach Wochentag/Stunde).
    *   Trendverlauf der Positionen pro Auftrag.

2.  **Numerische Daten:**
    *   Analyse von numerischen Ausreißern.
    *   Checks auf Aufträge > 50.000€.
    *   **Summenabgleich:** Prüft, ob `Auftragssumme == Summe(Positionen)`.
    *   Zeitwert-Fehler.

3.  **Textuelle Daten:**
    *   Erkennung von Testdaten ("Test" in Kundengruppe).
    *   **Handwerker vs. Gewerk Analyse:**
        *   *Regelbasiert:* Ungewöhnliche Gewerk-Häufigkeiten pro Handwerker.
        *   *Semantisch:* KI-Vergleich, ob der Handwerkername zum Gewerk passt (z.B. "Maler Müller" macht "Elektroinstallation" -> Fehler).

4.  **Plausibilitätscheck:**
    *   Detaillierte Analyse von Logikfehlern.
    *   **Forderung vs. Einigung:** Fälle, in denen mehr geeinigt als gefordert wurde.
    *   **Rabatt-Check:** Validierung von negativen Beträgen basierend auf Bezeichnungen (Skonto, Storno, etc.).
    *   **Vorzeichen-Logik:** Inkonsistenzen zwischen Menge, Einzelpreis und Gesamtpreis.
    *   Proforma-Belege (Einigung zwischen 0,01€ und 1,00€).
    *   Aufträge ohne Positionen (Anzahl der Aufträge, denen keine Positionen zugeordnet sind (PositionsAnzahl ist leer))
    *   Ausreißer in der Forderungssumme (1. & 99. Perzentil je Schadensart)

5.  **Data Drift:**
    *   Erstellung und Anzeige von HTML-Reports mittels Evidently AI.
    *   Vergleich von zwei Zeiträumen (Referenz vs. Vergleichszeitraum), um festzustellen, ob sich die Datencharakteristik signifikant verändert hat.

---

### Fehlerbehebung

*   **FileNotFoundError:** Stelle sicher, dass der Ordner `resources/` existiert und die Parquet-Dateien dort liegen.
*   **Performance:** Der erste Lauf von `build_db.py` kann aufgrund der `SentenceTransformer` Berechnungen (Download des Modells und Inferenz) einige Zeit dauern.
*   **Datenbank gesperrt:** Wenn das Dashboard läuft, ist die DuckDB im Read-Only Modus. Für einen neuen `build_db.py` Lauf sollte das Dashboard idealerweise gestoppt oder sichergestellt werden, dass keine Schreibkonflikte auftreten (obwohl das Skript versucht, dies zu handhaben).