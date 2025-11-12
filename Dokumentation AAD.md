---
tags:
  - module/analysisappdev
---

# Eigenschaften Rohdaten

Zwei *parquet*-Dateien, "Auftragsdaten" 71,7 MB, "Positionsdaten" 416 MB.
Die Überführung der komprimierten Daten in Pandas-Dataframes ergibt Daten mit den folgend beschriebenen Eigenschaften.
## Auftragsdaten.parquet

Zeilen: 868489
Spalten: 19

Zweck: Vermutlich ein Sammeldatensatz für alle eingegangenen und zu prüfenden Versicherungsforderungen. Enthält grobe Informationen über Aufträge (z.B. interne IDs, betroffene Versicherungen, Schadensfallbeschreibungen, Kundendaten).

| Spaltenname                  | dtype   | Anzahl unique values | Beschreibung (Syntax)                        | Beschreibung (Semantik)                                         | Anomalien                          |
| ---------------------------- | ------- | -------------------- | -------------------------------------------- | --------------------------------------------------------------- | ---------------------------------- |
| Auftrags_ID                  | object  |                      | 32-char ID, 36-char mit Trennzeichen "-"     | Trailing 20 chars in 32 Ausführungen                            |                                    |
| Schadensnummer               | object  |                      | divers, alphanumerisch                       | wahrscheinlich externe IDs                                      | Textdaten hinter einigen Einträgen |
| KvaRechnung_ID               | object  |                      | 32-char ID, 36-char mit Trennzeichen "-"<br> | trailing 20 analog zu Auftrags_ID                               |                                    |
| KvaRechnung_Nummer           | object  |                      | KVR-X<br>X= 7 Zahlen                         | Nicht unique, buchhaltärischer                                  |                                    |
| Forderung_Netto              | float64 |                      | Kommazahlen                                  | Geldbetrag                                                      |                                    |
| Empfehlung_Netto             | float64 |                      | Kommazahlen                                  | Geldbetrag                                                      |                                    |
| Einigung_Netto               | float64 |                      | Kommazahlen                                  | Geldbetrag                                                      |                                    |
| DH_ID                        | int64   |                      | int (1,2,4)                                  | Länderkennung ?                                                 |                                    |
| Land                         | object  |                      | 2-char String                                | Länderkennung (DE, CH, AT)                                      | Null als "-"                       |
| PLZ_SO                       | object  |                      | PLZ                                          | Schadensort-PLZ                                                 | Viele Null                         |
| PLZ_HW                       | object  |                      | PLZ                                          | Handwerker-PLZ                                                  | Viele Null                         |
| PLZ_VN                       | object  |                      | PLZ                                          | Versicherungsnehmer-PLZ (?)                                     | Viele Null                         |
| address1_postalcode          | object  |                      | PLZ                                          | Rechnungsadresse HW PLZ                                         |                                    |
| Schadenart_Name              | object  |                      | String, Kategoriedaten                       | Einordnung Schadenskategorie                                    |                                    |
| Falltyp_Name                 | object  |                      | String, Freiform                             | Genauere Beschreibung des Schadens                              |                                    |
| Gewerk_Name                  | object  |                      | String, Kategoriendaten                      | Beschreibung Fachbereich Handwerker                             |                                    |
| Kundengruppe                 | object  |                      | String, Kategoriendaten                      | Name des jeweiligen Versicherers                                |                                    |
| Differenz_vor_Zeitwert_Netto | float64 |                      | Float                                        | Geldbetrag, Differenz zur Abschreibung des geschädigten Objekts |                                    |
| Handwerker_Name              | object  |                      | String                                       | Firmennamen                                                     |                                    |
