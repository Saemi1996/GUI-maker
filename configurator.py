"""
Maß-Konfigurator
================
Eingabe von Länge (L1), Breite (L2), Höhe (h) sowie Anzahl Füße L1/L2.
Ausgabe: equations.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  LOGO-PFADE – hier eigene Bilder eintragen:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HEADER_LOGO_PATH  – Logo oben links im Header
                      (empfohlen: PNG, ~160 × 50 px)

  SIDEBAR_LOGO_PATH – Logo unten in der Seitenleiste
                      (empfohlen: PNG, ~120 × 120 px)

  APP_ICON_PATH     – Fenster-Icon (ICO oder PNG,
                      mind. 32 × 32 px)

  Beispiel:
      HEADER_LOGO_PATH  = "assets/logo_header.png"
      SIDEBAR_LOGO_PATH = "assets/logo_sidebar.png"
      APP_ICON_PATH     = "assets/icon.ico"

  Wird ein Pfad leer gelassen oder die Datei nicht
  gefunden, erscheint automatisch ein Platzhalter.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Klassen-Übersicht
-----------------
  EquationsExporter  – reine Datei-Logik, kein UI
  LogoImage          – lädt Bild oder zeigt Platzhalter
  LabeledEntry       – wiederverwendbares Label+Eingabefeld-Widget
  Sidebar            – linke Navigationsleiste mit Logo
  HeaderFrame        – Titelleiste mit Header-Logo
  InputCard          – Karte mit den fünf Eingabefeldern
  ResultPanel        – zeigt Vorschau der erzeugten Datei
  ActionBar          – Speichern / Zurücksetzen-Buttons
  MassKonfigurator   – Hauptfenster, orchestriert alle Komponenten
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOGO-PFADE – hier eigene Bilder eintragen
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEADER_LOGO_PATH  = ""   # z. B. "assets/logo_header.png"
SIDEBAR_LOGO_PATH = ""   # z. B. "assets/logo_sidebar.png"
APP_ICON_PATH     = ""   # z. B. "assets/icon.ico"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Appearance-Standardwerte
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OUTPUT_FILENAME = "equations.txt"

# Farbpalette (leicht anpassbar)
ACCENT       = "#1a73e8"
ACCENT_HOVER = "#1558b0"
SIDEBAR_BG   = ("#1e1e2e", "#1e1e2e")   # dark / light
CARD_BG      = ("#f0f0f8", "#2a2a3e")


# ── Datei-Logik (kein UI) ────────────────────────────────────────────────────

class EquationsExporter:
    """Wandelt die fünf Maß-Werte in den equations.txt-Inhalt um und speichert ihn.

    Enthält ausschließlich Geschäftslogik — vollständig unabhängig vom GUI-Framework.
    """

    @staticmethod
    def parse_number(raw: str, field_label: str) -> int | float:
        """Validiert und konvertiert einen Rohstring in int oder float.

        Raises:
            ValueError: Wenn der String leer oder keine Zahl ist.
        """
        raw = raw.strip()
        if not raw:
            raise ValueError(f"Bitte {field_label} eingeben.")
        try:
            num = float(raw)
        except ValueError:
            raise ValueError(f"'{raw}' ist kein gültiger Zahlenwert für {field_label}.")
        return int(num) if num == int(num) else num

    @classmethod
    def build_content(
        cls,
        l1: int | float,
        l2: int | float,
        h: int | float,
        anzahl_fuesse_l1: int | float,
        anzahl_fuesse_l2: int | float,
    ) -> str:
        """Erstellt den equations.txt-Dateiinhalt."""
        return (
            f'"L1"= {l1}\n'
            f'"L2"= {l2}\n'
            f'"h"= {h}\n'
            f'"Anzahl Fuesse L1"= {anzahl_fuesse_l1}\n'
            f'"Anzahl Fuesse L2"= {anzahl_fuesse_l2}\n'
        )

    @classmethod
    def save(
        cls,
        path: str,
        l1: int | float,
        l2: int | float,
        h: int | float,
        anzahl_fuesse_l1: int | float,
        anzahl_fuesse_l2: int | float,
    ) -> None:
        """Schreibt den equations.txt-Inhalt in eine Datei."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(cls.build_content(l1, l2, h, anzahl_fuesse_l1, anzahl_fuesse_l2))


# ── Logo-Helper ──────────────────────────────────────────────────────────────

