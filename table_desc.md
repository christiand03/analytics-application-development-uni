## Auftragsdaten Table

# Auftrags_ID
- 36 Zeichen lang (inklusive "-")
- Tupel 1: 8 Zeichen
- Tupel 2: 4 Zeichen
- Tupel 3: 4 Zeichen (4 unterschiedliche Werte)
- Tupel 4: 4 Zeichen (letzten 3 Values sind selten)
- Tupel 5: 12 Zeichen (ca 4.000x Ausnahmewert, sonst gleich)

# Schadensnummer

# KvaRechnung_ID
- 36 Zeichen lang (inklusive "-")
- Tupel 1: 8 Zeichen
- Tupel 2: 4 Zeichen
- Tupel 3: 4 Zeichen (5 unterschiedliche Werte)
- Tupel 4: 4 Zeichen (letzten 5 Values sind selten)
- Tupel 5: 12 Zeichen (ca 4.000x Ausnahmewert, sonst gleich)

# KvaRechnung_Nummer

# Forderung_Netto

# Empfehlung_Netto

# Einigung_Netto

# DH_ID
- 4 verschiedene Werte mit Länder verknüft
- viele null Werte mit zuordnung
- 1 Deutschland
- 2 AT
- 4 CH

# Land
- 4 verschiedene Werte 

# PLZ_SO

# PLZ_HW

# PLZ_VN

# address1_postalcose

# Schadenart_Name
- 23 verschiedene Werte inklusive "-" und Rechtschreibfehler bei "Betriebsunterbrechnung"

# Falltyp_Name
- 152 verschieden Werte inklusive "-"

# Gewerk_Name
- 64 verschiedene Werte inklusive (leer)

# Kundengruppe
- 153 verschiedene Werte inklusive Testdaten

# Differenz_vor_Zeitwert_Netto 

# Handwerker_Name


## Positionsdaten Table

# KvaRechnungID
- Tupel 1: unique
- Tupel 2: unique
- Tupel 3: 5 verschieden Werte (Alle im Millionenbereich, außer einer mit 42 Stück)
- Tupel 4: unique (letzten beiden Varianten haben drastisch weniger)
- Tupel 5: 2 verschiedene Werte (Einer davon ist deutlich weniger (ca 7000))


# PositionID
- Tupel 1: unique
- Tupel 2: unique
- Tupel 3: 5 verschieden Werte (letzte ziemlich selten)
- Tupel 4: unique (letzten 5 Werte relativ selten)
- Tupel 5: 2 verschiedene Werte (Einer davon deutlich weniger)