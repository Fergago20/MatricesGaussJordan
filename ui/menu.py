# ui/menu.py — menú con fondo azul oscuro, botones celestes
import os
import tkinter as tk
from soporte import preparar_ventana
from ui.gauss_app import AppGauss
from ui.gauss_jordan_app import AppGaussJordan
from ui.matrices_app import AppMatrices   # ← este será tu nuevo módulo

# ===== Paleta =====
FONDO_MENU   = "#0F172A"   # azul muy oscuro (fondo principal)
TEXTO_BLANCO = "#FFFFFF"   # texto general blanco
CARD_BG      = "#EAF5FF"   # celeste claro para los botones
CARD_TEXT    = "#6889AA"   # texto de los botones (azul grisáceo)
CARD_BG_HOV  = "#DDEEFF"   # hover más claro
BORDE        = "#CBD5E1"

def _ruta_recurso(relpath: str) -> str:
    base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, relpath)

def _cargar_y_escalar(ruta: str, max_w: int = 220, max_h: int = 220) -> tk.PhotoImage | None:
    if not os.path.exists(ruta):
        return None
    try:
        img = tk.PhotoImage(file=ruta)
    except Exception:
        return None

    w, h = img.width(), img.height()
    if w == 0 or h == 0:
        return img

    down = max(w // max_w if w > max_w else 1,
               h // max_h if h > max_h else 1)
    if down > 1:
        img = img.subsample(down, down)
        w, h = img.width(), img.height()

    up_w = max(1, min(3, max_w // max(1, w)))
    up_h = max(1, min(3, max_h // max(1, h)))
    up = max(1, min(up_w, up_h))
    if up > 1:
        img = img.zoom(up, up)

    return img

class BotonCard(tk.Frame):
    """Card con imagen + texto, mismo tamaño."""
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
            bd=0, font=("Segoe UI", 12, "bold"), padx=18, pady=14
        )
        self._btn.image = imagen
        self._btn.pack(fill="both", expand=True)

        self.bind("<Enter>", lambda _e: self.configure(bg=CARD_BG_HOV))
        self.bind("<Leave>", lambda _e: self.configure(bg=CARD_BG))
        for w in (self, self._btn):
            w.bind("<Enter>", lambda _e, fr=self: fr.configure(bg=CARD_BG_HOV))
            w.bind("<Leave>", lambda _e, fr=self: fr.configure(bg=CARD_BG))

def mostrar_menu():
    root = tk.Tk()
    root.title("Sistema de Ecuaciones — Métodos de Eliminación")
    root.configure(bg=FONDO_MENU)
    preparar_ventana(root, usar_maximizada=True)

    # Contenedor principal centrado
    centro = tk.Frame(root, bg=FONDO_MENU)
    centro.pack(expand=True)

    titulo = tk.Label(
        centro,
        text="Sistemas de Ecuaciones y Operaciones con Matrices",
        fg=TEXTO_BLANCO, bg=FONDO_MENU, font=("Segoe UI", 26, "bold")
    )
    titulo.pack(pady=(10, 6))

    subtitulo = tk.Label(
        centro,
        text="Resuelve sistemas de ecuaciones por métodos de Gauss o Gauss-Jordan y aplica operaciones básicas con matrices.",
        fg=TEXTO_BLANCO, bg=FONDO_MENU, font=("Segoe UI", 12)
    )
    subtitulo.pack(pady=(0, 24))

    # Imágenes
    ruta_gauss = _ruta_recurso(os.path.join("imagenes", "Gauss_Royal.png"))
    ruta_gj    = _ruta_recurso(os.path.join("imagenes", "GaussJordan_Royal.png"))
    ruta_mat   = _ruta_recurso(os.path.join("imagenes", "OperacionesMatrices.png"))

    img_gauss  = _cargar_y_escalar(ruta_gauss, 220, 220)
    img_gj     = _cargar_y_escalar(ruta_gj,    220, 220)
    img_mat    = _cargar_y_escalar(ruta_mat,   220, 220)

    # Acciones de navegación
    def volver_desde_hijas():
        root.deiconify()
        try: root.state("zoomed")
        except Exception: pass

    def abrir_gauss():
        root.withdraw()
        AppGauss(toplevel_parent=root, on_volver=volver_desde_hijas)

    def abrir_gj():
        root.withdraw()
        AppGaussJordan(toplevel_parent=root, on_volver=volver_desde_hijas)

    def abrir_matrices():
        root.withdraw()
        AppMatrices(toplevel_parent=root, on_volver=volver_desde_hijas)

    # Fila de cards
    fila = tk.Frame(centro, bg=FONDO_MENU)
    fila.pack()

    card1 = BotonCard(fila, "Método de Gauss", img_gauss, abrir_gauss)
    card1.grid(row=0, column=0, padx=28, pady=8)

    card2 = BotonCard(fila, "Método de Gauss-Jordan", img_gj, abrir_gj)
    card2.grid(row=0, column=1, padx=28, pady=8)

    card3 = BotonCard(fila, "Operaciones con Matrices", img_mat, abrir_matrices)
    card3.grid(row=0, column=2, padx=28, pady=8)

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
