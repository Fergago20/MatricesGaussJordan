import sympy as sp
import math
from fractions import Fraction
import numpy as np


def fraccion(x):
    """Convierte la entrada a fracción si es posible (cadena como '1/2' o número)."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int) or isinstance(x, float):
        return Fraction(x)
    try:
        return Fraction(str(x))
    except ValueError:
        raise ValueError(f"No se puede convertir {x} a una fracción válida.")


def punto_medio(a, b):
    """Calcula el punto medio entre a y b."""
    return (a + b) / 2


def limpiar_ecuacion(ecuacion_str: str) -> str:
    """Normaliza la ecuación para que sea entendible por sympy."""
    reemplazos = {
        '^': '**',
        'ln(': 'log(',
        'e^': 'exp(',
        '÷': '/',
        '√': 'sqrt('
    }

    for viejo, nuevo in reemplazos.items():
        ecuacion_str = ecuacion_str.replace(viejo, nuevo)

    return ecuacion_str


def evaluar_en_punto(ecuacion_str, x_val):
    """Evalúa la ecuación en un punto x_val. Limpia y normaliza antes de procesar."""
    x = sp.symbols('x')
    try:
        # 🔹 Limpieza básica
        ecuacion_str = ecuacion_str.strip()
        ecuacion_str = ecuacion_str.replace("=0", "").strip()
        ecuacion_str = ecuacion_str.replace("^", "**")
        ecuacion_str = ecuacion_str.replace("ln(", "log(")
        ecuacion_str = ecuacion_str.replace("e^", "exp(")
        ecuacion_str = ecuacion_str.replace("√", "sqrt(")
        ecuacion_str = ecuacion_str.replace("÷", "/")

        #Cerrar paréntesis si se abrió por exp( pero no se cerró
        # (esto evita errores en expresiones tipo e^(-x))
        if ecuacion_str.count("(") > ecuacion_str.count(")"):
            ecuacion_str += ")" * (ecuacion_str.count("(") - ecuacion_str.count(")"))

        #Crear expresión Sympy y evaluar
        expr = sp.sympify(ecuacion_str)
        resultado = expr.subs(x, x_val)

        # Validar dominio (por ejemplo, log(0))
        if resultado.is_real is False or resultado.has(sp.zoo) or resultado.has(sp.nan):
            raise ValueError("La función no está definida en este punto.")

        return float(resultado)

    except Exception as e:
        raise ValueError(
            f"No se pudo evaluar la función en x={x_val}. "
            f"Revisa la ecuación: '{ecuacion_str}'. Detalle: {e}"
        )



def valor_funcion(funcion_input, x):
    """Evalúa la función en el punto x (string o callable)."""
    if isinstance(funcion_input, str):
        return evaluar_en_punto(funcion_input, x)
    elif callable(funcion_input):
        return funcion_input(x)
    else:
        raise TypeError("El argumento 'funcion' debe ser un string o un callable.")


def valores_intervalos(fa, fc):
    """Determina en qué subintervalo se encuentra la raíz."""
    return fa * fc < 0


def evaluar_tolerancia(fc, tol):
    """Verifica si el valor absoluto de fc es menor que la tolerancia."""
    return abs(fc) < tol


def evaluar_primera_condicion(fa, fb):
    """Verifica si los valores en los extremos del intervalo tienen signos opuestos."""
    return fa * fb < 0


def interpretar_tolerancia(tol_str):
    """Permite ingresar tolerancias como 10^-4, 1e-4, etc."""
    try:
        # Reemplazar ^ por ** para potencias correctas
        tol_str = str(tol_str).replace("^", "**")
        return float(eval(tol_str, {"__builtins__": None}, {"pow": pow, "e": math.e, "E": math.e}))
    except Exception:
        raise ValueError(f"Tolerancia no válida: {tol_str}")


def calcular_biseccion(funcion, a, b, tol):
    """Ejecuta el método de bisección clásico."""
    # Permitir que tol llegue como cadena tipo "10^-4"
    if isinstance(tol, str):
        tol = interpretar_tolerancia(tol)

    intervalo1 = fraccion(a)
    intervalo2 = fraccion(b)
    c = punto_medio(intervalo1, intervalo2)

    # Evaluar extremos
    fa = valor_funcion(funcion, intervalo1)
    fb = valor_funcion(funcion, intervalo2)

    if not evaluar_primera_condicion(fa, fb):
        raise ValueError("La función debe tener signos opuestos en los extremos del intervalo [a, b].")

    fc = valor_funcion(funcion, c)
    iteraciones = 0
    resultados = []

    # Evitar bucles infinitos por funciones planas
    max_iter = 200

    while not evaluar_tolerancia(fc, tol) and iteraciones < max_iter:
        if valores_intervalos(fa, fc):
            intervalo2 = c
            fb = fc
        else:
            intervalo1 = c
            fa = fc

        c = punto_medio(intervalo1, intervalo2)
        fc = valor_funcion(funcion, c)

        resultados.append([
            iteraciones + 1,
            float(intervalo1),
            float(intervalo2),
            float(c),
            float(fa),
            float(fb),
            float(fc)
        ])
        iteraciones += 1

    if iteraciones >= max_iter:
        raise ValueError("El método no converge después de 200 iteraciones.")

    return float(c), iteraciones, resultados
