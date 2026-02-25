"""
Maß-Konfigurator
Eingabe von Länge (L1), Breite (L2) und Höhe (h).
Ausgabe: equations.txt
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# ── Appearance ───────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

OUTPUT_FILENAME = "equations.txt"


class MassKonfigurator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("📐  Maß-Konfigurator")
        self.geometry("480x420")
        self.resizable(False, False)

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, corner_radius=0, fg_color=("#1a73e8", "#1558b0"))
        header.grid(row=0, column=0, sticky="we")
        ctk.CTkLabel(
            header,
            text="📐  Maß-Konfigurator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white",
        ).grid(padx=24, pady=18)

        # ── Input card ────────────────────────────────────────────────────────
        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=1, column=0, padx=32, pady=(28, 0), sticky="we")
        card.grid_columnconfigure(1, weight=1)

        fields = [
            ("Länge  (L1)", "entry_l1", "z. B. 400"),
            ("Breite  (L2)", "entry_l2", "z. B. 800"),
            ("Höhe  (h)", "entry_h", "z. B. 100"),
        ]

        for row, (label_text, attr, placeholder) in enumerate(fields):
            ctk.CTkLabel(
                card,
                text=label_text,
                font=ctk.CTkFont(size=14),
                anchor="w",
            ).grid(row=row, column=0, padx=(20, 16), pady=12, sticky="w")

            entry = ctk.CTkEntry(
                card,
                placeholder_text=placeholder,
                font=ctk.CTkFont(size=14),
                height=36,
            )
            entry.grid(row=row, column=1, padx=(0, 20), pady=12, sticky="ew")
            setattr(self, attr, entry)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=32, pady=24, sticky="we")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="💾  equations.txt speichern",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#1a73e8",
            hover_color="#1558b0",
            command=self._save_equations,
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="↺  Zurücksetzen",
            font=ctk.CTkFont(size=14),
            height=42,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray25"),
            command=self._reset,
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        # ── Preview label ─────────────────────────────────────────────────────
        self.preview_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, family="Courier"),
            justify="left",
            text_color=("gray40", "gray60"),
        )
        self.preview_label.grid(row=3, column=0, padx=32, pady=(0, 20), sticky="w")

        # ── Appearance toggle ─────────────────────────────────────────────────
        appearance_frame = ctk.CTkFrame(self, fg_color="transparent")
        appearance_frame.grid(row=4, column=0, padx=32, pady=(0, 12), sticky="e")
        ctk.CTkLabel(appearance_frame, text="Design:", font=ctk.CTkFont(size=12)).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkOptionMenu(
            appearance_frame,
            values=["Dark", "Light", "System"],
            width=110,
            font=ctk.CTkFont(size=12),
            command=lambda m: ctk.set_appearance_mode(m),
        ).pack(side="left")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _get_values(self):
        """Return (l1, l2, h) as strings, or raise ValueError if any field is empty/non-numeric."""
        values = {}
        for name, attr in [("Länge (L1)", "entry_l1"), ("Breite (L2)", "entry_l2"), ("Höhe (h)", "entry_h")]:
            raw = getattr(self, attr).get().strip()
            if not raw:
                raise ValueError(f"Bitte {name} eingeben.")
            try:
                # Accept integers or floats; store as-is (no trailing .0 for whole numbers)
                num = float(raw)
                values[attr] = int(num) if num == int(num) else num
            except ValueError:
                raise ValueError(f"'{raw}' ist kein gültiger Zahlenwert für {name}.")
        return values["entry_l1"], values["entry_l2"], values["entry_h"]

    def _build_content(self, l1, l2, h) -> str:
        return f'"L1"= {l1}\n"L2"= {l2}\n"h"= {h}\n'

    def _save_equations(self):
        try:
            l1, l2, h = self._get_values()
        except ValueError as exc:
            messagebox.showerror("Eingabefehler", str(exc))
            return

        content = self._build_content(l1, l2, h)

        # Ask where to save
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text-Dateien", "*.txt"), ("Alle Dateien", "*.*")],
            initialfile=OUTPUT_FILENAME,
            title="Speichern unter",
        )
        if not path:
            return  # user cancelled

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # Show preview
        self.preview_label.configure(
            text=f"✅  Gespeichert: {os.path.basename(path)}\n\n{content.strip()}"
        )
        messagebox.showinfo("Gespeichert", f"✅  Datei gespeichert:\n{path}")

    def _reset(self):
        for attr in ("entry_l1", "entry_l2", "entry_h"):
            entry = getattr(self, attr)
            entry.delete(0, "end")
        self.preview_label.configure(text="")


if __name__ == "__main__":
    app = MassKonfigurator()
    app.mainloop()
