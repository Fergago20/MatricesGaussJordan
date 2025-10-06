# soporte/helpers.py
import tkinter as tk
import os

# =====================================================
#   CONFIGURACIÓN Y UTILIDADES DE INTERFAZ (UI)
# =====================================================

def preparar_ventana(ventana: tk.Toplevel, usar_maximizada: bool = False):
    """
    Configura una ventana Tkinter:
    - Centrada en pantalla (si usar_maximizada=False)
    - Maximizada (si usar_maximizada=True)
    - Define color de fondo uniforme si existe atributo bg.
    """
    ventana.update_idletasks()
    if usar_maximizada:
        try:
            ventana.state("zoomed")  # Windows
        except Exception:
            ventana.attributes("-zoomed", True)  # Linux/Mac
    else:
        ancho = 900
        alto = 600
        x = (ventana.winfo_screenwidth() - ancho) // 2
        y = (ventana.winfo_screenheight() - alto) // 2
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    # Fondo coherente si la ventana tiene un color definido
    color_bg = getattr(ventana, "bg", None)
    if color_bg:
        ventana.configure(bg=color_bg)

    ventana.minsize(800, 500)


def centrar_widget(widget: tk.Widget):
    """
    Centra un widget dentro de su contenedor usando pack().
    Ideal para mensajes de carga, pantallas iniciales, etc.
    """
    widget.pack(expand=True, anchor="center")


def crear_separador(parent, altura=2, color="#ccc"):
    """
    Crea una línea horizontal como separador visual entre secciones.
    """
    separador = tk.Frame(parent, height=altura, bg=color)
    separador.pack(fill="x", pady=4)
    return separador


def limpiar_textos(*widgets):
    """
    Limpia el contenido de múltiples widgets Text o Entry.
    Ejemplo:
        limpiar_textos(texto_proc, texto_sol)
    """
    for w in widgets:
        try:
            if isinstance(w, tk.Text):
                w.delete("1.0", "end")
            elif isinstance(w, tk.Entry):
                w.delete(0, "end")
        except Exception:
            pass


def mostrar_info(titulo: str, mensaje: str):
    """
    Muestra una ventana emergente de información.
    """
    from tkinter import messagebox
    messagebox.showinfo(titulo, mensaje)


def mostrar_error(titulo: str, mensaje: str):
    """
    Muestra una ventana emergente de advertencia o error.
    """
    from tkinter import messagebox
    messagebox.showwarning(titulo, mensaje)

def ruta_recurso(relpath: str) -> str:
    """
    Devuelve la ruta absoluta de un recurso (imagen, etc.)
    relativo al directorio base del proyecto.
    """
    base = os.path.dirname(os.path.dirname(__file__))  # sube desde soporte/
    return os.path.join(base, relpath)

def cargar_y_escalar(ruta: str, max_w: int = 220, max_h: int = 220) -> tk.PhotoImage | None:
    """
    Carga una imagen desde 'ruta' y la escala a un tamaño máximo.
    Si no se puede cargar, devuelve None.
    """
    if not os.path.exists(ruta):
        return None
    try:
        img = tk.PhotoImage(file=ruta)
    except Exception:
        return None

    w, h = img.width(), img.height()
    if w == 0 or h == 0:
        return img

    # Escalado proporcional hacia abajo
    down = max(w // max_w if w > max_w else 1, h // max_h if h > max_h else 1)
    if down > 1:
        img = img.subsample(down, down)
        w, h = img.width(), img.height()

    # Escalado leve hacia arriba si es necesario
    up_w = max(1, min(3, max_w // max(1, w)))
    up_h = max(1, min(3, max_h // max(1, h)))
    up = max(1, min(up_w, up_h))
    if up > 1:
        img = img.zoom(up, up)

    return img