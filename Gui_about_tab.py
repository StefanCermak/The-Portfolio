import tkinter.ttk as ttk
import globals


class AboutTab:
    """
    Tab for displaying application information such as name, version, author, and copyright.
    """
    def __init__(self, parent: object) -> None:
        """
        Initialize the AboutTab with application information.

        Args:
            parent: The parent tkinter widget.
        """
        self.about_label = ttk.Label(
            parent,
            text=f"{globals.APP_NAME}\nVersion: {globals.APP_VERSION}\nAuthor: {globals.APP_AUTHOR}\n{globals.APP_COPYRIGHT}",
            justify="center"
        )
        self.about_label.pack(expand=True)
