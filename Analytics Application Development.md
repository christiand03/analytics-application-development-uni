---
tags:
  - module/ws25
  - module/analysisappdev
---
# Kick-Off/Projektvorstellung

## Partner
solera / sachcontrol GmbH
- Belegprüfung für Versicherungsfälle
- Kostenprüfung für Schäden mit Expertenwissen
- Informationen aus Geschäftsprozessen für Referenzdatenbanken
- Integrationslösungen zur Informationserhebung (Sachverständigen-Unterstützung)

Dreistufenprozess für ungesteuerte Schäden
- Digitalisierung Beleg, Einpflegen (OCR: Escher)
- Erstprüfung mit ML
	- evtl. Tiefenprüfung bei Randfällen, auch Vor-Ort-Termine
- Belegbewertung entsprechend Service-Level
-> Prüfprozess wirft Durchflussdaten ab (Laufzeiten, falsch-positiv/negativ-Raten, Personal)

10% der positiv bew. Belege werden intern geprüft, alle anderen falsch-positiv-Bewertungen muss Kunde prüfen/erkennen

Referenzdatenbank für örtliche Material/Dienstleistungskosten zur genauen Kostenkalkulation und möglichen Einsparungen

Bewertungskriterien:
- Marktübliche Preise
- Mengen und Massen
- Plausibilität (Dachreparatur bei Leitungsschaden)
- Ersatzpflicht

Welche Daten können hierzu genutzt werden?
Addressdaten, Rechnungsbeträge, Schadensarten, Ortsbezug

Rohdaten extrahieren und semantisch auswerten

## Projekte
- (Datenvalidierung)
- ***Datenqualität*** -> Gruppe 2
	- Metriken für Datenqualität entwickeln
	- Tracking der Metriken zur 
- (SLA-Tool)
- (Handwerker-Empfehlungsdashboard)
### Datengrundlage
JSON Key-Value-Pairs (Dokumentation?) aus OCR von Rechnung
Auftrags- und Prozessdaten
Rohdaten von Escher OCR
### Projektziele
Monitoring selbst erstellter Metriken zur frühzeitigen Erkennung von Änderungen in Datengrundlage zur Anpassung des ML-Modells


### Konkrete Anforderungen
Verarbeitung: Python
UI/Dashboard: Streamlit o.ä., Display-Sprache Deutsch


# Datenqualität

Dimensionen der Datenqualität

Die Datenqualität wird anhand einer Reihe von Dimensionen bewertet, die sich je nach Informationsquelle unterscheiden können. Diese Dimensionen werden zur Kategorisierung von Datenqualitätsmetriken verwendet:

- **Vollständigkeit:** Dies stellt die Menge an Daten dar, die nutzbar oder vollständig sind. Wenn ein hoher Prozentsatz an Missing Values vorliegt, kann dies zu einer verzerrten oder irreführenden Analyse führen, wenn die Daten nicht repräsentativ für eine typische Datenstichprobe sind.
- **Einzigartigkeit:** Damit wird die Menge doppelter Daten in einem Datensatz bestimmt. Wenn Sie beispielsweise Kundendaten überprüfen, sollten Sie davon ausgehen, dass jeder Kunde eine eindeutige Kunden-ID hat.
-  **Gültigkeit:** Diese Dimension misst, wie viele Daten dem erforderlichen Format für alle Business Rules entsprechen. Die Formatierung umfasst in der Regel Metadaten wie gültige Datentypen, Bereiche, Muster und mehr.
- **Aktualität:** Diese Dimension bezieht sich auf die Verfügbarkeit der Daten innerhalb eines erwarteten Zeitrahmens. Kunden erwarten beispielsweise, dass sie unmittelbar nach einem Einkauf eine Bestellnummer erhalten und dass die Daten in Echtzeit generiert werden.
- **Genauigkeit:** Diese Dimension bezieht sich auf die Korrektheit der Datenwerte basierend auf der vereinbarten „Source of Truth“. Da es mehrere Quellen geben kann, die über dieselbe Metrik berichten, ist es wichtig, eine primäre Datenquelle zu bestimmen. Andere Datenquellen können verwendet werden, um die Genauigkeit der primären Quelle zu bestätigen. Zum Beispiel können Tools überprüfen, ob die Datenquellen alle in dieselbe Richtung tendieren, um das Vertrauen in die Datengenauigkeit zu stärken.
- **Konsistenz:** Diese Dimension bewertet Datensätze aus zwei verschiedenen Datensätzen. Wie bereits erwähnt, können mehrere Quellen identifiziert werden, um über eine einzige Metrik zu berichten. Die Verwendung verschiedener Quellen zur Überprüfung einheitlicher Datentrends und Verhaltensweisen ermöglicht es Unternehmen, allen umsetzbaren Erkenntnissen aus ihren Analysen zu vertrauen. Diese Logik kann auch auf Beziehungen zwischen Daten angewendet werden. Zum Beispiel sollte die Anzahl der Mitarbeiter in einer Abteilung die Gesamtzahl der Mitarbeiter in einem Unternehmen nicht überschreiten.
- **Eignung für den Zweck:** Schließlich trägt die Zweckmäßigkeit dazu bei, sicherzustellen, dass der Datenbestand einem geschäftlichen Bedarf entspricht. Diese Dimension kann schwierig zu bewerten sein, insbesondere bei neuen, entstehenden Datensätzen.
- **Data Drift**
- **Plausibilität** -> Gültigkeit