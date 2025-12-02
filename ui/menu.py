import os
import tkinter as tk
from soporte.helpers import preparar_ventana, ruta_recurso, cargar_y_escalar
from ui.componentes import BotonCard
from ui.estilos import FONDO_MENU, TEXTO_BLANCO, FUENTE_TITULO, FUENTE_SUBTITULO
from ui.resolver_sistemas_app import AppResolverSistemas  
from ui.matrices_app import AppMatrices
from ui.app_vectores import AppIndependenciaLineal
from ui.Met_numericos import AppMetodosNumericos
from ui.met_numericos2 import AppMetodosNumericos as AppMetodosNumericos2


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
        text="Sistemas de Ecuaciones, Operaciones con Matrices y Métodos Numéricos",
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
    img_resolver = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "gauss_gaussjordan.png")))  
    img_mat = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "OperacionesMatrices.png")))
    img_vectores = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "Vectores.png")))
    img_numericos = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "MetodoNumerico.png")))

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
        "Resolución\nSistemas de Ecuaciones",
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

    BotonCard(
        fila,
        "Métodos Numéricos",
        img_numericos,
        lambda: abrir_submenu_metodos(root)
    ).grid(row=0, column=3, padx=28, pady=8)

    def abrir_modulo(AppClase):
        root.withdraw()
        AppClase(toplevel_parent=root, on_volver=volver_desde_hijas)

    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()



# ============================================================
#    ⬇ SUBMENÚ DE MÉTODOS NUMÉRICOS — VENTANA SEPARADA ⬇
# ============================================================

def abrir_submenu_metodos(root):
    root.withdraw()   # Ocultar menú principal

    sub = tk.Toplevel(root)
    sub.title("Métodos Numéricos")
    sub.configure(bg=FONDO_MENU)

    try:
        sub.state("zoomed")
    except:
        pass

    # Contenedor central — Igual que en el menú principal
    centro = tk.Frame(sub, bg=FONDO_MENU)
    centro.pack(expand=True)

    # ===== TÍTULO =====
    titulo = tk.Label(
        centro,
        text="Métodos Numéricos",
        fg=TEXTO_BLANCO,
        bg=FONDO_MENU,
        font=FUENTE_TITULO
    )
    titulo.pack(pady=(10, 6))

    # ===== DESCRIPCIÓN =====
    descripcion = tk.Label(
        centro,
        text="Selecciona el método numérico que deseas utilizar. "
             "\nCada método permite aproximar raíces de ecuaciones aplicando técnicas distintas.",
        fg=TEXTO_BLANCO,
        bg=FONDO_MENU,
        font=FUENTE_SUBTITULO,
        wraplength=900,
        justify="center"
    )
    descripcion.pack(pady=(0, 24))

    # ===== FILA DE BOTONES =====
    fila_botones = tk.Frame(centro, bg=FONDO_MENU)
    fila_botones.pack()

    # Cargar imágenes
    img_bfp = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "Biseccion_FalsaPosicion.png")))
    img_nr = cargar_y_escalar(ruta_recurso(os.path.join("imagenes", "Newton-Raphson.png")))

    # Botón 1: Bisección y Falsa Posición
    BotonCard(
        fila_botones,
        "Bisección\nFalsa Posición",
        img_bfp,
        lambda: abrir_biseccion(root, sub),
        color_fondo="#BADFF9"
    ).grid(row=0, column=0, padx=28, pady=8)

    # Botón 2: Newton-Raphson
    BotonCard(
        fila_botones,
        "Newton-Raphson\nSecante",
        img_nr,
        lambda: abrir_newton(root, sub),
        color_fondo="#C7EAFD"
    ).grid(row=0, column=1, padx=28, pady=8)

    # ===== BARRA INFERIOR (BOTÓN VOLVER) =====
    barra_inf = tk.Frame(sub, bg=FONDO_MENU)
    barra_inf.pack(fill="x", pady=(0, 8), padx=10)

    estilo_btn = {
        "bg": "#445566",
        "fg": "white",
        "font": ("Arial", 13),
        "padx": 10,
        "pady": 6
    }

    tk.Button(
        barra_inf,
        text="← Volver al menú principal",
        command=lambda: volver(sub, root),
        **estilo_btn
    ).pack(side="left")

    # Si presiona X se cierra TODA la app
    sub.protocol("WM_DELETE_WINDOW", lambda: cerrar_todo(root))

def abrir_biseccion(root, sub):
    # Cerrar submenú
    sub.destroy()

    # Abrir la ventana completa de Bisección/Falsa Posición
    AppMetodosNumericos(
        toplevel_parent=root,
        on_volver=lambda: volver_a_submenu(root)
    )

def abrir_newton(root, sub):
    # Cerrar submenú
    sub.destroy()

    # Abrir la ventana completa de Newton-Raphson
    AppMetodosNumericos2(
        toplevel_parent=root,
        on_volver=lambda: volver_a_submenu(root)
    )
    
def volver_a_submenu(root):
    root.withdraw()  # vuelve a ocultar el menú principal
    abrir_submenu_metodos(root)

def volver(sub, root):
    sub.destroy()
    root.deiconify()  # mostrar ventana principal
    try:
        root.state("zoomed")
    except:
        pass


def cerrar_todo(root):
    root.destroy()