class LogoImage:
    """Lädt ein Logo-Bild oder erzeugt einen stilisierten Platzhalter.

    Args:
        path:           Pfad zur Bilddatei (leer → Platzhalter).
        size:           Zielgröße als (Breite, Höhe)-Tupel.
        placeholder_text: Text im Platzhalter (z. B. "Ihr Logo").
    """

    def __init__(self, path: str, size: tuple[int, int], placeholder_text: str = "Ihr Logo"):
        self._size = size
        self._ctk_image = self._load(path, size, placeholder_text)

    def _load(self, path: str, size: tuple[int, int], text: str) -> ctk.CTkImage:
        if path and os.path.isfile(path):
            img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
        else:
            img = self._make_placeholder(size, text)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    @staticmethod
    def _make_placeholder(size: tuple[int, int], text: str) -> Image.Image:
        """Zeichnet einen abgerundeten Platzhalter-Rahmen mit Text."""
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        radius = min(w, h) // 6

        # Hintergrund-Rechteck (abgerundet simuliert via Ellipsen + Rechtecke)
        fill   = (80, 80, 120, 200)
        border = (120, 120, 200, 255)
        draw.rounded_rectangle([2, 2, w - 3, h - 3], radius=radius, fill=fill, outline=border, width=2)

        # Icon-Symbol oben
        icon_size = min(w, h) // 3
        cx, cy = w // 2, h // 2 - icon_size // 4
        draw.ellipse([cx - icon_size, cy - icon_size, cx + icon_size, cy + icon_size],
                     outline=border, width=2)
        draw.line([cx, cy - icon_size // 2, cx, cy + icon_size // 2], fill=border, width=2)
        draw.line([cx - icon_size // 2, cy, cx + icon_size // 2, cy], fill=border, width=2)

        # Text darunter
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", max(10, h // 6))
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((w - tw) // 2, h - th - 6), text, fill=(180, 180, 220, 255), font=font)

        return img

    @property
    def ctk_image(self) -> ctk.CTkImage:
        return self._ctk_image


# ── Wiederverwendbares Widget ────────────────────────────────────────────────

class LabeledEntry(ctk.CTkFrame):
    """Ein Label-Eingabefeld-Paar als eigenständiges Widget.

    Args:
        parent:      Übergeordnetes Widget.
        label_text:  Anzeigetext des Labels.
        unit:        Optionale Einheitenbezeichnung (z. B. "mm").
        placeholder: Platzhaltertext im Eingabefeld.
    """

    def __init__(self, parent, label_text: str, unit: str = "", placeholder: str = ""):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont(size=14),
            anchor="w",
            width=140,
        ).grid(row=0, column=0, padx=(0, 12), sticky="w")

        self._entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=ctk.CTkFont(size=14),
            height=38,
            border_width=2,
        )
        self._entry.grid(row=0, column=1, sticky="ew")

        if unit:
            ctk.CTkLabel(
                self,
                text=unit,
                font=ctk.CTkFont(size=13),
                text_color=("gray50", "gray60"),
                width=36,
            ).grid(row=0, column=2, padx=(8, 0), sticky="w")

    def get(self) -> str:
        return self._entry.get()

    def clear(self) -> None:
        self._entry.delete(0, "end")


# ── UI-Komponenten ───────────────────────────────────────────────────────────

class Sidebar(ctk.CTkFrame):
    """Linke Seitenleiste mit App-Titel, Navigationspunkten und Sidebar-Logo.

    Args:
        parent:           Übergeordnetes Widget.
        sidebar_logo_path: Pfad zum Sidebar-Logo (leer → Platzhalter).
    """

    def __init__(self, parent, sidebar_logo_path: str):
        super().__init__(parent, width=200, corner_radius=0, fg_color=SIDEBAR_BG)
        self.grid_rowconfigure(5, weight=1)
        self.grid_propagate(False)

        # App-Name
        ctk.CTkLabel(
            self,
            text="📐",
            font=ctk.CTkFont(size=40),
        ).grid(row=0, column=0, padx=20, pady=(28, 4))

        ctk.CTkLabel(
            self,
            text="Maß-\nKonfigurator",
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center",
        ).grid(row=1, column=0, padx=20, pady=(0, 24))

        # Trennlinie
        ctk.CTkFrame(self, height=1, fg_color=("gray60", "gray35")).grid(
            row=2, column=0, sticky="ew", padx=16, pady=(0, 20)
        )

        # Navigationspunkte (statisch; erweiterbar)
        nav_items = [
            ("📏", "Maße eingeben"),
            ("💾", "Datei speichern"),
        ]
        for i, (icon, label) in enumerate(nav_items):
            ctk.CTkLabel(
                self,
                text=f"  {icon}  {label}",
                font=ctk.CTkFont(size=13),
                anchor="w",
                text_color=("gray80", "gray80"),
            ).grid(row=3 + i, column=0, padx=16, pady=4, sticky="ew")

        # Design-Umschalter
        ctk.CTkLabel(
            self, text="Design", font=ctk.CTkFont(size=11), text_color=("gray55", "gray55")
        ).grid(row=6, column=0, padx=20, pady=(0, 4), sticky="w")
        ctk.CTkOptionMenu(
            self,
            values=["Dark", "Light", "System"],
            width=160,
            font=ctk.CTkFont(size=12),
            command=lambda m: ctk.set_appearance_mode(m),
        ).grid(row=7, column=0, padx=20, pady=(0, 16), sticky="ew")

        # Sidebar-Logo
        logo = LogoImage(sidebar_logo_path, size=(160, 80), placeholder_text="Ihr Logo")
        ctk.CTkLabel(self, image=logo.ctk_image, text="").grid(
            row=8, column=0, padx=20, pady=(8, 24)
        )
        self._sidebar_logo = logo  # Referenz halten, damit GC es nicht löscht


class HeaderFrame(ctk.CTkFrame):
    """Farbige Titelleiste mit Header-Logo rechts.

    Args:
        parent:            Übergeordnetes Widget.
        header_logo_path:  Pfad zum Header-Logo (leer → Platzhalter).
    """

    def __init__(self, parent, header_logo_path: str):
        super().__init__(parent, corner_radius=0, fg_color=(ACCENT, ACCENT_HOVER))
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Maß-Konfigurator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white",
            anchor="w",
        ).grid(row=0, column=0, padx=24, pady=16, sticky="w")

        logo = LogoImage(header_logo_path, size=(120, 44), placeholder_text="Header-Logo")
        ctk.CTkLabel(self, image=logo.ctk_image, text="").grid(
            row=0, column=1, padx=16, pady=8, sticky="e"
        )
        self._header_logo = logo  # Referenz halten


class InputCard(ctk.CTkFrame):
    """Karte mit den fünf Eingabefeldern Länge, Breite, Höhe und Anzahl Füße L1/L2.

    Args:
        parent: Übergeordnetes Widget.
    """

    # Feldkonfiguration: (Anzeigename, Einheit, Platzhalter, interner Schlüssel)
    _FIELDS = [
        ("Länge  (L1)",        "mm", "z. B. 400", "l1"),
        ("Breite  (L2)",       "mm", "z. B. 800", "l2"),
        ("Höhe  (h)",          "mm", "z. B. 100", "h"),
        ("Anz. Füße  (L1)",    "",   "3",          "anzahl_fuesse_l1"),
        ("Anz. Füße  (L2)",    "",   "3",          "anzahl_fuesse_l2"),
    ]

    def __init__(self, parent):
        super().__init__(parent, corner_radius=14, fg_color=CARD_BG)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Abmessungen eingeben",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=24, pady=(20, 8), sticky="w")

        ctk.CTkFrame(self, height=1, fg_color=("gray60", "gray45")).grid(
            row=1, column=0, sticky="ew", padx=16, pady=(0, 12)
        )

        self._entries: dict[str, LabeledEntry] = {}
        for i, (label, unit, placeholder, key) in enumerate(self._FIELDS):
            entry = LabeledEntry(self, label_text=label, unit=unit, placeholder=placeholder)
            entry.grid(row=i + 2, column=0, padx=24, pady=8, sticky="ew")
            self._entries[key] = entry

        # Abstand unten
        ctk.CTkFrame(self, height=12, fg_color="transparent").grid(row=99, column=0)

    def get_values(self) -> dict[str, str]:
        """Gibt die Rohwerte aller Eingabefelder als Dict zurück."""
        return {key: entry.get() for key, entry in self._entries.items()}

    def clear(self) -> None:
        """Leert alle Eingabefelder."""
        for entry in self._entries.values():
            entry.clear()


class ResultPanel(ctk.CTkFrame):
    """Zeigt eine Vorschau des erzeugten Dateiinhalts nach dem Speichern.

    Args:
        parent: Übergeordnetes Widget.
    """

    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, fg_color=CARD_BG)
        self.grid_columnconfigure(0, weight=1)

        self._title = ctk.CTkLabel(
            self,
            text="Vorschau",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            text_color=("gray30", "gray70"),
        )
        self._title.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        self._body = ctk.CTkLabel(
            self,
            text='—',
            font=ctk.CTkFont(size=13, family="Courier"),
            justify="left",
            anchor="w",
            text_color=("gray20", "gray75"),
        )
        self._body.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

    def update(self, filename: str, content: str) -> None:
        """Aktualisiert die Vorschau mit Dateiname und Inhalt."""
        self._title.configure(text=f"✅  {filename}")
        self._body.configure(text=content.strip())

    def clear(self) -> None:
        """Setzt die Vorschau zurück."""
        self._title.configure(text="Vorschau")
        self._body.configure(text="—")


class ActionBar(ctk.CTkFrame):
    """Leiste mit den Aktions-Buttons „Speichern" und „Zurücksetzen".

    Args:
        parent:   Übergeordnetes Widget.
        on_save:  Callback für den Speichern-Button.
        on_reset: Callback für den Zurücksetzen-Button.
    """

    def __init__(self, parent, on_save: callable, on_reset: callable):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            self,
            text="💾  equations.txt speichern",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=on_save,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            self,
            text="↺  Zurücksetzen",
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray25"),
            command=on_reset,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")


# ── Hauptfenster ─────────────────────────────────────────────────────────────

class MassKonfigurator(ctk.CTk):
    """Hauptfenster des Maß-Konfigurators.

    Orchestriert alle Komponenten und verbindet die UI mit der
    ``EquationsExporter``-Logik.
    """

    def __init__(self):
        super().__init__()
        self.title("📐  Maß-Konfigurator")
        self.geometry("760x700")
        self.minsize(680, 640)
        self._set_icon()
        self._build_ui()

    # ── Icon ──────────────────────────────────────────────────────────────────

    def _set_icon(self) -> None:
        """Setzt das Fenster-Icon, falls APP_ICON_PATH gesetzt und gültig ist."""
        if APP_ICON_PATH and os.path.isfile(APP_ICON_PATH):
            try:
                self.iconbitmap(APP_ICON_PATH)
            except Exception:
                pass

    # ── Layout-Aufbau ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Sidebar (Spalte 0, alle Zeilen)
        self._sidebar = Sidebar(self, sidebar_logo_path=SIDEBAR_LOGO_PATH)
        self._sidebar.grid(row=0, column=0, rowspan=3, sticky="nswe")

        # Header (Zeile 0, Spalte 1)
        self._header = HeaderFrame(self, header_logo_path=HEADER_LOGO_PATH)
        self._header.grid(row=0, column=1, sticky="we")

        # Haupt-Content (Zeile 1, Spalte 1)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=1, sticky="nswe", padx=28, pady=20)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self._input_card = InputCard(content)
        self._input_card.grid(row=0, column=0, sticky="ew")

        self._result_panel = ResultPanel(content)
        self._result_panel.grid(row=1, column=0, sticky="ew", pady=(16, 0))

        # Action-Bar (Zeile 2, Spalte 1)
        self._action_bar = ActionBar(
            self, on_save=self._save_equations, on_reset=self._reset
        )
        self._action_bar.grid(row=2, column=1, sticky="we", padx=28, pady=(0, 20))

    # ── Aktionen ──────────────────────────────────────────────────────────────

    def _save_equations(self) -> None:
        """Liest Eingaben, validiert sie und speichert die equations.txt."""
        raw = self._input_card.get_values()
        try:
            l1               = EquationsExporter.parse_number(raw["l1"],               "Länge (L1)")
            l2               = EquationsExporter.parse_number(raw["l2"],               "Breite (L2)")
            h                = EquationsExporter.parse_number(raw["h"],                "Höhe (h)")
            anzahl_fuesse_l1 = EquationsExporter.parse_number(raw["anzahl_fuesse_l1"], "Anzahl Füße L1")
            anzahl_fuesse_l2 = EquationsExporter.parse_number(raw["anzahl_fuesse_l2"], "Anzahl Füße L2")
        except ValueError as exc:
            messagebox.showerror("Eingabefehler", str(exc))
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")],
            initialfile=OUTPUT_FILENAME,
            title="Speichern unter",
        )
        if not path:
            return

        EquationsExporter.save(path, l1, l2, h, anzahl_fuesse_l1, anzahl_fuesse_l2)

        content = EquationsExporter.build_content(l1, l2, h, anzahl_fuesse_l1, anzahl_fuesse_l2)
        self._result_panel.update(os.path.basename(path), content)
        messagebox.showinfo("Gespeichert", f"✅  Datei gespeichert:\n{path}")

    def _reset(self) -> None:
        """Leert alle Eingabefelder und die Ergebnis-Vorschau."""
        self._input_card.clear()
        self._result_panel.clear()


# ── Einstiegspunkt ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MassKonfigurator()
    app.mainloop()
