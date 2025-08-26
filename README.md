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

Das SRUQueryTool kann als Standalone-Anwendung heruntergeladen und einfach ausgeführt werden. Alternativ kann die Anwendung über den in diesem Repository bereitgestellten Python-Code installiert und genutzt werden. 

### Standalone-Anwendung 

In diesem Repository stehen momentan [zwei Versionen des SRUQueryTool als Release](https://github.com/ssp24/SRUQueryTool/releases/tag/v0.9) zur Verfügung: 

  - Windows: Für Windows steht die SRUQueryTool.exe zum Download bereit. 
  - MacOS: Für Mac steht das SRUQueryTool als .dmg-Datei zum Download bereit.

Beide Standalone-Versionen wurden aus dem hier bereitgestellten Quellcode mit Hilfe von Pyinstaller gepackt.
Eine Version für Linux ist geplant. 


### Installation der Python-Anwendung

  1. Repository klonen:

  ```bash
  git clone https://github.com/dein-benutzername/sru-query-tool.git
  cd sru-query-tool
  ```

  2. Virtuelle Umgebung erstellen (optional, empfohlen):
  ```bash
  python -m venv venv
  # macOS/Linux
  source venv/bin/activate
  # Windows
  venv\Scripts\activate
  ```

  3. Abhängigkeiten installieren:
  ```bash
  pip install -r requirements.txt
  ```

#### Nutzung

Starten der Anwendung:
```bash
python SRUQueryTool.py
```


## Hinweise 
  * Bei mehr als 100.000 Treffern muss die Suchanfrage weiter eingeschränkt werden, da die SRU-Schnittstelle der DNB hier aktuell ein Limit besitzt. 
  * Die Anwendung setzt Python 3.9+ und PyQt5 voraus.
  * Die XML-Dateien können lokal an einem beliebigen Speicherort abgelegt werden.

