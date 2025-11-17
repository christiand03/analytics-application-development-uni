#### 

- Über zeitliche Abstände mit Key Facts gut
- wahrscheinlich wird monatlich

- Kundengruppenfokus? Warum nach typen? Begründen in der Arbeit

- Einigung größer als Forderung ist ein Fehler

- Ziel: Nur anzeigen, nicht korrigieren
- Interessant ist Menge an Daten

- zwei Datenkanäle (Email und maschinell)

Datenqualitätsfälle (Für uns nur Kundengruppen interessant)
- Kundengruppe: Wie sauber sind die Daten die über den Kunden reinkommen (Auftragseingang nach der Kundengruppe)
- Kollegenspezifisch: Wann oder Wer gibt Daten ein und wann macht wer Fehler

- 3 Länder als Kunden bei KVA RechnungsID, die jeweils anfangen
- KVA Rechnungnummer muss pro Land unique sein

- Zeitspalte wird zur Verfügungestellt

- KvaRechID muss unique sein

- Positionsdaten: Bezeichnung Datenfehler ab 2023 -> Fehler bei Azure -> Wurde umgestellt
- Wie oft ist da Müll drin?

- Positiondaten (Bezeichnung) + Handwerkername soll verknüpft werden zum Gewerkname
- Wie sauber wird die Gewerk_Name gesetzt?
- Passt das Gewerk zur Firma?
- Gruppieren
- Data Mining Algorithmen

- Anzahl Aufträge ohne Positionsdaten -> Wenn Versicherer anfrage stellt, dass eine Prüfung erfolgen soll ohne Prüfdokument
-> 1€ Proformabeleg wird erstellt
- Prüfen, wie viele Proformabelege es gibt

- Wie größ ist die Steigerung von Position der Belege? -> Arbeitslast bzw. Arbeitszeit wird länger
- 

- adress1_postalcode kommt aus einer anderen Datenbank

- negativbeträge dürfen nicht sein -> Es gibt Gutschriften (Wenn alle Position negativ sind)
- 0.01€ - 1€ sind Proformabelege
- ab 50.000€ was ist der Grund?
- Währungsabweichung

- Jeder Kunde hat unterschiedliches System für Schadensnummer
- Gibt auch Kunden, die kein einheitliches Schema
- Schadensnummer kann ausgeklammert werden -> macht andere Gruppe

- Auftrags_ID sind reine DatenbankID Spalten

- Differenz_vor_Zeitwert_Netto: Differenz Forderung und Einigung

- Positionsdaten und Auftragsdaten abgleichen auch interessant

- manuelle Betrag = Empfehlung 

Dashboard:

- Wie viele Aufträge hat man pro Zeitraum (monat als kleinste Einheit)
- Kategorie: Was ist nicht sauber? (Buchhaltung, ...)
- Auf Tagebene, wann wurden Positionsdaten nicht korrekt erfasst?
- Balkendiagramm -> draufklicken -> welche Aufträge sind falsch (Kundengruppe filtern) -> Was ist das für ein Fehler? (Buchfuhrung, Positionarten,...)
- Wie viele Datenpunkte pro Woche?
- Größte Kategorie: Jahr
- Fehlerquote aggregieren über alle Datenarten, aber auch in Detail 
- Man kann auf Daten klicken und es werden detailierte Informationen angezeigt
- 