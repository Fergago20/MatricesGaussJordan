# core/newton.py

import sympy as sp
from core.biserccion import fraccion, evaluar_tolerancia

def calcular_newton_raphson(funcion, x0, tol, max_iter: int = 1000):
    """
    Método de Newton-Raphson clásico con punto inicial x0.

    Parámetros:
        funcion   : str o callable.
        x0        : punto inicial.
        tol       : tolerancia para el error aproximado (Ea).
        max_iter  : máximo de iteraciones.

    Retorna:
        (raiz, iteraciones, resultados)

    Donde resultados = [iter, xi, xi1, Ea, f(xi), f'(xi)]
    """

    # -------------------------------
    # Normalizar x0 (permite "1/3")
    # -------------------------------
    x0 = float(fraccion(x0))

    # -------------------------------
    # Construir f y f'
    # -------------------------------
    if isinstance(funcion, str):
        x = sp.symbols('x')

        # Permitir que 'e' y 'E' sean la constante matemática
        locals_dict = {
            "e": sp.E,
            "E": sp.E,
            "exp": sp.exp,
            "ln": sp.log,
            "sen": sp.sin,
            "tg": sp.tan
        }

        try:
            expr = sp.sympify(funcion, locals=locals_dict)
        except Exception as e:
            raise ValueError(f"Error al interpretar la función: {e}")

        # Derivada simbólica
        df_expr = sp.diff(expr, x)

        # Crear funciones numéricas seguras
        f_sym = sp.lambdify(x, expr, modules=["math"])
        df_sym = sp.lambdify(x, df_expr, modules=["math"])

        def f(xval):
            val = f_sym(xval)
            return float(val)

        def df(xval):
            val = df_sym(xval)
            return float(val)

    elif callable(funcion):
        # Función numérica directa
        f = funcion

        def df(xval, h=1e-6):
            return float((f(xval + h) - f(xval - h)) / (2 * h))

    else:
        raise TypeError("El argumento 'funcion' debe ser un string o callable.")

    # -------------------------------
    # Iteración de Newton-Raphson
    # -------------------------------
    xi = x0
    resultados = []

    for it in range(1, max_iter + 1):

        fxi = f(xi)
        dfxi = df(xi)

        # Evitar división entre cero o derivada peligrosa
        if abs(dfxi) < 1e-14:
            raise ZeroDivisionError(
                f"La derivada es demasiado pequeña (f'({xi}) = {dfxi}). "
                f"Newton-Raphson no puede continuar."
            )

        # Cálculo de Newton
        xi1 = xi - fxi / dfxi

        # Error relativo
        if xi1 != 0:
            Ea = abs((xi1 - xi) / xi1)
        else:
            Ea = abs(xi1 - xi)

        resultados.append([
            it,
            float(xi),
            float(xi1),
            float(Ea),
            float(fxi),
            float(dfxi)
        ])

        # Criterio de paro
        if evaluar_tolerancia(Ea, tol):
            return float(xi1), it, resultados

        xi = xi1

    raise RuntimeError(
        "Newton-Raphson alcanzó el máximo de iteraciones sin converger."
    )
