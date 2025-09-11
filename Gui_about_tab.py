import tkinter.ttk as ttk
import globals


class AboutTab:
    def __init__(self, parent):
        """Initialisiert das About-Tab mit App-Informationen."""
        self.about_label = ttk.Label(
            parent,
            text=f"{globals.APP_NAME}\nVersion: {globals.APP_VERSION}\nAuthor: {globals.APP_AUTHOR}\n{globals.APP_COPYRIGHT}",
            justify="center"
        )
        self.about_label.pack(expand=True)
