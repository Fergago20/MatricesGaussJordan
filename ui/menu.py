# ui/menu.py
import os
import tkinter as tk

from soporte import preparar_ventana
from ui.gauss_app import AppGauss
from ui.gauss_jordan_app import AppGaussJordan


def _ruta_recurso(relpath: str) -> str:
    base = os.path.dirname(os.path.dirname(__file__))  # raíz del proyecto
    return os.path.join(base, relpath)

def _cargar_y_escalar(ruta: str, max_w: int = 180, max_h: int = 120):
    """Carga un PhotoImage y lo reescala (zoom/subsample entero) para que
    quepa dentro de max_w × max_h. Si no existe, devuelve None."""
    if not os.path.exists(ruta):
        return None
    try:
        img = tk.PhotoImage(file=ruta)
    except Exception:
        return None

    w, h = img.width(), img.height()
    if w == 0 or h == 0:
        return img

    # Reducir si se pasa del límite (división entera)
    down = max(w // max_w if w > max_w else 1,
               h // max_h if h > max_h else 1)
    if down > 1:
        img = img.subsample(down, down)
        w, h = img.width(), img.height()

    # Ampliar un poco si quedó muy pequeña (máx ×3)
    up_w = max(1, min(3, max_w // w))
    up_h = max(1, min(3, max_h // h))
    up = max(1, min(up_w, up_h))
    if up > 1:
        img = img.zoom(up, up)

    return img


class BotonGrandeImagen(tk.Frame):
    """Contenedor fijo para forzar el MISMO tamaño visual de ambos botones."""
    def __init__(self, master, texto, imagen, comando,
                 ancho=240, alto=220, **btnstyle):
        super().__init__(master, width=ancho, height=alto, bg="#E8C2D3", highlightthickness=0)
        self.pack_propagate(False)
        self._btn = tk.Button(self,
                              text=texto,
                              image=imagen,
                              command=comando,
                              compound="top",
                              **btnstyle)
        self._btn.image = imagen  # evitar GC
        self._btn.pack(fill="both", expand=True)


def mostrar_menu():
    root = tk.Tk()
    root.title("Sistema de Ecuaciones — Métodos de Eliminación")
    root.configure(bg="#E8C2D3")
    preparar_ventana(root, usar_maximizada=True)

    # ---------- Contenedor central ----------
    centro = tk.Frame(root, bg="#E8C2D3")
    centro.pack(expand=True)

    titulo = tk.Label(
        centro,
        text="Sistema de Ecuaciones — Métodos de Eliminación",
        fg="#0f172a",
        bg="#E8C2D3",
        font=("Segoe UI", 22, "bold")
    )
    titulo.pack(pady=(0, 6))

    subtitulo = tk.Label(
        centro,
        text="Elige un método para resolver tu sistema",
        fg="#0f172a",
        bg="#E8C2D3",
        font=("Segoe UI", 11)
    )
    subtitulo.pack(pady=(0, 20))

    # ---------- Imágenes ----------
    ruta_gauss = _ruta_recurso(os.path.join("imagenes", "black_G.png")) #
    ruta_gj    = _ruta_recurso(os.path.join("imagenes", "black_GJ.png")) #
    img_gauss  = _cargar_y_escalar(ruta_gauss, 180, 120)
    img_gj     = _cargar_y_escalar(ruta_gj,    180, 120)

    # ---------- Acciones ----------
    def volver_a_menu():
        root.deiconify()
        try:
            root.state("zoomed")
        except Exception:
            pass

    def abrir_gauss():
        root.withdraw()
        AppGauss(toplevel_parent=root, on_volver=volver_a_menu)

    def abrir_gauss_jordan():
        root.withdraw()
        AppGaussJordan(toplevel_parent=root, on_volver=volver_a_menu)

    # ---------- Botones centrados ----------
    fila = tk.Frame(centro, bg="#E8C2D3")
    fila.pack()

    estilo_btn = dict(
        bg="#D874A3",
        activebackground="#D874A3",
        fg="#111827",
        activeforeground="#111827",
        relief="raised",
        bd=2,
        cursor="hand2",
        font=("Segoe UI", 13, "bold"),
        padx=18,
        pady=14,
    )

    BotonGrandeImagen(fila, "Método de Gauss", img_gauss, abrir_gauss, **estilo_btn)\
        .grid(row=0, column=0, padx=28, pady=12)
    BotonGrandeImagen(fila, "Método de Gauss-Jordan", img_gj, abrir_gauss_jordan, **estilo_btn)\
        .grid(row=0, column=1, padx=28, pady=12)


    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
