
import tkinter as tk
from ui.estilos import CARD_BG, CARD_BG_HOV, CARD_TEXT, BORDE, FUENTE_BOTON

class BotonCard(tk.Frame):
    """Card con imagen y texto, tamaño fijo y colores coherentes."""
    def __init__(self, master, texto, imagen: tk.PhotoImage | None, comando,
                 ancho=300, alto=280):
        super().__init__(master, width=ancho, height=alto, bg=CARD_BG, bd=1, highlightthickness=1)
        self.configure(highlightbackground=BORDE)
        self.pack_propagate(False)

        self._btn = tk.Button(
            self, text=texto, image=imagen, compound="top",
            command=comando, cursor="hand2",
            bg=CARD_BG, activebackground=CARD_BG_HOV,
            fg=CARD_TEXT, activeforeground=CARD_TEXT,
            bd=0, font=FUENTE_BOTON, padx=18, pady=14
        )
        self._btn.image = imagen
        self._btn.pack(fill="both", expand=True)

        # Efecto hover
        for w in (self, self._btn):
            w.bind("<Enter>", lambda _e, fr=self: fr.configure(bg=CARD_BG_HOV))
            w.bind("<Leave>", lambda _e, fr=self: fr.configure(bg=CARD_BG))
