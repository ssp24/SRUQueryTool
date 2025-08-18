# SRUQueryTool

Desktop-Tool zur Abfrage der SRU-Schnittstelle der Deutschen Nationalbibliothek (DNB). 

Das Tool unterstützt verschiedene Kataloge und Metadatenformate. Es zeigt nach einer Suchanfrage an die Schnittstelle zunächst die Trefferanzahl in der Oberfläche direkt an und ermöglicht dann den Download der zugehörigen Metadaten im XML-Format.

---

## Funktionen

- Auswahl des gewünschten Katalogs und Metadatenformats
- Eingabe von Suchanfragen in einer intuitiven Benutzeroberfläche
- Anzeige der Trefferanzahl
- Warnung bei zu vielen Treffern (über 100.000 - aktuelles Limit der Schnittstelle)
- Download der Ergebnisse als XML-Datei

---

## Installation

1. Repository klonen:

'''bash
git clone https://github.com/dein-benutzername/sru-query-tool.git
cd sru-query-tool'''

2. Virtuelle Umgebung erstellen (optional, empfohlen):
```python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate´´´

