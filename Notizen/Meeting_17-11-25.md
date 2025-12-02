#### 


- Key Facts: Veränderung über zeitlichen Abstand darstellen
- Alle Entscheidungen, die wir treffen, im Report begründen (siehe Kundengruppenfokus)
- Dashboard: Aggregation nach Kundengruppe  /// erledigt: groupby_col() -> erlaubt gruppierung nach allen Spalten
- Bedingung: Einigung dürfen nicht größer sein als Forderungen /// erledigt: plausibilitaetscheck_forderung_einigung(input_df)
- Ziel: Nur anzeigen, nicht korrigieren (Data Cleaning Zwischenschritte um invalide Werte zu löschen)
- Metrik: Absolutwerte im betrachteten Zeitraum /// erledigt: count_rows()
- Dateninput: Daten kommen aus zwei Kanälen (Email/manuell/OCR und maschinell)
- Metrik: Sauberkeit der Daten vom Kunden pro Kundengruppe /// erledigt: data_cleanliness()
- Info: KVA_Rechnungsnummer pro Land unique (Wichtig sonst ab in Knast) Fehlerquelle: Race-condition
- Zeitspalte wird zur Verfügung gestellt
- Metrik: Kva_RechnungsID muss unqiue sein /// erledigt: uniqueness_check()
- Info: Positionsdaten: Bezeichnung (nach 165 Zeichen über gesamte Zeile wird abgeschnitten) Datenfehler ab 2023 -> Fehler bei Azure -> Wurde umgestellt
- TODO: Extra Spalte mit Regex Wort finden: Skonto, Rabatt, Nachlass etc. (Positionsdaten Bezeichnung) -> Boolean Spalte, ob negative Position erlaubt /// erledigt: in data_cleaning.py wird eine neue spalte zum schluss hinzugefügt
- TODO: Alle Ausprägungen überprüfen (False, aber negativ wäre Fehler & True, aber positiv wäre Fehler) /// erledigt: Spalte 'Plausibel' in data_cleaning.py und in metrics.py: discount_check()
- TODO: Positiondaten (Bezeichnung) + Handwerkername soll verknüpft werden zum Gewerkname
- TODO: Wie sauber wird die Gewerk_Name gesetzt?
- TODO: Passt das Gewerk zur Firma?
- TODO: Sinnvolle Gruppierung für Feature Engineering
- Info: Anzahl Aufträge ohne Positionsdaten -> Wenn Versicherer anfrage stellt, dass eine Prüfung erfolgen soll ohne Prüfdokument -> 1€ Proformabeleg wird erstellt 
- Info: Es gibt keine AuftragIDs die keine KvaRechnung_ID haben, Alle Aufträge mit Einigung zwischen 0.01 und 1 werden als Prüfungen deklariert 
- TODO: Prüfen, wie viele Proformabelege es gibt /// erledigt: proformabelege()
- Metrik: Steigerung der Anzahl an Positionen pro Auftrag je Zeitraum
- Info: adress1_postalcode kommt aus einer anderen Datenbank
- Info: Negative Beträge inkorrekt, außer gesamter Forderungsbetrag, Empfehlung und Einigung negativ (Auftragsart: Gutschrift) /// erledigt: einigung_negativ()
- Info: 0.01€ - 1€ sind Proformabelege
- Metrik: Zeilen ab 50.000€ Forderungen ausgeben (manuelle Durchsicht) /// erledigt: above_50k
- TODO: Mehr Informationen zu Metriken per Button zu Hidden Pages gelangen !
- Info: Jeder Kunde hat unterschiedliches System für Schadensnummer (Gibt auch Kunden, die kein einheitliches Schema) -> Wörter dahintern sind gewollt
- Info: Schadensnummer kann ausgeklammert werden -> macht andere Gruppe
- Info: Alle ID Spalten sind reine DatenbankID´s (Enthalten keine Informationen)
- Info: Differenz_vor_Zeitwert_Netto: Differenz Forderung und Einigung /// erledigt: check_zeitwert()
- TODO: Abgleich Positionsdaten und Auftragsdaten: Summe zwischen Position und Auftrag | Metrik: Anzahl Aufträge ohne Position
- TODO: Wenn wir Spalte bekommen, ob manueller Betrag: Empfehlung und Einigung immer gleich, außer wenn manueller Betrag gesetzt (machen wir das überhaupt noch?)

- Metrik: Steigerung der Anzahl an Positionen pro Auftrag je Zeitraum /// erledigt: positions_per_order_over_time()
- Fehlerhäufigkeit nach Tageszeit und Wochentag aggregieren // error_frequency_by_weekday_hour()


# Dashboard:
- Fehlerquelle darstellen
- Wie viele Aufträge hat man pro Zeitraum (monat als kleinste Einheit)
- Timestamps für Fehler: Wann wurden Fehler gemacht?
- Größte Kategorie: Jahr
- Wie viele Fehler pro Zeile und pro Spalte



To-Do:
- data_cleanliness() erweitern? Nicht nur None als Fehler sondern auch fehlerhafte punkte? -> Gesamtanzahl an gefundenen Fehlern 
- TODO: Positiondaten (Bezeichnung) + Handwerkername soll verknüpft werden zum Gewerkname
- TODO: Wie sauber wird die Gewerk_Name gesetzt?
- TODO: Passt das Gewerk zur Firma?
- TODO: Sinnvolle Gruppierung für Feature Engineering
- TODO: Mehr Informationen zu Metriken per Button zu Hidden Pages gelangen !
- TODO: Aufgaben aus dem Kanban Board beachten
