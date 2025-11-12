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

| Spaltenname                  | dtype   | Anzahl unique values | Beschreibung (Syntax)                        | Beschreibung (Semantik)                                         | Anomalien                                                |
| ---------------------------- | ------- | -------------------- | -------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------- |
| Auftrags_ID                  | object  | 691084               | 32-char ID, 36-char mit Trennzeichen "-"     | Trailing 20 chars in 32 Ausführungen                            |                                                          |
| Schadensnummer               | object  | 579566               | divers, alphanumerisch                       | wahrscheinlich externe IDs                                      | Textdaten hinter einigen Einträgen                       |
| KvaRechnung_ID               | object  | 868489               | 32-char ID, 36-char mit Trennzeichen "-"<br> | trailing 20 analog zu Auftrags_ID                               |                                                          |
| KvaRechnung_Nummer           | object  | 866651               | KVR-X<br>X= 7 Zahlen                         | Nicht unique, buchhaltärischer                                  |                                                          |
| Forderung_Netto              | float64 | N/A                  | Kommazahlen                                  | Geldbetrag                                                      |                                                          |
| Empfehlung_Netto             | float64 | N/A                  | Kommazahlen                                  | Geldbetrag                                                      |                                                          |
| Einigung_Netto               | float64 | N/A                  | Kommazahlen                                  | Geldbetrag                                                      |                                                          |
| DH_ID                        | int64   | 3+1                  | int (1,2,4)                                  | Länderkennung ?                                                 |                                                          |
| Land                         | object  | 3+1                  | 2-char String                                | Länderkennung (DE, CH, AT)                                      | Null-Value "-"                                           |
| PLZ_SO                       | object  |                      | PLZ (4/5-stellig, leading zeroes möglich)    | Schadensort-PLZ                                                 | Viele Null, Null-Value "-"                               |
| PLZ_HW                       | object  |                      | PLZ                                          | Handwerker-PLZ                                                  | Viele Null, Null-Value "-"                               |
| PLZ_VN                       | object  |                      | PLZ                                          | Versicherungsnehmer-PLZ (?)                                     | Viele Null, Null-Value "-"                               |
| address1_postalcode          | object  |                      | PLZ                                          | Rechnungsadresse HW PLZ                                         |                                                          |
| Schadenart_Name              | object  | 22+1                 | String, Kategoriedaten                       | Einordnung Schadenskategorie                                    | Null-Value "-",<br>Tippfehler ("Betriebsunterbrechnung") |
| Falltyp_Name                 | object  | 151+1                | String, Freiform                             | Genauere Beschreibung des Schadens                              | Null-Value "-"                                           |
| Gewerk_Name                  | object  | 63+1                 | String, Kategoriendaten                      | Beschreibung Fachbereich Handwerker                             | Null-Value "(leer)"                                      |
| Kundengruppe                 | object  | 153                  | String, Kategoriendaten                      | Name des jeweiligen Versicherers                                | Enthält Einträge für KI-Tests ("KI-Test" etc)            |
| Differenz_vor_Zeitwert_Netto | float64 |                      | Float                                        | Geldbetrag, Differenz zur Abschreibung des geschädigten Objekts |                                                          |
| Handwerker_Name              | object  |                      | String                                       | Firmennamen                                                     |                                                          |
## Positionsdaten.parquet


# Eigenschaften Soll-Daten

## Auftragsdaten_konvertiert


| Spaltenname                  | dtype    | Anzahl unique values | Beschreibung (Syntax)                        | Beschreibung (Semantik)                                         | Anomalien                                                |
| ---------------------------- | -------- | -------------------- | -------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------- |
| Auftrags_ID                  | string   | 691084               | 32-char ID, 36-char mit Trennzeichen "-"     | Trailing 20 chars in 32 Ausführungen                            |                                                          |
| Schadensnummer               | string   | 579566               | divers, alphanumerisch                       | wahrscheinlich externe IDs                                      | Textdaten hinter einigen Einträgen                       |
| KvaRechnung_ID               | string   | 868489               | 32-char ID, 36-char mit Trennzeichen "-"<br> | trailing 20 analog zu Auftrags_ID                               |                                                          |
| KvaRechnung_Nummer           | string   | 866651               | KVR-X<br>X= 7 Zahlen                         | Nicht unique, buchhaltärischer                                  |                                                          |
| Forderung_Netto              | float32  | N/A                  | Kommazahlen                                  | Geldbetrag                                                      |                                                          |
| Empfehlung_Netto             | float32  | N/A                  | Kommazahlen                                  | Geldbetrag                                                      |                                                          |
| Einigung_Netto               | float32  | N/A                  | Kommazahlen                                  | Geldbetrag                                                      |                                                          |
| DH_ID                        | int8     | 3+1                  | int (1,2,4)                                  | Länderkennung ?                                                 |                                                          |
| Land                         | category | 3+1                  | 2-char String                                | Länderkennung (DE, CH, AT)                                      | Null-Value "-"                                           |
| PLZ_SO                       | category |                      | PLZ (4/5-stellig, leading zeroes möglich)    | Schadensort-PLZ                                                 | Viele Null, Null-Value "-"                               |
| PLZ_HW                       | category |                      | PLZ                                          | Handwerker-PLZ                                                  | Viele Null, Null-Value "-"                               |
| PLZ_VN                       | category |                      | PLZ                                          | Versicherungsnehmer-PLZ (?)                                     | Viele Null, Null-Value "-"                               |
| address1_postalcode          | category |                      | PLZ                                          | Rechnungsadresse HW PLZ                                         |                                                          |
| Schadenart_Name              | category | 22+1                 | String, Kategoriedaten                       | Einordnung Schadenskategorie                                    | Null-Value "-",<br>Tippfehler ("Betriebsunterbrechnung") |
| Falltyp_Name                 | category | 151+1                | String, Freiform                             | Genauere Beschreibung des Schadens                              | Null-Value "-"                                           |
| Gewerk_Name                  | category | 63+1                 | String, Kategoriendaten                      | Beschreibung Fachbereich Handwerker                             | Null-Value "(leer)"                                      |
| Kundengruppe                 | category | 153                  | String, Kategoriendaten                      | Name des jeweiligen Versicherers                                | Enthält Einträge für KI-Tests ("KI-Test" etc)            |
| Differenz_vor_Zeitwert_Netto | float32  |                      | Float                                        | Geldbetrag, Differenz zur Abschreibung des geschädigten Objekts |                                                          |
| Handwerker_Name              | category |                      | String                                       | Firmennamen                                                     |                                                          |


 

