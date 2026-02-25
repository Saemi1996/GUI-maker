"""
Modern Python Configurator GUI
Built with CustomTkinter for a contemporary look and feel.
"""

import json
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# ── Appearance defaults ──────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "general": {
        "app_name": "MyApp",
        "language": "English",
        "theme": "Dark",
        "auto_save": True,
    },
    "network": {
        "host": "localhost",
        "port": "8080",
        "timeout": "30",
        "ssl_enabled": False,
    },
    "performance": {
        "max_threads": "4",
        "cache_size": "256",
        "log_level": "INFO",
        "debug_mode": False,
    },
    "notifications": {
        "enable_notifications": True,
        "sound_alerts": False,
        "email_alerts": False,
        "email_address": "",
    },
}


class ConfiguratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚙  Configurator")
        self.geometry("920x640")
        self.minsize(800, 560)

        self.config_data = self._load_config()

        self._build_layout()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left sidebar ──────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(6, weight=1)

        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="⚙  Configurator",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(28, 20))

        self.nav_buttons: list[ctk.CTkButton] = []
        sections = ["General", "Network", "Performance", "Notifications"]
        icons = ["🏠", "🌐", "⚡", "🔔"]
        for i, (section, icon) in enumerate(zip(sections, icons)):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {section}",
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                font=ctk.CTkFont(size=14),
                command=lambda s=section: self._show_section(s),
            )
            btn.grid(row=i + 1, column=0, padx=10, pady=4, sticky="ew")
            self.nav_buttons.append(btn)

        # appearance toggle at the bottom of the sidebar
        appearance_label = ctk.CTkLabel(self.sidebar, text="Appearance", anchor="w")
        appearance_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="w")

        self.appearance_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self._change_appearance,
        )
        self.appearance_menu.grid(row=8, column=0, padx=20, pady=(4, 20), sticky="ew")

        # ── Main content area ─────────────────────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Title bar
        self.section_title = ctk.CTkLabel(
            self.content_frame,
            text="General Settings",
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        )
        self.section_title.grid(row=0, column=0, sticky="w", pady=(0, 16))

        # Scrollable settings panel
        self.settings_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.settings_frame.grid(row=1, column=0, sticky="nswe")
        self.settings_frame.grid_columnconfigure(1, weight=1)

        # ── Bottom action bar ─────────────────────────────────────────────────
        action_bar = ctk.CTkFrame(self, height=56, corner_radius=0)
        action_bar.grid(row=1, column=0, columnspan=2, sticky="we")
        action_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            action_bar,
            text="📂  Load Config",
            width=140,
            command=self._load_from_file,
        ).grid(row=0, column=0, padx=12, pady=10)

        ctk.CTkButton(
            action_bar,
            text="💾  Save Config",
            width=140,
            command=self._save_to_file,
        ).grid(row=0, column=1, padx=4, pady=10)

        ctk.CTkButton(
            action_bar,
            text="✅  Apply",
            width=140,
            fg_color="#1f6aa5",
            hover_color="#144870",
            command=self._apply_config,
        ).grid(row=0, column=3, padx=12, pady=10)

        ctk.CTkButton(
            action_bar,
            text="↺  Reset Defaults",
            width=140,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self._reset_defaults,
        ).grid(row=0, column=4, padx=(0, 12), pady=10)

        # Build widget registry and show first section
        self.widgets: dict = {}
        self._show_section("General")
        self._highlight_nav("General")

    # ── Section rendering ─────────────────────────────────────────────────────

    def _clear_settings(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        self.widgets = {}

    def _show_section(self, section: str):
        self._clear_settings()
        self.section_title.configure(text=f"{section} Settings")
        self._highlight_nav(section)

        section_key = section.lower()
        data = self.config_data.get(section_key, {})

        builders = {
            "general": self._build_general,
            "network": self._build_network,
            "performance": self._build_performance,
            "notifications": self._build_notifications,
        }
        builders.get(section_key, lambda d: None)(data)

    def _highlight_nav(self, active: str):
        sections = ["General", "Network", "Performance", "Notifications"]
        for btn, name in zip(self.nav_buttons, sections):
            if name == active:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    # ── Individual section builders ───────────────────────────────────────────

    def _add_entry(self, row: int, label: str, key: str, value: str):
        ctk.CTkLabel(
            self.settings_frame, text=label, anchor="w", font=ctk.CTkFont(size=13)
        ).grid(row=row, column=0, padx=(10, 20), pady=8, sticky="w")
        entry = ctk.CTkEntry(self.settings_frame, placeholder_text=label)
        entry.insert(0, value)
        entry.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
        self.widgets[key] = entry

    def _add_switch(self, row: int, label: str, key: str, value: bool):
        ctk.CTkLabel(
            self.settings_frame, text=label, anchor="w", font=ctk.CTkFont(size=13)
        ).grid(row=row, column=0, padx=(10, 20), pady=8, sticky="w")
        switch = ctk.CTkSwitch(self.settings_frame, text="")
        if value:
            switch.select()
        else:
            switch.deselect()
        switch.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        self.widgets[key] = switch

    def _add_optionmenu(self, row: int, label: str, key: str, value: str, options: list):
        ctk.CTkLabel(
            self.settings_frame, text=label, anchor="w", font=ctk.CTkFont(size=13)
        ).grid(row=row, column=0, padx=(10, 20), pady=8, sticky="w")
        menu = ctk.CTkOptionMenu(self.settings_frame, values=options)
        menu.set(value)
        menu.grid(row=row, column=1, padx=10, pady=8, sticky="w")
        self.widgets[key] = menu

    def _add_separator(self, row: int, title: str):
        ctk.CTkLabel(
            self.settings_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
            text_color=("gray30", "gray70"),
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(20, 4), sticky="w")

    def _build_general(self, data: dict):
        self._add_separator(0, "Application")
        self._add_entry(1, "App Name", "app_name", data.get("app_name", ""))
        self._add_optionmenu(
            2, "Language", "language", data.get("language", "English"),
            ["English", "German", "French", "Spanish", "Italian"],
        )
        self._add_optionmenu(
            3, "Theme", "theme", data.get("theme", "Dark"),
            ["Dark", "Light", "System"],
        )
        self._add_separator(4, "Behaviour")
        self._add_switch(5, "Auto-Save on Exit", "auto_save", data.get("auto_save", True))

    def _build_network(self, data: dict):
        self._add_separator(0, "Server")
        self._add_entry(1, "Host", "host", data.get("host", "localhost"))
        self._add_entry(2, "Port", "port", data.get("port", "8080"))
        self._add_entry(3, "Timeout (s)", "timeout", data.get("timeout", "30"))
        self._add_separator(4, "Security")
        self._add_switch(5, "Enable SSL / TLS", "ssl_enabled", data.get("ssl_enabled", False))

    def _build_performance(self, data: dict):
        self._add_separator(0, "Resources")
        self._add_entry(1, "Max Threads", "max_threads", data.get("max_threads", "4"))
        self._add_entry(2, "Cache Size (MB)", "cache_size", data.get("cache_size", "256"))
        self._add_separator(3, "Logging")
        self._add_optionmenu(
            4, "Log Level", "log_level", data.get("log_level", "INFO"),
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        self._add_switch(5, "Debug Mode", "debug_mode", data.get("debug_mode", False))

    def _build_notifications(self, data: dict):
        self._add_separator(0, "Alerts")
        self._add_switch(
            1, "Enable Notifications", "enable_notifications",
            data.get("enable_notifications", True),
        )
        self._add_switch(2, "Sound Alerts", "sound_alerts", data.get("sound_alerts", False))
        self._add_separator(3, "Email")
        self._add_switch(4, "Email Alerts", "email_alerts", data.get("email_alerts", False))
        self._add_entry(5, "Email Address", "email_address", data.get("email_address", ""))

    # ── Actions ────────────────────────────────────────────────────────────────

    def _collect_current_section(self) -> dict:
        """Read all widget values from the currently displayed section."""
        result = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                result[key] = widget.get()
            elif isinstance(widget, ctk.CTkSwitch):
                result[key] = widget.get() == 1
            elif isinstance(widget, ctk.CTkOptionMenu):
                result[key] = widget.get()
        return result

    def _apply_config(self):
        # Determine the current section from the title label
        title = self.section_title.cget("text").replace(" Settings", "").lower()
        self.config_data[title] = self._collect_current_section()
        self._save_config()
        messagebox.showinfo("Configurator", "✅  Settings applied and saved successfully!")

    def _reset_defaults(self):
        if messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            self.config_data = json.loads(json.dumps(DEFAULT_CONFIG))
            title = self.section_title.cget("text").replace(" Settings", "")
            self._show_section(title)

    def _save_to_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="config.json",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2)
            messagebox.showinfo("Configurator", f"💾  Config saved to:\n{path}")

    def _load_from_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            try:
                with open(path, encoding="utf-8") as f:
                    self.config_data = json.load(f)
                title = self.section_title.cget("text").replace(" Settings", "")
                self._show_section(title)
                messagebox.showinfo("Configurator", "📂  Config loaded successfully!")
            except Exception as exc:
                messagebox.showerror("Error", f"Could not load config:\n{exc}")

    # ── Persistence ────────────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return json.loads(json.dumps(DEFAULT_CONFIG))

    def _save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2)

    def _change_appearance(self, mode: str):
        ctk.set_appearance_mode(mode)


if __name__ == "__main__":
    app = ConfiguratorApp()
    app.mainloop()
