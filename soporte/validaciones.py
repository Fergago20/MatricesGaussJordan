# soporte/validaciones.py
from fractions import Fraction
import re

# =====================================================
#   FUNCIONES DE VALIDACIÓN Y CONVERSIÓN DE VALORES
# =====================================================

# --- Expresiones válidas para entradas ---
PATRON_COEF = re.compile(r"^-?\d*(?:\.\d*)?(?:/\d*)?$")


def patron_valido_para_coeficiente(texto: str) -> bool:
    """
    Valida el texto ingresado en los Entry para permitir:
    - Enteros: 2, -5
    - Decimales: 3.14, -0.5
    - Fracciones: 3/4, -2/5
    También permite vacío temporalmente durante la escritura.
    """
    return texto == "" or bool(PATRON_COEF.fullmatch(texto))


# =====================================================
#   CONVERSIONES DE TIPO
# =====================================================

def a_fraccion(valor) -> Fraction:
    """
    Convierte una cadena o número a fracción exacta.
    Ejemplo:
    >>> a_fraccion("3/4") → Fraction(3, 4)
    >>> a_fraccion("1.5") → Fraction(3, 2)
    >>> a_fraccion(2)     → Fraction(2, 1)
    """
    try:
        if isinstance(valor, Fraction):
            return valor
        if isinstance(valor, (int, float)):
            return Fraction(valor)
        valor = valor.strip()
        if "/" in valor:
            return Fraction(valor)
        if valor == "" or valor == "-":
            return Fraction(0)
        return Fraction(str(float(valor)))
    except Exception:
        return Fraction(0)


def fraccion_a_str(valor: Fraction) -> str:
    """
    Devuelve una fracción como cadena simplificada.
    Si el denominador es 1, devuelve solo el numerador.
    Ejemplo: 3/1 → "3"
    """
    if not isinstance(valor, Fraction):
        valor = a_fraccion(valor)
    return str(valor.numerator) if valor.denominator == 1 else f"{valor.numerator}/{valor.denominator}"


def hay_fracciones_en_lista(lista):
    """
    Retorna True si en una lista de fracciones hay denominadores distintos de 1.
    Ejemplo:
    >>> hay_fracciones_en_lista([Fraction(1, 2), Fraction(3, 1)]) → True
    """
    try:
        return any(x.denominator != 1 for x in lista)
    except Exception:
        return False


# =====================================================
#   LECTURA Y LIMPIEZA DE MATRICES
# =====================================================

def limpiar_matriz(entradas):
    """
    Convierte una matriz de Entry (Tkinter) a una lista numérica (Fraction).
    Sustituye vacíos o errores por 0.
    """
    matriz = []
    for fila in entradas:
        fila_vals = []
        for e in fila:
            try:
                texto = e.get().strip()
                if texto == "":
                    fila_vals.append(Fraction(0))
                else:
                    fila_vals.append(a_fraccion(texto))
            except Exception:
                fila_vals.append(Fraction(0))
        matriz.append(fila_vals)
    return matriz

def matriz_esta_vacia(matriz):
    """
    Devuelve True si todos los campos de la matriz están vacíos o contienen solo espacios.
    """
    for fila in matriz:
        for e in fila:
            if e.get().strip() != "":
                return False
    return True
