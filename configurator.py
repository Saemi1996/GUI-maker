"""
Maß-Konfigurator
================
Eingabe von Länge (L1), Breite (L2) und Höhe (h).
Ausgabe: equations.txt

Klassen-Übersicht
-----------------
  EquationsExporter   – reine Datei-Logik, kein UI
  LabeledEntry        – wiederverwendbares Label+Eingabefeld-Widget
  HeaderFrame         – Titelleiste oben
  InputCard           – Karte mit den drei Eingabefeldern
  ActionBar           – Speichern / Zurücksetzen-Buttons
  FooterBar           – Design-Umschalter
  MassKonfigurator    – Hauptfenster, orchestriert alle Komponenten
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# ── Appearance-Standardwerte ─────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OUTPUT_FILENAME = "equations.txt"


# ── Datei-Logik (kein UI) ────────────────────────────────────────────────────

class EquationsExporter:
    """Wandelt die drei Maß-Werte in den equations.txt-Inhalt um und speichert ihn.

    Diese Klasse enthält ausschließlich Geschäftslogik und ist vollständig
    unabhängig vom GUI-Framework – leicht testbar und wiederverwendbar.
    """

    # Reihenfolge und Variablen-Namen der Ausgabe
    FIELDS = [
        ("L1", "Länge (L1)"),
        ("L2", "Breite (L2)"),
        ("h",  "Höhe (h)"),
    ]

    @staticmethod
    def parse_number(raw: str, field_label: str) -> int | float:
        """Validiert und konvertiert einen Rohstring in int oder float.

        Args:
            raw:         Benutzereingabe als String.
            field_label: Anzeigename des Feldes für Fehlermeldungen.

        Returns:
            int wenn der Wert ganzzahlig ist, sonst float.

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
    def build_content(cls, l1: int | float, l2: int | float, h: int | float) -> str:
        """Erstellt den equations.txt-Dateiinhalt.

        Args:
            l1: Länge-Wert.
            l2: Breite-Wert.
            h:  Höhe-Wert.

        Returns:
            Fertig formatierter Dateiinhalt als String.
        """
        return f'"L1"= {l1}\n"L2"= {l2}\n"h"= {h}\n'

    @classmethod
    def save(cls, path: str, l1: int | float, l2: int | float, h: int | float) -> None:
        """Schreibt den equations.txt-Inhalt in eine Datei.

        Args:
            path: Vollständiger Dateipfad.
            l1, l2, h: Maß-Werte.
        """
        content = cls.build_content(l1, l2, h)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


# ── Wiederverwendbares Widget ────────────────────────────────────────────────

class LabeledEntry(ctk.CTkFrame):
    """Ein einzelnes Label-Eingabefeld-Paar als eigenständiges Widget.

    Kann in jeder Frame-Komponente mehrfach verwendet werden.

    Args:
        parent:      Übergeordnetes Widget.
        label_text:  Anzeigetext des Labels.
        placeholder: Platzhaltertext im Eingabefeld.
    """

    def __init__(self, parent: ctk.CTkFrame, label_text: str, placeholder: str = ""):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont(size=14),
            anchor="w",
            width=130,
        ).grid(row=0, column=0, padx=(0, 16), sticky="w")

        self._entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=ctk.CTkFont(size=14),
            height=36,
        )
        self._entry.grid(row=0, column=1, sticky="ew")

    def get(self) -> str:
        """Gibt den aktuellen Eingabewert zurück."""
        return self._entry.get()

    def clear(self) -> None:
        """Leert das Eingabefeld."""
        self._entry.delete(0, "end")


# ── UI-Komponenten ───────────────────────────────────────────────────────────

class HeaderFrame(ctk.CTkFrame):
    """Farbige Titelleiste am oberen Rand des Fensters.

    Args:
        parent: Übergeordnetes Widget.
        title:  Anzeigetext der Überschrift.
    """

    def __init__(self, parent: ctk.CTk, title: str):
        super().__init__(parent, corner_radius=0, fg_color=("#1a73e8", "#1558b0"))
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white",
        ).grid(padx=24, pady=18)


