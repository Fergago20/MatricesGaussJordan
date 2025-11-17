
import tkinter as tk
from ui.estilos import CARD_BG, CARD_BG_HOV, CARD_TEXT, BORDE, FUENTE_BOTON

class BotonCard(tk.Frame):
    """
    Card con imagen y texto, ahora con color de fondo personalizable.
    """
    def __init__(self, master, texto, imagen: tk.PhotoImage | None, comando,
                 ancho=300, alto=280, color_fondo=None):

        # Elegir color base
        self.color_base = color_fondo if color_fondo else CARD_BG

        # Elegir hover (si se da un color personalizado: oscurecer un poco)
        if color_fondo:
            self.color_hover = self._oscurecer(color_fondo, porcentaje=0.12)
        else:
            self.color_hover = CARD_BG_HOV

        super().__init__(
            master, width=ancho, height=alto,
            bg=self.color_base,
            bd=1, highlightthickness=1
        )
        self.configure(highlightbackground=BORDE)
        self.pack_propagate(False)

        self._btn = tk.Button(
            self, text=texto, image=imagen, compound="top",
            command=comando, cursor="hand2",
            bg=self.color_base, activebackground=self.color_hover,
            fg=CARD_TEXT, activeforeground=CARD_TEXT,
            bd=0, font=FUENTE_BOTON, padx=18, pady=14
        )

        self._btn.image = imagen
        self._btn.pack(fill="both", expand=True)

        # Efecto hover
        for w in (self, self._btn):
            w.bind("<Enter>", lambda _e, fr=self: fr._set_hover(True))
            w.bind("<Leave>", lambda _e, fr=self: fr._set_hover(False))


    # === Aplica hover a frame y botón ===
    def _set_hover(self, estado):
        if estado:
            self.configure(bg=self.color_hover)
            self._btn.configure(bg=self.color_hover)
        else:
            self.configure(bg=self.color_base)
            self._btn.configure(bg=self.color_base)

    # === Función para oscurecer un color hex ===
    def _oscurecer(self, color_hex, porcentaje=0.15):
        color_hex = color_hex.lstrip("#")
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)

        r = max(0, int(r * (1 - porcentaje)))
        g = max(0, int(g * (1 - porcentaje)))
        b = max(0, int(b * (1 - porcentaje)))

        return f"#{r:02X}{g:02X}{b:02X}"
