"""
Utilidades compactas para la app:
- Conversión segura texto → Fraction y presentación de fracciones
- Formateo de ecuaciones y matrices con columnas alineadas
- Validación de entradas en los Entry (sin letras ni símbolos raros)
- Utilidades de ventana: centrar, tamaño mínimo y cubrir pantalla
"""
from __future__ import annotations
import sys, re
import tkinter as tk
from fractions import Fraction

# ====== Fracciones / Decimales ======

def texto_a_fraccion(texto: str) -> Fraction:
    """Convierte '3', '2.5', '1,75', '7/4' → Fraction. Vacío → 0."""
    t = (texto or "").strip()
    if not t:
        return Fraction(0, 1)
    t = t.replace(" ", "")
    try:
        if "," in t and "." not in t and "/" not in t:
            t = t.replace(",", ".")
        return Fraction(t)           # acepta 'a/b' o decimal en str
    except Exception:
        return Fraction(float(t)).limit_denominator()

def fraccion_a_str(fr: Fraction) -> str:
    fr = fr if isinstance(fr, Fraction) else Fraction(fr).limit_denominator()
    return f"{fr.numerator}" if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"

def hay_fracciones_en_lista(valores) -> bool:
    for v in valores:
        if isinstance(v, Fraction) and v.denominator != 1:
            return True
    return False

# Fachada para la interfaz (nombres en español)
a_fraccion = texto_a_fraccion

# ====== Formato de ecuaciones y matrices ======

def formatear_ecuacion_linea(fila):
    """'2x1 + 3x2 - 4x3 = 7' a partir de [a1,...,an,b]."""
    n = len(fila) - 1
    b = fila[-1]
    partes = []
    for i in range(n):
        c = fila[i]
        if c == 0:
            continue
        signo = " - " if c < 0 else (" + " if partes else "")
        partes.append(f"{signo}{fraccion_a_str(abs(c))}x{i+1}")
    izquierda = "".join(partes) if partes else "0"
    return f"{izquierda} = {fraccion_a_str(b)}"

def matriz_alineada(matriz, con_barra: bool = False) -> str:
    """Alinea columnas. Si con_barra es True, separa la última columna con '|'.
    Retorna SIN salto final (útil si quieres controlar tú los \n).
    """
    if not matriz:
        return ""
    cols = len(matriz[0])
    anchos = [0]*cols
    celdas = []
    for fila in matriz:
        fila_txt = []
        for c in range(cols):
            t = fraccion_a_str(fila[c])
            anchos[c] = max(anchos[c], len(t))
            fila_txt.append(t)
        celdas.append(fila_txt)

    lineas = []
    for fila_txt in celdas:
        piezas = []
        for c in range(cols):
            celda = fila_txt[c].rjust(anchos[c])
            if con_barra and c == cols-2:  # antes de la última columna
                piezas.append(celda + " |")
            else:
                piezas.append(celda)
        lineas.append("[ " + "  ".join(piezas) + " ]")
    return "\n".join(lineas)

def bloque_matriz(matriz, con_barra: bool = True) -> str:
    """Devuelve la matriz alineada + un salto de línea al final."""
    return matriz_alineada(matriz, con_barra=con_barra) + "\n"

def matriz_alineada_con_titulo(titulo, matriz, con_barra: bool = True) -> str:
    """Incluye salto de línea al final (obligatorio pedirlo el profe)."""
    return f"{titulo}\n{matriz_alineada(matriz, con_barra=con_barra)}\n"

def encabezado_operacion(texto: str) -> str:
    return f"\nOperación: {texto}\n"

def ecuaciones_desde_matriz(matriz) -> str:
    """Devuelve las ecuaciones (una por fila) generadas desde la matriz aumentada."""
    return "\n".join(formatear_ecuacion_linea(f) for f in matriz) + "\n"

# ====== Validación de entradas ======

_PATRON = re.compile(r"""^$|^[-+]?(\d+)?([.,]\d+)?(\/\d+)?$""")
def patron_valido_para_coeficiente(texto_propuesto: str) -> bool:
    """
    Retorna True si 'texto_propuesto' es una entrada aceptable mientras se escribe.
    Acepta:
      - vacío (permite que el usuario borre y vuelva a escribir)
      - signo inicial (+/-)
      - dígitos
      - UN punto o UNA coma en el numerador ('.' o ',')
      - UNA barra '/' (fracciones). El denominador debe contener solo dígitos.
    Ejemplos permitidos durante edición: ".", "-.", ".5", "1.", "-0.7", "3/","3/4","-1.2/5"
    """
    t = (texto_propuesto or "").strip()
    if t == "":
        return True  # permitir vacío mientras escribe
    
    # Caracteres permitidos globalmente
    permitidos = set("+-0123456789.,/")
    if any(ch not in permitidos for ch in t):
        return False
    
    # El signo (si existe) solo al inicio y solo 1
    if t.count("+") + t.count("-") > 1:
        return False
    if ("+" in t or "-" in t) and not (t[0] in "+-"):
        return False
    
    # Separar numerador/denominador si hay '/'
    partes = t.split("/")
    if len(partes) > 2:
        return False
    
    numerador = partes[0]  # puede ser "", "+", "-", ".", "-.", etc. durante la edición
    # Solo 1 separador decimal global en el numerador ('.' o ',')
    if numerador.count(".") + numerador.count(",") > 1:
        return False
    
    # Si hay denominador, permitir que esté vacío durante edición pero solo con dígitos (sin signos ni decimales)
    if len(partes) == 2:
        denominador = partes[1]
        # Nada de signos ni puntos/commas en el denominador
        if any(ch in "+-.,"
               for ch in denominador):
            return False
        if not denominador.isdigit() and denominador != "":
            return False
    return True

# ====== Utilidades de ventana (centrar, minsize, cubrir pantalla) ======

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
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{sw}x{sh}+0+0")

def preparar_ventana(win: tk.Tk | tk.Toplevel, usar_maximizada: bool=True,
                     min_ancho: int=MIN_ANCHO, min_alto: int=MIN_ALTO):
    win.minsize(min_ancho, min_alto)
    _centrar_ventana(win, min_ancho, min_alto)
    if usar_maximizada:
        _maximizar_cubrir_pantalla(win)