class InputCard(ctk.CTkFrame):
    """Karte mit den drei Eingabefeldern Länge, Breite und Höhe.

    Stellt die Eingabewerte über ``get_values()`` zur Verfügung
    und bietet ``clear()`` zum Zurücksetzen aller Felder.

    Args:
        parent: Übergeordnetes Widget.
    """

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent, corner_radius=12)
        self.grid_columnconfigure(0, weight=1)

        # Feldkonfiguration: (Anzeigename, Platzhalter, Schlüssel für EquationsExporter)
        field_configs = [
            ("Länge  (L1)", "z. B. 400", "l1"),
            ("Breite  (L2)", "z. B. 800", "l2"),
            ("Höhe  (h)",   "z. B. 100", "h"),
        ]

        self._entries: dict[str, LabeledEntry] = {}
        for row, (label, placeholder, key) in enumerate(field_configs):
            entry = LabeledEntry(self, label_text=label, placeholder=placeholder)
            entry.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
            self._entries[key] = entry

    def get_values(self) -> dict[str, str]:
        """Gibt die Rohwerte aller Eingabefelder als Dict zurück.

        Returns:
            Dict mit den Schlüsseln ``'l1'``, ``'l2'``, ``'h'``.
        """
        return {key: entry.get() for key, entry in self._entries.items()}

    def clear(self) -> None:
        """Leert alle Eingabefelder."""
        for entry in self._entries.values():
            entry.clear()


class ActionBar(ctk.CTkFrame):
    """Leiste mit den Aktions-Buttons „Speichern" und „Zurücksetzen".

    Args:
        parent:         Übergeordnetes Widget.
        on_save:        Callback für den Speichern-Button.
        on_reset:       Callback für den Zurücksetzen-Button.
    """

    def __init__(self, parent: ctk.CTk, on_save: callable, on_reset: callable):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            self,
            text="💾  equations.txt speichern",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#1a73e8",
            hover_color="#1558b0",
            command=on_save,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            self,
            text="↺  Zurücksetzen",
            font=ctk.CTkFont(size=14),
            height=42,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray25"),
            command=on_reset,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")


class FooterBar(ctk.CTkFrame):
    """Leiste am unteren Rand mit Design-Umschalter (Dark / Light / System).

    Args:
        parent: Übergeordnetes Widget.
    """

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(self, text="Design:", font=ctk.CTkFont(size=12)).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkOptionMenu(
            self,
            values=["Dark", "Light", "System"],
            width=110,
            font=ctk.CTkFont(size=12),
            command=lambda mode: ctk.set_appearance_mode(mode),
        ).pack(side="left")


# ── Hauptfenster ─────────────────────────────────────────────────────────────

class MassKonfigurator(ctk.CTk):
    """Hauptfenster des Maß-Konfigurators.

    Orchestriert alle Komponenten und verbindet die UI mit der
    ``EquationsExporter``-Logik.
    """

    def __init__(self):
        super().__init__()
        self.title("📐  Maß-Konfigurator")
        self.geometry("480x430")
        self.resizable(False, False)
        self._build_ui()

    # ── Layout-Aufbau ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        HeaderFrame(self, title="📐  Maß-Konfigurator").grid(
            row=0, column=0, sticky="we"
        )

        self._input_card = InputCard(self)
        self._input_card.grid(row=1, column=0, padx=32, pady=(28, 0), sticky="we")

        ActionBar(self, on_save=self._save_equations, on_reset=self._reset).grid(
            row=2, column=0, padx=32, pady=24, sticky="we"
        )

        self._preview = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, family="Courier"),
            justify="left",
            text_color=("gray40", "gray60"),
        )
        self._preview.grid(row=3, column=0, padx=32, pady=(0, 16), sticky="w")

        FooterBar(self).grid(row=4, column=0, padx=32, pady=(0, 12), sticky="e")

    # ── Aktionen ──────────────────────────────────────────────────────────────

    def _save_equations(self) -> None:
        """Liest die Eingaben, validiert sie und speichert die equations.txt."""
        raw = self._input_card.get_values()
        try:
            l1 = EquationsExporter.parse_number(raw["l1"], "Länge (L1)")
            l2 = EquationsExporter.parse_number(raw["l2"], "Breite (L2)")
            h  = EquationsExporter.parse_number(raw["h"],  "Höhe (h)")
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
            return  # Nutzer hat abgebrochen

        EquationsExporter.save(path, l1, l2, h)

        preview_text = EquationsExporter.build_content(l1, l2, h).strip()
        self._preview.configure(
            text=f"✅  Gespeichert: {os.path.basename(path)}\n\n{preview_text}"
        )
        messagebox.showinfo("Gespeichert", f"✅  Datei gespeichert:\n{path}")

    def _reset(self) -> None:
        """Leert alle Eingabefelder und die Vorschau."""
        self._input_card.clear()
        self._preview.configure(text="")


# ── Einstiegspunkt ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = MassKonfigurator()
    app.mainloop()
