import os
import tkinter as tk
from soporte.helpers import preparar_ventana, ruta_recurso, cargar_y_escalar
from ui.componentes import BotonCard
from ui.estilos import FONDO_MENU, TEXTO_BLANCO, FUENTE_TITULO, FUENTE_SUBTITULO
from ui.resolver_sistemas_app import AppResolverSistemas   # ✅ nuevo archivo unificado
from ui.matrices_app import AppMatrices
from ui.app_vectores import AppIndependenciaLineal

def mostrar_menu():
    root = tk.Tk()
    root.title("Calculadora de Álgebra Lineal — Métodos y Operaciones")
    root.configure(bg=FONDO_MENU)
    preparar_ventana(root, usar_maximizada=True)

    # --- CONTENEDOR CENTRAL ---
    centro = tk.Frame(root, bg=FONDO_MENU)
    centro.pack(expand=True)

    titulo = tk.Label(
        centro,
        text="Sistemas de Ecuaciones y Operaciones con Matrices",
        fg=TEXTO_BLANCO, bg=FONDO_MENU, font=FUENTE_TITULO
    )
    titulo.pack(pady=(10, 6))

    subtitulo = tk.Label(
        centro,
        text="Resuelve sistemas de ecuaciones con Gauss o Gauss-Jordan, o realiza operaciones básicas con matrices.",
        fg=TEXTO_BLANCO, bg=FONDO_MENU, font=FUENTE_SUBTITULO
    )
    subtitulo.pack(pady=(0, 24))

    # --- IMÁGENES ---
    img_resolver = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "gauss_gaussjordan.png")))  # ✅ nueva imagen
    img_mat = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "OperacionesMatrices.png")))
    img_vectores = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "Vectores.png")))

    # --- ACCIONES ---
    def volver_desde_hijas():
        root.deiconify()
        try:
            root.state("zoomed")
        except Exception:
            pass

    fila = tk.Frame(centro, bg=FONDO_MENU)
    fila.pack()

    BotonCard(
        fila,
        "Gauss / Gauss-Jordan",
        img_resolver,
        lambda: abrir_modulo(AppResolverSistemas)
    ).grid(row=0, column=0, padx=28, pady=8)

    BotonCard(
        fila,
        "Operaciones con Matrices",
        img_mat,
        lambda: abrir_modulo(AppMatrices)
    ).grid(row=0, column=1, padx=28, pady=8)

    BotonCard(
        fila,
        "Dependencia de Vectores",
        img_vectores,
        lambda: abrir_modulo(AppIndependenciaLineal)
    ).grid(row=0, column=2, padx=28, pady=8)

    def abrir_modulo(AppClase):
        root.withdraw()
        AppClase(toplevel_parent=root, on_volver=volver_desde_hijas)

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
