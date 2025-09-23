# __future__.annotations permite usar anotaciones de tipo con nombres definidos más adelante
# (y evita algunos problemas de orden de definición en Python 3.7+).
from __future__ import annotations

# sys: para detectar plataforma (Windows/Linux/macOS) al maximizar ventana.
# re: expresiones regulares (validación de texto mientras se escribe).
import sys, re

# tkinter: GUI nativa de Python (Tk). Solo usamos tipos base como Tk, Toplevel.
import tkinter as tk

# Fraction: aritmética exacta con fracciones racionales (a/b) sin errores de redondeo.
from fractions import Fraction


# =============================================================================
# SECCIÓN 1 · Fracciones / Decimales
# =============================================================================

def texto_a_fraccion(texto: str) -> Fraction:
    t = (texto or "").strip()
    if not t:
        return Fraction(0, 1)
    t = t.replace(" ", "")
    try:
        # Si el usuario usa coma decimal y no hay punto ni barra, cámbiala por punto.
        if "," in t and "." not in t and "/" not in t:
            t = t.replace(",", ".")
        return Fraction(t)  # acepta 'a/b' o un decimal en str
    except Exception:
        # Si Fraction(str) falla (p.ej. algo como "-.5"), probamos con float
        # y luego aproximamos a una fracción razonable.
        return Fraction(float(t)).limit_denominator()


def fraccion_a_str(fr: Fraction) -> str:
    fr = fr if isinstance(fr, Fraction) else Fraction(fr).limit_denominator()
    return f"{fr.numerator}" if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def hay_fracciones_en_lista(valores) -> bool:
    for v in valores:
        if isinstance(v, Fraction) and v.denominator != 1:
            return True
    return False


# Fachada para la interfaz (nombre en español para mantener consistencia en UI).
a_fraccion = texto_a_fraccion


# =============================================================================
# SECCIÓN 2 · Formato de ecuaciones y matrices
# =============================================================================

def formatear_ecuacion_linea(fila):
    n = len(fila) - 1
    b = fila[-1]
    partes = []
    for i in range(n):
        c = fila[i]
        if c == 0:
            continue
        # Si es el primer término, no anteponer " + "; si es negativo, usar " - ".
        signo = " - " if c < 0 else (" + " if partes else "")
        partes.append(f"{signo}{fraccion_a_str(abs(c))}x{i+1}")
    izquierda = "".join(partes) if partes else "0"
    return f"{izquierda} = {fraccion_a_str(b)}"


def matriz_alineada(matriz, con_barra: bool = False) -> str:
    if not matriz:
        return ""
    cols = len(matriz[0])
    anchos = [0] * cols    # ancho máximo de cada columna, en caracteres
    celdas = []

    # 1) Calcular anchos: convierte cada valor a 'a/b' o entero y mide longitud.
    for fila in matriz:
        fila_txt = []
        for c in range(cols):
            t = fraccion_a_str(fila[c])
            anchos[c] = max(anchos[c], len(t))
            fila_txt.append(t)
        celdas.append(fila_txt)

    # 2) Construir líneas con padding y barra opcional antes de la última columna.
    lineas = []
    for fila_txt in celdas:
        piezas = []
        for c in range(cols):
            celda = fila_txt[c].rjust(anchos[c])  # alinear a la derecha
            if con_barra and c == cols - 2:       # posición antes de la última columna
                piezas.append(celda + " |")
            else:
                piezas.append(celda)
        lineas.append("[ " + "  ".join(piezas) + " ]")
    return "\n".join(lineas)


def bloque_matriz(matriz, con_barra: bool = True) -> str:
    return matriz_alineada(matriz, con_barra=con_barra) + "\n"


def matriz_alineada_con_titulo(titulo, matriz, con_barra: bool = True) -> str:
    return f"{titulo}\n{matriz_alineada(matriz, con_barra=con_barra)}\n"


def encabezado_operacion(texto: str) -> str:
    return f"\nOperación: {texto}\n"


def ecuaciones_desde_matriz(matriz) -> str:
    return "\n".join(formatear_ecuacion_linea(f) for f in matriz) + "\n"


# =============================================================================
# SECCIÓN 3 · Validación de entradas (Entry de Tkinter)
# =============================================================================

# Patrón permisivo "mientras escribes":
# - vacío
# - signo inicial opcional (+/-)
# - dígitos
# - un único separador decimal (punto o coma) en el numerador
# - una barra '/' para fracción (denominador solo dígitos, sin signo ni decimales)
_PATRON = re.compile(r"""^$|^[-+]?(\d+)?([.,]\d+)?(\/\d+)?$""")


def patron_valido_para_coeficiente(texto_propuesto: str) -> bool:
    t = (texto_propuesto or "").strip()
    if t == "":
        return True  # permitir vacío mientras escribe

    # 1) Filtro rápido: caracteres globalmente permitidos
    permitidos = set("+-0123456789.,/")
    if any(ch not in permitidos for ch in t):
        return False

    # 2) Signos: como máximo 1, y solo en la primera posición
    if t.count("+") + t.count("-") > 1:
        return False
    if ("+" in t or "-" in t) and not (t[0] in "+-"):
        return False

    # 3) Partir por '/', como máximo 2 partes (numerador/denominador)
    partes = t.split("/")
    if len(partes) > 2:
        return False

    numerador = partes[0]  # puede ser '', '+', '-', '.', '-.', etc. durante la edición

    # 4) Solo 1 separador decimal en el numerador ('.' o ',')
    if numerador.count(".") + numerador.count(",") > 1:
        return False

    # 5) Si hay denominador, permitir vacío durante edición,
    #    pero sin signos ni decimales; solo dígitos.
    if len(partes) == 2:
        denominador = partes[1]
        if any(ch in "+-.,"
               for ch in denominador):
            return False
        if not denominador.isdigit() and denominador != "":
            return False

    return True


# =============================================================================
# SECCIÓN 4 · Utilidades de ventana (centrar, minsize, cubrir pantalla)
# =============================================================================

# Tamaños mínimos para que la UI no se rompa al redimensionar.
MIN_ANCHO = 1100
MIN_ALTO  = 680


def _centrar_ventana(win: tk.Tk | tk.Toplevel, ancho: int, alto: int):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw // 2) - (ancho // 2), (sh // 2) - (alto // 2)
    win.geometry(f"{ancho}x{alto}+{x}+{y}")


def _maximizar_cubrir_pantalla(win: tk.Tk | tk.Toplevel):
    win.update_idletasks()
    if sys.platform.startswith("win"):
        try:
            win.state("zoomed")
            return
        except Exception:
            pass
    # Fallback genérico: ocupar toda la pantalla
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{sw}x{sh}+0+0")


def preparar_ventana(win: tk.Tk | tk.Toplevel, usar_maximizada: bool = True,
                     min_ancho: int = MIN_ANCHO, min_alto: int = MIN_ALTO):
    win.minsize(min_ancho, min_alto)
    _centrar_ventana(win, min_ancho, min_alto)
    if usar_maximizada:
        _maximizar_cubrir_pantalla(win)
