# GUI-maker — Maß-Konfigurator

Ein modernes Python-GUI zur Eingabe von **Länge**, **Breite** und **Höhe**, das automatisch eine `equations.txt` erzeugt.

## Ausgabe-Format (`equations.txt`)

```
"L1"= 400
"L2"= 800
"h"= 100
```

| GUI-Feld | Variable |
|----------|----------|
| Länge    | `L1`     |
| Breite   | `L2`     |
| Höhe     | `h`      |

## Installation

```bash
pip install -r requirements.txt
```

## Starten

```bash
python configurator.py
```

## Verwendung

1. Werte für **Länge (L1)**, **Breite (L2)** und **Höhe (h)** eingeben
2. Auf **„💾 equations.txt speichern"** klicken
3. Speicherort auswählen — die Datei wird im gewünschten Format gespeichert
4. Mit **„↺ Zurücksetzen"** können alle Felder geleert werden

## Eigene Logos einbinden

Die drei Logo-Konstanten befinden sich ganz oben in `configurator.py`:

```python
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOGO-PFADE – hier eigene Bilder eintragen
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEADER_LOGO_PATH  = ""   # Logo oben rechts im Header    (~160 × 50 px)
SIDEBAR_LOGO_PATH = ""   # Logo unten in der Seitenleiste (~160 × 80 px)
APP_ICON_PATH     = ""   # Fenster-Icon (ICO oder PNG,   mind. 32 × 32 px)
```

Pfad eintragen → fertig. Wird ein Pfad leer gelassen oder die Datei nicht gefunden, erscheint automatisch ein stilisierter Platzhalter.

**Empfohlene Formate:** PNG mit Transparenz (RGBA)

## Klassenstruktur

| Klasse               | Aufgabe |
|----------------------|---------|
| `EquationsExporter`  | Reine Datei-Logik, kein UI — leicht erweiterbar & testbar |
| `LogoImage`          | Lädt ein Bild oder erzeugt einen Platzhalter |
| `LabeledEntry`       | Wiederverwendbares Label + Eingabefeld-Widget |
| `Sidebar`            | Linke Navigationsleiste mit Logo & Design-Toggle |
| `HeaderFrame`        | Farbige Titelleiste mit Header-Logo |
| `InputCard`          | Karte mit den drei Eingabefeldern |
| `ResultPanel`        | Vorschau der erzeugten Datei |
| `ActionBar`          | Speichern / Zurücksetzen-Buttons |
| `MassKonfigurator`   | Hauptfenster, orchestriert alle Komponenten |

## Voraussetzungen

- Python 3.10+
- `customtkinter >= 5.2.0`
- `pillow >= 10.0.0`
